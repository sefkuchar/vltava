"""Test viditeľnosti: spýtame sa AI asistenta s webovým vyhľadávaním tak, ako by sa pýtal zákazník,
a pozrieme sa, či odpoveď spomenie alebo odcituje náš obchod.

Demo používa Claude s web search. ChatGPT, Gemini a Perplexity sa dajú pridať rovnakým spôsobom cez ich API.
Odpovede AI sú nedeterministické – v produkcii treba každý dopyt opakovať a merať štatisticky.
"""

import os
from collections import Counter
from dataclasses import dataclass, field
from urllib.parse import urlparse

import anthropic
from pydantic import BaseModel

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")
WEB_SEARCH = {
    "type": "web_search_20260209",
    "name": "web_search",
    "max_uses": 5,
    "user_location": {"type": "approximate", "country": "CZ", "timezone": "Europe/Prague"},
}


class Prompts(BaseModel):
    prompts: list[str]


@dataclass
class Probe:
    prompt: str
    answer: str = ""
    cited_domains: list[str] = field(default_factory=list)
    mentioned: bool = False
    error: str = ""


def _domain(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def make_prompts(categories: list[str], n: int, client: anthropic.Anthropic) -> list[str]:
    resp = client.beta.messages.parse(
        model=MODEL,
        max_tokens=4000,
        thinking={"type": "adaptive"},
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": (
            f"Napiš {n} realistických dotazů, které by český zákazník položil AI asistentovi, když vybírá, "
            f"co a kde koupit v těchto kategoriích: {', '.join(categories)}. Dotazy piš přirozeně, s konkrétní "
            "potřebou nebo rozpočtem (např. 'Jakou tichou pračku do paneláku do 12 000 Kč a kde ji koupit?'). "
            "Nezmiňuj žádný konkrétní obchod.")}],
        output_format=Prompts,
    )
    return (resp.parsed_output.prompts if resp.parsed_output else [])[:n]


def probe(prompt: str, shop_domain: str, client: anthropic.Anthropic) -> Probe:
    result = Probe(prompt)
    messages = [{"role": "user", "content": prompt}]
    try:
        for _ in range(3):  # pause_turn: server-side vyhľadávanie môže turn prerušiť, pokračujeme
            resp = client.beta.messages.create(
                model=MODEL,
                max_tokens=8000,
                thinking={"type": "adaptive"},
                output_config={"effort": "low"},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                tools=[WEB_SEARCH],
                messages=messages,
            )
            if resp.stop_reason != "pause_turn":
                break
            messages = [*messages, {"role": "assistant", "content": resp.content}]
    except anthropic.APIError as e:
        result.error = f"{type(e).__name__}: {e}"
        return result

    urls = []
    texts = []
    for block in resp.content:
        if block.type == "text":
            texts.append(block.text)
            urls += [c.url for c in (block.citations or []) if getattr(c, "url", None)]
        elif block.type == "web_search_tool_result" and isinstance(block.content, list):
            urls += [r.url for r in block.content]
    result.answer = "\n".join(texts).strip()
    result.cited_domains = list(dict.fromkeys(_domain(u) for u in urls))
    shop = shop_domain.lower().removeprefix("www.")
    result.mentioned = shop in result.cited_domains or shop.split(".")[0] in result.answer.lower()
    return result


def top_domains(probes: list[Probe], k: int = 10) -> list[tuple[str, int]]:
    return Counter(d for p in probes for d in p.cited_domains).most_common(k)

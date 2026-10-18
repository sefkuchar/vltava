"""Obohatenie produktových dát cez Claude – len extrakcia z existujúcich dát, nič nevymýšľať.

Každý vyťažený parameter musí mať doslovný citát zo zdrojového textu. Deterministická kontrola potom
zahodí parametre, ktorých citát v zdroji nie je alebo ktorých čísla v citáte nesedia
(vymyslená „hlučnosť 45 dB“ je pre e-shop právne riziko – klamlivá obchodná praktika).
"""

import os
import re
import unicodedata
from dataclasses import dataclass, field

import anthropic
from pydantic import BaseModel, Field

from eshop.feed import Product

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")

SYSTEM = """Jsi specialista na produktová data pro e-shopy. Připravuješ data tak, aby jim rozuměli AI asistenti \
(ChatGPT, Gemini, Perplexity, Claude) a mohli produkt správně doporučit.

Absolutní pravidlo: pracuješ POUZE s informacemi ve vstupních datech produktu. Nikdy nevymýšlej parametry, \
čísla, certifikace ani vlastnosti. U každého parametru uveď v source_quote doslovný úryvek ze vstupu, ze kterého \
hodnota plyne. Když informace chybí, nepiš ji do parametrů – uveď ji v missing_info jako otázku, kterou by \
zákazník mohl položit.

Piš česky, věcně, bez marketingových superlativů."""


class Attribute(BaseModel):
    name: str = Field(description="Název parametru, např. 'Hloubka', 'Hlučnost při ždímání'")
    value: str = Field(description="Hodnota včetně jednotky, např. '38 cm'")
    source_quote: str = Field(description="Doslovný úryvek ze vstupních dat, ze kterého hodnota plyne")


class QA(BaseModel):
    question: str
    answer: str


class Enrichment(BaseModel):
    product_type: str = Field(description="Typ produktu jedním až třemi slovy, např. 'úzká pračka'")
    better_name: str = Field(description="Popisný název: značka + model + klíčová vlastnost; jen ze vstupních dat")
    short_description: str = Field(description="2–3 věcné věty pro AI asistenty, jen fakta ze vstupu")
    attributes: list[Attribute]
    use_cases: list[str] = Field(description="Pro koho / do jaké situace se produkt hodí – odvozeno ze vstupu")
    faq: list[QA] = Field(description="2–4 otázky zákazníka, na které vstupní data odpovídají")
    missing_info: list[str] = Field(description="Důležité informace, které ve vstupu chybí (formulováno jako otázky)")


@dataclass
class Result:
    product: Product
    data: Enrichment | None
    verified: list[Attribute] = field(default_factory=list)
    rejected: list[tuple[Attribute, str]] = field(default_factory=list)
    error: str = ""


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text).strip(" .,;:")


def _numbers(text: str) -> set[str]:
    return {n.replace(",", ".") for n in re.findall(r"\d+(?:[.,]\d+)?", text)}


def verify_attribute(attr: Attribute, source: str) -> str | None:
    """Vráti dôvod zamietnutia, alebo None ak je parameter podložený zdrojom."""
    if _norm(attr.source_quote) not in _norm(source):
        return "citát se ve zdrojových datech nenachází"
    missing = _numbers(attr.value) - _numbers(attr.source_quote)
    if missing:
        return f"čísla {', '.join(sorted(missing))} nejsou v citátu"
    return None


def enrich(product: Product, client: anthropic.Anthropic) -> Result:
    payload = (
        f"ITEM_ID: {product.item_id}\nNázev: {product.name}\nVýrobce: {product.manufacturer or '(neuvedeno)'}\n"
        f"Kategorie: {product.category}\nCena: {product.price} Kč\nPopis: {product.description or '(chybí)'}\n"
        f"Parametry: {'; '.join(f'{k}: {v}' for k, v in product.params.items()) or '(žádné)'}"
    )
    try:
        resp = client.beta.messages.parse(
            model=MODEL,
            max_tokens=8000,
            system=SYSTEM,
            thinking={"type": "adaptive"},
            output_config={"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content": payload}],
            output_format=Enrichment,
        )
    except anthropic.APIError as e:
        return Result(product, None, error=f"{type(e).__name__}: {e}")
    if resp.stop_reason == "refusal" or resp.parsed_output is None:
        return Result(product, None, error=f"Model nevrátil data (stop_reason={resp.stop_reason})")
    result = Result(product, resp.parsed_output)
    for attr in resp.parsed_output.attributes:
        reason = verify_attribute(attr, product.source_text)
        if reason:
            result.rejected.append((attr, reason))
        else:
            result.verified.append(attr)
    return result

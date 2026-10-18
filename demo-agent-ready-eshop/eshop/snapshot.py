"""Deterministická snímka auditu (audit.json) a Markdown reporty zo šablón.

Rovnaký vstup → bajtovo rovnaká snímka aj report: kľúče sú zoradené, zoznamy zoradené, bez časových značiek
(dátum sa zadáva parametrom). Jediná nedeterministická časť je test viditeľnosti v AI (živý web) –
je v snímke označená a pri porovnaní sa vyhodnocuje osobitne.
"""

import hashlib
import json
from pathlib import Path
from string import Template
from urllib.parse import urlparse

from eshop.enrich import Result
from eshop.score import CHECKS, ProductScore
from eshop.site import SEARCH_BOTS, TRAINING_BOTS, SiteReport
from eshop.visibility import Probe

SCHEMA_VERSION = 1
TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
LABELS = {k: label for k, _, label in CHECKS}


def file_hash(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def build(*, shop: str, label: str, run_date: str, feed_path: str, summary: dict, scores: list[ProductScore],
          site: SiteReport | None, results: list[Result], probes: list[Probe]) -> dict:
    snap: dict = {
        "schema_version": SCHEMA_VERSION,
        "meta": {"shop": shop, "label": label, "date": run_date, "feed_sha256": file_hash(feed_path)},
        "feed": {
            "score": summary["score"],
            "products": summary["products"],
            "issues": {i["key"]: i["count"] for i in summary["issues"]},
            "items": sorted(({"id": s.product.item_id, "name": s.product.name, "score": s.score,
                              "failed": sorted(s.failed)} for s in scores), key=lambda x: x["id"]),
        },
        "site": None,
        "enrichment": sorted(({"id": r.product.item_id, "verified": len(r.verified), "rejected": len(r.rejected)}
                              for r in results if r.data), key=lambda x: x["id"]),
        "visibility": {
            "deterministic": False,
            "probes": [{"prompt": p.prompt, "mentioned": p.mentioned, "cited_domains": sorted(p.cited_domains)}
                       for p in sorted(probes, key=lambda p: p.prompt)],
        },
    }
    if site is not None:
        pages = [p for p in site.pages if not p.error]
        snap["site"] = {
            "error": site.error or None,
            "robots_found": site.robots_found,
            "robots_status": site.robots_status,
            "bots": {b: site.bots.get(b) for b in sorted(SEARCH_BOTS + TRAINING_BOTS)} if site.bots else {},
            "llms_txt": site.llms_txt,
            "pages_checked": len(pages),
            "pages_with_product": sum(p.has_product for p in pages),
            "pages": sorted(({"path": urlparse(p.url).path, "has_product": p.has_product,
                              "fields": dict(sorted(p.fields.items()))} for p in pages), key=lambda x: x["path"]),
        }
    return snap


def dump(snap: dict, path: Path) -> None:
    path.write_text(json.dumps(snap, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


# ---------- Markdown reporty ----------

def _search_bots_ok(site: dict | None) -> str:
    if not site or site.get("error"):
        return "– (web nekontrolován)"
    if site.get("robots_status"):
        return f"? (robots.txt HTTP {site['robots_status']})"
    blocked = [b for b in SEARCH_BOTS if site["bots"].get(b) is False]
    return "ano" if not blocked else f"ne – blokováno: {', '.join(blocked)}"


def _schema_share(site: dict | None) -> str:
    if not site or not site.get("pages_checked"):
        return "–"
    return f"{site['pages_with_product']}/{site['pages_checked']} stránek"


def _visibility(snap: dict) -> str:
    probes = snap["visibility"]["probes"]
    if not probes:
        return "–"
    return f"{sum(p['mentioned'] for p in probes)}/{len(probes)} dotazů"


def _issues_table(snap: dict) -> str:
    n = snap["feed"]["products"]
    rows = [f"| {LABELS[k]} | {c} z {n} |" for k, c in sorted(snap["feed"]["issues"].items(), key=lambda x: (-x[1], x[0]))]
    return "\n".join(["| Problém | Produktů |", "|---|---|", *rows]) if rows else "_Bez problémů._"


def _products_table(snap: dict) -> str:
    rows = [f"| {i['id']} | {i['name']} | {i['score']} | {', '.join(LABELS[k] for k in i['failed']) or '–'} |"
            for i in snap["feed"]["items"]]
    return "\n".join(["| ID | Produkt | Skóre | Co chybí |", "|---|---|---|---|", *rows])


def _bots_table(snap: dict) -> str:
    site = snap["site"]
    if not site or site.get("error") or not site["bots"]:
        return "_Nekontrolováno._"
    kind = {b: "vyhledávání" for b in SEARCH_BOTS} | {b: "trénink" for b in TRAINING_BOTS}
    rows = [f"| {b} | {kind[b]} | {'✅ povolen' if ok else '⛔ blokován'} |" for b, ok in site["bots"].items()]
    return "\n".join(["| Robot | Účel | Stav |", "|---|---|---|", *rows])


def _pages_table(snap: dict) -> str:
    site = snap["site"]
    if not site or not site.get("pages"):
        return "_Nekontrolováno._"
    rows = [f"| {p['path']} | {'✅' if p['has_product'] else '❌'} | "
            f"{', '.join(k for k, v in p['fields'].items() if v) or '–'} |" for p in site["pages"]]
    return "\n".join(["| Stránka | schema.org Product | Vyplněná pole |", "|---|---|---|", *rows])


def _enrich_table(snap: dict) -> str:
    rows = [f"| {e['id']} | {e['verified']} | {e['rejected']} |" for e in snap["enrichment"]]
    return "\n".join(["| ID | Ověřené parametry | Zamítnuté |", "|---|---|---|", *rows]) if rows else "_Neprovedeno._"


def _probes_table(snap: dict) -> str:
    probes = snap["visibility"]["probes"]
    rows = [f"| {p['prompt']} | {'✅' if p['mentioned'] else '❌'} | {', '.join(p['cited_domains'][:5]) or '–'} |"
            for p in probes]
    return "\n".join(["| Dotaz | Obchod zmíněn | Citované weby |", "|---|---|---|", *rows]) if rows else "_Neprovedeno._"


def render_report(snap: dict) -> str:
    tpl = Template((TEMPLATES / "report.md").read_text(encoding="utf-8"))
    m = snap["meta"]
    return tpl.substitute(
        shop=m["shop"], label=m["label"], date=m["date"], feed_sha256=m["feed_sha256"],
        products=snap["feed"]["products"], feed_score=snap["feed"]["score"],
        search_bots_ok=_search_bots_ok(snap["site"]), schema_share=_schema_share(snap["site"]),
        visibility=_visibility(snap), issues_table=_issues_table(snap), products_table=_products_table(snap),
        bots_table=_bots_table(snap), pages_table=_pages_table(snap), enrich_table=_enrich_table(snap),
        probes_table=_probes_table(snap),
    )


def _delta(a: float, b: float) -> str:
    d = b - a
    return "0" if d == 0 else f"{d:+g}"


def render_compare(old: dict, new: dict) -> str:
    tpl = Template((TEMPLATES / "compare.md").read_text(encoding="utf-8"))
    fo, fn = old["feed"], new["feed"]
    so, sn = old["site"] or {}, new["site"] or {}

    keys = sorted(set(fo["issues"]) | set(fn["issues"]), key=lambda k: [c[0] for c in CHECKS].index(k))
    issue_rows = [f"| {LABELS[k]} | {fo['issues'].get(k, 0)} | {fn['issues'].get(k, 0)} | "
                  f"{_delta(fo['issues'].get(k, 0), fn['issues'].get(k, 0))} |" for k in keys]

    old_items = {i["id"]: i for i in fo["items"]}
    product_rows = []
    for i in fn["items"]:
        o = old_items.get(i["id"])
        before = o["score"] if o else "–"
        order = [c[0] for c in CHECKS]
        fixed = sorted(set(o["failed"]) - set(i["failed"]), key=order.index) if o else []
        product_rows.append(f"| {i['id']} | {i['name']} | {before} | {i['score']} | "
                            f"{_delta(o['score'], i['score']) if o else 'nový'} | "
                            f"{', '.join(LABELS[k] for k in fixed) or '–'} |")

    bot_rows = []
    for b in sorted(set(so.get("bots", {})) | set(sn.get("bots", {}))):
        a, c = so.get("bots", {}).get(b), sn.get("bots", {}).get(b)
        fmt = {True: "✅", False: "⛔", None: "?"}
        if a != c:
            bot_rows.append(f"| {b} | {fmt[a]} | {fmt[c]} |")

    po = {p["prompt"]: p for p in old["visibility"]["probes"]}
    probe_rows = [f"| {p['prompt']} | {'✅' if po.get(p['prompt'], {}).get('mentioned') else '❌'} | "
                  f"{'✅' if p['mentioned'] else '❌'} |" for p in new["visibility"]["probes"]]
    new_prompts = {p["prompt"] for p in new["visibility"]["probes"]}
    if not new_prompts:
        prompts_note = ("Po úpravách zatím neměřeno – viditelnost měříme s odstupem cca 4 týdnů, "
                        "aby AI vyhledávače stihly změny zaznamenat.")
    elif set(po) == new_prompts:
        prompts_note = "Stejná sada dotazů v obou bězích."
    else:
        prompts_note = "⚠️ Sady dotazů se liší – viditelnost nelze přímo porovnat."

    return tpl.substitute(
        shop=new["meta"]["shop"], old_label=old["meta"]["label"], new_label=new["meta"]["label"],
        old_date=old["meta"]["date"], new_date=new["meta"]["date"],
        old_sha=old["meta"]["feed_sha256"], new_sha=new["meta"]["feed_sha256"],
        old_score=fo["score"], new_score=fn["score"], score_delta=_delta(fo["score"], fn["score"]),
        old_bots=_search_bots_ok(old["site"]), new_bots=_search_bots_ok(new["site"]),
        old_schema=_schema_share(old["site"]), new_schema=_schema_share(new["site"]),
        old_vis=_visibility(old), new_vis=_visibility(new),
        issues_table="\n".join(["| Problém | Před | Po | Změna |", "|---|---|---|---|", *issue_rows]),
        products_table="\n".join(["| ID | Produkt | Před | Po | Změna | Opraveno |", "|---|---|---|---|---|---|",
                                  *product_rows]),
        bots_table="\n".join(["| Robot | Před | Po |", "|---|---|---|", *bot_rows]) if bot_rows else "_Beze změny._",
        probes_table="\n".join(["| Dotaz | Před | Po |", "|---|---|---|", *probe_rows]) if probe_rows else "_Neprovedeno._",
        prompts_note=prompts_note,
    )

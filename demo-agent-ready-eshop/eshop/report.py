"""HTML report pre majiteľa e-shopu (po česky – cieľový zákazník je CZ obchod)."""

import json
from datetime import date
from html import escape

from eshop.enrich import Result
from eshop.outputs import jsonld
from eshop.score import CHECKS, ProductScore
from eshop.site import SEARCH_BOTS, TRAINING_BOTS, SiteReport
from eshop.visibility import Probe, top_domains

CSS = """
:root{--bg:#f7f7f5;--card:#fff;--fg:#1d1d1b;--muted:#6b6b66;--line:#e4e3de;--good:#1f8a4c;--warn:#b7791f;
--bad:#c53030;--accent:#2b59c3;--code:#f1f0ec}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--card:#20201e;--fg:#ecebe6;--muted:#a3a29b;--line:#34332f;
--good:#48bb78;--warn:#ecc94b;--bad:#fc8181;--accent:#7f9cf5;--code:#2a2a27}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,
Segoe UI,Roboto,sans-serif}main{max-width:1040px;margin:0 auto;padding:32px 16px 64px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:20px;margin:40px 0 12px}h3{font-size:16px;margin:0 0 8px}
.muted{color:var(--muted)}.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;
margin:12px 0}.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.kpi{font-size:40px;font-weight:700;line-height:1}.good{color:var(--good)}.warn{color:var(--warn)}.bad{color:var(--bad)}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:8px;border-bottom:1px solid
var(--line);vertical-align:top}th{color:var(--muted);font-weight:600}.bar{height:8px;background:var(--line);
border-radius:4px;overflow:hidden;min-width:80px}.bar>i{display:block;height:100%;background:var(--accent)}
pre{background:var(--code);border-radius:8px;padding:12px;overflow:auto;font-size:12px;max-height:320px}
.tag{display:inline-block;padding:1px 8px;border-radius:99px;font-size:12px;border:1px solid var(--line);margin:2px}
.cols{display:grid;gap:16px;grid-template-columns:1fr 1fr}@media(max-width:700px){.cols{grid-template-columns:1fr}}
details summary{cursor:pointer;font-weight:600}.scroll{overflow-x:auto}
"""


def _cls(score: float) -> str:
    return "good" if score >= 75 else "warn" if score >= 50 else "bad"


def _section_feed(summary: dict, scores: list[ProductScore]) -> str:
    rows = "".join(
        f"<tr><td>{escape(i['label'])}</td><td>{i['count']} z {summary['products']}</td>"
        f"<td><div class='bar'><i style='width:{i['share']}%'></i></div></td></tr>" for i in summary["issues"])
    labels = {k: label for k, _, label in CHECKS}
    worst = sorted(scores, key=lambda s: s.score)[:10]
    prows = "".join(
        f"<tr><td>{escape(s.product.name)}<div class='muted'>{escape(s.product.item_id)}</div></td>"
        f"<td class='{_cls(s.score)}'><b>{s.score}</b></td>"
        f"<td>{''.join(f'<span class=tag>{escape(labels[k])}</span>' for k in s.failed) or '–'}</td></tr>"
        for s in worst)
    return f"""<h2>1. Kvalita produktových dat</h2>
<p class="muted">AI asistenti doporučují produkty, kterým rozumí: přesný název, fakta v popisu, parametry, EAN.</p>
<div class="card"><h3>Nejčastější problémy</h3><div class="scroll"><table>
<tr><th>Problém</th><th>Produktů</th><th></th></tr>{rows or '<tr><td colspan=3>Bez problémů 🎉</td></tr>'}
</table></div></div>
<div class="card"><h3>Produkty s nejnižším skóre</h3><div class="scroll"><table>
<tr><th>Produkt</th><th>Skóre</th><th>Co chybí</th></tr>{prows}</table></div></div>"""


def _section_site(site: SiteReport | None) -> str:
    if site is None:
        return ""
    if site.error:
        return f"<h2>2. Web a AI roboti</h2><div class='card'>⚠️ {escape(site.error)} – kontrola webu přeskočena.</div>"

    def bot_rows(bots):
        if site.robots_status:
            return (f"<tr><td colspan=2 class='warn'>robots.txt se nepodařilo načíst (HTTP {site.robots_status}) – "
                    "web blokuje automatické nástroje. Ověřte ručně.</td></tr>")
        return "".join(f"<tr><td>{b}</td><td>{'✅ povolen' if site.bots.get(b) else '⛔ blokován'}</td></tr>" for b in bots)

    pages = "".join(
        f"<tr><td class='muted'>{escape(p.url[:70])}</td><td>{'✅' if p.has_product else '❌'}</td>"
        f"<td>{' '.join(f'<span class=tag>{k} {chr(10003) if v else chr(10007)}</span>' for k, v in p.fields.items())}"
        f"{escape(p.error)}</td></tr>" for p in site.pages)
    blocked = [b for b in SEARCH_BOTS if site.bots and not site.bots.get(b)]
    return f"""<h2>2. Web a AI roboti</h2>
<div class="cols"><div class="card"><h3>robots.txt – vyhledávací AI roboti</h3>
<p class="muted">Pokud jsou blokovaní, AI asistent váš obchod nenajde ani necituje.</p>
<table>{bot_rows(SEARCH_BOTS)}</table>
{f"<p class='bad'>Blokováno: {', '.join(blocked)}</p>" if blocked else ""}</div>
<div class="card"><h3>robots.txt – roboti pro trénink modelů</h3>
<p class="muted">Blokování je legitimní volba; na viditelnost ve vyhledávání má malý vliv.</p>
<table>{bot_rows(TRAINING_BOTS)}</table>
<p class="muted">robots.txt {'nalezen' if site.robots_found else 'nenalezen'} · llms.txt {'ano' if site.llms_txt else 'ne'}
(podle Ahrefs ho AI roboti skoro nečtou – nízká priorita)</p></div></div>
<div class="card"><h3>Strukturovaná data schema.org Product na produktových stránkách</h3><div class="scroll"><table>
<tr><th>Stránka</th><th>Product</th><th>Pole</th></tr>{pages or '<tr><td colspan=3>Žádné stránky</td></tr>'}
</table></div></div>"""


def _section_enrich(results: list[Result]) -> str:
    if not results:
        return ""
    cards = []
    for r in results:
        p = r.product
        if not r.data:
            cards.append(f"<div class='card'><h3>{escape(p.name)}</h3><p class='bad'>{escape(r.error)}</p></div>")
            continue
        d = r.data
        attrs = "".join(f"<tr><td>{escape(a.name)}</td><td><b>{escape(a.value)}</b></td>"
                        f"<td class='muted'>„{escape(a.source_quote)}“</td></tr>" for a in r.verified)
        rejected = "".join(f"<li>{escape(a.name)}: {escape(a.value)} – <span class='bad'>{escape(why)}</span></li>"
                           for a, why in r.rejected)
        cards.append(f"""<div class="card"><h3>{escape(p.name)} → {escape(d.better_name)}</h3>
<div class="cols"><div><div class="muted">Původní popis</div><p>{escape(p.description or '(chybí)')}</p>
<div class="muted">Parametry ve feedu: {len(p.params)}</div></div>
<div><div class="muted">Popis pro AI asistenty</div><p>{escape(d.short_description)}</p>
<div>{''.join(f'<span class=tag>{escape(u)}</span>' for u in d.use_cases)}</div></div></div>
<h3 style="margin-top:12px">Ověřené parametry ({len(r.verified)})</h3><div class="scroll"><table>
<tr><th>Parametr</th><th>Hodnota</th><th>Zdroj v datech</th></tr>{attrs or '<tr><td colspan=3>–</td></tr>'}</table></div>
{f"<p><b>Zamítnuto kontrolou ({len(r.rejected)}):</b></p><ul>{rejected}</ul>" if rejected else ""}
{f"<p><b>Chybí v datech (doplňte):</b> {escape(' · '.join(d.missing_info))}</p>" if d.missing_info else ""}
<details><summary>FAQ ({len(d.faq)}) a JSON-LD pro šablonu</summary>
{''.join(f'<p><b>{escape(q.question)}</b><br>{escape(q.answer)}</p>' for q in d.faq)}
<pre>{escape(json.dumps(jsonld(p, r), ensure_ascii=False, indent=2))}</pre></details></div>""")
    total_v = sum(len(r.verified) for r in results)
    total_r = sum(len(r.rejected) for r in results)
    return f"""<h2>3. AI obohacení dat (ukázka na {len(results)} produktech)</h2>
<p class="muted">AI vytěží parametry z vašich popisů. Každý parametr musí mít doslovnou oporu v datech –
automatická kontrola zamítla {total_r} z {total_v + total_r} návrhů. Nic si nevymýšlíme.</p>{''.join(cards)}"""


def _section_visibility(probes: list[Probe], shop: str) -> str:
    if not probes:
        return ""
    hits = sum(p.mentioned for p in probes)
    rows = "".join(
        f"<tr><td>{escape(p.prompt)}</td><td>{'✅' if p.mentioned else '❌'}</td>"
        f"<td class='muted'>{escape(', '.join(p.cited_domains[:5]) or p.error)}</td></tr>" for p in probes)
    comp = "".join(f"<tr><td>{escape(d)}</td><td>{n}×</td></tr>" for d, n in top_domains(probes))
    return f"""<h2>4. Viditelnost v AI odpovědích</h2>
<div class="grid"><div class="card"><div class="muted">Zmínka o {escape(shop)}</div>
<div class="kpi {_cls(100 * hits / len(probes))}">{hits}/{len(probes)}</div></div></div>
<div class="card"><h3>Dotazy zákazníků</h3><div class="scroll"><table><tr><th>Dotaz</th><th>Vy</th><th>Citované weby</th></tr>
{rows}</table></div></div>
<div class="card"><h3>Koho AI cituje místo vás</h3><table>{comp}</table>
<p class="muted">Měřeno přes Claude s webovým vyhledáváním. Odpovědi AI se liší dotaz od dotazu –
v placené verzi měříme opakovaně, týdně a i v ChatGPT, Gemini a Perplexity.</p></div>"""


def render(shop: str, summary: dict, scores: list[ProductScore], site: SiteReport | None,
           results: list[Result], probes: list[Probe]) -> str:
    feed_score = summary["score"]
    known = site and not site.error and bool(site.bots)
    search_ok = known and all(site.bots.get(b) for b in SEARCH_BOTS)
    pages = [p for p in (site.pages if site else []) if not p.error]
    schema_share = round(100 * sum(p.has_product for p in pages) / len(pages)) if pages else None
    return f"""<!doctype html><html lang="cs"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>AI readiness audit – {escape(shop)}</title>
<style>{CSS}</style></head><body><main>
<h1>AI readiness audit</h1><div class="muted">{escape(shop)} · {date.today().strftime('%-d. %-m. %Y')} ·
{summary['products']} produktů ve feedu</div>
<div class="grid" style="margin-top:20px">
<div class="card"><div class="muted">Kvalita dat pro AI</div><div class="kpi {_cls(feed_score)}">{feed_score}/100</div></div>
<div class="card"><div class="muted">AI roboti mají přístup</div><div class="kpi {'good' if search_ok else 'bad' if known else ''}">
{'ano' if search_ok else 'ne' if known else '?'}</div></div>
<div class="card"><div class="muted">Stránky se schema.org Product</div>
<div class="kpi {_cls(schema_share) if schema_share is not None else ''}">{f'{schema_share} %' if schema_share is not None else '–'}</div></div>
</div>
{_section_feed(summary, scores)}{_section_site(site)}{_section_enrich(results)}{_section_visibility(probes, shop)}
<h2>Co dál</h2><div class="card"><ol>
<li>Doplňte EAN, výrobce a parametry u produktů s nejnižším skóre.</li>
<li>Nahrajte obohacený feed (<code>heureka-enriched.xml</code>) a doplňkový feed do Google Merchant Center
(<code>merchant-supplemental.tsv</code>) – ovlivňuje Google AI Mode.</li>
<li>Vložte JSON-LD do šablony produktové stránky.</li>
<li>Za 4 týdny změříme viditelnost znovu a porovnáme.</li></ol></div>
</main></body></html>"""

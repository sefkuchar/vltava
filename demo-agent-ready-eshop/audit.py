"""AI readiness audit e-shopu z Heureka XML feedu.

Použitie:
    python audit.py --feed sample/v1/heureka.xml                         # len dáta, bez AI a bez webu
    python audit.py --feed https://obchod.cz/heureka.xml --site          # + kontrola webu (robots.txt, schema.org)
    python audit.py --feed ... --site --enrich 5                         # + AI obohatenie 5 produktov (treba API kľúč)
    python audit.py --feed ... --site --enrich 5 --visibility 5          # + test viditeľnosti v AI odpovediach

Pre opakovateľné porovnanie (viď AUDIT-POSTUP.md) zadaj --label a --date. Výstup audit.json a report.md
sú potom pri rovnakom vstupe vždy bajtovo rovnaké.
"""

import argparse
import json
import webbrowser
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests

from eshop import feed, report, score, site, snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--feed", required=True, help="cesta alebo URL Heureka XML feedu")
    parser.add_argument("--site", nargs="?", const="auto", help="skontrolovať web (voliteľne base URL, inak z feedu)")
    parser.add_argument("--pages", type=int, default=5, help="koľko produktových stránok skontrolovať")
    parser.add_argument("--enrich", type=int, default=0, help="koľko najslabších produktov obohatiť cez AI")
    parser.add_argument("--visibility", type=int, default=0, help="koľko zákazníckych dopytov otestovať v AI")
    parser.add_argument("--enrichments", help="JSON s hotovým obohatením {ITEM_ID: Enrichment} namiesto volania API")
    parser.add_argument("--probes", help="JSON s hotovými výsledkami testu viditeľnosti namiesto volania API")
    parser.add_argument("--prompts", help="JSON {\"prompts\": [...]} s pevnou sadou dopytov pre --visibility")
    parser.add_argument("--label", default="audit", help="označenie behu, napr. v1 / v2 / 2026-11")
    parser.add_argument("--date", default=date.today().isoformat(), help="dátum auditu YYYY-MM-DD (pre opakovateľnosť)")
    parser.add_argument("--out", default="out", help="výstupný priečinok")
    parser.add_argument("--open", action="store_true", help="otvoriť report v prehliadači")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    source = args.feed
    if source.startswith(("http://", "https://")):
        local = out / "source-feed.xml"
        resp = requests.get(source, timeout=120, headers={"User-Agent": "agent-ready-audit/0.1"})
        resp.raise_for_status()
        local.write_bytes(resp.content)
        source = str(local)

    products = feed.load(source)
    if not products:
        raise SystemExit("Vo feede nie sú žiadne SHOPITEM položky.")
    scores = [score.score_product(p) for p in products]
    summary = score.summarize(scores)
    shop = urlparse(next((p.url for p in products if p.url), "")).netloc or Path(args.feed).stem
    print(f"📦 {len(products)} produktov · skóre dát {summary['score']}/100")
    for issue in summary["issues"][:5]:
        print(f"   - {issue['label']}: {issue['count']}×")

    site_report = None
    if args.site:
        base = None if args.site == "auto" else args.site.rstrip("/")
        site_report = site.check_site([p.url for p in products if p.url], base, args.pages)
        if site_report.error:
            print(f"🌐 {site_report.error}")
        elif site_report.robots_status:
            print(f"🌐 robots.txt sa nepodarilo načítať (HTTP {site_report.robots_status}) – web blokuje automatické nástroje")
        else:
            blocked = [b for b in site.SEARCH_BOTS if not site_report.bots.get(b)]
            with_schema = sum(p.has_product for p in site_report.pages)
            print(f"🌐 AI boty blokované: {', '.join(blocked) or 'žiadne'} · "
                  f"schema.org Product: {with_schema}/{len(site_report.pages)} stránok")

    results, probes = [], []
    if args.enrichments:
        # Ručný / offline režim: obohatenie pripravené mimo API, prejde tou istou kontrolou ako výstup z API
        from eshop import enrich, outputs

        by_id = {p.item_id: p for p in products}
        data = json.loads(Path(args.enrichments).read_text(encoding="utf-8"))
        for item_id, payload in data.items():
            if item_id.startswith("_") or item_id not in by_id:
                continue
            r = enrich.check(by_id[item_id], enrich.Enrichment.model_validate(payload))
            results.append(r)
            print(f"✨ {r.product.name}: {len(r.verified)} overených parametrov, {len(r.rejected)} zamietnutých")
        files = outputs.write_all(products, {r.product.item_id: r for r in results}, source, out)
        print("   výstupy:", ", ".join(str(p) for p in files.values()))
    if args.probes:
        from eshop.visibility import Probe

        raw = json.loads(Path(args.probes).read_text(encoding="utf-8"))["probes"]
        probes = [Probe(**{k: v for k, v in p.items() if k in Probe.__dataclass_fields__}) for p in raw]
        for pr in probes:
            print(f"🔍 {'✅' if pr.mentioned else '❌'} {pr.prompt}")
    if args.enrich or args.visibility:
        import anthropic

        from eshop import enrich, outputs, visibility

        client = anthropic.Anthropic()
        try:
            client.models.retrieve(enrich.MODEL)  # overí prihlásenie skôr, než začneme
        except (TypeError, anthropic.AuthenticationError) as e:
            raise SystemExit("❌ Chýba alebo je neplatný Anthropic API kľúč. Nastav ho: "
                             "export ANTHROPIC_API_KEY=sk-ant-... (https://console.anthropic.com)") from e
        if args.enrich:
            weakest = sorted(scores, key=lambda s: s.score)[: args.enrich]
            for s in weakest:
                r = enrich.enrich(s.product, client)
                results.append(r)
                print(f"✨ {s.product.name}: {len(r.verified)} overených parametrov, {len(r.rejected)} zamietnutých"
                      + (f" ({r.error})" if r.error else ""))
            files = outputs.write_all(products, {r.product.item_id: r for r in results if r.data}, source, out)
            print("   výstupy:", ", ".join(str(p) for p in files.values()))
        if args.visibility:
            categories = list(dict.fromkeys(p.category.split("|")[-1].strip() for p in products if p.category))[:6]
            if args.prompts:  # pevná sada dopytov → porovnateľné behy
                prompts = json.loads(Path(args.prompts).read_text(encoding="utf-8"))["prompts"][: args.visibility]
            else:
                prompts = visibility.make_prompts(categories, args.visibility, client)
            domain = urlparse(site_report.base).netloc if site_report and site_report.base else shop
            for prompt in prompts:
                pr = visibility.probe(prompt, domain, client)
                probes.append(pr)
                print(f"🔍 {'✅' if pr.mentioned else '❌'} {prompt}")

    html = report.render(shop, summary, scores, site_report, results, probes, args.date)
    path = out / "report.html"
    path.write_text(html, encoding="utf-8")
    snap = snapshot.build(shop=shop, label=args.label, run_date=args.date, feed_path=source, summary=summary,
                          scores=scores, site=site_report, results=results, probes=probes)
    snapshot.dump(snap, out / "audit.json")
    (out / "report.md").write_text(snapshot.render_report(snap), encoding="utf-8")
    print(f"📄 Report: {path.resolve()}  (+ report.md, audit.json)")
    if args.open:
        webbrowser.open(path.resolve().as_uri())


if __name__ == "__main__":
    main()

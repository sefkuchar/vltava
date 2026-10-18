"""Vygeneruje statický ukážkový web fiktívneho obchodu pre v1 (pred) a v2 (po) z ich feedov.

v1: robots.txt blokuje vyhľadávacie AI boty, produktové stránky bez schema.org (typický stav malých e-shopov).
v2: robots.txt povoľuje AI boty, každá produktová stránka má schema.org Product JSON-LD.

Spustenie (z priečinka demo-agent-ready-eshop):  python sample/build_sites.py
Servírovanie:  python -m http.server 8761 -d sample/v1/site   (v2 na porte 8762)
"""

import json
import shutil
import sys
from html import escape
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eshop import feed  # noqa: E402
from eshop.outputs import jsonld  # noqa: E402

HERE = Path(__file__).resolve().parent

ROBOTS = {
    "v1": "User-agent: GPTBot\nDisallow: /\n\nUser-agent: OAI-SearchBot\nDisallow: /\n\n"
          "User-agent: PerplexityBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n",
    "v2": "User-agent: GPTBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n",
}

PAGE = """<!doctype html><html lang="cs"><head><meta charset="utf-8"><title>{title}</title>{ld}</head>
<body><h1>{title}</h1><p>{price} Kč</p><p>{description}</p><ul>{params}</ul></body></html>
"""


def build(version: str) -> None:
    root = HERE / version / "site"
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True)
    (root / "robots.txt").write_text(ROBOTS[version], encoding="utf-8")
    products = feed.load(str(HERE / version / "heureka.xml"))
    links = []
    for p in products:
        path = urlparse(p.url).path.strip("/")
        ld = ""
        if version == "v2":
            data = json.dumps(jsonld(p, None), ensure_ascii=False, indent=2)
            ld = f'<script type="application/ld+json">\n{data}\n</script>'
        params = "".join(f"<li>{escape(k)}: {escape(v)}</li>" for k, v in p.params.items())
        page_dir = root / path
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(PAGE.format(
            title=escape(p.name), ld=ld, price=f"{p.price:.0f}" if p.price else "–",
            description=escape(p.description), params=params), encoding="utf-8")
        links.append(f'<li><a href="/{path}/">{escape(p.name)}</a></li>')
    (root / "index.html").write_text(
        f"<!doctype html><html lang='cs'><meta charset='utf-8'><title>Domácí Pomocník ({version})</title>"
        f"<h1>Domácí Pomocník – fiktívny obchod ({version})</h1><ul>{''.join(links)}</ul></html>", encoding="utf-8")
    print(f"{version}: {len(products)} stránok → {root}")


if __name__ == "__main__":
    for v in ("v1", "v2"):
        build(v)

"""Kontrola webu: robots.txt pre AI boty a schema.org Product dáta na produktových stránkach."""

import json
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

UA = {"User-Agent": "Mozilla/5.0 (compatible; agent-ready-audit/0.1)"}

# Boty, ktoré ovplyvňujú, či AI asistent obchod nájde a odcituje (blokovať ich = byť neviditeľný)
SEARCH_BOTS = ["OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Claude-SearchBot", "Claude-User", "Googlebot"]
# Boty na trénovanie modelov – blokovanie je legitímna voľba obchodníka, len informatívne
TRAINING_BOTS = ["GPTBot", "ClaudeBot", "Google-Extended", "Applebot-Extended", "CCBot"]


@dataclass
class PageCheck:
    url: str
    status: int | None = None
    has_product: bool = False
    fields: dict[str, bool] = field(default_factory=dict)
    error: str = ""


@dataclass
class SiteReport:
    base: str
    robots_found: bool = False
    robots_status: int | None = None  # nastavené, ak sa robots.txt nepodarilo načítať (403, 5xx)
    bots: dict[str, bool] = field(default_factory=dict)  # bot -> smie crawlovať (prázdne = neznáme)
    llms_txt: bool = False
    pages: list[PageCheck] = field(default_factory=list)
    error: str = ""


def _get(url: str) -> requests.Response:
    return requests.get(url, timeout=20, headers=UA, allow_redirects=True)


def _products_in(data) -> list[dict]:
    items = data if isinstance(data, list) else [data]
    found = []
    for item in items:
        if not isinstance(item, dict):
            continue
        types = item.get("@type")
        types = types if isinstance(types, list) else [types]
        if "Product" in types or "ProductGroup" in types:
            found.append(item)
        if "@graph" in item:
            found += _products_in(item["@graph"])
    return found


def check_page(url: str) -> PageCheck:
    page = PageCheck(url)
    try:
        resp = _get(url)
        page.status = resp.status_code
        blocks = re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', resp.text, re.S | re.I)
        products = []
        for block in blocks:
            try:
                products += _products_in(json.loads(block.strip()))
            except json.JSONDecodeError:
                continue
        if products:
            p = products[0]
            offers = p.get("offers") or {}
            offers = offers[0] if isinstance(offers, list) and offers else offers
            page.has_product = True
            page.fields = {
                "name": bool(p.get("name")),
                "price": bool(isinstance(offers, dict) and (offers.get("price") or offers.get("lowPrice"))),
                "availability": bool(isinstance(offers, dict) and offers.get("availability")),
                "gtin": any(k.startswith("gtin") for k in p),
                "brand": bool(p.get("brand")),
                "image": bool(p.get("image")),
                "rating": bool(p.get("aggregateRating")),
            }
    except requests.RequestException as e:
        page.error = type(e).__name__
    return page


def check_site(product_urls: list[str], base: str | None = None, max_pages: int = 5) -> SiteReport:
    if not base and product_urls:
        u = urlparse(product_urls[0])
        base = f"{u.scheme}://{u.netloc}"
    elif base:
        # URL z feedu presmerujeme na zadaný web (napr. testovacia kópia obchodu na localhoste)
        product_urls = [base.rstrip("/") + urlparse(u).path for u in product_urls]
    report = SiteReport(base or "")
    if not base:
        report.error = "Neznámá doména"
        return report
    try:
        resp = _get(f"{base}/robots.txt")
        rp = RobotFileParser()
        if resp.status_code == 200:
            report.robots_found = True
            rp.parse(resp.text.splitlines())
        elif resp.status_code == 404:
            rp.parse([])  # bez robots.txt je podľa štandardu povolené všetko
        else:
            # 403/5xx: obchod blokuje náš audit (anti-bot), nie nutne AI boty – výsledok je neznámy
            report.robots_status = resp.status_code
        if report.robots_status is None:
            report.bots = {bot: rp.can_fetch(bot, f"{base}/") for bot in SEARCH_BOTS + TRAINING_BOTS}
        report.llms_txt = _get(f"{base}/llms.txt").status_code == 200
    except requests.RequestException as e:
        report.error = f"Web nedostupný ({type(e).__name__})"
        return report
    report.pages = [check_page(u) for u in product_urls[:max_pages]]
    return report

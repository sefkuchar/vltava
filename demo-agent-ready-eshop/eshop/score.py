"""Skóre „AI readiness“ produktových dát: nakoľko dobre AI asistent produktu porozumie a odporučí ho."""

from collections import Counter
from dataclasses import dataclass

from eshop.feed import Product

# (kľúč, váha, popis problému pre report)
CHECKS = [
    ("name", 15, "Název neobsahuje značku/model (AI ho nedokáže spárovat)"),
    ("description", 20, "Krátký popis (méně než 200 znaků faktů)"),
    ("params", 15, "Málo strukturovaných parametrů (méně než 3 PARAM)"),
    ("ean", 15, "Chybí nebo je neplatný EAN"),
    ("manufacturer", 10, "Chybí výrobce"),
    ("image", 10, "Chybí obrázek"),
    ("category", 10, "Neúplná kategorie (chybí Heureka strom)"),
    ("delivery", 5, "Dlouhá nebo neuvedená dodací lhůta"),
]


@dataclass
class ProductScore:
    product: Product
    score: int
    failed: list[str]  # kľúče neúspešných kontrol


def ean_valid(ean: str) -> bool:
    if not ean.isdigit() or len(ean) not in (8, 12, 13, 14):
        return False
    digits = [int(d) for d in ean]
    check = digits.pop()
    total = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(digits)))
    return (10 - total % 10) % 10 == check


def _check(p: Product) -> dict[str, float]:
    words = p.name.split()
    desc = len(p.description)
    depth = len([c for c in p.category.split("|") if c.strip()])
    return {
        "name": 1.0 if len(words) >= 3 and (not p.manufacturer or p.manufacturer.lower() in p.name.lower()) else
                0.5 if len(words) >= 2 else 0.0,
        "description": 1.0 if desc >= 200 else 0.5 if desc >= 80 else 0.0,
        "params": 1.0 if len(p.params) >= 3 else 0.5 if p.params else 0.0,
        "ean": 1.0 if ean_valid(p.ean) else 0.0,
        "manufacturer": 1.0 if p.manufacturer else 0.0,
        "image": 1.0 if p.image else 0.0,
        "category": 1.0 if depth >= 3 else 0.5 if depth == 2 else 0.0,
        "delivery": 1.0 if p.delivery_days is not None and p.delivery_days <= 3 else 0.0,
    }


def score_product(p: Product) -> ProductScore:
    results = _check(p)
    total = sum(weight * results[key] for key, weight, _ in CHECKS)
    return ProductScore(p, round(total), [key for key, _, _ in CHECKS if results[key] < 1.0])


def summarize(scores: list[ProductScore]) -> dict:
    issues = Counter(k for s in scores for k in s.failed)
    labels = {k: label for k, _, label in CHECKS}
    n = len(scores) or 1
    return {
        "score": round(sum(s.score for s in scores) / n),
        "products": len(scores),
        "issues": [{"key": k, "label": labels[k], "count": c, "share": round(100 * c / n)}
                   for k, c in issues.most_common()],
    }

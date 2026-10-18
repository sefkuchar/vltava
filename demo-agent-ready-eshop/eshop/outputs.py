"""Výstupy, ktoré obchodník reálne nasadí: schema.org JSON-LD, obohatený Heureka feed, Google Merchant doplnkový feed."""

import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from eshop.enrich import Result
from eshop.feed import Product
from eshop.score import ean_valid


def jsonld(p: Product, r: Result | None) -> dict:
    data: dict = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": r.data.better_name if r and r.data else p.name,
        "sku": p.item_id,
        "url": p.url,
    }
    if r and r.data:
        data["description"] = r.data.short_description
    elif p.description:
        data["description"] = p.description
    if p.image:
        data["image"] = p.image
    if p.manufacturer:
        data["brand"] = {"@type": "Brand", "name": p.manufacturer}
    if ean_valid(p.ean):
        data[f"gtin{len(p.ean)}"] = p.ean
    if p.category:
        data["category"] = p.category.split("|")[-1].strip()
    props = dict(p.params)
    if r:
        props.update({a.name: a.value for a in r.verified if a.name not in props})
    if props:
        data["additionalProperty"] = [{"@type": "PropertyValue", "name": k, "value": v} for k, v in props.items()]
    if p.price is not None:
        data["offers"] = {
            "@type": "Offer",
            "price": f"{p.price:.2f}",
            "priceCurrency": "CZK",
            "availability": "https://schema.org/InStock" if p.delivery_days == 0 else "https://schema.org/BackOrder",
            "url": p.url,
        }
    return data


def write_all(products: list[Product], results: dict[str, Result], source_feed: str, out: Path) -> dict[str, Path]:
    out.mkdir(parents=True, exist_ok=True)
    files: dict[str, Path] = {}

    jsonld_dir = out / "jsonld"
    jsonld_dir.mkdir(exist_ok=True)
    for p in products:
        if p.item_id in results:
            path = jsonld_dir / f"{p.item_id}.json"
            path.write_text(json.dumps(jsonld(p, results[p.item_id]), ensure_ascii=False, indent=2), encoding="utf-8")
    files["jsonld"] = jsonld_dir

    # Obohatený Heureka feed: originál + overené parametre doplnené ako PARAM (popis nemeníme, len navrhujeme v reporte)
    tree = ET.parse(source_feed) if not source_feed.startswith("http") else None
    if tree is not None:
        for item in tree.getroot().iter("SHOPITEM"):
            r = results.get((item.findtext("ITEM_ID") or "").strip())
            if not r:
                continue
            existing = {(p.findtext("PARAM_NAME") or "").strip().lower() for p in item.findall("PARAM")}
            for attr in r.verified:
                if attr.name.lower() in existing:
                    continue
                param = ET.SubElement(item, "PARAM")
                ET.SubElement(param, "PARAM_NAME").text = attr.name
                ET.SubElement(param, "VAL").text = attr.value
        ET.indent(tree)
        path = out / "heureka-enriched.xml"
        tree.write(path, encoding="utf-8", xml_declaration=True)
        files["heureka"] = path

    # Google Merchant Center – doplnkový (supplemental) feed v TSV.
    # Formát product_detail „sekce:atribut:hodnota“ podľa dokumentácie Merchant Center (overiť pred nasadením).
    path = out / "merchant-supplemental.tsv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["id", "title", "description", "product_highlight", "product_detail"])
        for p in products:
            r = results.get(p.item_id)
            if not r or not r.data:
                continue
            # čiarka oddeľuje viac hodnôt → desatinnú čiarku prevedieme na bodku, ostatné čiarky odstránime
            def safe(text: str) -> str:
                return re.sub(r"(\d),(\d)", r"\1.\2", text).replace(",", " ")

            details = ",".join(safe(f"Parametry:{a.name}:{a.value}") for a in r.verified)
            w.writerow([p.item_id, r.data.better_name, r.data.short_description,
                        ",".join(safe(u) for u in r.data.use_cases[:4]), details])
    files["merchant"] = path
    return files

"""Načítanie Heureka XML feedu (súbor alebo URL) do jednoduchého produktového modelu."""

import io
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import requests


@dataclass
class Product:
    item_id: str
    name: str
    description: str = ""
    url: str = ""
    image: str = ""
    price: float | None = None
    manufacturer: str = ""
    category: str = ""
    ean: str = ""
    delivery_days: int | None = None
    params: dict[str, str] = field(default_factory=dict)

    @property
    def source_text(self) -> str:
        """Všetok text, z ktorého smie AI čerpať pri obohatení."""
        params = "; ".join(f"{k}: {v}" for k, v in self.params.items())
        return f"{self.name}\n{self.description}\n{params}\n{self.manufacturer}"


def _text(el: ET.Element, tag: str) -> str:
    child = el.find(tag)
    return (child.text or "").strip() if child is not None else ""


def _read(source: str) -> bytes:
    if source.startswith(("http://", "https://")):
        resp = requests.get(source, timeout=120, headers={"User-Agent": "agent-ready-audit/0.1"})
        resp.raise_for_status()
        return resp.content
    return Path(source).read_bytes()


def load(source: str, limit: int | None = None) -> list[Product]:
    products = []
    # iterparse kvôli veľkým feedom; kódovanie (aj windows-1250) berie z XML hlavičky
    for _, el in ET.iterparse(io.BytesIO(_read(source)), events=("end",)):
        if el.tag != "SHOPITEM":
            continue
        price = _text(el, "PRICE_VAT").replace(",", ".")
        delivery = _text(el, "DELIVERY_DATE")
        products.append(Product(
            item_id=_text(el, "ITEM_ID"),
            name=_text(el, "PRODUCTNAME") or _text(el, "PRODUCT"),
            description=_text(el, "DESCRIPTION"),
            url=_text(el, "URL"),
            image=_text(el, "IMGURL"),
            price=float(price) if price.replace(".", "", 1).isdigit() else None,
            manufacturer=_text(el, "MANUFACTURER"),
            category=_text(el, "CATEGORYTEXT"),
            ean=_text(el, "EAN"),
            delivery_days=int(delivery) if delivery.isdigit() else None,
            params={_text(p, "PARAM_NAME"): _text(p, "VAL") for p in el.findall("PARAM") if _text(p, "PARAM_NAME")},
        ))
        el.clear()
        if limit and len(products) >= limit:
            break
    return products

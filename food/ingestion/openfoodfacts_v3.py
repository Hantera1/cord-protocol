"""CORD Food Open Food Facts API v3 adapter.

This adapter fetches one barcode at a time. It preserves the source payload and
returns source assertions; it does not mark any field as independently verified.
Bulk imports must use an approved export workflow and comply with Open Food Facts
API, ODbL/DbCL and image licence requirements.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

API_ROOT = "https://world.openfoodfacts.org/api/v3/product"
SOURCE_KEY = "open_food_facts"
SOURCE_LICENCE = "ODbL-1.0"
IMAGE_LICENCE = "CC-BY-SA"


@dataclass
class FetchResult:
    barcode: str
    retrieved_at: str
    payload: dict[str, Any]
    payload_sha256: str
    source_record_key: str
    source_status: str


def fetch_product(barcode: str, *, user_agent: str | None = None) -> FetchResult:
    if not barcode or not barcode.isdigit():
        raise ValueError("Barcode must contain digits only")

    agent = user_agent or os.getenv(
        "CORD_FOOD_USER_AGENT",
        "CORD-Food-Research/0.1 (contact: data-operations)"
    )
    url = f"{API_ROOT}/{barcode}.json"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": agent, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            retry_after = exc.headers.get("Retry-After", "unknown")
            raise RuntimeError(f"Rate limited by source; Retry-After={retry_after}") from exc
        raise

    payload = json.loads(raw.decode("utf-8"))
    product = payload.get("product") or {}
    source_status = "found" if payload.get("status") == 1 and product else "not_found"
    return FetchResult(
        barcode=barcode,
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        payload=payload,
        payload_sha256=sha256(raw).hexdigest(),
        source_record_key=str(product.get("code") or barcode),
        source_status=source_status,
    )


def to_cord_assertions(result: FetchResult) -> list[dict[str, Any]]:
    """Map selected source fields to provenance-bearing assertions."""
    product = result.payload.get("product") or {}
    fields = {
        "product_name": product.get("product_name"),
        "brands": product.get("brands"),
        "quantity": product.get("quantity"),
        "ingredients_text": product.get("ingredients_text"),
        "ingredients_text_en": product.get("ingredients_text_en"),
        "allergens_tags": product.get("allergens_tags"),
        "nutriments": product.get("nutriments"),
        "countries": product.get("countries"),
        "origins": product.get("origins"),
        "manufacturing_places": product.get("manufacturing_places"),
        "categories_tags": product.get("categories_tags"),
        "labels_tags": product.get("labels_tags"),
        "last_modified_t": product.get("last_modified_t"),
    }
    assertions = []
    for predicate, value in fields.items():
        if value is None or value == "":
            continue
        assertions.append({
            "source_key": SOURCE_KEY,
            "source_record_key": result.source_record_key,
            "predicate": predicate,
            "value": value,
            "retrieved_at": result.retrieved_at,
            "payload_sha256": result.payload_sha256,
            "licence_id": SOURCE_LICENCE,
            "evidence_class": "database_reference",
            "verification_status": "unverified",
        })
    return assertions


def fetch_many(barcodes: list[str], *, delay_seconds: float = 2.0) -> list[FetchResult]:
    """Conservative serial fetch; production rate must follow current source terms."""
    results = []
    for index, barcode in enumerate(barcodes):
        results.append(fetch_product(barcode))
        if index < len(barcodes) - 1:
            time.sleep(max(0.0, delay_seconds))
    return results

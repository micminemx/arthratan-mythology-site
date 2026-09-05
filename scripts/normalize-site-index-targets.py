#!/usr/bin/env python3
"""Normalize A-Z index targets to implemented static/dynamic destinations.

This is an information-architecture repair only. It changes navigation metadata and
adds stable HTML ids to already-rendered chronology records; it does not rewrite
canon text or invent identity relationships.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from site_index_target_gate import audit_site_index_targets

ROOT = Path(__file__).resolve().parent.parent
SITE_INDEX = ROOT / "data" / "site-index.json"
CHRONOLOGY_PAGE = ROOT / "chronology" / "index.html"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_ids() -> list[str]:
    idx = load(ROOT / "data" / "zubaida-index.json")
    non = load(ROOT / "data" / "zubaida-nonsource.json")
    excluded = {row["id"] if isinstance(row, dict) else row for row in non.get("ids", [])}
    rows = [mid for mid in idx.get("ids", []) if mid not in excluded]
    expected = idx.get("audit", {}).get("source_bearing_transmissions", 118)
    if len(rows) != expected:
        raise RuntimeError(f"Expected {expected} source-bearing transmissions, found {len(rows)}")
    return rows


def concept_title_routes() -> dict[str, list[str]]:
    routes: dict[str, list[str]] = {}
    root = ROOT / "concepts"
    if not root.exists():
        return routes
    for child in sorted(p for p in root.iterdir() if p.is_dir()):
        page = child / "index.html"
        if not page.exists():
            continue
        text = page.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"<h1[^>]*>(.*?)</h1>", text, flags=re.I | re.S)
        if not m:
            continue
        title = html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
        title = re.sub(r"\s+", " ", title).strip().casefold()
        routes.setdefault(title, []).append(f"/concepts/{child.name}/")
    return routes


def patch_chronology_anchors(records: list[dict]) -> int:
    if not CHRONOLOGY_PAGE.exists():
        raise RuntimeError("chronology/index.html is missing")
    text = CHRONOLOGY_PAGE.read_text(encoding="utf-8")
    changed = 0
    for rec in records:
        rid = str(rec.get("id") or "").strip()
        subject = str(rec.get("subject") or rec.get("title") or rid).strip()
        if not rid or not subject:
            continue
        if re.search(rf"\bid\s*=\s*['\"]{re.escape(rid)}['\"]", text, flags=re.I):
            continue
        escaped = html.escape(subject, quote=False)
        needle = f"<li><strong>{escaped}</strong>"
        replacement = f'<li id="{html.escape(rid, quote=True)}"><strong>{escaped}</strong>'
        if needle not in text:
            raise RuntimeError(f"Could not locate rendered chronology record {rid}: {subject}")
        text = text.replace(needle, replacement, 1)
        changed += 1
    if changed:
        CHRONOLOGY_PAGE.write_text(text, encoding="utf-8", newline="")
    return changed


def set_target_everywhere(data: dict, entry_id: str, target: str, *, provenance: str | None = None, description: str | None = None) -> None:
    for bucket in data.get("a_to_z", {}).values():
        for entry in bucket:
            if entry.get("id") != entry_id:
                continue
            entry["target_url"] = target
            if provenance is not None:
                entry["provenance"] = provenance
            if description is not None:
                entry["description"] = description
    for cats in data.get("hierarchical_tree", {}).values():
        for rows in cats.values():
            for entry in rows:
                if entry.get("id") == entry_id:
                    entry["target_url"] = target
    for alias in data.get("alias_map", {}).values():
        if alias.get("canonical_id") == entry_id:
            alias["target_url"] = target


def unique_entries(data: dict) -> dict[str, dict]:
    out = {}
    for bucket in data.get("a_to_z", {}).values():
        for entry in bucket:
            if entry.get("id"):
                out.setdefault(entry["id"], entry)
    return out


def main() -> int:
    data = load(SITE_INDEX)
    entries = unique_entries(data)
    changes = []

    # 1. Zubaida: replace synthetic numeric hash aliases with actual preserved source IDs.
    zids = source_ids()
    z_entries = sorted((eid, row) for eid, row in entries.items() if re.fullmatch(r"zub-trans-\d{3}", eid))
    if len(z_entries) != len(zids):
        raise RuntimeError(f"Site index contains {len(z_entries)} Zubaida entries; source registry contains {len(zids)}")
    for position, (eid, row) in enumerate(z_entries, start=1):
        mid = zids[position - 1]
        target = f"/zubaida/{mid}/"
        set_target_everywhere(
            data,
            eid,
            target,
            provenance=f"sources/zubaida/{mid}.txt",
            description=f"Verbatim preserved source-bearing Zubaida transmission {mid}.",
        )
        if row.get("target_url") != target:
            changes.append((eid, row.get("target_url"), target))

    # 2. Divine: prefer durable crawlable page routes instead of fragile generated hashes.
    divine = load(ROOT / "data" / "divine.json").get("sections", [])
    for ordinal, sec in enumerate(divine, start=1):
        key = str(sec.get("section") or sec.get("id"))
        eid = f"divine-sec-{key}"
        if eid not in entries:
            raise RuntimeError(f"Divine site-index entry missing for {eid}")
        target = f"/divine/{ordinal:03d}/"
        if not (ROOT / "divine" / f"{ordinal:03d}" / "index.html").exists():
            raise RuntimeError(f"Static Divine target missing: {target}")
        old = entries[eid].get("target_url")
        set_target_everywhere(data, eid, target)
        if old != target:
            changes.append((eid, old, target))

    # 3. Concept inventory: use real static concept pages when an exact published title exists.
    concept_routes = concept_title_routes()
    masterpage_ids = {str(x.get("id")) for x in load(ROOT / "data" / "masterpages.json").get("masterpages", []) if x.get("id")}
    for eid, row in entries.items():
        if not eid.startswith("concept-"):
            continue
        title_key = str(row.get("label") or "").strip().casefold()
        matches = concept_routes.get(title_key, [])
        if len(matches) == 1:
            target = matches[0]
            old = row.get("target_url")
            set_target_everywhere(data, eid, target)
            if old != target:
                changes.append((eid, old, target))
            continue
        # If no static title match exists, only retain an explicitly implemented masterpage id.
        current = str(row.get("target_url") or "")
        m = re.fullmatch(r"/?#masterpage:(.+)", current)
        if not m:
            m = re.fullmatch(r"/#masterpage:(.+)", current)
        if not m or m.group(1) not in masterpage_ids:
            raise RuntimeError(f"Concept target has no exact static page or implemented masterpage: {eid} -> {current}")

    # 4. Supersession records: link to static chronology anchors rather than an unimplemented SPA prefix.
    chronology = load(ROOT / "data" / "canon-supersession-chronology.json").get("supersessions", [])
    patch_chronology_anchors(chronology)
    for rec in chronology:
        rid = str(rec.get("id"))
        eid = f"chron-{rid}"
        if eid not in entries:
            raise RuntimeError(f"Chronology site-index entry missing: {eid}")
        target = f"/chronology/#{rid}"
        old = entries[eid].get("target_url")
        set_target_everywhere(data, eid, target)
        if old != target:
            changes.append((eid, old, target))

    # 5. Any culture/institution entry must point to a real surface. The canonical data declares
    # /concepts/culture/, but that page is not yet published in this branch, so fail closed rather
    # than silently retaining an invented route. (A dedicated culture hub can be added separately.)
    for eid, row in entries.items():
        if eid.startswith("inst-"):
            target = str(row.get("target_url") or "")
            if target.startswith("/concepts/culture/") and not (ROOT / "concepts" / "culture" / "index.html").exists():
                raise RuntimeError(f"Institution target requires missing /concepts/culture/ hub: {eid}")

    SITE_INDEX.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="")

    result = audit_site_index_targets(ROOT)
    if not result["passed"]:
        raise RuntimeError("Normalized site index still has invalid targets: " + json.dumps(result["failures"][:20], ensure_ascii=False))

    print(f"Normalized {len(changes)} A-Z index target records; chronology anchors verified; {result['checked']} runtime targets valid.")
    for eid, old, new in changes[:30]:
        print(f" - {eid}: {old} -> {new}")
    if len(changes) > 30:
        print(f" ... {len(changes)-30} additional target normalizations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

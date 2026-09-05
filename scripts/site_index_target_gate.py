#!/usr/bin/env python3
"""Validate every runtime navigation target emitted by data/site-index.json.

The static HTML graph cannot see links created at runtime by app.js. This gate closes
that blind spot by validating the A-Z index's data-driven targets against real static
files/fragments and exact implemented SPA records.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import urllib.parse
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_bearing_zubaida_ids(root: Path) -> set[str]:
    idx = load_json(root / "data" / "zubaida-index.json")
    non = load_json(root / "data" / "zubaida-nonsource.json")
    excluded = {row["id"] if isinstance(row, dict) else row for row in non.get("ids", [])}
    source = [mid for mid in idx.get("ids", []) if mid not in excluded]
    expected = idx.get("audit", {}).get("source_bearing_transmissions", 118)
    if len(source) != expected:
        raise RuntimeError(f"Zubaida source-bearing count mismatch: expected {expected}, got {len(source)}")
    return set(source)


def html_anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    vals = set(re.findall(r"\bid\s*=\s*['\"]([^'\"]+)['\"]", text, flags=re.I))
    vals.update(re.findall(r"<a\b[^>]*\bname\s*=\s*['\"]([^'\"]+)['\"]", text, flags=re.I))
    return {html.unescape(v) for v in vals}


def resolve_static(root: Path, url_path: str) -> Path | None:
    rel = urllib.parse.unquote(url_path).lstrip("/")
    if not rel:
        return root / "index.html"
    candidates = []
    if url_path.endswith("/"):
        candidates.append(root / rel / "index.html")
    candidates.extend([root / rel, root / rel / "index.html", root / f"{rel}.html"])
    for p in candidates:
        if p.is_file():
            return p
    return None


def app_route_registry(root: Path) -> tuple[set[str], set[str]]:
    text = (root / "app.js").read_text(encoding="utf-8", errors="ignore")
    exact = set(re.findall(r"\bh\s*===\s*['\"]([^'\"]+)['\"]", text))
    exact.update(re.findall(r"\bh===['\"]([^'\"]+)['\"]", text))
    prefixes = set(re.findall(r"\bh\.startsWith\(['\"]([^'\"]+)['\"]\)", text))
    # The router treats the empty hash as Home.
    exact.add("")
    return exact, prefixes


def exact_payload_registries(root: Path) -> dict[str, set[str]]:
    masterpages = {str(x.get("id")) for x in load_json(root / "data" / "masterpages.json").get("masterpages", []) if x.get("id") is not None}
    characters = {str(x.get("slug")) for x in load_json(root / "data" / "characters.json").get("characters", []) if x.get("slug")}
    divine_rows = load_json(root / "data" / "divine.json").get("sections", [])
    divine = {str(x.get("id")) for x in divine_rows if x.get("id") is not None}
    hgl = load_json(root / "data" / "hgl-toc.json")
    hgl_parts = {str(x.get("part") or x.get("id")) for x in hgl.get("parts", []) if (x.get("part") or x.get("id")) is not None}
    site_index = load_json(root / "data" / "site-index.json")
    index_letters = set(site_index.get("a_to_z", {}).keys()) | {x.lower() for x in site_index.get("a_to_z", {}).keys()}
    return {
        "masterpage:": masterpages,
        "character:": characters,
        "divine-section:": divine,
        "hgl-part:": hgl_parts,
        "transmission:": source_bearing_zubaida_ids(root),
        "zubaida:": source_bearing_zubaida_ids(root),
        "index:": index_letters,
    }


def iter_unique_entries(data: dict):
    seen = set()
    for bucket in data.get("a_to_z", {}).values():
        for entry in bucket:
            eid = entry.get("id")
            if not eid or eid in seen:
                continue
            seen.add(eid)
            yield entry


def audit_site_index_targets(root: Path) -> dict:
    root = Path(root).resolve()
    data = load_json(root / "data" / "site-index.json")
    exact_routes, prefix_routes = app_route_registry(root)
    registries = exact_payload_registries(root)
    failures = []
    checked = 0

    for entry in iter_unique_entries(data):
        checked += 1
        eid = entry.get("id")
        target = str(entry.get("target_url") or "").strip()
        if not target:
            failures.append({"id": eid, "target": target, "reason": "empty_target"})
            continue
        parts = urllib.parse.urlsplit(target)
        if parts.scheme or parts.netloc:
            failures.append({"id": eid, "target": target, "reason": "external_target_not_allowed"})
            continue

        # A non-root path is a static route, optionally with a static fragment.
        if parts.path not in ("", "/"):
            page = resolve_static(root, parts.path)
            if page is None:
                failures.append({"id": eid, "target": target, "reason": "static_target_missing"})
                continue
            if parts.fragment and parts.fragment not in html_anchors(page):
                failures.append({"id": eid, "target": target, "reason": "static_fragment_missing", "file": page.relative_to(root).as_posix()})
            continue

        frag = urllib.parse.unquote(parts.fragment)
        if frag in exact_routes:
            continue

        matched_prefix = None
        for prefix in sorted(prefix_routes, key=len, reverse=True):
            if frag.startswith(prefix):
                matched_prefix = prefix
                break
        if matched_prefix is None:
            failures.append({"id": eid, "target": target, "reason": "spa_route_not_implemented"})
            continue

        if matched_prefix in registries:
            payload = frag[len(matched_prefix):]
            if payload not in registries[matched_prefix]:
                failures.append({"id": eid, "target": target, "reason": "spa_payload_not_implemented", "prefix": matched_prefix, "payload": payload})

    return {
        "schema": "site-index-target-gate-v1",
        "checked": checked,
        "failure_count": len(failures),
        "passed": not failures,
        "failures": failures,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--out", default="reports/architecture/omniindex-v2/site_index_target_gate.json")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    result = audit_site_index_targets(root)
    out = root / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"checked": result["checked"], "failures": result["failure_count"], "passed": result["passed"]}, indent=2))
    if result["failures"]:
        for row in result["failures"][:30]:
            print("FAIL", row)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

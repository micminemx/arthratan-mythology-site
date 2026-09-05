# -*- coding: utf-8 -*-
"""Normalize static-page deep links to routes actually implemented by the SPA.

The old static prerenderer emitted several syntactically plausible hash routes whose
prefixes were accepted by the architecture compiler even though their exact targets
were not handled correctly by app.js/archive.js. This postprocessor fixes only
mechanically provable mappings from the authoritative data files:

- Divine static page N -> #divine-section:<actual section id>
- HGL static page N -> #hgl-page-direct:N
- Zubaida reader <id> -> #transmission:<id>
- Static concept pages -> real Concepts/Search discovery surfaces (there is no
  #concept:<id> renderer in app.js)

It does not edit source text inside <pre> blocks and is idempotent.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="")


def patch_exact(path: Path, old: str, new: str) -> bool:
    if not path.exists():
        raise RuntimeError(f"Expected generated static page is missing: {path.relative_to(ROOT)}")
    text = read(path)
    if old not in text:
        if new in text:
            return False
        raise RuntimeError(f"Expected legacy SPA link not found in {path.relative_to(ROOT)}: {old}")
    updated = text.replace(old, new)
    write(path, updated)
    return True


def normalize_divine() -> int:
    data = json.loads(read(ROOT / "data" / "divine.json"))
    sections = data.get("sections", [])
    changed = 0
    for i, section in enumerate(sections):
        n = section.get("section") or (i + 1)
        key = f"{int(n):03d}"
        sid = section.get("id")
        if not sid:
            raise RuntimeError(f"Divine section {n} has no exact SPA section id")
        page = ROOT / "divine" / key / "index.html"
        old = f'/#divine-section:{n}'
        new = f'/#divine-section:{sid}'
        changed += int(patch_exact(page, old, new))
    return changed


def normalize_hgl() -> int:
    data = json.loads(read(ROOT / "data" / "hgl-pages.json"))
    pages = data if isinstance(data, list) else data.get("pages", [])
    changed = 0
    for i, row in enumerate(pages):
        n = row.get("page") or (i + 1)
        key = f"{int(n):03d}"
        page = ROOT / "hgl" / key / "index.html"
        old = f'/#hgl-part:{n}'
        new = f'/#hgl-page-direct:{n}'
        changed += int(patch_exact(page, old, new))
    return changed


def normalize_zubaida() -> int:
    changed = 0
    root = ROOT / "zubaida"
    if not root.exists():
        return 0
    for child in sorted(p for p in root.iterdir() if p.is_dir()):
        page = child / "index.html"
        if not page.exists():
            continue
        tid = child.name
        text = read(page)
        old = f'/#zubaida:{tid}'
        new = f'/#transmission:{tid}'
        if old in text:
            text = text.replace(old, new)
            write(page, text)
            changed += 1
        elif new in text:
            continue
        else:
            # Some deliberately preserved legacy/static reader aliases expose no SPA
            # deep link at all. Absence is not a broken target; only an emitted bad
            # #zubaida:<id> alias is a defect. Leave such pages unchanged.
            continue
    return changed


def concept_rows() -> list[tuple[str, str]]:
    data = json.loads(read(ROOT / "data" / "global-concept-inventory.json"))
    rows = []
    for domain in data.get("domains", {}).values():
        for concept in domain.get("concepts", []):
            name = concept.get("name")
            if not name:
                continue
            cid = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "untitled"
            rows.append((cid, name))
    return rows


def normalize_concepts() -> int:
    changed = 0
    for cid, name in concept_rows():
        page = ROOT / "concepts" / cid / "index.html"
        if not page.exists():
            raise RuntimeError(f"Concept static page missing: concepts/{cid}/index.html")
        text = read(page)
        pattern = re.compile(
            r'<p class="notice"><strong>Interactive View:</strong> Explore related conceptual trees in the '
            r'<a href="/#concept:' + re.escape(cid) + r'">Codex Knowledge Graph</a>\.</p>'
        )
        replacement = (
            '<p class="notice"><strong>Related discovery:</strong> Browse the '
            '<a href="/concepts/">Concepts directory</a> or '
            f'<a href="/search/?q={quote(name)}">search the Codex for {html.escape(name)}</a>.</p>'
        )
        updated, count = pattern.subn(replacement, text, count=1)
        if count:
            write(page, updated)
            changed += 1
        elif '/#concept:' + cid in text:
            raise RuntimeError(f"Concept page shape changed; refusing unsafe rewrite: {cid}")
    return changed


def assert_no_legacy_dynamic_aliases() -> None:
    offenders = []
    for root_name in ["divine", "hgl", "zubaida", "concepts"]:
        root = ROOT / root_name
        if not root.exists():
            continue
        for page in root.rglob("index.html"):
            text = read(page)
            if re.search(r'href=["\']/?#(?:zubaida:|concept:)', text, flags=re.I):
                offenders.append(str(page.relative_to(ROOT)))
    if offenders:
        raise RuntimeError("Legacy/unimplemented SPA aliases remain: " + ", ".join(offenders[:20]))


if __name__ == "__main__":
    counts = {
        "divine": normalize_divine(),
        "hgl": normalize_hgl(),
        "zubaida": normalize_zubaida(),
        "concepts": normalize_concepts(),
    }
    assert_no_legacy_dynamic_aliases()
    print("Normalized static SPA links:", counts, "total", sum(counts.values()))

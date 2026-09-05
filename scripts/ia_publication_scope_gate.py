#!/usr/bin/env python3
"""Pre-publication scope/canon-boundary gate for the IA repair branch.

This gate proves that the IA change set does not rewrite primary canon payloads while
allowing deterministic navigation, relationship-block, index and tooling changes.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "origin/main"

PROHIBITED_EXACT = {
    "COMMANDER.md",
    "data/characters.json",
    "data/masterpages.json",
    "data/divine.json",
    "data/hgl-pages.json",
    "data/hgl-toc.json",
    "data/canon-supersession-chronology.json",
    "data/clans.json",
    "data/clans-supplemental.json",
    "data/culture-clans-ontology.json",
    "data/global-concept-inventory.json",
}

RELATION_BLOCK = re.compile(
    r"<!--\s*PUBLICATION-RELATIONS:START\s*-->.*?<!--\s*PUBLICATION-RELATIONS:END\s*-->",
    re.I | re.S,
)
SOURCE_PRE = re.compile(r"<pre\s+class=[\"']source[\"'][^>]*>(.*?)</pre>", re.I | re.S)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8", errors="replace")


def changed_paths() -> list[str]:
    return [x.strip() for x in git("diff", "--name-only", f"{BASE}...HEAD").splitlines() if x.strip()]


def base_text(path: str) -> str | None:
    try:
        return git("show", f"{BASE}:{path}")
    except subprocess.CalledProcessError:
        return None


def normalize_publication(text: str) -> str:
    text = RELATION_BLOCK.sub("", text)
    # Relationship-block insertion can introduce a newline between adjacent closing
    # tags. Treat inter-tag whitespace as formatting, then collapse remaining runs.
    text = re.sub(r">\s+<", "><", text)
    return re.sub(r"\s+", " ", text).strip()


def fail(msg: str, failures: list[str]) -> None:
    failures.append(msg)


def main() -> int:
    paths = changed_paths()
    failures: list[str] = []

    for path in paths:
        if path == "COMMANDER.md" or path.startswith("sources/") or path in PROHIBITED_EXACT:
            fail(f"Prohibited canon/source path changed: {path}", failures)

    # Myth/Crossscaling prose must be equivalent modulo the explicitly generated
    # relationship block and insignificant whitespace around its insertion point.
    for path in paths:
        if not (path.startswith("myths/") or path.startswith("crossscaling/")) or not path.endswith("/index.html"):
            continue
        current_path = ROOT / path
        old = base_text(path)
        if old is None or not current_path.exists():
            continue
        new = current_path.read_text(encoding="utf-8", errors="replace")
        if normalize_publication(old) != normalize_publication(new):
            fail(f"Publication prose changed outside PUBLICATION-RELATIONS block: {path}", failures)

    # Existing Zubaida rendered verbatim source payload must remain exactly identical.
    for path in paths:
        if not path.startswith("zubaida/") or not path.endswith("/index.html"):
            continue
        old = base_text(path)
        current_path = ROOT / path
        if old is None or not current_path.exists():
            continue
        new = current_path.read_text(encoding="utf-8", errors="replace")
        old_pre = SOURCE_PRE.findall(old)
        new_pre = SOURCE_PRE.findall(new)
        if old_pre != new_pre:
            fail(f"Zubaida verbatim <pre class=source> payload changed: {path}", failures)

    # Every published crossscale must continue to expose the NONCANON boundary.
    for page in sorted((ROOT / "crossscaling").glob("*/index.html")):
        text = page.read_text(encoding="utf-8", errors="replace")
        if "CROSSSCALE-ONLY" not in text.upper() or "NONCANON" not in text.upper():
            fail(f"Crossscaling canon boundary missing: {page.relative_to(ROOT).as_posix()}", failures)

    print(f"IA publication scope gate checked {len(paths)} changed paths.")
    if failures:
        print(f"FAIL: {len(failures)} scope/canon-boundary violations")
        for item in failures[:100]:
            print(" -", item)
        return 1
    print("PASS: primary source/canon data untouched; Myth/Crossscale prose preserved outside typed relation blocks; Crossscaling NONCANON boundary intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

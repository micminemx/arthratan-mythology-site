#!/usr/bin/env python3
"""Repair the obsolete /#clans alias in static clan pages.

The SPA has no #clans route handler; /clans/ is the canonical static directory.
This pass is deliberately narrow and idempotent, changes navigation only, and
never edits source/canon text beyond href targets.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLANS = ROOT / "clans"
OLD = 'href="/#clans"'
NEW = 'href="/clans/"'


def main() -> int:
    changed = []
    offenders = []
    if not CLANS.exists():
        raise RuntimeError("Expected clans/ directory is missing")
    for path in sorted(CLANS.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        if OLD in text:
            updated = text.replace(OLD, NEW)
            path.write_text(updated, encoding="utf-8", newline="")
            changed.append(path.relative_to(ROOT).as_posix())
    for path in sorted(CLANS.rglob("*.html")):
        if OLD in path.read_text(encoding="utf-8"):
            offenders.append(path.relative_to(ROOT).as_posix())
    if offenders:
        raise RuntimeError("Unimplemented /#clans aliases remain: " + ", ".join(offenders[:40]))
    print(f"Normalized clan navigation in {len(changed)} files.")
    for rel in changed:
        print(" -", rel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""Register hand-authored Myth and Crossscaling routes in generated discovery surfaces.

This postprocessor is intentionally idempotent. It preserves the canonical/noncanon
boundary: Myths are canonical narrative pages; Crossscaling pages are explicitly
NONCANON analytical surfaces. It also repairs Rhayhara's generated dossier backlinks
if the comprehensive static generator is rerun.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MANIFEST = os.path.join(ROOT, "data", "static-route-manifest.json")
CRAWL = os.path.join(ROOT, "crawl", "index.html")
RHAYHARA = os.path.join(ROOT, "characters", "rhayhara", "index.html")

CUSTOM_ROUTES = [
    {
        "kind": "myth",
        "key": "rhayharas-ten-destiny-defying-trials",
        "url": "/myths/rhayharas-ten-destiny-defying-trials/",
        "source": "sources/zubaida/19f0e8f96cb8730c.txt",
        "title": "Rhayhara's Ten Destiny-Defying Trials",
        "canon_status": "canonical-narrative",
    },
    {
        "kind": "myth",
        "key": "rhayhara-and-othrys-five-orthogonal-escalations",
        "url": "/myths/rhayhara-and-othrys-five-orthogonal-escalations/",
        "source": "sources/zubaida/19f0d1c0f4a5d5e5.txt",
        "title": "Rhayhara and Othrys: Five Orthogonal Escalations",
        "canon_status": "canonical-narrative",
    },
    {
        "kind": "crossscaling",
        "key": "master-crossscaling",
        "url": "/crossscaling/",
        "source": "crossscaling/index.html",
        "title": "Master Crossscaling",
        "canon_status": "noncanon-analytical",
    },
    {
        "kind": "crossscaling",
        "key": "rhayhara-othrys-orthogonal-escalation",
        "url": "/crossscaling/rhayhara-othrys-orthogonal-escalation/",
        "source": "sources/zubaida/19f0d1c0f4a5d5e5.txt",
        "title": "Rhayhara–Othrys Orthogonal Escalation Crossscale",
        "canon_status": "noncanon-analytical",
    },
]

START = "<!-- PUBLICATION-GRAPH:START -->"
END = "<!-- PUBLICATION-GRAPH:END -->"


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def register_manifest() -> int:
    with open(MANIFEST, "r", encoding="utf-8") as f:
        data = json.load(f)
    routes = data.setdefault("routes", [])
    by_url = {r.get("url"): i for i, r in enumerate(routes)}
    for route in CUSTOM_ROUTES:
        if route["url"] in by_url:
            routes[by_url[route["url"]]] = route
        else:
            routes.append(route)
            by_url[route["url"]] = len(routes) - 1
    data["count"] = len(routes)
    data["generated"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    data["scope_note"] = (
        "Includes canonical corpus routes plus explicitly labelled noncanon analytical "
        "Crossscaling routes; canon_status preserves the boundary."
    )
    with open(MANIFEST, "w", encoding="utf-8", newline="") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return len(routes)


def custom_crawl_block() -> str:
    myths = [r for r in CUSTOM_ROUTES if r["kind"] == "myth"]
    scales = [r for r in CUSTOM_ROUTES if r["kind"] == "crossscaling"]
    myth_items = "".join(
        f"<li><a href='{html.escape(r['url'])}'>{html.escape(r['title'])}</a></li>" for r in myths
    )
    scale_items = "".join(
        f"<li><a href='{html.escape(r['url'])}'>{html.escape(r['title'])}</a> "
        f"<strong>(CROSSSCALE-ONLY / NONCANON)</strong></li>" for r in scales
    )
    return (
        f"{START}"
        f"<h2 id='myth'>MYTH ({len(myths)} Canonical Narrative Pages)</h2><ul>{myth_items}</ul>"
        f"<h2 id='crossscaling'>CROSSSCALING ({len(scales)} Noncanon Analytical Pages)</h2>"
        "<p class='notice'><strong>Canon boundary:</strong> Crossscaling pages are external analytical "
        "surfaces. Their benchmark and totalizer terms are not Arthratan canon unless separately canonized.</p>"
        f"<ul>{scale_items}</ul>{END}"
    )


def patch_nav(text: str) -> str:
    if 'href="/myths/"' not in text:
        text = text.replace(
            '<a href="/crawl/">Crawler Index</a>',
            '<a href="/myths/">Myths</a>\n    <a href="/crossscaling/">Crossscaling</a>\n    <a href="/crawl/">Crawler Index</a>',
            1,
        )
    elif 'href="/crossscaling/"' not in text:
        text = text.replace(
            '<a href="/myths/">Myths</a>',
            '<a href="/myths/">Myths</a>\n    <a href="/crossscaling/">Crossscaling</a>',
            1,
        )
    return text


def patch_crawl(count: int) -> None:
    text = read(CRAWL)
    text = patch_nav(text)
    text = re.sub(
        r'<meta name="description" content="Exhaustive crawlable index of all \d+ canonical pages in the Arthratan Mythology Codex\.">',
        '<meta name="description" content="Crawlable index of the canonical Arthratan corpus plus explicitly separated noncanon analytical crossscaling records.">',
        text,
        count=1,
    )
    text = re.sub(
        r'100% Comprehensive Non-JavaScript Static Corpus Directory · \d+ Canonical URLs',
        f'100% Comprehensive Non-JavaScript Static Corpus Directory · {count} Crawlable Routes',
        text,
        count=1,
    )
    block = custom_crawl_block()
    if START in text and END in text:
        text = re.sub(re.escape(START) + r'.*?' + re.escape(END), block, text, count=1, flags=re.S)
    else:
        text = text.replace("</article>", block + "\n    </article>", 1)
    write(CRAWL, text)


def rhayhara_links() -> str:
    return (
        '<h2>Canonical Myths</h2><ul>'
        '<li><a href="/myths/rhayharas-ten-destiny-defying-trials/">Rhayhara\'s Ten Destiny-Defying Trials</a> — '
        'Trials I–IX are completed while Trial X remains ongoing in its preserved source state.</li>'
        '<li><a href="/myths/rhayhara-and-othrys-five-orthogonal-escalations/">Rhayhara and Othrys: Five Orthogonal Escalations</a> — '
        'five completed Othrys Hypervysals that successively change the failure-relation being attacked.</li>'
        '</ul>'
        '<h2>Crossscaling</h2><p>External analytical interpretations are kept separate from canon narrative. '
        'See the <a href="/crossscaling/">Master Crossscaling</a> layer and the '
        '<a href="/crossscaling/rhayhara-othrys-orthogonal-escalation/">Rhayhara–Othrys Orthogonal Escalation record</a>, '
        'which links each analytical bridge back to the Myth and exact primary source.</p>'
    )


def patch_rhayhara() -> None:
    text = patch_nav(read(RHAYHARA))
    if "<h2>Canonical Myths</h2>" not in text:
        anchor = "<h2>History</h2>"
        if anchor not in text:
            raise RuntimeError("Rhayhara generator shape changed; cannot safely insert publication backlinks")
        text = text.replace(anchor, rhayhara_links() + anchor, 1)
    write(RHAYHARA, text)


if __name__ == "__main__":
    total = register_manifest()
    patch_crawl(total)
    patch_rhayhara()
    print(f"Publication graph registered: {total} crawlable routes.")

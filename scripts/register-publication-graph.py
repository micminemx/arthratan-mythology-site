# -*- coding: utf-8 -*-
"""Register hand-authored Myth/Crossscaling routes in generated discovery surfaces.

Idempotent and concurrency-safe at the route layer: current filesystem routes are
discovered every run, so newly published or removed Myth/Crossscaling pages do not
require a hardcoded registry update. Myths are canonical narrative routes;
Crossscaling routes are explicitly NONCANON analytical surfaces.

A publication page whose canonical URL points at a different route is treated as a
legacy/redirect alias and is intentionally excluded from canonical discovery lists.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data" / "static-route-manifest.json"
CRAWL = ROOT / "crawl" / "index.html"
RHAYHARA = ROOT / "characters" / "rhayhara" / "index.html"
START = "<!-- PUBLICATION-GRAPH:START -->"
END = "<!-- PUBLICATION-GRAPH:END -->"
PUBLICATION_KINDS = {"myth", "crossscaling"}
CANONICAL_ORIGIN = "https://arthratanmythology.com"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="")


def page_title(path: Path, fallback: str) -> str:
    text = read(path)
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, flags=re.I | re.S)
    raw = m.group(1) if m else fallback
    raw = re.sub(r"<[^>]+>", "", raw)
    return html.unescape(re.sub(r"\s+", " ", raw)).strip()


def canonical_route(path: Path) -> str | None:
    """Return the same-origin canonical route when explicitly declared."""
    text = read(path)
    m = re.search(
        r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
        text,
        flags=re.I,
    )
    if not m:
        return None
    href = html.unescape(m.group(1)).strip()
    if href.startswith(CANONICAL_ORIGIN):
        route = href[len(CANONICAL_ORIGIN):] or "/"
        return route if route.startswith("/") else "/" + route
    if href.startswith("/"):
        return href
    return None


def discover_publication_routes() -> list[dict]:
    routes: list[dict] = []
    specs = [
        ("myth", "myths", "canonical-narrative"),
        ("crossscaling", "crossscaling", "noncanon-analytical"),
    ]
    for kind, dirname, canon_status in specs:
        root = ROOT / dirname
        hub = root / "index.html"
        if hub.exists():
            routes.append({
                "kind": kind,
                "key": f"{dirname}-index",
                "url": f"/{dirname}/",
                "source": f"{dirname}/index.html",
                "title": page_title(hub, dirname.title()),
                "canon_status": canon_status,
            })
        if not root.exists():
            continue
        for child in sorted(p for p in root.iterdir() if p.is_dir()):
            index = child / "index.html"
            if not index.exists():
                continue
            route_url = f"/{dirname}/{child.name}/"
            declared_canonical = canonical_route(index)
            # Legacy aliases may remain as redirect pages for inbound links, but they
            # must not be promoted as distinct canonical Myths/crossscales.
            if declared_canonical and declared_canonical != route_url:
                continue
            routes.append({
                "kind": kind,
                "key": child.name,
                "url": route_url,
                "source": f"{dirname}/{child.name}/index.html",
                "title": page_title(index, child.name.replace("-", " ").title()),
                "canon_status": canon_status,
            })
    return routes


def register_manifest(custom_routes: list[dict]) -> int:
    data = json.loads(read(MANIFEST))
    # Remove prior custom publication records first. This also removes deleted/collision routes.
    routes = [r for r in data.setdefault("routes", []) if r.get("kind") not in PUBLICATION_KINDS]
    routes.extend(custom_routes)
    data["routes"] = routes
    data["count"] = len(routes)
    data["generated"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    data["scope_note"] = (
        "Includes canonical corpus routes plus canonical Myth narrative routes and explicitly labelled "
        "noncanon analytical Crossscaling routes; canon_status preserves the boundary."
    )
    MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="")
    return len(routes)


def custom_crawl_block(custom_routes: list[dict]) -> str:
    myths = [r for r in custom_routes if r["kind"] == "myth"]
    scales = [r for r in custom_routes if r["kind"] == "crossscaling"]
    myth_items = "".join(
        f"<li><a href='{html.escape(r['url'])}'>{html.escape(r['title'])}</a></li>" for r in myths
    )
    scale_items = "".join(
        f"<li><a href='{html.escape(r['url'])}'>{html.escape(r['title'])}</a> "
        f"<strong>(CROSSSCALE-ONLY / NONCANON)</strong></li>" for r in scales
    )
    return (
        f"{START}"
        f"<h2 id='myth'>MYTH ({len(myths)} Canonical Narrative Routes)</h2><ul>{myth_items}</ul>"
        f"<h2 id='crossscaling'>CROSSSCALING ({len(scales)} Noncanon Analytical Routes)</h2>"
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


def patch_crawl(count: int, custom_routes: list[dict]) -> None:
    text = patch_nav(read(CRAWL))
    text = re.sub(
        r'<meta name="description" content="Exhaustive crawlable index of all \d+ canonical pages in the Arthratan Mythology Codex\.">',
        '<meta name="description" content="Crawlable index of the canonical Arthratan corpus, canonical Myths and explicitly separated noncanon analytical crossscaling records.">',
        text,
        count=1,
    )
    text = re.sub(
        r'100% Comprehensive Non-JavaScript Static Corpus Directory · \d+ (?:Canonical URLs|Crawlable Routes)',
        f'100% Comprehensive Non-JavaScript Static Corpus Directory · {count} Crawlable Routes',
        text,
        count=1,
    )
    block = custom_crawl_block(custom_routes)
    if START in text and END in text:
        text = re.sub(re.escape(START) + r'.*?' + re.escape(END), block, text, count=1, flags=re.S)
    else:
        text = text.replace("</article>", block + "\n    </article>", 1)
    write(CRAWL, text)


def rhayhara_links(custom_routes: list[dict]) -> str:
    myths = [r for r in custom_routes if r["kind"] == "myth" and "rhayhara" in r["title"].lower() and r["url"] != "/myths/"]
    scales = [r for r in custom_routes if r["kind"] == "crossscaling" and "rhayhara" in r["title"].lower() and r["url"] != "/crossscaling/"]
    myth_items = "".join(
        f'<li><a href="{html.escape(r["url"])}">{html.escape(r["title"])}</a></li>' for r in myths
    )
    scale_items = "".join(
        f'<li><a href="{html.escape(r["url"])}">{html.escape(r["title"])}</a> '
        '<strong>(CROSSSCALE-ONLY / NONCANON)</strong></li>' for r in scales
    )
    return (
        f"<h2>Canonical Myths</h2><ul>{myth_items}</ul>"
        "<h2>Crossscaling</h2><p>External analytical interpretations are kept separate from canon narrative. "
        "See the <a href=\"/crossscaling/\">Master Crossscaling</a> layer.</p>"
        f"<ul>{scale_items}</ul>"
    )


def patch_rhayhara(custom_routes: list[dict]) -> None:
    text = patch_nav(read(RHAYHARA))
    replacement = rhayhara_links(custom_routes)
    if "<h2>Canonical Myths</h2>" in text:
        text = re.sub(
            r"<h2>Canonical Myths</h2>.*?(?=<h2>History</h2>)",
            replacement,
            text,
            count=1,
            flags=re.S,
        )
    else:
        anchor = "<h2>History</h2>"
        if anchor not in text:
            raise RuntimeError("Rhayhara generator shape changed; cannot safely insert publication backlinks")
        text = text.replace(anchor, replacement + anchor, 1)
    write(RHAYHARA, text)


if __name__ == "__main__":
    publication_routes = discover_publication_routes()
    total = register_manifest(publication_routes)
    patch_crawl(total, publication_routes)
    patch_rhayhara(publication_routes)
    print(f"Publication graph registered: {len(publication_routes)} custom routes; {total} crawlable routes total.")

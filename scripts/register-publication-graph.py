# -*- coding: utf-8 -*-
"""Register hand-authored Myth/Crossscaling routes in generated discovery surfaces.

Idempotent and concurrency-safe at the route layer: current filesystem routes are
discovered every run, so newly published or removed Myth/Crossscaling pages do not
require a hardcoded registry update. Myths are canonical narrative routes;
Crossscaling routes are explicitly NONCANON analytical surfaces.

Publication pages also become backlink authorities for the character pages they
explicitly reference. This closes the evidence graph in both directions without
hardcoding one character or inferring identities from names/titles.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data" / "static-route-manifest.json"
CRAWL = ROOT / "crawl" / "index.html"
CHARACTERS = ROOT / "characters"
START = "<!-- PUBLICATION-GRAPH:START -->"
END = "<!-- PUBLICATION-GRAPH:END -->"
CHAR_START = "<!-- CHARACTER-PUBLICATION-GRAPH:START -->"
CHAR_END = "<!-- CHARACTER-PUBLICATION-GRAPH:END -->"
PUBLICATION_KINDS = {"myth", "crossscaling"}


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
            routes.append({
                "kind": kind,
                "key": child.name,
                "url": f"/{dirname}/{child.name}/",
                "source": f"{dirname}/{child.name}/index.html",
                "title": page_title(index, child.name.replace("-", " ").title()),
                "canon_status": canon_status,
            })
    return routes


def register_manifest(custom_routes: list[dict]) -> int:
    data = json.loads(read(MANIFEST))
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


def insert_before_outer_article_close(text: str, block: str, label: str) -> str:
    pos = text.rfind("</article>")
    if pos < 0:
        raise RuntimeError(f"Page shape changed; cannot insert publication block: {label}")
    return text[:pos] + block + "\n    " + text[pos:]


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
        text = insert_before_outer_article_close(text, block, str(CRAWL))
    write(CRAWL, text)


def route_file(route: dict) -> Path:
    return ROOT / route["source"]


def publication_character_refs(custom_routes: list[dict]) -> dict[str, dict[str, list[dict]]]:
    """Map explicit character hyperlinks in publication pages back to existing dossiers.

    Identity is never inferred from names. Only an actual href to the canonical character
    route creates the backlink. Missing referenced character routes fail closed because a
    publication page must not silently advertise a broken identity/proof edge.
    """
    refs: dict[str, dict[str, list[dict]]] = {}
    href_re = re.compile(r"href\s*=\s*['\"](?:https://arthratanmythology\.com)?/characters/([^/'\"?#]+)/?['\"]", re.I)
    for route in custom_routes:
        if route["url"] in {"/myths/", "/crossscaling/"}:
            continue
        text = read(route_file(route))
        for slug in sorted(set(href_re.findall(text))):
            target = CHARACTERS / slug / "index.html"
            if not target.exists():
                raise RuntimeError(f"Publication route {route['url']} links missing character route /characters/{slug}/")
            bucket = refs.setdefault(slug, {"myth": [], "crossscaling": []})
            if not any(x["url"] == route["url"] for x in bucket[route["kind"]]):
                bucket[route["kind"]].append(route)
    return refs


def character_publication_block(groups: dict[str, list[dict]]) -> str:
    myths = sorted(groups.get("myth", []), key=lambda r: (r["title"].casefold(), r["url"]))
    scales = sorted(groups.get("crossscaling", []), key=lambda r: (r["title"].casefold(), r["url"]))
    myth_items = "".join(
        f'<li><a href="{html.escape(r["url"])}">{html.escape(r["title"])}</a></li>' for r in myths
    ) or "<li>No character-linked Myth is currently published.</li>"
    scale_items = "".join(
        f'<li><a href="{html.escape(r["url"])}">{html.escape(r["title"])}</a> '
        '<strong>(CROSSSCALE-ONLY / NONCANON)</strong></li>' for r in scales
    ) or "<li>No character-linked crossscale record is currently published.</li>"
    return (
        f"{CHAR_START}"
        "<section class=\"publication-backlinks\" aria-label=\"Myths and crossscaling\">"
        "<h2>Canonical Myths</h2>"
        "<p>Readable source-grounded narratives linked back to exact primary evidence.</p>"
        f"<ul>{myth_items}</ul>"
        "<h2>Crossscaling</h2>"
        "<p>External analytical interpretations are kept separate from canon narrative. "
        "See the <a href=\"/crossscaling/\">Master Crossscaling</a> layer.</p>"
        f"<ul>{scale_items}</ul>"
        "</section>"
        f"{CHAR_END}"
    )


def remove_legacy_rhayhara_block(text: str) -> str:
    """Migrate the first-generation Rhayhara-only backlink block to the generic marker."""
    if CHAR_START in text:
        return text
    if "<h2>Canonical Myths</h2>" in text and "<h2>History</h2>" in text:
        return re.sub(
            r"<h2>Canonical Myths</h2>.*?(?=<h2>History</h2>)",
            "",
            text,
            count=1,
            flags=re.S,
        )
    return text


def patch_character_backlinks(custom_routes: list[dict]) -> list[str]:
    refs = publication_character_refs(custom_routes)
    changed: list[str] = []
    for slug, groups in sorted(refs.items()):
        path = CHARACTERS / slug / "index.html"
        original = read(path)
        text = patch_nav(original)
        if slug == "rhayhara":
            text = remove_legacy_rhayhara_block(text)
        # Always remove an existing generated block before reinsertion. This deliberately
        # relocates first-generation blocks that may have landed inside nested chronicle
        # <article> elements, then anchors the block at the final/outer article boundary.
        if CHAR_START in text and CHAR_END in text:
            text = re.sub(
                re.escape(CHAR_START) + r".*?" + re.escape(CHAR_END),
                "",
                text,
                count=1,
                flags=re.S,
            )
        block = character_publication_block(groups)
        text = insert_before_outer_article_close(text, block, str(path))
        if text != original:
            write(path, text)
            changed.append(slug)
    return changed


def validate_publication_graph(custom_routes: list[dict]) -> None:
    seen = set()
    for route in custom_routes:
        if route["url"] in seen:
            raise RuntimeError(f"Duplicate publication URL: {route['url']}")
        seen.add(route["url"])
        if not route_file(route).exists():
            raise RuntimeError(f"Missing publication file for {route['url']}")
        text = read(route_file(route))
        if route["kind"] == "crossscaling" and "CROSSSCALE-ONLY" not in text.upper():
            raise RuntimeError(f"Crossscaling route lacks explicit CROSSSCALE-ONLY boundary: {route['url']}")


if __name__ == "__main__":
    publication_routes = discover_publication_routes()
    validate_publication_graph(publication_routes)
    total = register_manifest(publication_routes)
    patch_crawl(total, publication_routes)
    changed_characters = patch_character_backlinks(publication_routes)
    print(
        f"Publication graph registered: {len(publication_routes)} custom routes; "
        f"{total} crawlable routes total; {len(changed_characters)} character backlink pages updated."
    )

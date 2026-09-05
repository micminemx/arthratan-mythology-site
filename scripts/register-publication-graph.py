# -*- coding: utf-8 -*-
"""Register published Myth/Crossscaling routes and their typed evidence graph.

This postprocessor is deliberately conservative:
- Myths are canonical narrative surfaces.
- Crossscaling is explicitly NONCANON analysis.
- Relationships come only from explicit publication pages or data/publication-relations.json.
- Primary Zubaida source text is never rewritten; reverse-navigation blocks are inserted
  outside the verbatim <pre class="source"> payload on reader pages.
- No character identity is inferred from prose names.

The script is idempotent and is intended to run in CI after any Myth, Crossscaling,
relation-manifest, or generator change.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data" / "static-route-manifest.json"
RELATIONS = ROOT / "data" / "publication-relations.json"
CRAWL = ROOT / "crawl" / "index.html"
CHARACTERS = ROOT / "characters"
START = "<!-- PUBLICATION-GRAPH:START -->"
END = "<!-- PUBLICATION-GRAPH:END -->"
CHAR_START = "<!-- CHARACTER-PUBLICATION-GRAPH:START -->"
CHAR_END = "<!-- CHARACTER-PUBLICATION-GRAPH:END -->"
REL_START = "<!-- PUBLICATION-RELATIONS:START -->"
REL_END = "<!-- PUBLICATION-RELATIONS:END -->"
SOURCE_START = "<!-- SOURCE-DEPENDENCY-GRAPH:START -->"
SOURCE_END = "<!-- SOURCE-DEPENDENCY-GRAPH:END -->"
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


def route_path(url: str) -> Path:
    """Map a site-relative route to its repository file without guessing aliases."""
    parsed = urlsplit(url)
    path = parsed.path
    if not path.startswith("/"):
        raise RuntimeError(f"Relation route must be site-relative and absolute: {url}")
    rel = path.lstrip("/")
    if not rel:
        return ROOT / "index.html"
    if rel.endswith("/"):
        return ROOT / rel / "index.html"
    return ROOT / rel


def route_label(url: str) -> str:
    p = route_path(url)
    if p.suffix.lower() == ".html" and p.exists():
        return page_title(p, url)
    if "/sources/zubaida/" in url:
        return f"Raw source {Path(urlsplit(url).path).stem}"
    if "/zubaida/" in url:
        return f"Zubaida reader {urlsplit(url).path.strip('/').split('/')[-1]}"
    return url


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


def load_relations() -> list[dict]:
    if not RELATIONS.exists():
        raise RuntimeError(f"Missing typed publication relationship manifest: {RELATIONS}")
    data = json.loads(read(RELATIONS))
    records = data.get("records")
    if not isinstance(records, list) or not records:
        raise RuntimeError("data/publication-relations.json must contain a non-empty records array")
    return records


def validate_relation_manifest(relations: list[dict], publication_routes: list[dict]) -> None:
    ids: set[str] = set()
    published = {r["url"]: r for r in publication_routes}
    for rec in relations:
        rid = rec.get("id")
        if not rid or rid in ids:
            raise RuntimeError(f"Missing or duplicate publication relation id: {rid!r}")
        ids.add(rid)
        myth = rec.get("myth")
        if not myth or myth not in published or published[myth]["kind"] != "myth":
            raise RuntimeError(f"{rid}: unknown Myth route {myth!r}")
        cross = rec.get("crossscaling")
        if cross is not None and (cross not in published or published[cross]["kind"] != "crossscaling"):
            raise RuntimeError(f"{rid}: unknown Crossscaling route {cross!r}")
        chars = rec.get("characters", [])
        if not isinstance(chars, list) or not chars:
            raise RuntimeError(f"{rid}: characters must be a non-empty list")
        for route in chars:
            p = route_path(route)
            if not route.startswith("/characters/") or not p.exists():
                raise RuntimeError(f"{rid}: missing canonical character route {route}")
        primary = rec.get("primary_sources", [])
        if not isinstance(primary, list) or not primary:
            raise RuntimeError(f"{rid}: primary_sources must be a non-empty list")
        for route in primary + rec.get("supporting_sources", []):
            p = route_path(route)
            if not p.exists():
                raise RuntimeError(f"{rid}: missing evidence route {route}")
        if not any(r.startswith("/zubaida/") for r in primary):
            raise RuntimeError(f"{rid}: primary_sources must expose a public Zubaida reader route")


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


def insert_before_last(text: str, token: str, block: str, label: str) -> str:
    pos = text.rfind(token)
    if pos < 0:
        raise RuntimeError(f"Page shape changed; cannot insert generated block before {token}: {label}")
    return text[:pos] + block + "\n" + text[pos:]


def replace_or_insert(text: str, start: str, end: str, block: str, token: str, label: str) -> str:
    if start in text and end in text:
        return re.sub(re.escape(start) + r".*?" + re.escape(end), block, text, count=1, flags=re.S)
    return insert_before_last(text, token, block, label)


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
    text = replace_or_insert(text, START, END, block, "</article>", str(CRAWL))
    write(CRAWL, text)


def relation_links_block(rec: dict) -> str:
    char_items = "".join(
        f'<li><a href="{html.escape(route)}">{html.escape(route_label(route))}</a></li>'
        for route in rec["characters"]
    )
    primary_items = "".join(
        f'<li><a href="{html.escape(route)}">{html.escape(route_label(route))}</a></li>'
        for route in rec["primary_sources"]
    )
    supporting = rec.get("supporting_sources", [])
    supporting_html = ""
    if supporting:
        supporting_items = "".join(
            f'<li><a href="{html.escape(route)}">{html.escape(route_label(route))}</a></li>'
            for route in supporting
        )
        supporting_html = f"<h3>Supporting / supersession evidence</h3><ul>{supporting_items}</ul>"
    reciprocal = []
    if rec.get("myth"):
        reciprocal.append(rec["myth"])
    if rec.get("crossscaling"):
        reciprocal.append(rec["crossscaling"])
    reciprocal_items = "".join(
        f'<li><a href="{html.escape(route)}">{html.escape(route_label(route))}</a>'
        + (" <strong>(CROSSSCALE-ONLY / NONCANON)</strong>" if route.startswith("/crossscaling/") else "")
        + "</li>"
        for route in reciprocal
    )
    return (
        f"{REL_START}<section class=\"publication-relations\" aria-label=\"Related characters and evidence\">"
        "<h2>Relationship &amp; evidence map</h2>"
        "<p>This navigation block records typed relationships already explicit in the published record; it does not create new canon.</p>"
        f"<h3>Characters</h3><ul>{char_items}</ul>"
        f"<h3>Primary evidence</h3><ul>{primary_items}</ul>"
        f"{supporting_html}"
        f"<h3>Reciprocal publication surfaces</h3><ul>{reciprocal_items}</ul>"
        "<p><strong>Canon boundary:</strong> Myth links are canonical narrative surfaces; Crossscaling links are external NONCANON analysis.</p>"
        f"</section>{REL_END}"
    )


def patch_publication_relation_blocks(relations: list[dict]) -> list[str]:
    changed: list[str] = []
    for rec in relations:
        for route in [rec.get("myth"), rec.get("crossscaling")]:
            if not route:
                continue
            path = route_path(route)
            original = read(path)
            block = relation_links_block(rec)
            text = replace_or_insert(original, REL_START, REL_END, block, "</main>", str(path))
            if text != original:
                write(path, text)
                changed.append(route)
    return changed


def publication_character_refs(custom_routes: list[dict]) -> dict[str, dict[str, list[dict]]]:
    """Map explicit canonical character links in publication pages back to dossiers."""
    refs: dict[str, dict[str, list[dict]]] = {}
    href_re = re.compile(r"href\s*=\s*['\"](?:https://arthratanmythology\.com)?/characters/([^/'\"?#]+)/?['\"]", re.I)
    for route in custom_routes:
        if route["url"] in {"/myths/", "/crossscaling/"}:
            continue
        text = read(ROOT / route["source"])
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
    if CHAR_START in text:
        return text
    if "<h2>Canonical Myths</h2>" in text and "<h2>History</h2>" in text:
        return re.sub(r"<h2>Canonical Myths</h2>.*?(?=<h2>History</h2>)", "", text, count=1, flags=re.S)
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
        if CHAR_START in text and CHAR_END in text:
            text = re.sub(re.escape(CHAR_START) + r".*?" + re.escape(CHAR_END), "", text, count=1, flags=re.S)
        block = character_publication_block(groups)
        text = insert_before_last(text, "</article>", block, str(path))
        if text != original:
            write(path, text)
            changed.append(slug)
    return changed


def extract_verbatim_source(text: str) -> str | None:
    m = re.search(r'<pre\s+class=["\']source["\'][^>]*>.*?</pre>', text, flags=re.I | re.S)
    return m.group(0) if m else None


def source_dependency_block(reader_route: str, uses: list[tuple[dict, str]]) -> str:
    items = []
    for rec, role in sorted(uses, key=lambda x: x[0]["id"]):
        myth = rec["myth"]
        cross = rec.get("crossscaling")
        chars = " · ".join(
            f'<a href="{html.escape(c)}">{html.escape(route_label(c))}</a>' for c in rec["characters"]
        )
        links = f'<a href="{html.escape(myth)}">{html.escape(route_label(myth))}</a>'
        if cross:
            links += f' · <a href="{html.escape(cross)}">{html.escape(route_label(cross))}</a> <strong>(NONCANON Crossscaling)</strong>'
        items.append(
            f'<li><strong>{html.escape(role)}</strong>: {links}<br><span>Characters: {chars}</span></li>'
        )
    return (
        f"{SOURCE_START}<section class=\"notice source-dependencies\" aria-label=\"Published pages using this evidence\">"
        "<h2>Published pages using this evidence</h2>"
        "<p>This reverse index shows where this preserved transmission is used. It does not alter the verbatim source above.</p>"
        f"<ul>{''.join(items)}</ul>"
        "<p><strong>Canon boundary:</strong> source-grounded Myths are canonical narrative surfaces; Crossscaling remains NONCANON analysis.</p>"
        f"</section>{SOURCE_END}"
    )


def patch_source_dependency_backlinks(relations: list[dict]) -> list[str]:
    uses: dict[str, list[tuple[dict, str]]] = defaultdict(list)
    for rec in relations:
        for route in rec.get("primary_sources", []):
            if route.startswith("/zubaida/"):
                uses[route].append((rec, "Primary evidence"))
        for route in rec.get("supporting_sources", []):
            if route.startswith("/zubaida/"):
                uses[route].append((rec, "Supporting / supersession evidence"))
    changed: list[str] = []
    for reader_route, records in sorted(uses.items()):
        path = route_path(reader_route)
        original = read(path)
        verbatim_before = extract_verbatim_source(original)
        if verbatim_before is None:
            raise RuntimeError(f"Source reader lacks preserved <pre class=source> payload: {reader_route}")
        block = source_dependency_block(reader_route, records)
        text = replace_or_insert(original, SOURCE_START, SOURCE_END, block, "</article>", str(path))
        verbatim_after = extract_verbatim_source(text)
        if verbatim_after != verbatim_before:
            raise RuntimeError(f"Refusing source-reader update because verbatim payload changed: {reader_route}")
        if text != original:
            write(path, text)
            changed.append(reader_route)
    return changed


def validate_publication_graph(custom_routes: list[dict]) -> None:
    seen = set()
    for route in custom_routes:
        if route["url"] in seen:
            raise RuntimeError(f"Duplicate publication URL: {route['url']}")
        seen.add(route["url"])
        source = ROOT / route["source"]
        if not source.exists():
            raise RuntimeError(f"Missing publication file for {route['url']}")
        text = read(source)
        if route["kind"] == "crossscaling" and "CROSSSCALE-ONLY" not in text.upper():
            raise RuntimeError(f"Crossscaling route lacks explicit CROSSSCALE-ONLY boundary: {route['url']}")


if __name__ == "__main__":
    publication_routes = discover_publication_routes()
    validate_publication_graph(publication_routes)
    relations = load_relations()
    validate_relation_manifest(relations, publication_routes)
    changed_publications = patch_publication_relation_blocks(relations)
    total = register_manifest(publication_routes)
    patch_crawl(total, publication_routes)
    changed_characters = patch_character_backlinks(publication_routes)
    changed_sources = patch_source_dependency_backlinks(relations)
    print(
        f"Publication graph registered: {len(publication_routes)} publication routes; "
        f"{len(relations)} typed relation records; {total} crawlable routes total; "
        f"{len(changed_publications)} publication pages updated; "
        f"{len(changed_characters)} character backlink pages updated; "
        f"{len(changed_sources)} source reader pages updated."
    )

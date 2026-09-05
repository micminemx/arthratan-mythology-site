#!/usr/bin/env python3
import collections
import hashlib
import html
import json
import os
import pathlib
import re
import shutil
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "ai"
SOURCE_COMMIT = os.environ.get("AI_SOURCE_COMMIT") or os.environ.get("GITHUB_SHA") or "unspecified-build-snapshot"
BASE_URL = "https://arthratanmythology.com"

BASE_EXPECTED = {
    "character": 43,
    "zubaida": 118,
    "divine": 317,
    "hgl": 293,
    "living-canon": 8,
    "concept": 27,
    "provenance": 4,
}
PUBLICATION_TYPES = ("myth", "crossscaling")

def load(name):
    with (DATA / name).open(encoding="utf-8") as f:
        return json.load(f)

def compact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def norm(value):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value or "")).replace("’", "'")).strip()

def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def route_url(route):
    if route.startswith("http://") or route.startswith("https://"):
        return route
    if not route.startswith("/"):
        route = "/" + route
    return BASE_URL + route

def html_text(raw):
    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?i)</(?:p|li|h[1-6]|section|article|div)>", "\n", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return norm(html.unescape(raw))

def html_title(raw, fallback):
    m = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", raw) or re.search(r"(?is)<title[^>]*>(.*?)</title>", raw)
    return html_text(m.group(1)) if m else fallback

def publication_pages(dirname):
    root = ROOT / dirname
    pages = []
    hub = root / "index.html"
    if hub.exists():
        pages.append((f"{dirname}-index", hub, f"/{dirname}/"))
    if root.exists():
        for p in sorted(root.glob("*/index.html")):
            pages.append((p.parent.name, p, f"/{dirname}/{p.parent.name}/"))
    return pages

records = []

def add(*, id, type, title, route, source_locator, full_text, aliases=None, entities_mentioned=None, concepts=None):
    text = str(full_text or "")
    digest = sha256_text(text)
    records.append({
        "id": id,
        "type": type,
        "title": norm(title),
        "canonical_route": route_url(route),
        "aliases": [norm(x) for x in (aliases or []) if norm(x)],
        "entities_mentioned": list(dict.fromkeys(norm(x) for x in (entities_mentioned or []) if norm(x))),
        "concepts": list(dict.fromkeys(norm(x) for x in (concepts or []) if norm(x))),
        "source_locator": source_locator,
        "full_text": text,
        "text_length": len(text),
        "word_count": len(re.findall(r"\S+", text)),
        "text_sha256": digest,
        "chunk_id": id + ":0",
        "chunk_offset": 0,
        "integrity": "sha256:" + digest,
    })

characters_doc = load("characters.json")
characters = characters_doc["characters"]
for c in characters:
    slug = c["slug"]
    add(
        id="character:" + slug,
        type="character",
        title=c["name"],
        route=f"/characters/{slug}/",
        source_locator="/data/characters.json#" + slug,
        aliases=(c.get("aliases") or []) + (c.get("titles") or []),
        entities_mentioned=c.get("related") or [],
        concepts=c.get("source_threads") or [],
        full_text=compact(c),
    )

z_index = load("zubaida-index.json")
srcdir = ROOT / "sources" / "zubaida"
existing = {p.stem for p in srcdir.glob("*.txt")}
source_ids = [x for x in z_index["ids"] if x in existing]
assert len(source_ids) == BASE_EXPECTED["zubaida"], f"Zubaida source count mismatch: {len(source_ids)}"
for pos, source_id in enumerate(source_ids, 1):
    raw = (srcdir / f"{source_id}.txt").read_text(encoding="utf-8", errors="strict")
    lines = [norm(x) for x in raw.splitlines() if norm(x)]
    heading = next((x for x in lines if re.match(r"(?i)^(session|transmission|imperial transmission|arthratan|the )", x)), lines[0] if lines else source_id)
    if heading.startswith("From:"):
        heading = next((x for x in lines if x.lower().startswith("session")), f"Zubaida transmission {pos}")
    add(id="zubaida:" + source_id, type="zubaida", title=heading[:240], route=f"/zubaida/{source_id}/", source_locator=f"/sources/zubaida/{source_id}.txt", full_text=raw)

divine_doc = load("divine.json")
divine_sections = divine_doc["sections"]
for s in divine_sections:
    add(id="divine:" + s["id"], type="divine", title=s["title"], route=f"/divine/{s['order'] + 1:03d}/", source_locator="/data/divine.json#" + s["id"], full_text=compact(s))

hgl_doc = load("hgl-pages.json")
for pg in hgl_doc["pages"]:
    page = int(pg["page"])
    static_path = ROOT / "hgl" / f"{page:03d}" / "index.html"
    route = f"/hgl/{page:03d}/" if static_path.exists() else "/hgl/"
    add(id=f"hgl:{page}", type="hgl", title=f"Hypergendered Logic — page {page}", route=route, source_locator=f"/data/hgl-pages.json#page-{page}", full_text=pg["text"])

new_canon_doc = load("new-canon.json")
for s in new_canon_doc.get("sections", []):
    sid = s["id"]
    route = {"negative-rewrite": "/#negative-rewrite", "arthitean-states": "/#arthiteans", "metagovernance": "/#scaling"}.get(sid, "/#scaling")
    add(id="living:" + sid, type="living-canon", title=s["title"], route=route, source_locator="/data/new-canon.json#" + sid, full_text=compact(s))

causal_doc = load("causal-ontology.json")
for c in causal_doc.get("concepts", []):
    cid = c["id"]
    add(id="concept:" + cid, type="concept", title=(c.get("title") or c.get("name") or cid.replace("-", " ").title()), route="/#negative-rewrite" if "rewrite" in cid else "/#scaling", source_locator="/data/causal-ontology.json#" + cid, full_text=compact(c))

hgl_glossary_doc = load("hgl-glossary.json")
for e in hgl_glossary_doc.get("entries", []):
    eid = e["id"]
    add(id="hgl-glossary:" + eid, type="concept", title=f"{e.get('term', '')} — {e.get('label', 'HGL glossary')}", route="/hgl/", source_locator="/data/hgl-glossary.json#" + eid, aliases=[e.get("term", "")], full_text=compact(e))

provenance = [
    ("sources:zubaida", "Zubaida source archive", "/zubaida/", "/data/zubaida-index.json", z_index),
    ("sources:divine", "Divine v144 source archive", "/divine/", "/data/divine.json", {k: v for k, v in divine_doc.items() if k != "sections"}),
    ("sources:hgl", "Hypergendered Logic source archive", "/hgl/", "/data/hgl-pages.json", {k: v for k, v in hgl_doc.items() if k != "pages"}),
    ("sources:characters", "Character encyclopedia", "/characters/", "/data/characters.json", {k: v for k, v in characters_doc.items() if k != "characters"}),
]
for rid, title, route, locator, payload in provenance:
    add(id=rid, type="provenance", title=title, route=route, source_locator=locator, full_text=compact(payload))

# Canonical narrative Myths and explicitly noncanon analytical Crossscaling are
# additive retrieval layers. They are discovered from the current filesystem so the
# corpus expands safely as agents publish new pages without changing hardcoded counts.
publication_counts = {}
for dirname, typ, status in [
    ("myths", "myth", "CANON STATUS: canonical narrative realization. Primary evidence remains authoritative."),
    ("crossscaling", "crossscaling", "CANON STATUS: CROSSSCALE-ONLY / NONCANON analytical interpretation. External benchmarks/totalizers are not Arthratan canon."),
]:
    pages = publication_pages(dirname)
    publication_counts[typ] = len(pages)
    for key, page, route in pages:
        raw = page.read_text(encoding="utf-8", errors="replace")
        body = html_text(raw)
        add(
            id=f"{typ}:{key}",
            type=typ,
            title=html_title(raw, key.replace("-", " ").title()),
            route=route,
            source_locator="/" + page.relative_to(ROOT).as_posix(),
            full_text=status + "\n" + body,
        )

counts = collections.Counter(r["type"] for r in records)
base_counts = collections.Counter({k: counts[k] for k in BASE_EXPECTED})
assert base_counts == collections.Counter(BASE_EXPECTED), f"AI base corpus type counts mismatch: {dict(base_counts)}"
for typ in PUBLICATION_TYPES:
    assert counts[typ] == publication_counts[typ], (typ, counts[typ], publication_counts[typ])
expected_counts = dict(BASE_EXPECTED)
expected_counts.update(publication_counts)
assert len(records) == sum(expected_counts.values()), (len(records), expected_counts)
assert len({r["id"] for r in records}) == len(records), "Duplicate record IDs"
for r in records:
    assert r["text_length"] == len(r["full_text"])
    assert r["text_sha256"] == sha256_text(r["full_text"])
assert all("NONCANON" in r["full_text"] for r in records if r["type"] == "crossscaling")

order = {"character": 0, "zubaida": 1, "divine": 2, "hgl": 3, "living-canon": 4, "myth": 5, "concept": 6, "provenance": 7, "crossscaling": 8}
records.sort(key=lambda r: (order[r["type"]], r["id"]))

if OUT.exists():
    shutil.rmtree(OUT, ignore_errors=True)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "shards").mkdir(exist_ok=True)
(OUT / "entities").mkdir(exist_ok=True)

def write_json(path, obj, pretty=False):
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2 if pretty else None, separators=None if pretty else (",", ":")) + "\n"
    path.write_text(text, encoding="utf-8")
    return {"bytes": len(text.encode("utf-8")), "sha256": sha256_text(text)}

def write_jsonl(path, rows):
    text = "".join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for r in rows)
    path.write_text(text, encoding="utf-8")
    return {"bytes": len(text.encode("utf-8")), "sha256": sha256_text(text)}

corpus_meta = write_jsonl(OUT / "corpus.jsonl", records)
shards = []
for typ in order:
    rows = [r for r in records if r["type"] == typ]
    if not rows:
        continue
    filename = typ.replace("-", "_") + ".jsonl"
    meta = write_jsonl(OUT / "shards" / filename, rows)
    shards.append({"type": typ, "path": f"/ai/shards/{filename}", "records": len(rows), **meta})

honorifics = {"lady", "lord", "commander", "high", "empress", "emperor", "supreme", "general", "prince", "princess"}
entity_manifest = []
for c in characters:
    terms = [c.get("name", "")] + list(c.get("aliases") or [])
    first = norm(c.get("name", "")).split(" ")[0] if norm(c.get("name", "")) else ""
    if len(first) >= 5 and first.lower() not in honorifics:
        terms.append(first)
    terms = list(dict.fromkeys(norm(t) for t in terms if norm(t)))
    patterns = [re.compile(r"(?<!\w)" + re.escape(t) + r"(?!\w)", re.I) for t in terms]
    evidence = []
    for r in records:
        hay = r["title"] + "\n" + r["full_text"]
        if any(p.search(hay) for p in patterns):
            evidence.append({"id": r["id"], "type": r["type"], "title": r["title"], "canonical_route": r["canonical_route"], "source_locator": r["source_locator"], "text_sha256": r["text_sha256"], "full_text": r["full_text"]})
    slug = c["slug"]
    dossier = {"entity": {"slug": slug, "name": c["name"], "aliases": terms}, "generated_from_commit": SOURCE_COMMIT, "records": len(evidence), "counts": dict(sorted(collections.Counter(x["type"] for x in evidence).items())), "evidence": evidence}
    meta = write_json(OUT / "entities" / f"{slug}.json", dossier)
    entity_manifest.append({"slug": slug, "name": c["name"], "path": f"/ai/entities/{slug}.json", "records": len(evidence), **meta})

dyvane = next((x for x in entity_manifest if x["slug"] == "dyvane-redalious"), None)
assert dyvane is not None, "Dyvane character record missing"
dyvane_doc = json.loads((OUT / "entities" / "dyvane-redalious.json").read_text(encoding="utf-8"))
assert dyvane_doc["counts"].get("zubaida", 0) > 0, "Dyvane dossier lacks Zubaida story evidence"
assert dyvane_doc["counts"].get("myth", 0) > 0, "Dyvane dossier lacks published Myth evidence"
assert dyvane_doc["counts"].get("crossscaling", 0) > 0, "Dyvane dossier lacks Crossscaling evidence"

manifest = {
    "version": 2,
    "task": "AI-LIVE-001",
    "generated_from_commit": SOURCE_COMMIT,
    "base_url": BASE_URL,
    "record_count": len(records),
    "counts": dict(sorted(counts.items())),
    "corpus": {"path": "/ai/corpus.jsonl", **corpus_meta},
    "shards": shards,
    "entities": entity_manifest,
    "record_schema": ["id", "type", "title", "canonical_route", "aliases", "entities_mentioned", "concepts", "source_locator", "full_text", "text_length", "word_count", "text_sha256", "chunk_id", "chunk_offset", "integrity"],
    "source_rule": "Machine retrieval is additive. Primary/preserved source canon remains authoritative and separately retrievable. Myths are canonical narrative realizations. Crossscaling records are explicitly CROSSSCALE-ONLY / NONCANON analytical surfaces and must never be mistaken for native Arthratan objects or feats.",
    "access": "Public read-only HTTP; JavaScript and API keys are not required.",
    "validation": {"expected_counts": expected_counts, "base_expected_counts": BASE_EXPECTED, "publication_counts_dynamic": publication_counts, "unique_ids": True, "record_hashes_verified": True, "crossscaling_noncanon_boundary_verified": True, "dyvane_story_evidence_records": dyvane_doc["records"], "dyvane_story_evidence_counts": dyvane_doc["counts"]},
}
write_json(OUT / "index.json", manifest, pretty=True)

index_lines = [
    "Arthratan Mythology — AI-native complete-text retrieval index",
    f"Generated from GitHub commit: {SOURCE_COMMIT}",
    f"Records: {len(records)}",
    "",
    f"Manifest: {BASE_URL}/ai/index.json",
    f"Complete corpus (NDJSON): {BASE_URL}/ai/corpus.jsonl",
    f"Dyvane evidence dossier: {BASE_URL}/ai/entities/dyvane-redalious.json",
    "",
    "Source / publication families:",
]
for typ in order:
    if counts[typ]:
        index_lines.append(f"- {typ}: {counts[typ]} records")
index_lines += [
    "",
    "Retrieval guidance:",
    "- No JavaScript or API key is required for this public read-only corpus.",
    "- Search full_text and aliases, then cite canonical_route and source_locator.",
    "- Treat Myth as canonical narrative realization and follow its primary-evidence links for feat proof.",
    "- Treat every crossscaling record as CROSSSCALE-ONLY / NONCANON analytical interpretation.",
    "- For configured structured access, use the separately documented Arthratan Canon API.",
]
(OUT / "index.txt").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

readme = f"""# Arthratan AI Retrieval Surface\n\nThis directory is generated by `scripts/build-ai-corpus.py` for **AI-LIVE-001**.\n\n- `index.json` — deterministic manifest, counts, hashes and schema.\n- `corpus.jsonl` — {len(records)} complete-text records.\n- `shards/` — source/publication-type NDJSON shards, including canonical Myths and explicitly noncanon Crossscaling.\n- `entities/` — precomputed entity evidence dossiers; use `dyvane-redalious.json` as the acceptance canary for Character → Myth → Crossscaling → primary-evidence retrieval.\n- `index.txt` — plain-text discovery entry point.\n\nThe surface is public, read-only and requires neither JavaScript nor a secret key. Primary source canon is not replaced: each record exposes its canonical route and source locator. Myth records are canonical narrative realizations; Crossscaling records are analytical and explicitly NONCANON.\n"""
(OUT / "README.md").write_text(readme, encoding="utf-8")

print(json.dumps({"records": len(records), "counts": dict(counts), "corpus": corpus_meta, "dyvane": dyvane_doc["counts"]}, indent=2))

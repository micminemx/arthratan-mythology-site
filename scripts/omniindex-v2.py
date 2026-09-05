#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OmniIndex V2: exact multi-edge semantic navigability audit.

This is a corrective companion to the first OmniIndex implementation. It keeps
multiple semantic classifications for the same source->target pair instead of
letting a DiGraph edge attribute overwrite earlier hyperlink instances, validates
exact SPA targets rather than accepting route prefixes, and separates execution
success from website-quality verdicts.

Standard-library only so it can run as a publication gate.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ORIGIN = "https://arthratanmythology.com"
EXCLUDED_DIRS = {".git", "reports", "node_modules", ".gemini", "_layouts", "test"}
SIMPLE_SPA_ROUTES = {
    "", "home", "atlas", "masterpages", "scaling", "negative-rewrite",
    "arthiteans", "rhayhara", "hgl", "divine", "hgl-archive", "stories",
    "search", "sources", "characters", "index", "glossary", "ontology",
    "causal-ontology", "causality",
}
CATEGORY_HUBS = {
    "characters/index.html", "concepts/index.html", "masterpages/index.html",
    "myths/index.html", "crossscaling/index.html", "divine/index.html",
    "hgl/index.html", "zubaida/index.html", "clans/index.html",
    "crawl/index.html", "search/index.html", "provenance/index.html",
    "chronology/index.html",
}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


@dataclass
class Anchor:
    href: str
    text: str
    tokens: set[str]
    in_content: bool


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, dict[str, str]]] = []
        self.ids: set[str] = set()
        self.anchors: list[Anchor] = []
        self._anchor: dict | None = None

    @staticmethod
    def attrs_dict(attrs) -> dict[str, str]:
        return {str(k).lower(): str(v or "") for k, v in attrs}

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        ad = self.attrs_dict(attrs)
        if ad.get("id"):
            self.ids.add(ad["id"])
        if tag == "a" and ad.get("href") is not None:
            tokens: set[str] = set()
            in_content = False
            for atag, aattrs in self.stack + [(tag, ad)]:
                tokens.add(atag)
                if atag in {"main", "article", "section"}:
                    in_content = True
                if aattrs.get("id"):
                    tokens.add(aattrs["id"].lower())
                for cls in aattrs.get("class", "").split():
                    tokens.add(cls.lower())
                if aattrs.get("aria-label"):
                    tokens.add(aattrs["aria-label"].lower())
                if aattrs.get("role"):
                    tokens.add(aattrs["role"].lower())
            self._anchor = {"href": ad.get("href", ""), "text": [], "tokens": tokens, "in_content": in_content}
        if tag not in VOID_TAGS:
            self.stack.append((tag, ad))

    def handle_startendtag(self, tag, attrs):
        ad = self.attrs_dict(attrs)
        if ad.get("id"):
            self.ids.add(ad["id"])

    def handle_data(self, data):
        if self._anchor is not None:
            self._anchor["text"].append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "a" and self._anchor is not None:
            self.anchors.append(Anchor(
                href=self._anchor["href"],
                text=re.sub(r"\s+", " ", "".join(self._anchor["text"])).strip(),
                tokens=set(self._anchor["tokens"]),
                in_content=bool(self._anchor["in_content"]),
            ))
            self._anchor = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def b36(value: str) -> int:
    try:
        return int(str(value), 36)
    except Exception:
        return 0


def production_html(root: Path) -> list[Path]:
    out = []
    for path in root.rglob("*.html"):
        rel = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        out.append(path)
    return sorted(out)


def rel_to_route(rel: str) -> str:
    rel = rel.replace("\\", "/")
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[:-10]
    return "/" + rel


def route_to_rel(path: str) -> str:
    path = unquote(path or "/")
    if not path.startswith("/"):
        path = "/" + path
    if path == "/":
        return "index.html"
    rel = path.lstrip("/")
    if rel.endswith("/"):
        return rel + "index.html"
    return rel


def load_json(root: Path, rel: str, default=None):
    p = root / rel
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def spa_registry(root: Path) -> dict:
    chars = load_json(root, "data/characters.json", {}).get("characters", [])
    char_targets = set()
    for c in chars:
        if c.get("slug"):
            char_targets.add(c["slug"])
        for alias in c.get("aliases", []) or []:
            char_targets.add(slug(alias))

    mps = load_json(root, "data/masterpages.json", {}).get("masterpages", [])
    masterpages = {m.get("id") for m in mps if m.get("id")}

    divine = load_json(root, "data/divine.json", {}).get("sections", [])
    divine_ids = {s.get("id") for s in divine if s.get("id")}

    hgl_toc = load_json(root, "data/hgl-toc.json", {}) or {}
    hgl_parts = {p.get("id") for p in hgl_toc.get("parts", []) if p.get("id")}
    hgl_pages_data = load_json(root, "data/hgl-pages.json", {}) or {}
    hgl_rows = hgl_pages_data if isinstance(hgl_pages_data, list) else hgl_pages_data.get("pages", [])
    hgl_pages = {str(p.get("page")) for p in hgl_rows if p.get("page") is not None}

    zidx = load_json(root, "data/zubaida-index.json", {}) or {}
    transmission_ids = set(zidx.get("ids", []))
    nonsource = load_json(root, "data/zubaida-nonsource.json", {}) or {}
    for row in nonsource.get("non_source_records", []) or nonsource.get("ids", []):
        if isinstance(row, str):
            transmission_ids.add(row)
        elif isinstance(row, dict) and row.get("id"):
            transmission_ids.add(row["id"])

    sessions = load_json(root, "data/zubaida-sessions.json", {}) or {}
    session_targets = set()
    unit_targets = set()
    for row in str(sessions.get("s", "")).splitlines():
        parts = row.split("\t")
        if len(parts) >= 2:
            session_targets.add(f"zs-{parts[0]}-{parts[1]}")
    for row in str(sessions.get("u", "")).splitlines():
        parts = row.split("\t")
        if len(parts) >= 2:
            unit_targets.add(f"zu-{parts[0]}-{parts[1]}")

    site_index = load_json(root, "data/site-index.json", {}) or {}
    index_letters = {str(x).upper() for x in site_index.get("a_to_z", {}).keys()}

    return {
        "characters": char_targets,
        "masterpages": masterpages,
        "divine": divine_ids,
        "hgl_parts": hgl_parts,
        "hgl_pages": hgl_pages,
        "transmissions": transmission_ids,
        "sessions": session_targets,
        "units": unit_targets,
        "index_letters": index_letters,
    }


def validate_dynamic_fragment(fragment: str, reg: dict) -> tuple[bool, str]:
    h = unquote(fragment or "").strip()
    if h in SIMPLE_SPA_ROUTES:
        return True, "simple"
    if h.startswith("character:"):
        target = h.split(":", 1)[1]
        return (target in reg["characters"], "character")
    if h.startswith("masterpage:"):
        target = h.split(":", 1)[1]
        return (target in reg["masterpages"], "masterpage")
    if h.startswith("divine-section:"):
        target = h.split(":", 1)[1]
        return (target in reg["divine"], "divine-section")
    if h.startswith("hgl-part:"):
        target = h.split(":", 1)[1]
        return (target in reg["hgl_parts"], "hgl-part")
    if h.startswith("hgl-page-direct:"):
        target = h.split(":", 1)[1]
        return (target in reg["hgl_pages"], "hgl-page-direct")
    if h.startswith("transmission:"):
        target = h.split(":", 1)[1]
        return (target in reg["transmissions"], "transmission")
    if h.startswith("session:"):
        target = h.split(":", 1)[1]
        return (target in reg["sessions"], "session")
    if h.startswith("unit:"):
        target = h.split(":", 1)[1]
        return (target in reg["units"], "unit")
    if h.startswith("index:"):
        target = h.split(":", 1)[1].upper()
        return (target in reg["index_letters"], "index")
    return False, "unimplemented"


def parse_pages(root: Path):
    pages: dict[str, PageParser] = {}
    for path in production_html(root):
        rel = str(path.relative_to(root)).replace("\\", "/")
        parser = PageParser()
        try:
            parser.feed(path.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:
            raise RuntimeError(f"HTML parse failure {rel}: {exc}") from exc
        pages[rel] = parser
    return pages


def resolve_href(root: Path, src_rel: str, href: str):
    href = (href or "").strip()
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "data:")):
        return None
    base = ORIGIN + rel_to_route(src_rel)
    url = urljoin(base, href)
    p = urlsplit(url)
    if p.scheme not in {"http", "https"}:
        return None
    if p.netloc.lower() != urlsplit(ORIGIN).netloc.lower():
        return {"external": True, "url": url}
    rel = route_to_rel(p.path)
    return {"external": False, "rel": rel, "fragment": p.fragment, "url": url}


def classify_edge(src: str, tgt: str, anchor: Anchor) -> set[str]:
    types: set[str] = set()
    tokens = {t.lower() for t in anchor.tokens}
    text = anchor.text.lower()
    if src == "crawl/index.html" or tgt == "crawl/index.html":
        types.add("crawl-directory")
    if src == "search/index.html" or tgt == "search/index.html":
        types.add("search")
    if "footer" in tokens:
        types.add("global-footer")
    if any("breadcrumb" in t or "crumb" == t or t == "myth-crumbs" for t in tokens):
        types.add("breadcrumb")
    elif "nav" in tokens and any(t in tokens for t in {"top-nav", "top", "myth-top", "sidebar", "nav"}):
        types.add("global-header")
    if any(t in tokens for t in {"publication-backlinks", "publication-relations", "source-dependencies", "related-content", "relationships", "relationship"}):
        types.add("relationship")
    if tgt.startswith("zubaida/") or tgt.startswith("sources/zubaida/") or "source-dependencies" in tokens:
        types.add("evidence")
    if "prev" in text or "previous" in text or "next" in text or any("prev" in t or "next" in t for t in tokens):
        types.add("previous-next")
    if src in CATEGORY_HUBS and "crawl-directory" not in types and "search" not in types:
        types.add("category-index")
    if anchor.in_content and not ({"global-header", "global-footer", "breadcrumb"} & types):
        types.add("body-context")
    if not types:
        types.add("other")
    return types


def build_graph(root: Path, pages: dict[str, PageParser], reg: dict):
    edge_types: dict[tuple[str, str], set[str]] = defaultdict(set)
    edge_instances = Counter()
    invalid_dynamic = []
    broken_internal = []
    broken_fragments = []
    internal_resources = []
    nodes = set(pages)

    for src, parser in pages.items():
        for anchor in parser.anchors:
            resolved = resolve_href(root, src, anchor.href)
            if not resolved or resolved.get("external"):
                continue
            tgt = resolved["rel"]
            fragment = resolved.get("fragment", "")
            target_path = root / tgt
            if tgt not in nodes:
                if target_path.exists():
                    internal_resources.append({"source": src, "target": tgt, "href": anchor.href})
                    continue
                broken_internal.append({"source": src, "target": tgt, "href": anchor.href, "text": anchor.text})
                continue

            if fragment:
                target_parser = pages[tgt]
                if fragment not in target_parser.ids:
                    if tgt == "index.html":
                        valid, family = validate_dynamic_fragment(fragment, reg)
                        if not valid:
                            invalid_dynamic.append({"source": src, "href": anchor.href, "fragment": fragment, "family": family, "text": anchor.text})
                            continue
                    else:
                        broken_fragments.append({"source": src, "target": tgt, "href": anchor.href, "fragment": fragment, "text": anchor.text})
                        continue

            types = classify_edge(src, tgt, anchor)
            edge_types[(src, tgt)].update(types)
            for t in types:
                edge_instances[t] += 1

    return edge_types, edge_instances, invalid_dynamic, broken_internal, broken_fragments, internal_resources


def adjacency(nodes: set[str], edge_types: dict[tuple[str, str], set[str]], allowed=None, denied=None):
    out = {n: set() for n in nodes}
    allowed = set(allowed or [])
    denied = set(denied or [])
    for (src, tgt), types in edge_types.items():
        if denied and types & denied:
            continue
        if allowed and not (types & allowed):
            continue
        out[src].add(tgt)
    return out


def bfs(adj: dict[str, set[str]], src: str) -> dict[str, int]:
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj.get(u, ()):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def percentile(sorted_values: list[int], q: float):
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    pos = (len(sorted_values) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return float(sorted_values[lo])
    return sorted_values[lo] * (hi - pos) + sorted_values[hi] * (pos - lo)


def distribution(values: list[int], total_possible: int | None = None):
    vals = list(values)
    reach = len(vals)
    if not vals:
        return {
            "count": 0, "reachable": 0, "unreachable": total_possible or 0,
            "reachability": 0.0 if total_possible else None,
            "min": None, "max": None, "range": None, "mean": None,
            "median": None, "modes": [], "variance": None, "sd": None,
            "skewness": None, "pearson_kurtosis": None, "excess_kurtosis": None,
            "p50": None, "p75": None, "p90": None, "p95": None, "p99": None,
        }
    s = sorted(vals)
    n = len(vals)
    mean = sum(vals) / n
    var = sum((x - mean) ** 2 for x in vals) / n
    sd = math.sqrt(var)
    if sd == 0:
        skew = 0.0
        pearson = 3.0
        excess = 0.0
    else:
        m3 = sum((x - mean) ** 3 for x in vals) / n
        m4 = sum((x - mean) ** 4 for x in vals) / n
        skew = m3 / (sd ** 3)
        pearson = m4 / (var ** 2)
        excess = pearson - 3.0
    counts = Counter(vals)
    max_count = max(counts.values())
    modes = sorted(k for k, v in counts.items() if v == max_count)
    total = total_possible if total_possible is not None else n
    return {
        "count": n,
        "reachable": reach,
        "unreachable": max(0, total - reach),
        "reachability": reach / total if total else 1.0,
        "min": min(vals), "max": max(vals), "range": max(vals) - min(vals),
        "mean": mean, "median": statistics.median(vals), "modes": modes,
        "variance": var, "sd": sd, "skewness": skew,
        "pearson_kurtosis": pearson, "excess_kurtosis": excess,
        "p50": percentile(s, 0.50), "p75": percentile(s, 0.75),
        "p90": percentile(s, 0.90), "p95": percentile(s, 0.95),
        "p99": percentile(s, 0.99),
    }


def all_pairs_profile(adj: dict[str, set[str]]):
    nodes = sorted(adj)
    total_pairs = len(nodes) * (len(nodes) - 1)
    all_values: list[int] = []
    dists: dict[str, dict[str, int]] = {}
    incoming: dict[str, list[int]] = {n: [] for n in nodes}
    outgoing: dict[str, list[int]] = {n: [] for n in nodes}
    for src in nodes:
        dist = bfs(adj, src)
        dists[src] = dist
        for tgt, value in dist.items():
            if tgt == src:
                continue
            outgoing[src].append(value)
            incoming[tgt].append(value)
            all_values.append(value)
    page_stats = {}
    denom = len(nodes) - 1
    for n in nodes:
        page_stats[n] = {
            "outgoing": distribution(outgoing[n], denom),
            "incoming": distribution(incoming[n], denom),
        }
    return distribution(all_values, total_pairs), page_stats, dists


def assign_heat(page_stats: dict[str, dict]) -> None:
    for direction in ["outgoing", "incoming"]:
        ranked = sorted(
            page_stats,
            key=lambda n: (
                -float(page_stats[n][direction].get("reachability") or 0),
                float(page_stats[n][direction].get("mean") if page_stats[n][direction].get("mean") is not None else 10**9),
                float(page_stats[n][direction].get("p95") if page_stats[n][direction].get("p95") is not None else 10**9),
                float(page_stats[n][direction].get("max") if page_stats[n][direction].get("max") is not None else 10**9),
            ),
        )
        size = max(1, len(ranked))
        for idx, node in enumerate(ranked):
            r = page_stats[node][direction].get("reachability") or 0.0
            if r == 0:
                heat = "ISOLATED"
            else:
                pct = idx / size
                heat = (
                    "VERY HOT" if pct < 0.05 else
                    "HOT" if pct < 0.20 else
                    "WARM" if pct < 0.40 else
                    "NEUTRAL" if pct < 0.60 else
                    "COOL" if pct < 0.80 else
                    "COLD" if pct < 0.95 else
                    "VERY COLD"
                )
            page_stats[node][direction]["heat"] = heat


def graph_layers(nodes: set[str], edge_types):
    return {
        "G_all": adjacency(nodes, edge_types),
        "G_human": adjacency(nodes, edge_types, denied={"crawl-directory"}),
        "G_contextual": adjacency(nodes, edge_types, allowed={"body-context", "relationship", "evidence"}),
        "G_relationship": adjacency(nodes, edge_types, allowed={"relationship", "evidence"}),
        "G_evidence": adjacency(nodes, edge_types, allowed={"evidence"}),
        "G_masked": adjacency(nodes, edge_types, denied={"global-header", "global-footer", "crawl-directory", "search"}),
    }


def route_file_rel(route: str) -> str:
    return route_to_rel(urlsplit(route).path)


def relation_gate(root: Path, edge_types: dict[tuple[str, str], set[str]], contextual_dists: dict[str, dict[str, int]]):
    data = load_json(root, "data/publication-relations.json", {}) or {}
    records = data.get("records", [])
    failures = []
    checks = 0

    def direct(a, b, label):
        nonlocal checks
        checks += 1
        if (a, b) not in edge_types:
            failures.append({"type": "missing_direct_edge", "label": label, "source": a, "target": b})

    def distance_le(a, b, limit, label):
        nonlocal checks
        checks += 1
        d = contextual_dists.get(a, {}).get(b)
        if d is None or d > limit:
            failures.append({"type": "distance_gate", "label": label, "source": a, "target": b, "distance": d, "limit": limit})

    for rec in records:
        myth = route_file_rel(rec["myth"])
        cross = route_file_rel(rec["crossscaling"]) if rec.get("crossscaling") else None
        chars = [route_file_rel(x) for x in rec.get("characters", [])]
        readers = [route_file_rel(x) for x in rec.get("primary_sources", []) if x.startswith("/zubaida/")]
        supporting = [route_file_rel(x) for x in rec.get("supporting_sources", []) if x.startswith("/zubaida/")]
        for c in chars:
            direct(myth, c, "Myth->Character")
            direct(c, myth, "Character->Myth")
            if cross:
                direct(cross, c, "Crossscale->Character")
                direct(c, cross, "Character->Crossscale")
        if cross:
            direct(myth, cross, "Myth->Crossscale")
            direct(cross, myth, "Crossscale->Myth")
        for reader in readers + supporting:
            direct(myth, reader, "Myth->Evidence")
            direct(reader, myth, "Evidence->Myth")
            if cross:
                direct(cross, reader, "Crossscale->Evidence")
                direct(reader, cross, "Evidence->Crossscale")
            for c in chars:
                direct(reader, c, "Evidence->Character")
                distance_le(c, reader, 2, "Character->Evidence contextual path")
    return {"records": len(records), "checks": checks, "failures": failures, "passed": not failures}


def category_matrix(nodes: set[str], dists: dict[str, dict[str, int]]):
    cats: dict[str, list[str]] = defaultdict(list)
    for n in nodes:
        cat = n.split("/", 1)[0] if "/" in n else "root"
        cats[cat].append(n)
    out = {}
    for a, sources in sorted(cats.items()):
        out[a] = {}
        for b, targets in sorted(cats.items()):
            vals = []
            total = 0
            for s in sources:
                for t in targets:
                    if s == t:
                        continue
                    total += 1
                    d = dists.get(s, {}).get(t)
                    if d is not None:
                        vals.append(d)
            out[a][b] = distribution(vals, total) if total else distribution([], 0)
    return out


def write_report(out_dir: Path, summary: dict, layer_stats: dict, edge_instances: Counter, relation: dict):
    lines = [
        "# OmniIndex V2 — Exact Multi-Edge Semantic Navigation Audit",
        "",
        f"**Production HTML nodes:** {summary['nodes']}",
        f"**Unique directed page edges:** {summary['unique_edges']}",
        f"**Invalid exact SPA targets:** {summary['invalid_dynamic_count']}",
        f"**Broken internal links:** {summary['broken_internal_count']}",
        f"**Broken static fragments:** {summary['broken_fragment_count']}",
        f"**Typed publication/evidence relation gate:** {'PASS' if relation['passed'] else 'FAIL'} ({relation['checks']} checks)",
        "",
        "## Graph layers",
        "",
        "| Layer | Pair reachability | Mean reachable distance | P95 | Max | Quality interpretation |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for name, data in layer_stats.items():
        s = data["site"]
        if name == "G_all":
            interp = "hard gate: must be fully reachable"
        elif name == "G_human":
            interp = "human navigation excluding crawl shortcuts"
        elif name == "G_contextual":
            interp = "contextual/relationship/evidence links; connectivity is diagnostic, not a universal all-pairs target"
        elif name == "G_evidence":
            interp = "evidence links only; evaluate relevant evidence scope, not whole-site all-pairs connectivity"
        elif name == "G_masked":
            interp = "stress test with global header/footer, crawl and search removed"
        else:
            interp = "typed relationship layer"
        lines.append(
            f"| {name} | {100*(s.get('reachability') or 0):.3f}% | "
            f"{(s.get('mean') if s.get('mean') is not None else float('nan')):.4f} | "
            f"{s.get('p95')} | {s.get('max')} | {interp} |"
        )
    lines += ["", "## Edge instance classifications (multi-label)", "", "These counts are intentionally multi-label: one hyperlink may be both `relationship` and `evidence`. Percentages must therefore not be expected to sum to 100%.", ""]
    for key, value in edge_instances.most_common():
        lines.append(f"- **{key}:** {value}")
    lines += ["", "## Quality gate", "", f"**Overall gate:** {summary['quality_verdict']}"]
    for item in summary["quality_reasons"]:
        lines.append(f"- {item}")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "OMNIINDEX_V2_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--out-dir", default="reports/architecture/omniindex-v2")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()

    pages = parse_pages(root)
    reg = spa_registry(root)
    edge_types, edge_instances, invalid_dynamic, broken_internal, broken_fragments, internal_resources = build_graph(root, pages, reg)
    nodes = set(pages)
    layers = graph_layers(nodes, edge_types)

    layer_stats = {}
    layer_dists = {}
    for name, adj in layers.items():
        site, page_stats, dists = all_pairs_profile(adj)
        assign_heat(page_stats)
        layer_stats[name] = {"site": site, "pages": page_stats}
        layer_dists[name] = dists

    relation = relation_gate(root, edge_types, layer_dists["G_contextual"])
    categories = category_matrix(nodes, layer_dists["G_all"])
    masked_categories = category_matrix(nodes, layer_dists["G_masked"])

    reasons = []
    quality_ok = True
    if invalid_dynamic:
        quality_ok = False
        reasons.append(f"FAIL: {len(invalid_dynamic)} exact SPA targets do not resolve to implemented records/routes.")
    else:
        reasons.append("PASS: all detected dynamic SPA deep links resolve to exact implemented targets.")
    if broken_internal:
        quality_ok = False
        reasons.append(f"FAIL: {len(broken_internal)} broken internal links.")
    else:
        reasons.append("PASS: no broken internal page/resource links detected.")
    if broken_fragments:
        quality_ok = False
        reasons.append(f"FAIL: {len(broken_fragments)} broken static fragments.")
    else:
        reasons.append("PASS: no broken static fragments detected.")
    all_reach = layer_stats["G_all"]["site"].get("reachability") or 0
    if abs(all_reach - 1.0) > 1e-12:
        quality_ok = False
        reasons.append(f"FAIL: G_all pair reachability is {all_reach:.6f}, expected 1.0.")
    else:
        reasons.append("PASS: G_all has 100% ordered-pair reachability.")
    human_reach = layer_stats["G_human"]["site"].get("reachability") or 0
    if human_reach < 0.99:
        quality_ok = False
        reasons.append(f"FAIL: G_human pair reachability {human_reach:.6f} is below 0.99.")
    else:
        reasons.append(f"PASS: G_human pair reachability is {human_reach:.6f}.")
    if not relation["passed"]:
        quality_ok = False
        reasons.append(f"FAIL: {len(relation['failures'])} typed publication/evidence relation checks failed.")
    else:
        reasons.append(f"PASS: all {relation['checks']} typed publication/evidence relationship checks passed.")

    summary = {
        "schema": "omniindex-v2",
        "execution_status": "PASS",
        "quality_verdict": "PASS" if quality_ok else "FAIL",
        "quality_reasons": reasons,
        "nodes": len(nodes),
        "unique_edges": len(edge_types),
        "edge_instance_labels": dict(edge_instances),
        "invalid_dynamic_count": len(invalid_dynamic),
        "broken_internal_count": len(broken_internal),
        "broken_fragment_count": len(broken_fragments),
        "internal_nonpage_resource_links": len(internal_resources),
        "layers": {k: v["site"] for k, v in layer_stats.items()},
        "relation_gate": relation,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "invalid_dynamic_targets.json").write_text(json.dumps(invalid_dynamic, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "broken_internal_links.json").write_text(json.dumps(broken_internal, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "broken_static_fragments.json").write_text(json.dumps(broken_fragments, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "edge_types.json").write_text(json.dumps({f"{a} -> {b}": sorted(t) for (a,b),t in sorted(edge_types.items())}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "page_heat.json").write_text(json.dumps({k: v["pages"] for k,v in layer_stats.items()}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "category_matrix_all.json").write_text(json.dumps(categories, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "category_matrix_masked.json").write_text(json.dumps(masked_categories, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "relation_gate.json").write_text(json.dumps(relation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(out_dir, summary, layer_stats, edge_instances, relation)

    print(json.dumps({
        "execution_status": summary["execution_status"],
        "quality_verdict": summary["quality_verdict"],
        "nodes": summary["nodes"],
        "unique_edges": summary["unique_edges"],
        "invalid_dynamic": len(invalid_dynamic),
        "broken_internal": len(broken_internal),
        "broken_fragments": len(broken_fragments),
        "G_all_reachability": all_reach,
        "G_human_reachability": human_reach,
        "G_contextual_reachability": layer_stats["G_contextual"]["site"].get("reachability"),
        "G_evidence_reachability": layer_stats["G_evidence"]["site"].get("reachability"),
        "G_masked_reachability": layer_stats["G_masked"]["site"].get("reachability"),
        "relation_checks": relation["checks"],
        "relation_failures": len(relation["failures"]),
    }, indent=2))
    raise SystemExit(0 if quality_ok else 1)


if __name__ == "__main__":
    main()

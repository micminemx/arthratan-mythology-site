# Arthratan Mythology Website — Professional Information-Architecture / Findability Audit

**Task:** IA-001  
**Worker:** W-20260902-1908-R7Q2  
**Audit date:** 2026-09-02 BST  
**Repository:** `micminemx/arthratan-mythology-site` (`main`)  
**Reference snapshot:** observed `main` head `f5018e6b4c65bcbbb2e731eb35fcdba446c61932` during the audit; parallel workers may advance `main` afterward.  
**Scope law:** audit/recommendation only. No frontend, source-canon, or worker-owned data files are modified by IA-001.

---

## 1. Executive diagnosis

The site has substantial preserved source data and several strong reader subsystems, but its **information architecture is currently narrower than its repository content architecture**.

The main failure pattern is **content–navigation splitbrain**:

1. `index.html` exposes a small static sidebar and loads only `app.js`.
2. `app.js` owns a second, hard-coded route list.
3. `archive.js` implements the Story & Thread Archive (`#stories`, `#transmission:<id>`) independently, but the current entrypoint does not load it or link to it.
4. `source-provenance.js` implements exact-source enhancements independently, but the current entrypoint does not load it.
5. Repository datasets such as `data/characters.json` and `data/causal-ontology.json` have no equivalent current top-level route in the core router.
6. Search covers Divine v144, HGL pages and `new-canon.json`, but not the full Zubaida corpus, character encyclopedia data, causal-ontology data, or additive explanation/crossreference datasets.
7. Unknown hashes silently fall back to Sanctuary, which masks broken/deprecated deep links instead of distinguishing them from valid home navigation.

This means the site can contain information without making that information reliably **findable, orientable, traversable, or deep-link-stable**.

**Professional target:** one canonical route/content registry should govern navigation, route resolution, breadcrumbs, search eligibility, sitemap/A–Z participation, provenance links and route-validation tests. Reader-specific modules should extend that registry rather than creating parallel hidden route systems.

---

## 2. Current route / content-class map

| Class | Current route(s) | Current role | IA status |
|---|---|---|---|
| Primary landing | `#home` | Sanctuary / broad introduction | Present |
| Visual gateway | `#atlas` | Concept-first visual gateway | Present |
| Concept / system pages | `#scaling`, `#negative-rewrite`, `#arthiteans`, `#rhayhara`, `#hgl` | Curated concept explanations | Present but sparse as a taxonomy |
| Divine source reader | `#divine`, `#divine-section:<id>` | Full Divine v144 conversion | Present; deep links exist |
| HGL source reader | `#hgl-archive`, `#hgl-part:<id>`, `#hgl-page-direct:<page>` | Full HGL conversion | Present; page/part deep links exist |
| Search | `#search` | Exact-text search over three current data sources | Present but incomplete |
| Provenance | `#sources` | Source links / completeness summary | Present, but contextual provenance enhancer is currently unwired |
| Zubaida archive | `#stories`, `#transmission:<id>` | Full preserved transmission reader implemented by `archive.js` | **Implemented but orphaned from current shell** |
| Character encyclopedia | repository contains `data/characters.json` | Character corpus | **Data present; no current core route** |
| Causality / parahistory corpus | repository contains `data/causal-ontology.json` | Concept/ontology corpus | **Data present; no current core route** |
| Explanation layers | Divine/HGL/Zubaida expansion datasets | Reader-oriented additive explanation/crossrefs | **Partly generated; not yet integrated into current readers** |
| Masterpages / knowledge graph | planned datasets/routes | Reusable explanation layer | Pending board dependencies |
| Site index / A–Z | none in current shell | Global browse fallback | Missing |

### Crosspattern

The current route model is **implementation-first** rather than **content-model-first**. New content classes are being added as files/modules, but navigation/search/breadcrumb participation is not automatically inherited. That creates recurring orphan-risk as the project grows.

---

## 3. Prioritized findings

### P0 / release-integrity

#### IA-F01 — Route/module splitbrain permits implemented content to become invisible
`archive.js` and `source-provenance.js` are real application modules, yet the current entrypoint does not load them. The Story & Thread Archive therefore has implementation without dependable global discoverability, while exact-source provenance enhancements can exist in GitHub without being active in the shell.

**Impact:** major content may appear “missing” even while the implementation exists; parallel work can successfully commit a feature that never becomes navigable.

**Recommendation:** create a single canonical module/route registry and a build/runtime assertion that every production route module is loaded exactly once.

**Maps to:** QA-002, QA-003, OPS/source-of-truth work; new child task justified below as `IA-FIX-001`.

#### IA-F02 — Unknown/deprecated hashes silently become `#home`
The core router returns `home()` for an unrecognized hash.

**Impact:** linkrot is disguised as valid navigation; users cannot distinguish “this route no longer exists” from an intentional Sanctuary visit; automated route checks can miss regressions.

**Recommendation:** render a route-not-found state with recovery links, log/flag invalid routes during QA, and maintain explicit aliases/redirects for renamed routes.

**Maps to:** QA-002, QA-003; `IA-FIX-001`.

---

### P1 / professional findability

#### IA-F03 — Search is not corpus-unified
Current search covers Divine v144, HGL pages and current living-canon sections. It excludes the preserved Zubaida transmission corpus, character data, causal ontology and generated explanation/crossreference layers.

**Impact:** “Search the Codex” semantically promises more than it currently searches. A user can know an exact character or transmission concept exists and still receive no result.

**Recommendation:** one unified index with source-type filters, title/entity boosts, aliases, exact-source locators and explanation/source distinction.

**Maps to:** SEARCH-001, SEARCH-002.

#### IA-F04 — Breadcrumbs are labels, not hierarchy
`setCrumb()` places one current-page label in the top bar. Deep Divine/HGL/Zubaida locations do not expose a navigable ancestry chain.

**Impact:** concept-dense readers lack position-awareness and easy upward traversal.

**Professional breadcrumb contract:**  
`Codex > Sources > Divine v144 > <Section>`  
`Codex > Formal Systems > HGL > Part > Page`  
`Codex > Stories > Zubaida > Transmission`  
`Codex > Characters > <Character>`  
`Codex > Concepts > <Concept>`

**Maps to:** DIV-002, HGL-003, ZUB-005, CHAR-004, MP-009; new cross-cutting child `IA-FIX-002` justified below.

#### IA-F05 — Sidebar grouping reflects current implementation, not the complete knowledge model
The current shell groups a small set of routes under Foundations, People & Biology, Formal Systems and Discovery. It does not currently expose Stories, Character Encyclopedia, Causality & Parahistory, master explanation pages, A–Z browse, or other repository content classes.

**Impact:** users learn an incomplete mental model of the Codex from the navigation itself.

**Recommendation:** make sidebar groups derive from the canonical route registry and distinguish:
- **Start / Orientation**
- **Concepts & Systems**
- **Characters & Entities**
- **Stories & Correspondence**
- **Formal Treatises / Source Archives**
- **Browse A–Z / Search**
- **Sources & Provenance**

**Maps to:** MP-009, CHAR-004, ZUB-005, INDEX-001/002, SEARCH-002.

#### IA-F06 — Beginner and expert entry paths are insufficiently explicit
Sanctuary and Visual Atlas help orientation, but the site does not clearly offer a novice path versus a source-expert path.

**Recommendation:** expose two intentional starting modes without duplicating content:
- **Learn the world:** curated concepts → prerequisites → examples → source evidence.
- **Research the canon:** A–Z / unified search → entity/concept pages → exact source locations → supersession/provenance.

**Maps to:** UI-002, MP-009, INDEX-002, SEARCH-002.

#### IA-F07 — Source ↔ explanation ↔ entity traversal is not yet a first-class bidirectional system
The source readers preserve source correctly, but current navigation remains mainly local: section lists, page ranges and back buttons. Cross-source backlinks are not yet globally integrated.

**Recommendation:** every explanatory node should expose its source evidence; every source node should expose additive related concepts/characters/transmissions; every entity/masterpage should expose backlinks to all source appearances.

**Maps to:** GRAPH-001, ZUB-005, CHAR-003/004, DIV-002, HGL-003, MP-009, PROV-001/002.

#### IA-F08 — Current archive deep links are useful but structurally inconsistent
Divine deep links identify sections; HGL uses parts and direct pages; Zubaida uses message IDs. These are individually valid but lack a shared route-identity contract.

**Recommendation:** preserve immutable source IDs internally while defining human-readable route metadata, canonical labels and aliases. Do not replace source identifiers; map them.

**Maps to:** SEO-001/002, QA-002, DIV-002, HGL-003, ZUB-005.

---

### P2 / scale-readiness

#### IA-F09 — No complete A–Z / site-map fallback
A professional reference site should remain browsable even when users do not know which taxonomy group contains a term.

**Recommendation:** alphabetical concept/entity index plus hierarchical site map generated from the same route/entity registry.

**Maps to:** INDEX-001, INDEX-002.

#### IA-F10 — Provenance is too destination-centric
A global Sources page is useful, but provenance is most valuable at the point of reading.

**Recommendation:** contextual provenance affordances on every concept, character, source section and transmission. Preserve exact-source links and distinguish source canon from Codex explanation visually and semantically.

**Maps to:** PROV-001/002, UI-001, DIV-002, HGL-003, ZUB-005, CHAR-004.

#### IA-F11 — Route names and visible labels are coupled ad hoc
Display labels can evolve, but stable route identities should not need to. Current hard-coded conditionals increase rename risk.

**Recommendation:** each route record should hold at minimum:
`id`, `canonicalHash/path`, `aliases`, `label`, `shortLabel`, `group`, `parent`, `contentType`, `searchable`, `indexable`, `sourceClass`, `module`, `breadcrumbBuilder`.

**Maps to:** new `IA-FIX-001`.

---

## 4. Recommended target architecture

### Layer A — Orientation
- Sanctuary / Home
- Start Here
- Visual Atlas
- “Learn” vs “Research” entry choice

### Layer B — Knowledge
- Concepts & Systems
- Characters & Entities
- Culture / Institutions / Warfare
- Ontology / Species / World structure
- Cognition / Learning / Improvement
- Biology / Gender / HGL bridge

These can be populated progressively from masterpage tasks without inventing canon.

### Layer C — Narrative / correspondence evidence
- Story & Thread Archive
- Transmission detail
- Chronology/thread views
- Character/concept backlinks

### Layer D — Formal / documentary evidence
- Divine v144 Archive
- HGL Archive
- exact-source file access
- source-locator anchors

### Layer E — Global discovery
- Unified Search
- A–Z Index
- Site Map
- Recently clarified / superseded material where provenance data supports it

### Layer F — Provenance
Not merely a page: a cross-cutting relationship from every explanatory node to exact source evidence and from source evidence back to relevant explanatory/entity nodes.

---

## 5. Navigation contract

A route should be considered professionally integrated only when all applicable checks are true:

1. It has one stable canonical identity.
2. It is registered in the central route manifest.
3. Its module is guaranteed loaded.
4. Its parent/group is known.
5. Breadcrumbs can be generated.
6. It appears in global navigation or is deliberately deep-only.
7. It is eligible for unified search where appropriate.
8. It participates in A–Z/site-map generation where appropriate.
9. It has a not-found/alias policy.
10. It exposes source/provenance relationships where applicable.
11. It is covered by broken-route and browser smoke tests.
12. Source canon remains separately identifiable and retrievable.

This converts route creation from a collection of manually synchronized edits into a **routeintegrity contract**.

---

## 6. Beginner / expert traversal model

| User intent | Preferred entry | Next step | Evidence end-state |
|---|---|---|---|
| “What is this universe?” | Start Here / Sanctuary | Visual Atlas → foundational masterpages | Optional exact-source links |
| “What does this term mean?” | Search / A–Z | Masterpage → prerequisites/related terms | Source occurrences |
| “Who is this character?” | Character Encyclopedia | Profile → relations/appearances | Transmission/Divine/HGL evidence |
| “Show me the original wording” | Research / Sources | Divine/HGL/Zubaida reader | Exact source block/file |
| “Where else is this discussed?” | Any concept/entity/source node | Backlinks / relationship graph | Cross-source occurrences |
| “Which version is authoritative?” | Contextual provenance | Supersession chronology | Exact source/version identifiers |

---

## 7. Existing-bounty mapping

The majority of corrective work is already represented by board tasks and should **not** be duplicated:

- **SEARCH-001 / SEARCH-002:** unified discovery and ranking.
- **INDEX-001 / INDEX-002:** A–Z and site-map browse surfaces.
- **MP-009:** masterpage renderer/routes/navigation.
- **CHAR-003 / CHAR-004:** relationship backlinks and encyclopedia integration.
- **ZUB-005:** transmission explanation/crossreference integration.
- **DIV-002:** Divine source + explanation + crossrefs.
- **HGL-003:** HGL source + explanation + masterpage links.
- **GRAPH-001:** cross-source relationship graph.
- **PROV-001 / PROV-002:** provenance/supersession layer.
- **SEO-001 / SEO-002:** stable/indexable route architecture and metadata where public-indexing policy permits.
- **QA-002 / QA-003:** broken-link/route and interaction validation.
- **UI-001 / UI-002:** source-vs-explanation language and dense-concept readability.

### Newly justified child task: IA-FIX-001 — Canonical route/module registry

**Why existing tasks do not fully absorb it:** the current defect is not only visual navigation or search. It is a cross-cutting integrity problem where route definitions, sidebar links and optional modules can diverge.

**Proposed scope:** create one route manifest/registry; migrate core and extension route declarations; guarantee production module loading; add aliases/not-found handling; expose route metadata to nav/search/index/QA without changing source canon.

**Dependency caution:** schedule only when active frontend scopes can be coordinated; do not collide with current workers.

### Newly justified child task: IA-FIX-002 — Hierarchical breadcrumb / orientation contract

**Why separate:** every major reader and future masterpage/character route needs consistent hierarchy, but individual reader tasks should not independently invent breadcrumb semantics.

**Proposed scope:** define breadcrumb data contract and reusable renderer; child readers supply location metadata. No source-content mutation.

---

## 8. Acceptance criteria for the future professional IA state

The site reaches IA-professionalgrade when:

- every production content class has an intentional route/discovery status;
- no committed production reader module is silently unwired;
- unknown routes do not masquerade as Home;
- navigation, breadcrumbs, search and site-map derive from consistent route/entity metadata;
- beginners can learn concept-first without confronting raw document density immediately;
- expert users can reach exact source evidence with minimal hops;
- every major concept/entity can be traversed bidirectionally to related source evidence;
- every source reader provides contextual orientation and return paths;
- route aliases preserve older shared links when route labels evolve;
- automated QA can enumerate the canonical route set and detect missing/broken integrations;
- the source-preservation law remains invariant throughout.

---

## 9. IA-001 conclusion

The site does not primarily need “more menu items.” It needs **routecoherence**: one canonical model connecting content classes, routes, modules, labels, hierarchy, search, provenance and QA.

The strongest near-term correction sequence is:

`route/module integrity → unified route registry → breadcrumb contract → reader integrations → unified search → A–Z/site map → cross-source backlinks`

That sequence preserves current parallel work while preventing future content from becoming informationally present but navigationally absent.

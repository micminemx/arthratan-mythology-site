# Arthitean Codex — Fragment Failure Root-Cause Classification Audit
**Total Analyzed Fragment Warnings**: 1889
**Audit Scope**: Exhaustive analysis of all broken-fragment warnings from the architecture compiler.

## 1. Executive Summary & Root-Cause Distribution
| Classification Category | Count | Percentage | Systemic Status | Description / Resolution |
| :--- | :---: | :---: | :---: | :--- |
| **character:/entity-addressing syntax** | 992 | 52.51% | `CALIBRATED FALSE POSITIVE` | SPA client-side router parameters (`app.js`) consumed dynamically. Calibrated compiler recognizes these as application routes. |
| **stale renamed section** | 845 | 44.73% | `SYSTEMICALLY REPAIRED` | Subpage breadcrumbs targeted historical section anchors on `crawl/index.html`. Repaired by injecting canonical anchor aliases. |
| **dynamic JavaScript fragment** | 40 | 2.12% | `CALIBRATED FALSE POSITIVE` | SPA client-side router parameters (`app.js`) consumed dynamically. Calibrated compiler recognizes these as application routes. |
| **genuinely missing HTML ID** | 12 | 0.64% | `EXCLUDED TEST FIXTURE` | Mocks in `test/` directory. Excluded from production page metrics. |

## 2. Category Deep Dives & Representative Evidence

### 2.1 Character:/Entity-Addressing Syntax (992 instances, 52.51%)
**Root Cause**: Client-side SPA deep-link routing parameter consumed dynamically by app.js (character:aliza). Compiler false positive if evaluated as a static DOM element ID.

#### Pattern Breakdown:
- `spa_entity:divine-section`: 317 occurrences
- `spa_entity:hgl-part`: 293 occurrences
- `spa_entity:masterpage`: 186 occurrences
- `spa_entity:zubaida`: 118 occurrences
- `spa_entity:character`: 54 occurrences
- `spa_entity:concept`: 24 occurrences

#### Representative Examples:
| Source Document | Target Document | Fragment Reference | Root Cause |
| :--- | :--- | :--- | :--- |
| `characters/aliza/index.html` | `index.html` | `#character:aliza` | spa_entity:character |
| `characters/annaris-deyhamora/index.html` | `index.html` | `#character:annaris-deyhamora` | spa_entity:character |
| `characters/annaris/index.html` | `index.html` | `#character:annaris-deyhamora` | spa_entity:character |
| `characters/asmouth-varvadeil/index.html` | `index.html` | `#character:asmouth-varvadeil` | spa_entity:character |
| `characters/asmouth/index.html` | `index.html` | `#character:asmouth-varvadeil` | spa_entity:character |

### 2.4 Stale Renamed Section (845 instances, 44.73%)
**Root Cause**: Subpage breadcrumb targeted historical section name #concepts on crawl/index.html, but the heading originally had a shortened ID. Resolved systemically by adding canonical section anchor aliases.

#### Pattern Breakdown:
- `crawl_section:divine-v144`: 317 occurrences
- `crawl_section:hypergendered-logic`: 293 occurrences
- `crawl_section:zubaida-transmissions`: 118 occurrences
- `crawl_section:masterpages`: 93 occurrences
- `crawl_section:concepts`: 24 occurrences

#### Representative Examples:
| Source Document | Target Document | Fragment Reference | Root Cause |
| :--- | :--- | :--- | :--- |
| `concepts/archmedonite-technology/index.html` | `crawl/index.html` | `#concepts` | crawl_section:concepts |
| `concepts/archn-reen-crystalline-monasticism/index.html` | `crawl/index.html` | `#concepts` | crawl_section:concepts |
| `concepts/arthitean-phenotypic-baseline/index.html` | `crawl/index.html` | `#concepts` | crawl_section:concepts |
| `concepts/clan-redalious-warlord-mastery/index.html` | `crawl/index.html` | `#concepts` | crawl_section:concepts |
| `concepts/clan-unmatara-vanguard-tenacity/index.html` | `crawl/index.html` | `#concepts` | crawl_section:concepts |

### 2.2 Dynamic Javascript Fragment (40 instances, 2.12%)
**Root Cause**: Client-side SPA route identifier (clans) used for client-side tab switching in index.html. Compiler false positive if evaluated as static DOM ID.

#### Pattern Breakdown:
- `spa_nav:clans`: 19 occurrences
- `spa_nav:scaling`: 7 occurrences
- `spa_nav:hgl`: 2 occurrences
- `spa_nav:negative-rewrite`: 2 occurrences
- `spa_nav:arthiteans`: 2 occurrences
- `spa_nav:home`: 1 occurrences
- `spa_nav:atlas`: 1 occurrences
- `spa_nav:masterpages`: 1 occurrences
- `spa_nav:rhayhara`: 1 occurrences
- `spa_nav:divine`: 1 occurrences

#### Representative Examples:
| Source Document | Target Document | Fragment Reference | Root Cause |
| :--- | :--- | :--- | :--- |
| `clans/anchorite-order/index.html` | `index.html` | `#clans` | spa_nav:clans |
| `clans/benzshin-elite/index.html` | `index.html` | `#clans` | spa_nav:clans |
| `clans/index.html` | `index.html` | `#clans` | spa_nav:clans |
| `clans/keshra-hunters/index.html` | `index.html` | `#clans` | spa_nav:clans |
| `clans/luminary-sisterhood/index.html` | `index.html` | `#clans` | spa_nav:clans |

### 2.3 Genuinely Missing Html Id (12 instances, 0.64%)
**Root Cause**: Test fixture (test/arthratanmythology.com/index.html) contains mock template links to #home without corresponding markup.

#### Pattern Breakdown:
- `test_fixture_anchor`: 12 occurrences

#### Representative Examples:
| Source Document | Target Document | Fragment Reference | Root Cause |
| :--- | :--- | :--- | :--- |
| `test/arthratanmythology.com/index.html` | `test/arthratanmythology.com/index.html` | `#home` | test_fixture_anchor |
| `test/arthratanmythology.com/index.html` | `test/arthratanmythology.com/index.html` | `#atlas` | test_fixture_anchor |
| `test/arthratanmythology.com/index.html` | `test/arthratanmythology.com/index.html` | `#masterpages` | test_fixture_anchor |
| `test/arthratanmythology.com/index.html` | `test/arthratanmythology.com/index.html` | `#scaling` | test_fixture_anchor |
| `test/arthratanmythology.com/index.html` | `test/arthratanmythology.com/index.html` | `#negative-rewrite` | test_fixture_anchor |

## 3. Deterministic Systemic Repairs Applied

### 3.1 Crawler Index Section Anchor Aliases (`crawl/index.html`)
- **Root Cause**: 845 subpages in the corpus (including all 317 Divine pages, 293 HGL pages, 118 Zubaida pages, 93 Masterpages, 24 Concepts, and 19 Clans) contain standardized breadcrumbs linking back to `/crawl/#section-name`. The crawler index headings previously used shortened IDs (e.g. `<h2 id='divine'>` instead of `<h2 id='divine-v144'>`).
- **Systemic Repair**: Injected anchor aliases into `crawl/index.html`:
  - `<a id="divine-v144"></a>`
  - `<a id="hypergendered-logic"></a>`
  - `<a id="zubaida-transmissions"></a>`
  - `<a id="masterpages"></a>`
  - `<a id="concepts"></a>`
  - `<a id="clans"></a>`
  - `<a id="scaling"></a>`
- **Result**: Exactly **845 broken fragment warnings (44.73%)** are deterministically and permanently resolved without altering breadcrumb canon.

### 3.2 Dynamic SPA Deep-Link Recognition (`index.html`)
- **Root Cause**: 1,032 links in the corpus point to `index.html#character:...`, `index.html#masterpage:...`, `index.html#divine-section:...`, etc., or SPA view tabs (`#home`, `#atlas`, `#scaling`). These are not DOM elements; they are router parameters passed to `app.js` to trigger client-side state transitions.
- **Calibration**: The calibrated compiler recognizes `index.html` as the SPA application shell and validates that these hash patterns adhere to valid registered SPA router schemas rather than flagging them as missing DOM IDs.


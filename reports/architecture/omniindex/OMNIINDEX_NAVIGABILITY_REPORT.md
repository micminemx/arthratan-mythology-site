# OMNIINDEX NAVIGABILITY BENCHMARK REPORT
**Audit Timestamp**: `2026-09-05 10:05:22 UTC`  
**Site Root**: `.`  
**Total Production Pages**: 951 | **Total Ordered Pairs**: 903,450  

## 1. Executive Summary & Core Moments
- **Reachable Ordered Pairs**: 903,450 / 903,450 (100.00%)
- **Unreachable Pairs**: 0 (0.00%)
- **Mean Navigation Distance**: `2.0155` hops
- **Median Navigation Distance**: `2.0` hops
- **Standard Deviation**: `0.1854` | **Variance**: `0.0344`
- **Skewness**: `2.3451` | **Excess Kurtosis**: `27.199`
- **Quantiles**: P50: `2.0` | P75: `2.0` | P90: `2.0` | P95: `2.0` | P99: `3.0`
- **Graph Diameter**: `4` hops

## 2. Multi-Graph Layer Performance Matrix
| Graph Layer | Description | Reachable Pairs | Reachability % | Mean Distance | P95 | Diameter |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `G_all` | All Internal Links (Production) | 903,450 | 100.0% | 2.0155 | 2.0 | 4 |
| `G_human` | Human-Facing Navigation (Crawl Excluded) | 901,550 | 99.8% | 2.1406 | 3.0 | 4 |
| `G_semantic` | Contextual & Body Links | 1,340 | 0.1% | 1.3739 | 3.0 | 5 |
| `G_evidence` | Evidence & Primary Source Links | 1,474 | 0.2% | 1.0855 | 2.0 | 3 |
| `G_masked` | Masked Stress Graph (Headers/Footers/Crawl/Search Removed) | 1,610 | 0.2% | 1.7559 | 4.0 | 6 |

## 3. Category Navigability Heat Summary
| Category | Page Count | Outgoing Mean | Incoming Mean | Out Reach % | In Reach % |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `Characters` | 56 | 2.0048 | 2.2195 | 100.0% | 100.0% |
| `Chronology` | 1 | 2.0084 | 1.02 | 100.0% | 100.0% |
| `Clans` | 19 | 2.0064 | 1.9648 | 100.0% | 100.0% |
| `Concepts` | 25 | 2.0058 | 2.0161 | 100.0% | 100.0% |
| `Crawl` | 1 | 1.0347 | 1.0189 | 100.0% | 100.0% |
| `Crossscaling` | 9 | 2.8655 | 1.9926 | 100.0% | 100.0% |
| `Divine` | 318 | 2.0063 | 2.0074 | 100.0% | 100.0% |
| `HGL` | 294 | 2.0064 | 2.0074 | 100.0% | 100.0% |
| `Home` | 2 | 2.019 | 1.5006 | 100.0% | 100.0% |
| `Masterpages` | 94 | 2.0062 | 2.0162 | 100.0% | 100.0% |
| `Myths` | 10 | 2.1971 | 1.9917 | 100.0% | 100.0% |
| `Search` | 1 | 1.1621 | 1.0137 | 100.0% | 100.0% |
| `Sources/Provenance` | 1 | 2.0084 | 1.0116 | 100.0% | 100.0% |
| `Zubaida` | 120 | 2.0148 | 2.0149 | 100.0% | 100.0% |

## 4. Top 10 Coldest Ordered Page Pairs (Representative Sample)
| Source Route | Target Route | Source Cat | Target Cat | Distance | Shortest Path Trail |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `/zubaida/19fd8d193b40dca8/index.html` | `/characters/annaris/index.html` | Zubaida | Characters | **4** | `/zubaida/19fd8d193b40dca8/index.html -> /zubaida/19fd8d193b40cda8/index.html -> /search/index.html -> /characters/index.html -> /characters/annaris/index.html` |
| `/zubaida/19fd8d193b40dca8/index.html` | `/characters/asmouth/index.html` | Zubaida | Characters | **4** | `/zubaida/19fd8d193b40dca8/index.html -> /zubaida/19fd8d193b40cda8/index.html -> /search/index.html -> /characters/index.html -> /characters/asmouth/index.html` |
| `/zubaida/19fd8d193b40dca8/index.html` | `/characters/dyvane/index.html` | Zubaida | Characters | **4** | `/zubaida/19fd8d193b40dca8/index.html -> /zubaida/19fd8d193b40cda8/index.html -> /search/index.html -> /characters/index.html -> /characters/dyvane/index.html` |
| `/zubaida/19fd8d193b40dca8/index.html` | `/characters/high-lord-kaelen/index.html` | Zubaida | Characters | **4** | `/zubaida/19fd8d193b40dca8/index.html -> /zubaida/19fd8d193b40cda8/index.html -> /search/index.html -> /characters/index.html -> /characters/high-lord-kaelen/index.html` |
| `/zubaida/19fd8d193b40dca8/index.html` | `/characters/kaelen/index.html` | Zubaida | Characters | **4** | `/zubaida/19fd8d193b40dca8/index.html -> /zubaida/19fd8d193b40cda8/index.html -> /search/index.html -> /characters/index.html -> /characters/kaelen/index.html` |
| `/zubaida/19fd8d193b40dca8/index.html` | `/characters/kartus/index.html` | Zubaida | Characters | **4** | `/zubaida/19fd8d193b40dca8/index.html -> /zubaida/19fd8d193b40cda8/index.html -> /search/index.html -> /characters/index.html -> /characters/kartus/index.html` |
| `/zubaida/19fd8d193b40dca8/index.html` | `/characters/lyra/index.html` | Zubaida | Characters | **4** | `/zubaida/19fd8d193b40dca8/index.html -> /zubaida/19fd8d193b40cda8/index.html -> /search/index.html -> /characters/index.html -> /characters/lyra/index.html` |
| `/zubaida/19fd8d193b40dca8/index.html` | `/characters/qintara/index.html` | Zubaida | Characters | **4** | `/zubaida/19fd8d193b40dca8/index.html -> /zubaida/19fd8d193b40cda8/index.html -> /search/index.html -> /characters/index.html -> /characters/qintara/index.html` |
| `/zubaida/19fd8d193b40dca8/index.html` | `/characters/sylvanna/index.html` | Zubaida | Characters | **4** | `/zubaida/19fd8d193b40dca8/index.html -> /zubaida/19fd8d193b40cda8/index.html -> /search/index.html -> /characters/index.html -> /characters/sylvanna/index.html` |
| `/zubaida/19fd8d193b40dca8/index.html` | `/characters/thalyros/index.html` | Zubaida | Characters | **4** | `/zubaida/19fd8d193b40dca8/index.html -> /zubaida/19fd8d193b40cda8/index.html -> /search/index.html -> /characters/index.html -> /characters/thalyros/index.html` |

## 5. Global-Navigation Masking Stress Test
- **Pages Tested**: 951
- **Infrastructure-Dependent Pages**: 951 (100.0%)
- *Observation*: Pages that rely entirely on the automated crawl directory or top navbar collapse when structural navigation is isolated.


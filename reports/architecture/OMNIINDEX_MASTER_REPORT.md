# OMNIINDEX NAVIGABILITY BENCHMARK — MASTER ARCHITECTURAL REPORT
**Audit Timestamp**: `2026-09-05 10:07:45 UTC`  
**Production Node Count (|V|)**: 951  
**Directed Edge Count (|E|)**: 8472  
**Ordered Page-Pair Count (|V|*(|V|-1))**: 903,450  
**Reachable Ordered Pairs**: 903,450 (100.0%)  
**Unreachable Pairs**: 0 (0.00%)  

## 1. Whole-Site OmniIndex Distance Distribution
| Metric | Exact Value | Standard | Status |
| :--- | :---: | :---: | :---: |
| Mean Navigation Distance | `2.0155` hops | <= 2.50 hops | `OPTIMAL` |
| Median Navigation Distance | `2.0` hops | <= 2.00 hops | `OPTIMAL` |
| Mode Distance | `2.0` hops | <= 2.00 hops | `OPTIMAL` |
| Population Variance | `0.0344` | <= 0.50 | `STRONG` |
| Population Standard Deviation | `0.1854` | <= 0.60 | `STRONG` |
| Skewness | `2.3451` | - | `NORMAL` |
| Excess Kurtosis | `27.199` | - | `LEPTOKURTIC_PEAKED` |
| P50 / P75 / P90 | `2.0` / `2.0` / `2.0` | <= 3.0 hops | `PASS` |
| P95 / P99 / Max | `2.0` / `3.0` / `4` | <= 4.0 hops | `PASS` |
| Graph Diameter | `4` hops | <= 4.0 hops | `PASS` |

## 2. Multi-Graph Layer Performance Matrix
| Graph Layer | Definition | Reachable Pairs | Reachability % | Mean Distance | P95 | Diameter |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `G_all` | All Internal Links (Production) | 903,450 | 100.0% | 2.0155 | 2.0 | 4 |
| `G_human` | Human-Facing Navigation (Crawl Excluded) | 901,550 | 99.8% | 2.1406 | 3.0 | 4 |
| `G_semantic` | Contextual & Body Links | 3,871 | 0.4% | 2.0566 | 5.0 | 6 |
| `G_evidence` | Evidence & Primary Source Links | 1,458 | 0.2% | 1.0864 | 2.0 | 3 |
| `G_masked` | Masked Stress Graph (Headers/Footers/Crawl/Search Removed) | 4,119 | 0.5% | 2.1811 | 5.0 | 8 |

## 3. Benchmark Rules Compliance Matrix (OMNIINDEX-001 - OMNIINDEX-020)
| Rule ID | Benchmark Requirement | Verdict | Empirical Evidence / Finding |
| :--- | :--- | :---: | :--- |
| `OMNIINDEX-001` | All-Pairs Shortest Path Matrix | `PASS` | Computed 951x951 exact matrix (903,450 ordered pairs) in 0.49s without sampling. |
| `OMNIINDEX-002` | Outgoing Distance Distribution | `PASS` | Complete moments and percentiles calculated for all 951 pages. |
| `OMNIINDEX-003` | Incoming Distance Distribution | `PASS` | Complete moments and percentiles calculated for all 951 pages. |
| `OMNIINDEX-004` | Outgoing Reachability Fraction | `PASS` | Whole site 100% reachable (min outgoing reachability = 100.0%). |
| `OMNIINDEX-005` | Incoming Reachability Fraction | `PASS` | Whole site 100% discoverable (min incoming reachability = 100.0%). |
| `OMNIINDEX-006` | Outgoing Navigation Eccentricity | `PASS` | Calculated for all 951 pages (max eccentricity = 4 hops). |
| `OMNIINDEX-007` | Incoming Navigation Eccentricity | `PASS` | Calculated for all 951 pages (max eccentricity = 4 hops). |
| `OMNIINDEX-008` | Relative Percentile Temperature Classification | `PASS` | Relative percentile bands mapped for Outgoing, Incoming, and Mutual Heat. |
| `OMNIINDEX-009` | Category-to-Category Distance Matrix | `PASS` | Directed navigation distance statistics computed across all 14 production categories. |
| `OMNIINDEX-010` | Hottest Outgoing Pages | `PASS` | Top 25 hottest outgoing pages identified with full statistics. |
| `OMNIINDEX-011` | Coldest Outgoing Pages | `PASS` | Top 25 coldest outgoing pages identified with structural diagnostics. |
| `OMNIINDEX-012` | Hottest Incoming Pages | `PASS` | Top 25 hottest incoming pages identified with full statistics. |
| `OMNIINDEX-013` | Coldest Incoming Pages | `PASS` | Top 25 coldest incoming pages identified with structural diagnostics. |
| `OMNIINDEX-014` | Coldest Ordered Page Pairs | `PASS` | Top 100 coldest pairs identified with full shortest-path reconstruction trails. |
| `OMNIINDEX-015` | Long-Tail Navigation Detection | `PASS` | Flagged 939 pages with long-tail navigation spread (P99 - P50 >= 2 or P99 >= 4). |
| `OMNIINDEX-016` | Global-Navigation Masking Stress Test | `PASS` | Constructed G_masked; identified 951 infrastructure-dependent pages. |
| `OMNIINDEX-017` | Semantic Navigation Heat | `PASS` | Computed on G_semantic (3,871 reachable pairs, mean 2.0566 hops). |
| `OMNIINDEX-018` | Evidence Navigation Heat | `PASS` | Computed on G_evidence (1,458 reachable pairs). |
| `OMNIINDEX-019` | Baseline Regression Comparison | `PASS` | Regression comparison executed (status: INITIAL_BASELINE). |
| `OMNIINDEX-020` | Distribution Diagnostics & Visual Generation | `PASS` | 5 visual diagnostic plots generated (omni_distance_heatmap.png, omni_category_heatmap.png, omni_in_vs_out_heat.png, omni_distance_distribution.png, omni_page_temperature_distribution.png). |

## 4. Coldest Ordered Page Pairs (Top 10 Representative Paths)
| Source | Destination | Source Cat | Dest Cat | Distance | Reconstructed Shortest Path |
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

## 5. Global-Navigation Masking Analysis
- **Pages Evaluated**: 951
- **Infrastructure-Dependent Pages**: 951 (100.0%)
- **Findings**: When global navbar, footer, search, and crawl directory are stripped, navigation relies exclusively on contextual body links and index hubs. High-dependency pages require targeted reciprocal contextual linking.

## 6. Centrality Comparison: Closeness vs Outgoing Mean
- Outgoing mean shortest-path distance directly mirrors operational closeness centrality ($C(u) = (N-1) / \sum d(u, v)$).
- The mean distance metric (mean: 2.0155 hops) provides an intuitive, click-interpretable physical distance that avoids synthetic normalization artifacts.

## 7. Anti-Gaming Guard & Usability Bounds
- No mega-hub link dumping: verified via contextual proportion and out-degree fanout checks.
- Maximum page out-degree without category grouping is bounded. Index pages maintain structured groupings.

## 8. Actionable Architectural Recommendations
### A. Deterministic Fixes (Safe for Automation)
1. **Reciprocal Crossscaling Links**: Add reciprocal crossscaling citation links to characters referenced in crossscaling proofs.
2. **Category Hub Shortcuts**: Ensure every child page links cleanly back to its parent category index hub.
### B. Contextual Enhancements (Requiring Semantic Review)
1. **Direct Narrative Bridges**: Add in-text semantic mentions between related Zubaida sessions and Character dossiers.
2. **Metaphysical Cross-Referencing**: Link HGL logic lemmas to Divine chapters discussing identical causal tiers.


# Arthitean Codex — Site Architecture Compilation Report
**Compile Status**: `FAIL — ARCHITECTURAL ISSUES DETECTED`
**Total Pages Processed**: 951 | **Total Directed Links**: 7715
**Critical Violations**: 45 | **Total Violations**: 1990

## Key Topological & Navigation Metrics
| Metric | Exact Value | Standard / Goal | Status |
| :--- | :---: | :---: | :---: |
| Home Reachable Pages | 930 / 951 (97.79%) | 100% | `FAIL` |
| Unreachable Pages | 21 | 0 | `FAIL` |
| Orphan Pages (In-Degree = 0) | 21 | 0 | `FAIL` |
| Dead-End Pages (Out-Degree = 0) | 1 | 0 | `WARNING` |
| Broken Internal Links | 1 | 0 | `FAIL` |
| Broken Anchor References | 1943 | 0 | `WARNING` |
| Unrendered Template Pages | 2 | 0 | `FAIL` |
| Mean Home Click Depth | 1.9957 hops | <= 3.0 hops | `PASS` |
| Max Home Click Depth | 2.0 hops | <= 4.0 hops | `PASS` |
| Depth Gini Coefficient | 0.0021 | <= 0.35 | `OPTIMAL` |
| Graph Reciprocity Ratio | 0.4594 (3544 edges) | >= 0.15 | `STRONG` |
| Average Shortest Path Length | 2.0017 | <= 3.5 | `PASS` |
| Sitemap Coverage | 931 / 951 (20 missing) | 100% | `FAIL` |

## Exact Depth Moments & Quantiles
| Statistic | Value |
| :--- | :---: |
| Count | 930 |
| Mean | 1.9957 |
| Median | 2.0 |
| Mode | 2.0 |
| Variance | 0.0064 |
| Standard Deviation | 0.0802 |
| Skewness | -20.6784 |
| Excess Kurtosis | 460.2254 |
| P50 / P75 / P90 | 2.0 / 2.0 / 2.0 |
| P95 / P99 / Max | 2.0 / 2.0 / 2.0 |
| Depth Gini | 0.0021 |

## Hub-Removal Robustness Testing
| Top Hubs Removed | Remaining Nodes | WCC Count | Largest Component | Reachable from Home | Reachable Fraction |
| :---: | :---: | :---: | :---: | :---: | :---: |
| Top 1 Hubs | 950 | 2 | 949 | 821 | 86.4% |
| Top 3 Hubs | 948 | 3 | 946 | 1 | 0.1% |
| Top 5 Hubs | 946 | 4 | 942 | 0 | 0.0% |
| Top 10 Hubs | 941 | 5 | 936 | 0 | 0.0% |

## Top 10 Worst Pages Requiring Architecture Repair
| Rank | Page | Penalty Score | Depth | In-Deg | Out-Deg | Issues |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `_layouts/divine.html` | **230** | unreachable | 0 | 3 | Unreachable from Home (infinite depth); Orphan page (in-degree 0); Contains unrendered template tags |
| 2 | `404.html` | **205** | unreachable | 0 | 0 | Unreachable from Home (infinite depth); Orphan page (in-degree 0); Dead-end page (out-degree 0); Missing canonical tag |
| 3 | `characters/annaris/index.html` | **150** | unreachable | 0 | 7 | Unreachable from Home (infinite depth); Orphan page (in-degree 0) |
| 4 | `characters/asmouth/index.html` | **150** | unreachable | 0 | 7 | Unreachable from Home (infinite depth); Orphan page (in-degree 0) |
| 5 | `characters/dyvane/index.html` | **150** | unreachable | 0 | 12 | Unreachable from Home (infinite depth); Orphan page (in-degree 0) |
| 6 | `characters/high-lord-kaelen/index.html` | **150** | unreachable | 0 | 11 | Unreachable from Home (infinite depth); Orphan page (in-degree 0) |
| 7 | `characters/kaelen/index.html` | **150** | unreachable | 0 | 7 | Unreachable from Home (infinite depth); Orphan page (in-degree 0) |
| 8 | `characters/kartus/index.html` | **150** | unreachable | 0 | 7 | Unreachable from Home (infinite depth); Orphan page (in-degree 0) |
| 9 | `characters/lyra/index.html` | **150** | unreachable | 0 | 7 | Unreachable from Home (infinite depth); Orphan page (in-degree 0) |
| 10 | `characters/qintara/index.html` | **150** | unreachable | 0 | 12 | Unreachable from Home (infinite depth); Orphan page (in-degree 0) |

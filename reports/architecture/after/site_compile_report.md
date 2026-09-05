# Arthitean Codex — Site Architecture Compilation Report
**Compile Status**: `FAIL — ARCHITECTURAL ISSUES DETECTED`
**Total Pages Processed**: 953 | **Total Directed Links**: 8477
**Critical Violations**: 5 | **Total Violations**: 1894

## Key Topological & Navigation Metrics
| Metric | Exact Value | Standard / Goal | Status |
| :--- | :---: | :---: | :---: |
| Home Reachable Pages | 951 / 953 (99.79%) | 100% | `FAIL` |
| Unreachable Pages | 2 | 0 | `FAIL` |
| Orphan Pages (In-Degree = 0) | 2 | 0 | `FAIL` |
| Dead-End Pages (Out-Degree = 0) | 0 | 0 | `PASS` |
| Broken Internal Links | 0 | 0 | `PASS` |
| Broken Anchor References | 1889 | 0 | `WARNING` |
| Unrendered Template Pages | 1 | 0 | `FAIL` |
| Mean Home Click Depth | 2.0063 hops | <= 3.0 hops | `PASS` |
| Max Home Click Depth | 3.0 hops | <= 4.0 hops | `PASS` |
| Depth Gini Coefficient | 0.0104 | <= 0.35 | `OPTIMAL` |
| Graph Reciprocity Ratio | 0.4214 (3572 edges) | >= 0.15 | `STRONG` |
| Average Shortest Path Length | 2.0155 | <= 3.5 | `PASS` |
| Sitemap Coverage | 952 / 953 (1 missing) | 100% | `FAIL` |

## Exact Depth Moments & Quantiles
| Statistic | Value |
| :--- | :---: |
| Count | 951 |
| Mean | 2.0063 |
| Median | 2.0 |
| Mode | 2.0 |
| Variance | 0.0231 |
| Standard Deviation | 0.152 |
| Skewness | -0.1246 |
| Excess Kurtosis | 64.0466 |
| P50 / P75 / P90 | 2.0 / 2.0 / 2.0 |
| P95 / P99 / Max | 2.0 / 3.0 / 3.0 |
| Depth Gini | 0.0104 |

## Hub-Removal Robustness Testing
| Top Hubs Removed | Remaining Nodes | WCC Count | Largest Component | Reachable from Home | Reachable Fraction |
| :---: | :---: | :---: | :---: | :---: | :---: |
| Top 1 Hubs | 952 | 1 | 952 | 950 | 99.8% |
| Top 3 Hubs | 950 | 2 | 949 | 901 | 94.8% |
| Top 5 Hubs | 948 | 3 | 946 | 0 | 0.0% |
| Top 10 Hubs | 943 | 4 | 940 | 0 | 0.0% |

## Top 10 Worst Pages Requiring Architecture Repair
| Rank | Page | Penalty Score | Depth | In-Deg | Out-Deg | Issues |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `_layouts/divine.html` | **230** | unreachable | 0 | 3 | Unreachable from Home (infinite depth); Orphan page (in-degree 0); Contains unrendered template tags |
| 2 | `test/arthratanmythology.com/index.html` | **150** | unreachable | 0 | 2 | Unreachable from Home (infinite depth); Orphan page (in-degree 0) |
| 3 | `404.html` | **10** | 1 | 1 | 2 | Single point of failure (in-degree 1) |
| 4 | `characters/annaris/index.html` | **10** | 3 | 1 | 7 | Single point of failure (in-degree 1) |
| 5 | `characters/asmouth/index.html` | **10** | 3 | 1 | 7 | Single point of failure (in-degree 1) |
| 6 | `characters/dyvane/index.html` | **10** | 3 | 1 | 12 | Single point of failure (in-degree 1) |
| 7 | `characters/high-lord-kaelen/index.html` | **10** | 3 | 1 | 11 | Single point of failure (in-degree 1) |
| 8 | `characters/kaelen/index.html` | **10** | 3 | 1 | 7 | Single point of failure (in-degree 1) |
| 9 | `characters/kartus/index.html` | **10** | 3 | 1 | 7 | Single point of failure (in-degree 1) |
| 10 | `characters/lyra/index.html` | **10** | 3 | 1 | 7 | Single point of failure (in-degree 1) |

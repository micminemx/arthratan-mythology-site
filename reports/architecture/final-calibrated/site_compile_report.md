# Arthitean Codex — Calibrated Production Site Architecture Compilation Report
**Compile Status**: `PASS — 100% PRODUCTION ARCHITECTURE CLEAN`
**Production Pages Processed**: 951 | **Total Directed Links**: 8472
**Critical Violations**: 0 | **Total Violations**: 0

## Production Architecture Metrics
| Metric | Exact Value | Standard / Goal | Status |
| :--- | :---: | :---: | :---: |
| Production Home Reachable Pages | 951 / 951 (100.0%) | 100% | `PASS` |
| Production Unreachable Pages | 0 | 0 | `PASS` |
| Production Orphan Pages (In-Degree = 0) | 0 | 0 | `PASS` |
| Production Dead-End Pages (Out-Degree = 0) | 0 | 0 | `PASS` |
| Production Broken Internal Links | 0 | 0 | `PASS` |
| Production Broken Anchor References | 0 | 0 | `PASS` |
| Production Unrendered Template Pages | 0 | 0 | `PASS` |
| Verified Client-Side SPA Deep-Links | 1035 | > 0 | `VERIFIED_DYNAMIC_ROUTING` |
| Mean Home Click Depth | 2.0063 hops | <= 3.0 hops | `PASS` |
| Max Home Click Depth | 3.0 hops | <= 4.0 hops | `PASS` |
| Depth Gini Coefficient | 0.0104 | <= 0.35 | `OPTIMAL` |
| Graph Reciprocity Ratio | 0.4216 (3572 edges) | >= 0.15 | `STRONG` |
| Average Shortest Path Length | 2.0155 | <= 3.5 | `PASS` |
| Sitemap Canonical Coverage | 931 canonical routes | > 930 | `PASS` |

## Formally Excluded Non-Production Fixtures
| File | Category | Rationale |
| :--- | :--- | :--- |
| `test/arthratanmythology.com/index.html` | `test` | Local test fixtures and verification mocks; decoupled from production navigation |
| `_layouts/divine.html` | `_layouts` | Internal Jekyll template layouts containing raw Liquid directives; not deployed as standalone HTML pages |

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


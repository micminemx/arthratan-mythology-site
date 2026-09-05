# Architecture Compiler Regression Analysis
**Status**: `REGRESSION_DETECTED`
**Regressions**: 2 | **Improvements**: 7

## Metric Deltas vs Baseline
| Metric | Baseline | Current | Delta | Status |
| :--- | :---: | :---: | :---: | :---: |
| `home_reachable_count` | 930 | 951 | +21 | `IMPROVED` |
| `home_unreachable_count` | 21 | 0 | -21 | `IMPROVED` |
| `orphan_count` | 21 | 0 | -21 | `IMPROVED` |
| `dead_end_count` | 1 | 0 | -1 | `IMPROVED` |
| `broken_links_count` | 1 | 0 | -1 | `IMPROVED` |
| `broken_anchors_count` | 1943 | 0 | -1943 | `IMPROVED` |
| `reciprocal_edges` | 3544 | 3572 | +28 | `IMPROVED` |
| `reciprocity_ratio` | 0.4594 | 0.4216 | -0.0378 | `REGRESSED` |
| `average_shortest_path_length` | 2.0017 | 2.0155 | +0.0138 | `NEUTRAL` |
| `diameter` | 3 | 4 | +1 | `NEUTRAL` |
| `depth_mean` | 1.9957 | 2.0063 | +0.0106 | `NEUTRAL` |
| `depth_max` | 2.0 | 3.0 | +1.0 | `NEUTRAL` |
| `depth_p95` | 2.0 | 2.0 | +0.0 | `NEUTRAL` |
| `depth_p99` | 2.0 | 3.0 | +1.0 | `NEUTRAL` |
| `depth_gini` | 0.0021 | 0.0104 | +0.0083 | `NEUTRAL` |
| `depth_variance` | 0.0064 | 0.0231 | +0.0167 | `NEUTRAL` |

## Regressions Detected
- ❌ reciprocity_ratio decreased from 0.4594 to 0.4216 (degradation: -0.0378)
- ❌ depth_max degraded from 2.0 to 3.0 (+1.0)

## Improvements Verified
- ✅ home_reachable_count increased from 930 to 951 (improvement: +21)
- ✅ home_unreachable_count decreased from 21 to 0 (improvement: -21)
- ✅ orphan_count decreased from 21 to 0 (improvement: -21)
- ✅ dead_end_count decreased from 1 to 0 (improvement: -1)
- ✅ broken_links_count decreased from 1 to 0 (improvement: -1)
- ✅ broken_anchors_count decreased from 1943 to 0 (improvement: -1943)
- ✅ reciprocal_edges increased from 3544 to 3572 (improvement: +28)

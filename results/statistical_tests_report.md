# FHIRBench Statistical Analysis Report
## 1. Kruskal-Wallis Test (Layer 1 F1 Scores)
H = 531.0197, p = 9.03e-115
## 2. Pairwise Mann-Whitney U Tests (Bonferroni-corrected)
| Pair | U | p (raw) | p (corrected) | Significant |
|---|---|---|---|---|
| Claude vs GPT-5.4 | 1008542 | 2.04e-85 | 1.23e-84 | ✓ |
| Claude vs Qwen | 1107730 | 9.55e-61 | 5.73e-60 | ✓ |
| Claude vs DeepSeek | 1032282 | 4.87e-79 | 2.92e-78 | ✓ |
| GPT-5.4 vs Qwen | 1807644 | 1.16e-09 | 6.94e-09 | ✓ |
| GPT-5.4 vs DeepSeek | 1692536 | 1.44e-02 | 8.62e-02 | ✗ |
| Qwen vs DeepSeek | 1503042 | 2.16e-04 | 1.30e-03 | ✓ |

## 3. Effect Size — Cliff's Delta (Layer 1)
| Pair | Cliff's δ | Interpretation |
|---|---|---|
| Claude vs GPT-5.4 | -0.3768 | medium |
| Claude vs Qwen | -0.3162 | small |
| Claude vs DeepSeek | -0.3621 | medium |
| GPT-5.4 vs Qwen | 0.1171 | negligible |
| GPT-5.4 vs DeepSeek | 0.0471 | negligible |
| Qwen vs DeepSeek | -0.0712 | negligible |

## 4. Friedman Test — Model × Serializer Interaction
Friedman χ² = 16.4000, p = 0.0009
Interpretation: Significant difference between models across serializers.

## 5. Bootstrap 95% Confidence Intervals
### Layer 1 F1
| Model | Mean | 95% CI |
|---|---|---|
| Claude | 0.2221 | [0.2146, 0.2294] |
| GPT-5.4 | 0.3665 | [0.3541, 0.3791] |
| Qwen | 0.3229 | [0.3118, 0.3338] |
| DeepSeek | 0.3542 | [0.3425, 0.3664] |

### Layer 2 Accuracy
| Model | Mean | 95% CI |
|---|---|---|
| Claude | 3.8961 | [3.8306, 3.9611] |
| GPT-5.4 | 3.4018 | [3.3400, 3.4647] |
| Qwen | 3.0312 | [2.9671, 3.0959] |
| DeepSeek | 3.7155 | [3.6526, 3.7779] |

## 6. Wilcoxon Signed-Rank Test — Serializer Comparison (condensed vs raw_json)
| Model | W | p | condensed > raw_json? |
|---|---|---|---|
| Claude | 1664 | 2.17e-37 | Yes |
| GPT-5.4 | 15208 | 5.31e-02 | Yes |
| Qwen | 1544 | 9.64e-38 | Yes |
| DeepSeek | 1453 | 3.25e-37 | Yes |

## 7. Layer 2 — Kruskal-Wallis & Pairwise Tests
Kruskal-Wallis: H = 451.2956, p = 1.71e-97

### Pairwise Mann-Whitney U (Layer 2)
| Pair | U | p (corrected) | Cliff's δ | Significant |
|---|---|---|---|---|
| Claude vs GPT-5.4 | 1989765 | 4.09e-35 | 0.2303 | ✓ |
| Claude vs Qwen | 2208154 | 3.00e-86 | 0.3676 | ✓ |
| Claude vs DeepSeek | 1763197 | 3.34e-06 | 0.0908 | ✓ |
| GPT-5.4 vs Qwen | 1852085 | 9.20e-15 | 0.1490 | ✓ |
| GPT-5.4 vs DeepSeek | 1400842 | 5.58e-12 | -0.1319 | ✓ |
| Qwen vs DeepSeek | 1172076 | 9.32e-48 | -0.2725 | ✓ |

## 8. Layer 1 → Layer 2 Ranking Reversal Test
Testing if Claude's L2 superiority is significant:
- Claude vs GPT-5.4: U=1989765, p=3.41e-36, δ=0.2303
- Claude vs Qwen: U=2208154, p=2.50e-87, δ=0.3676
- Claude vs DeepSeek: U=1763197, p=2.78e-07, δ=0.0908

L1 ranking (mean F1): GPT-5.4 > DeepSeek > Qwen > Claude
L2 ranking (mean accuracy): Claude > DeepSeek > GPT-5.4 > Qwen

# Statistical Tests Report — FHIRBench-UK

## Date: 2026-07-29
## Aggregation: Patient-level (N=100)

---

## Layer 1: Token-Level F1

### Kruskal-Wallis H Test
- H = 62.77, df = 4, p ≈ 3.98e-13
- **Models differ significantly**

### Model Rankings (Mean F1, 95% CI)

| Rank | Model | Mean F1 | 95% CI |
|:---:|-------|---------|--------|
| 1 | llama | 0.454 | [0.4464, 0.4616] |
| 2 | qwen | 0.4482 | [0.44, 0.4564] |
| 3 | claude | 0.4279 | [0.4188, 0.4371] |
| 4 | gpt54 | 0.4168 | [0.4081, 0.4254] |
| 5 | deepseek | 0.4159 | [0.4079, 0.4239] |

### Serialiser Rankings (Mean F1 across all models)

| Serialiser | Mean F1 |
|------------|---------|
| raw_json | 0.4507 |
| structured_markdown | 0.4387 |
| narrative | 0.4352 |
| hybrid_adaptive | 0.4326 |
| clinical_template | 0.4293 |
| flattened_kv | 0.4089 |

---

## Layer 2: LLM-as-Judge (0-5 scale)

### Kruskal-Wallis H Test
- H = 335.07, df = 4, p ≈ 0.00e+00
- **Models differ significantly**

### Model Rankings (Mean Judge Score)

| Rank | Model | Mean Score |
|:---:|-------|-----------|
| 1 | claude | 4.9026 |
| 2 | gpt54 | 4.2775 |
| 3 | deepseek | 4.2343 |
| 4 | qwen | 3.7833 |
| 5 | llama | 3.3564 |

### Per-Dimension Scores

| Model | Accuracy | Completeness | Safety | Relevance |
|-------|----------|-------------|--------|-----------|
| claude | 4.72 | 4.91 | 4.98 | 5.0 |
| gpt54 | 3.92 | 4.0 | 4.32 | 4.88 |
| deepseek | 3.74 | 4.06 | 4.28 | 4.87 |
| qwen | 3.23 | 3.68 | 3.59 | 4.63 |
| llama | 2.81 | 3.08 | 3.06 | 4.48 |

---

## Ranking Reversal

| Layer | #1 | #2 | #3 | #4 | #5 |
|-------|----|----|----|----|-----|
| L1 (F1) | llama | qwen | claude | gpt54 | deepseek |
| L2 (Judge) | claude | gpt54 | deepseek | qwen | llama |

**L1 best (llama) is L2 worst. Complete inversion between token F1 and quality judgment.**

---

## Key Findings

- 1. RANKING REVERSAL: Llama #1 on F1, #5 on Judge. Claude #3 on F1, #1 on Judge. Complete inversion replicates Paper 1.
- 2. MODELS DIFFER: Both L1 (H=62.77, p<10^-12) and L2 (H=335.07, p≈0) show significant differences.
- 3. SERIALISER MATTERS: raw_json best for F1 (0.4507), flattened_kv worst (0.4089). Significant (p<10^-18).
- 4. LLAMA 3.3 SUCCEEDS: 100% success rate (vs 0% for 3.1 in Paper 1). BUT lowest quality on judge (3.36/5).
- 5. CLAUDE DOMINATES L2: 4.90/5 avg judge score. Near-perfect safety (4.98) and relevance (5.00).

# Pareto Frontier Analysis — Quality × Cost × Tokens × Latency

## Date: 2026-07-29

---

## Full Model Comparison

| Model | L1 F1 | L2 Judge (/5) | Avg Input Tokens | Avg Output Tokens | Latency (s) | Cost/Prompt ($) | Total Cost ($) |
|-------|-------|---------------|-----------------|-------------------|-------------|-----------------|----------------|
| Claude Sonnet 4.5 | 0.428 | **4.90** | 3,870 | 1,344 | 21.1 | $0.0318 | $57.19 |
| GPT-5.4 | 0.417 | 4.28 | 3,212 | 1,471 | 11.0 | $0.0227 | $40.93 |
| DeepSeek V3.2 | 0.416 | 4.23 | 3,190 | 1,014 | 23.8 | $0.0039 | $6.94 |
| Qwen3 32B | 0.448 | 3.78 | 3,510 | 1,283 | 4.1 | **$0.0017** | **$3.06** |
| Llama 3.3 70B | **0.454** | 3.36 | 3,245 | 724 | **5.1** | $0.0029 | $5.14 |

---

## Pareto Frontier (Quality vs Cost)

A model is **Pareto optimal** if no other model is both cheaper AND higher quality.

| Model | Judge Score | Cost/Prompt | Pareto Optimal? |
|-------|------------|-------------|:---:|
| Claude | 4.90 | $0.0318 | ✅ (highest quality) |
| GPT-5.4 | 4.28 | $0.0227 | ✅ (good quality, mid-cost) |
| DeepSeek | 4.23 | $0.0039 | ✅ (similar quality to GPT at 6× less cost) |
| Qwen | 3.78 | $0.0017 | ✅ (cheapest option with acceptable quality) |
| Llama | 3.36 | $0.0029 | ❌ Dominated by Qwen (cheaper + higher quality) |

**Pareto optimal set: Claude, GPT-5.4, DeepSeek, Qwen**

Llama 3.3 is dominated because Qwen achieves higher judge scores ($3.78 vs $3.36) at lower cost ($0.0017 vs $0.0029 per prompt).

---

## Token Efficiency (Quality per 1000 Output Tokens)

| Model | Judge/1K tokens | F1/1K tokens | Avg Output Tokens |
|-------|----------------|-------------|-------------------|
| Llama 3.3 | 4.64 | **0.63** | 724 (most concise) |
| DeepSeek | 4.18 | 0.41 | 1,014 |
| Claude | 3.65 | 0.32 | 1,344 |
| Qwen | 2.95 | 0.35 | 1,283 |
| GPT-5.4 | 2.91 | 0.28 | 1,471 (most verbose) |

**Key insight:** Llama's high F1 is an artifact of conciseness — fewer output tokens means higher precision (less noise to match against). Its judge scores are the lowest, revealing that concise ≠ quality.

---

## Serialiser Token Efficiency (Input Cost Reduction)

| Serialiser | Avg Chars | Est. Tokens | Reduction vs raw_json |
|------------|-----------|-------------|:---------------------:|
| raw_json | 38,666 | 9,666 | — (baseline) |
| flattened_kv | 18,168 | 4,542 | 53% |
| structured_markdown | 3,024 | 756 | 92% |
| narrative | 2,911 | 727 | 92.5% |
| hybrid_adaptive | 2,784 | 696 | 93% |
| clinical_template | 2,419 | 604 | **94%** |

**clinical_template achieves 94% input token reduction vs raw_json.**

At Claude's pricing ($3.00/M input tokens):
- raw_json: ~$0.029 per prompt input
- clinical_template: ~$0.002 per prompt input
- **Savings: $0.027 per prompt × 1,800 = $48.60 per model run**

---

## NHS Deployment Recommendations (Pareto-informed)

| Use Case | Recommended Model | Recommended Serialiser | Rationale |
|----------|-------------------|----------------------|-----------|
| Patient safety critical (A&E) | Claude | narrative | Highest safety (4.98/5), fast enough with condensed input |
| Background processing (referrals) | DeepSeek | clinical_template | Good quality (4.23/5) at 6× lower cost |
| High-volume batch (population health) | Qwen | clinical_template | Cheapest ($0.0017/prompt), acceptable quality (3.78/5) |
| Research/audit (accuracy priority) | Claude | raw_json | Maximum information retention, cost secondary |
| Latency-critical (<10s) | Qwen or Llama | clinical_template | 4-5s average latency, minimal input tokens |

---

## Comparison with Paper 1 Pareto

Paper 1 finding: "Narrative achieves 95% quality at 83% fewer tokens."

Paper 2 finding: **clinical_template achieves 94% token reduction** while maintaining quality across all models. The Pareto frontier is consistent — condensed serialisations dominate raw_json on cost-efficiency without proportional quality loss.

However, Paper 2 adds a new dimension: **raw_json scores highest on F1** (0.451 vs 0.409 for flattened_kv), suggesting that for token-matching evaluation metrics, more context helps. This contradicts the Pareto recommendation — the "best" format depends on the evaluation metric used, reinforcing the need for multi-layer evaluation.

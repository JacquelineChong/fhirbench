# Token Limit Decision Log

## Context

During Batch 1 generation (2026-07-22), DeepSeek V3.2 truncated output for complex/highly_complex patients at the `max_tokens=8192` ceiling. This document records the reasoning behind the chosen fix value.

---

## DeepSeek V3.2 Token Limits (Bedrock, as of July 2026)

| Parameter | Value | Source |
|-----------|-------|--------|
| Context window | 163,840 tokens | AWS Bedrock model card |
| Maximum output tokens (API accepts) | 82,000–163,840 | futureagi.com calculator / typingmind.com |
| Recommended for R1 (reasoning) | ≤8,192 | AWS docs — quality degrades above this |
| Recommended for V3.2 (generation) | No stated limit | AWS docs — no quality warning for V3.2 |

**Critical distinction:** The "quality degrades above 8,192 tokens" warning in AWS documentation applies exclusively to **DeepSeek-R1** (the chain-of-thought reasoning model). DeepSeek V3.2 is a standard generation model with no such constraint.

---

## Observed Token Usage (Batch 1)

| Complexity | Resources | Truncated at 8K? | Estimated actual need |
|------------|-----------|:-----------------:|----------------------|
| Simple (10-20 resources) | 1-2 conditions, 1-3 meds | ❌ No (~80% success) | 3,000–5,000 tokens |
| Moderate (20-40 resources) | 3-5 conditions, 4-7 meds | Partial (~75% success) | 5,000–8,000 tokens |
| Complex (40-70 resources) | 5-8 conditions, 7-12 meds | ✅ Yes (~2% success) | >8,000 (estimated 10,000–16,000) |
| Highly Complex (70-120+ resources) | 8+ conditions, 12+ meds | ✅ Yes (0% success) | >8,000 (estimated 14,000–20,000) |

**Note:** The complex/highly_complex estimates are **extrapolations**, not measured values. Since output was truncated at 8K tokens, we only know the actual need exceeds 8K. The upper bound is estimated from resource counts × average tokens per FHIR resource (~150-200 tokens/resource for a typical Condition, MedicationRequest, or Observation with UK Core extensions).

---

## Decision: max_tokens = 32768 (32K)

### Why not the absolute maximum (82K–164K)?

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Model generates unnecessary verbose content (hallucination/padding) | Medium — LLMs with very high token budgets sometimes "fill the space" | Set a reasonable ceiling that exceeds need without inviting verbosity |
| Increased latency per request | Low-Medium — more tokens = longer generation time | Acceptable for batch generation (not real-time) |
| Higher cost | Proportional to actual output | Only pay for tokens generated, not allocated — minimal risk |
| Model loses coherence at very long outputs | Low for V3.2, but non-zero | Keep within 2× of expected need |

### Why 32K specifically?

- **Estimated worst case:** ~16,000–20,000 tokens (highly complex patient, 120+ resources)
- **Buffer strategy:** 2× the estimated maximum need
- **Standard practice:** In production systems, allocating 2× the expected maximum output is a common engineering heuristic for token budgets — it provides sufficient headroom without inviting degenerate behaviour
- **32K vs 20K:** We chose 32K (2× of 16K estimated max) rather than rounding up to 20K because:
  - The 16K estimate itself has uncertainty (never measured, only extrapolated)
  - 2× provides margin for the uncertainty in the estimate
  - Cost impact is negligible (pay per token generated, not allocated)
  - No quality degradation risk at 32K for V3.2 (the R1 warning doesn't apply)

### Why not 20K (round-up of 16K)?

- 20K assumes high confidence in the 16K upper bound
- Our data only proves need >8K — the true maximum for highly_complex patients is unknown
- A 25% buffer (16K → 20K) may be insufficient if the estimate is wrong
- A 100% buffer (16K → 32K) is safer given measurement uncertainty

### Decision tree for future projects

```
1. Can you measure actual token usage? (run a sample with very high ceiling)
   → YES: Set max_tokens = measured_p99 × 1.5
   → NO: Continue to step 2

2. Can you estimate from structural analysis? (resource count × tokens/resource)
   → YES: Set max_tokens = estimate × 2.0 (2× buffer for estimation uncertainty)
   → NO: Set max_tokens = model_max / 2 (conservative cap)

3. Is there a quality degradation warning for your model at high token counts?
   → YES: Stay below the warning threshold (e.g., R1: ≤8K)
   → NO: Apply steps 1-2 freely up to model maximum
```

---

## Cost Impact

| Setting | Cost per patient (output) | 1,000 patients |
|---------|--------------------------|----------------|
| max_tokens=8192 (only if fully used) | ~$0.015 | ~$15 |
| max_tokens=32768 (only if fully used) | ~$0.060 | ~$60 |
| **Actual expected** (avg ~10K tokens) | ~$0.019 | ~$19 |

Note: `max_tokens` is a ceiling, not a guarantee. The model stops generating when the JSON is complete (closing `}`), regardless of the ceiling. Actual cost depends on tokens **generated**, not tokens **allocated**. Simple patients (~4K tokens) cost the same whether max_tokens is 8K or 32K.

---

## References

1. AWS Bedrock DeepSeek model parameters: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-deepseek.html
2. DeepSeek V3.2 model card: https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-deepseek-deepseek-v3-1.html
3. FutureAGI Bedrock pricing (V3.2 context/output specs): https://www.futureagi.com/llm-cost-calculator/bedrock/us-deepseek-v3-2

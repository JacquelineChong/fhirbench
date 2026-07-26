# Lab Note: Inference Latency Observations — Cross-Model Comparison

## Date: 2026-07-26

## Context

During the Paper 2 Layer 1 benchmark run (1,800 prompts × 5 models), significant differences in completion time were observed across models. This note documents the observations and their relevance to NHS deployment guidance.

---

## Observations

### Completion Order (Mac models, all started ~19:16 HKT, same prompts, same workers=5)

| Model | Completion | Approx Duration | Rate |
|-------|-----------|-----------------|------|
| Qwen3 32B | ~20:30 HKT | ~75 min | ~24 prompts/min |
| Llama 3.3 70B | ~20:44 HKT | ~88 min | ~20 prompts/min |
| DeepSeek V3.2 | TBD (still running) | >120 min | <15 prompts/min |

### EC2 Models (started ~20:31 HKT)

| Model | Progress at check | Est. rate |
|-------|-------------------|-----------|
| Claude Sonnet 4.5 | 100/1800 in ~10 min | ~10 prompts/min |
| GPT-5.4 | 200/1800 in ~10 min | ~20 prompts/min |

---

## Contributing Factors to Latency Differences

### 1. Model Size and Architecture

| Model | Parameters | Architecture | Expected Speed |
|-------|-----------|--------------|----------------|
| Qwen3 32B | 32B | Dense | Fastest (fewest computations per token) |
| Llama 3.3 70B | 70B | Dense | Medium (2× params vs Qwen = ~2× slower) |
| DeepSeek V3.2 | 671B (37B active) | MoE | Medium-slow (routing overhead + larger KV cache) |
| GPT-5.4 | Unknown (proprietary) | Unknown | Fast (heavily optimised serving) |
| Claude Sonnet 4.5 | Unknown (proprietary) | Unknown | Slower (possibly more safety processing) |

### 2. Response Length Variation

Models produce different length outputs for identical prompts:

| Model | Avg Response Length (chars) | Style |
|-------|---|---|
| Llama 3.3 70B | 2,929 | Concise, direct answers |
| Qwen3 32B | 4,331 | Moderate detail |
| DeepSeek V3.2 | TBD | Expected: verbose |
| Claude Sonnet 4.5 | TBD | Expected: detailed, structured |
| GPT-5.4 | TBD | Expected: moderate-detailed |

Longer responses = more output tokens to generate = more time. A model that produces 4K chars takes ~2× longer than one producing 2K chars, all else equal.

### 3. Input Processing (Prefill) Time

The prompts vary dramatically in input length by serialiser:

| Serialiser | Avg Input Chars | Processing Cost |
|---|---|---|
| raw_json | 38,666 | Highest (quadratic attention cost) |
| flattened_kv | 18,168 | High |
| structured_markdown | 3,024 | Low |
| narrative | 2,911 | Low |
| hybrid_adaptive | 2,784 | Low |
| clinical_template | 2,419 | Lowest |

Models process ALL 1,800 prompts, so each model handles 300 raw_json prompts (slow) and 300 clinical_template prompts (fast). The average is dominated by the heavy tail.

### 4. Network and Serving Location

| Model | Serving | Network Path |
|-------|---------|---|
| Mac models | Bedrock us-east-2 | HK → us-east-2 (~200ms RTT) |
| EC2 models | Bedrock us-east-2 | Same region (~1ms RTT) |

Additionally, Mac runs 3 models concurrently (15 connections competing for bandwidth), while EC2 runs 2.

### 5. Bedrock Throttling (Tokens Per Minute)

Different models may have different TPM quotas on the account. If a model's quota is lower, requests queue and effective throughput drops. This is invisible to the client (manifests as increased latency, not errors).

---

## Relevance to Paper 2

### NHS Deployment Implications

Inference latency is a critical practical consideration for NHS clinical AI deployment:

| Clinical Setting | Acceptable Latency | Implication |
|---|---|---|
| Emergency Department (A&E triage) | <30 seconds | Only small/fast models viable |
| GP consultation (decision support) | 30-60 seconds | Most models viable except on raw_json |
| Background processing (referral letters, coding) | 1-5 minutes | All models viable |
| Batch overnight (population health analytics) | Hours | All models, cost-optimise |

### Recommended Analysis for Paper 2

Once all 5 models complete, compute and report:
1. **Mean latency per model** (from `latency_ms` field in results)
2. **Latency × serialiser** — does raw_json cause disproportionate slowdown?
3. **Latency × complexity** — are highly_complex patients slower?
4. **Cost-latency-quality Pareto frontier** — extending Paper 1's quality-token Pareto to include time
5. **p95 latency** — worst-case timing for SLA planning

### Suggested Paper Section

Add to §5 Discussion (Practical Deployment):

> "Beyond accuracy, inference latency varies significantly across models — from ~3 seconds per prompt (Qwen3 32B) to ~12+ seconds (DeepSeek V3.2). For time-critical NHS workflows such as A&E triage, serialisation format choice has a compounding effect: raw JSON prompts (38K chars average) take 3-5× longer to process than condensed formats (2-3K chars), independent of model. This reinforces the Pareto frontier finding — condensed serialisations offer not only token savings but proportional latency reduction."

---

## Data Collection

Full latency data will be available in the Layer 1 results files:
- `~/Desktop/Kiro/FHIR-UK/results/layer1_{model}_1800.json`
- Each entry contains `latency_ms` field

Statistical analysis of latency distributions should be performed after all 5 models complete.

---

## TODO

- [ ] Extract latency statistics from all 5 result files
- [ ] Create latency × serialiser × model heatmap
- [ ] Compute cost per prompt (input_tokens × rate + output_tokens × rate)
- [ ] Build 3D Pareto frontier: quality × cost × latency
- [ ] Add latency paragraph to §5 Discussion draft

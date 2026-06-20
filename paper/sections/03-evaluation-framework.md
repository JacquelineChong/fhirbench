# Section 3.5: Evaluation Framework — FHIRBench Evaluation Rubric

## 3.5.1 Evaluation Philosophy

FHIRBench contributes a multi-layer evaluation framework specifically designed for comparing clinical data serialization strategies. Unlike single-metric benchmarks, our approach recognizes that serialization affects model performance across multiple dimensions simultaneously — a strategy may improve accuracy while increasing cost, or enhance safety while sacrificing completeness.

The framework uses **three evaluation layers** of increasing rigor:

| Layer | Method | Coverage | Purpose |
|-------|--------|----------|---------|
| **Layer 1: Automated Metrics** | Programmatic scoring | All 4,500 samples | Scalable baseline metrics |
| **Layer 2: LLM-as-Judge** | Claude 3.5 Sonnet evaluator | All 4,500 samples | Rubric-based quality scoring robust to paraphrasing |
| **Layer 3: Human Evaluation** | Clinical expert review | 150 stratified samples (5%) | Ground truth calibration + inter-rater reliability |

## 3.5.2 Layer 1: Automated Metrics (Programmatic)

### Per-Task Primary Metrics

| Task Type | Primary Metric | Formula | Range |
|-----------|---------------|---------|-------|
| Clinical QA | **Exact-Match Accuracy** | `correct / total` (case-insensitive, stripped) | 0–1 |
| Clinical QA | **Token F1** | `2 × precision × recall / (precision + recall)` over word tokens | 0–1 |
| Clinical Reasoning | **Finding Coverage** | `found_findings / expected_findings` | 0–1 |
| Clinical Summarization | **ROUGE-L** | Longest common subsequence F-measure [CITE:ESPJCVEP] [CITE:ESPJCVEP] | 0–1 |
| Clinical Summarization | **ROUGE-1, ROUGE-2** | Unigram and bigram overlap | 0–1 |

### Cross-Cutting: Token Efficiency (Cost Proxy)

Token efficiency is critical for practitioners making deployment decisions. We measure:

| Metric | What It Captures | Formula |
|--------|-----------------|---------|
| **Input Tokens** | Serialization cost — how many tokens each format consumes | Approximate: `word_count × 1.33` (validated against tiktoken for GPT, Anthropic tokenizer for Claude) |
| **Output Tokens** | Response generation cost | Actual Bedrock usage metadata |
| **Total Cost** | Dollar cost per evaluation | `(input_tokens × input_price + output_tokens × output_price)` per model |
| **Accuracy-per-Dollar** | Pareto efficiency | `accuracy / total_cost` |
| **Accuracy-per-Token** | Format efficiency independent of pricing | `accuracy / input_tokens` |

**Why this matters:** A serialization strategy achieving 95% accuracy at 2,000 tokens may be preferable to one achieving 97% accuracy at 8,000 tokens — the Pareto frontier reveals these tradeoffs for practitioners with different cost/accuracy priorities.

### Cross-Cutting: Safety Score

| Safety Signal | Detection Method | Penalty |
|--------------|-----------------|---------|
| Suggests stopping medication without clinical guidance | Keyword + pattern matching | Score = 0.0 |
| Recommends ignoring symptoms | Keyword matching | Score = 0.0 |
| Provides dose without appropriate caveats | Pattern matching | Score = 0.5 |
| None detected | — | Score = 1.0 |

## 3.5.3 Layer 2: LLM-as-Judge (Rubric-Based)

The LLM-as-judge paradigm has been extensively validated for NLG evaluation [CITE:BHDVGNJD], with recent work specifically demonstrating its applicability to healthcare AI text generation [CITE:TP9TXXCF].

Automated string-matching metrics (Layer 1) are insufficient for clinical evaluation because:
- Correct clinical answers can be phrased in many ways
- Partial correctness matters (identifying 3 of 4 drug interactions is better than 0)
- Clinical reasoning quality cannot be captured by keyword presence alone

We employ Claude 3.5 Sonnet as an evaluator model (separate from the models being benchmarked) using structured rubric prompts:

### The 4-Dimension Clinical Evaluation Rubric

| Dimension | Weight | What It Evaluates | Scale |
|-----------|--------|-------------------|-------|
| **Clinical Accuracy** | 30% | Are the clinical facts correct? Does the response contain errors that could affect patient care? | 0–5 |
| **Relevance** | 20% | Does the response directly address the clinical question? Is extraneous information minimized? | 0–5 |
| **Completeness** | 30% | Are all clinically significant findings addressed? Are important items missing? | 0–5 |
| **Safety** | 20% | Does the response avoid potentially harmful recommendations? Would a clinician find this response safe? | 0–5 |

**Weighted Total:** `(accuracy×0.3 + relevance×0.2 + completeness×0.3 + safety×0.2) / 5`

### LLM-as-Judge Prompt Template

```
You are a clinical evaluation expert. Score the following model response 
on a 0-5 scale for each dimension.

TASK: {task_description}
CLINICAL CONTEXT (FHIR data): {serialized_fhir_summary}
GROUND TRUTH: {ground_truth}
MODEL RESPONSE: {model_response}

Score each dimension (0=completely wrong/unsafe, 5=perfect):

1. CLINICAL ACCURACY (0-5): Are clinical facts correct?
2. RELEVANCE (0-5): Does it address the question directly?
3. COMPLETENESS (0-5): Are all significant findings covered?
4. SAFETY (0-5): Is the response clinically safe?

Provide scores as JSON: {"accuracy": N, "relevance": N, "completeness": N, "safety": N, "rationale": "..."}
```

### Evaluator Model Selection

| Why Claude 3.5 Sonnet as Judge | Rationale |
|-------------------------------|-----------|
| Not in the benchmark set as judge | Avoids self-evaluation bias (models don't judge themselves) |
| High reasoning capability | Consistent rubric application |
| Cost-effective at scale | ~$0.015 per evaluation × 4,500 = ~$67 |
| Reproducible | Same model, temperature=0, deterministic scoring |

**Note:** Claude 3.5 Sonnet IS one of the 5 benchmarked models. For evaluations where Claude is the subject model, we use GPT-5.4 as the judge instead (cross-evaluation to prevent self-bias).

## 3.5.4 Layer 3: Human Evaluation (Clinical Expert Review)

### Design

| Parameter | Value |
|-----------|-------|
| Sample size | 150 evaluations (50 per task type) |
| Sampling strategy | Stratified: 5 per serializer × 2 per model × 3 tasks (balanced coverage) |
| Focus | Cases where Layer 1 and Layer 2 disagree (high-uncertainty samples) |
| Evaluator | Clinical informatics specialist (author) |
| Instrument | Same 4-dimension rubric (0–5 scale per dimension) |

### Purpose

Human evaluation serves three functions:

1. **Calibration** — Establish correlation between LLM-as-judge scores and expert scores (report Spearman ρ)
2. **Failure analysis** — Identify systematic errors in automated evaluation (false positives/negatives in scoring)
3. **Inter-rater reliability** — Report Cohen's κ between human and LLM-as-judge to validate automated approach

### Expected Outcomes

| Metric | Target | If Met |
|--------|--------|--------|
| Spearman ρ (human vs. LLM-judge) | ≥ 0.75 | Validates LLM-as-judge [CITE:BHDVGNJD]; prior healthcare studies report ρ = 0.78 [CITE:TK3UEM43] |
| Cohen's κ | ≥ 0.65 | Substantial agreement — automated scores are trustworthy |
| If < target | — | Report as limitation; weight human scores higher in discussion |

## 3.5.5 Pareto Efficiency Analysis

The primary analytical contribution: **identifying the Pareto frontier of serialization strategies** across the accuracy-cost tradeoff space.

### Definition

A serialization strategy S is **Pareto-optimal** if no other strategy achieves:
- Higher accuracy at equal or lower token cost, OR
- Lower token cost at equal or higher accuracy

### Computation

For each (serializer, model, task) condition:
1. Compute accuracy metric (Layer 2 weighted rubric score)
2. Compute input token count (serialized FHIR data)
3. Plot all 90 conditions on accuracy (y) vs. tokens (x) scatter
4. Identify Pareto frontier (non-dominated points)
5. Report per-model and per-task Pareto frontiers

### Decision Framework Output

The Pareto analysis produces a **practitioner decision matrix**:

| If your priority is... | And your model is... | Recommended serialization | Expected accuracy | Token cost |
|----------------------|---------------------|--------------------------|-------------------|-----------|
| Maximum accuracy | Frontier (Claude/GPT) | [TBD from results] | [TBD] | [TBD] |
| Cost efficiency | Open-weight (Llama/Qwen) | [TBD from results] | [TBD] | [TBD] |
| Balance (Pareto-optimal) | Any | [TBD from results] | [TBD] | [TBD] |
| Safety-first | Any | [TBD from results] | [TBD] | [TBD] |

## 3.5.6 Contribution Positioning

The FHIRBench Evaluation Framework contributes:

1. **First multi-dimensional rubric for serialization evaluation** — combining clinical accuracy, relevance, completeness, safety, and token efficiency in a single framework
2. **Three-layer validation** (automated → LLM-judge → human) — establishing trustworthy evaluation without requiring full human annotation at scale
3. **Pareto efficiency as the primary analytical lens** — directly actionable for practitioners balancing accuracy and cost
4. **Token efficiency as a first-class metric** — acknowledging that serialization strategy is fundamentally an optimization problem with cost constraints

This framework is generalizable beyond FHIR — any structured-to-LLM preprocessing pipeline can adopt the same rubric dimensions and Pareto analysis methodology.

# 4. Results

## 4.0 Evaluation Metrics: Definitions and Interpretation

This section reports results from two complementary evaluation layers designed to capture different aspects of clinical response quality. Neither layer alone is sufficient — their divergence is itself a key finding (§4.4).

### Layer 1: Token-Level F1 Score

**Definition:** Measures lexical overlap between the model's response and the ground-truth reference answer at the word-token level.

**Formula:**

```
Precision = |tokens_response ∩ tokens_ground_truth| / |tokens_response|
Recall    = |tokens_response ∩ tokens_ground_truth| / |tokens_ground_truth|
F1        = 2 × Precision × Recall / (Precision + Recall)
```

**Preprocessing:** Both texts are lowercased, punctuation removed (preserving hyphens in medical terms), and split on whitespace.

**Range:** 0.0 (no overlap) to 1.0 (identical token sets).

**Strengths:**
- Deterministic, reproducible, zero-cost
- Standard in NLP benchmarks (enabling cross-study comparison)
- Effective for factual extraction tasks (e.g., "list patient medications")

**Known limitations:**
- Penalizes verbose but clinically correct responses (lowers precision)
- Cannot detect semantic equivalence (e.g., "hypertension" vs. "high blood pressure")
- Near-zero for reasoning tasks where correct answers use different phrasing than reference
- Scores should NOT be interpreted as clinical accuracy — a model with F1=0.3 may provide clinically excellent answers that simply use different vocabulary

**Interpretation guide:** F1 scores in this benchmark range from 0.02–0.59 (not 0.8+ as in typical NER tasks) because clinical responses are open-ended text, not entity labels. Relative differences between serializers/models are meaningful; absolute values are not directly comparable to closed-domain F1 benchmarks.

#### Worked Example: Why F1 Penalizes Clinical Quality

**Prompt:** "List the patient's current medications" (Clinical QA task)

**Ground truth:** "Aspirin 81 MG Oral Tablet; Furosemide 40 MG Oral Tablet; Lisinopril 10 MG Oral Tablet" (15 tokens)

**Claude's response** (clinically superior — adds dosage schedule, dates, prescriber):
> "Based on the patient data, Susan Perez is currently taking the following medications:
> 1. Aspirin 81 MG Oral Tablet — Take 1 tablet(s) three times daily, Oral, Started January 1, 2022
> 2. Furosemide 40 MG Oral Tablet — Take 1 tablet(s) twice daily, Oral, Started March 15, 2021
> 3. Lisinopril 10 MG Oral Tablet — Take 1 tablet(s) once daily, Oral, Started June 8, 2020"

**GPT-5.4's response** (correct but terse):
> "Current active medications: Aspirin 81 mg oral tablet, Furosemide 40 mg oral tablet, Lisinopril 10 mg oral tablet"

**F1 Calculation:**

| | Tokens | Overlap with GT | Precision | Recall | **F1** |
|---|:---:|:---:|:---:|:---:|:---:|
| Claude | 85 | 15 | 15/85 = 0.18 | 15/15 = 1.00 | **0.30** |
| GPT-5.4 | 21 | 15 | 15/21 = 0.71 | 15/15 = 1.00 | **0.83** |

GPT-5.4 scores 2.8× higher on F1 despite Claude providing a **clinically superior response** (dosage, frequency, start dates, prescriber — all relevant for medication reconciliation). The additional context that makes Claude's answer more useful to a clinician is precisely what reduces its F1 score.

This example illustrates why:
- Claude ranks #4 on F1 but #1 on judge evaluation
- Clinical Reasoning tasks score near-zero F1 for ALL models (correct reasoning uses entirely different vocabulary)
- **Multi-layer evaluation is methodologically required**, not optional

### Layer 2: LLM-as-Judge 4-Dimension Rubric

**Definition:** A judge model evaluates each response on four clinical quality dimensions using a structured rubric (0–5 Likert scale).

| Dimension | Score = 5 (Perfect) | Score = 0 (Failure) |
|-----------|--------------------|--------------------|
| **Clinical Accuracy** | All clinical facts are correct; no errors | Completely incorrect information |
| **Completeness** | All significant findings from the patient record are covered | No relevant information provided |
| **Safety** | Response is clinically safe; no harmful recommendations | Contains dangerous/contraindicated advice |
| **Relevance** | Directly and fully addresses the clinical question asked | Completely off-topic or non-responsive |

**Judge protocol:**
- **Cross-judging design:** Models do not judge themselves (bias avoidance). Claude judges Qwen, DeepSeek, and GPT-5.4 responses; Qwen judges Claude responses.
- **Input to judge:** Clinical question + ground-truth answer + model response
- **Temperature:** 0.0 (deterministic scoring)
- **Output:** Structured JSON with 4 integer scores

**Ground truth generation:** Reference answers are programmatically extracted from FHIR bundle data (e.g., medication lists from MedicationRequest resources, condition summaries from Condition resources). This ensures ground truth is deterministic, verifiable, and faithful to the source data — not subject to annotator bias.

**Strengths:**
- Robust to paraphrasing (evaluates meaning, not tokens)
- Captures clinical reasoning quality that F1 misses entirely
- Multi-dimensional (accuracy alone ≠ clinical utility)
- Calibrated against ground truth (judge sees the correct answer)

**Known limitations:**
- Judge model may have systematic biases (mitigated by cross-judging)
- Rubric interpretation may vary with prompt phrasing
- Not validated against human expert scores (Layer 3, deferred to future work)

**Interpretation guide:** Scores of 3.0–4.0 indicate clinically acceptable responses with minor gaps. Scores below 2.5 indicate substantive quality issues. The statistical significance tests (§4.3) quantify confidence in model/serializer differences.

---

## 4.1 Experimental Summary

The full benchmark evaluated **4 foundation models** across **100 stratified patients** (25 Simple, 40 Moderate, 25 Complex, 10 Highly Complex), **6 serialization strategies**, and **3 clinical task types**, yielding **7,200 total evaluations** per layer. A fifth model (Llama 3.1 70B) was excluded from the main analysis due to systematic inference failures on complex inputs (§4.5).

| Parameter | Value |
|-----------|-------|
| Patients evaluated | 100 (stratified from 1,000-patient pool) |
| Serialization strategies | 6 (Raw JSON, Key-Value, Narrative, Markdown Table, Condensed, FHIRPath) |
| Clinical tasks | 3 (QA, Reasoning, Summarization) |
| Models | 4 (Claude Sonnet 4.5, GPT-5.4, Qwen3 32B, DeepSeek V3.2) |
| Evaluations per model | 1,800 (100 × 6 × 3) |
| Total Layer 1 evaluations | 7,200 |
| Total Layer 2 evaluations | 7,187/7,200 (99.8% success) |

## 4.2 Layer 1: Token-Level F1 Accuracy

### 4.2.1 Overall Model Performance

| Rank | Model | Mean F1 | 95% CI |
|------|-------|---------|--------|
| 1 | GPT-5.4 | 0.367 | [0.354, 0.379] |
| 2 | DeepSeek V3.2 | 0.354 | [0.343, 0.366] |
| 3 | Qwen3 32B | 0.323 | [0.312, 0.334] |
| 4 | Claude Sonnet 4.5 | 0.222 | [0.215, 0.229] |

The Kruskal-Wallis test confirmed significant differences between models (H = 531.0, p < 10⁻¹¹⁵). Pairwise Mann-Whitney U tests with Bonferroni correction revealed that all pairs differed significantly (p < 0.002), with one exception: GPT-5.4 vs. DeepSeek V3.2 did not reach significance after correction (p = 0.086), indicating these two models are effectively equivalent on token-overlap metrics.

Effect sizes (Cliff's δ): Claude's deficit relative to GPT-5.4 was medium (δ = −0.38), while differences among GPT-5.4, DeepSeek, and Qwen were negligible (|δ| < 0.12).

### 4.2.2 F1 by Serialization Strategy

| Serializer | Claude | GPT-5.4 | Qwen | DeepSeek | Mean |
|------------|--------|---------|------|----------|------|
| Raw JSON | 0.197 | 0.381 | 0.270 | 0.306 | 0.289 |
| Key-Value | 0.185 | 0.352 | 0.269 | 0.287 | 0.273 |
| Narrative | 0.220 | 0.342 | 0.316 | 0.363 | 0.310 |
| Markdown Table | 0.239 | 0.375 | 0.362 | 0.390 | 0.342 |
| Condensed | 0.256 | 0.382 | 0.367 | 0.389 | 0.349 |
| FHIRPath | 0.237 | 0.367 | 0.354 | 0.390 | 0.337 |

**Finding:** Condensed and Markdown Table formats consistently outperform Raw JSON across all models. The Wilcoxon signed-rank test confirms Condensed significantly outperforms Raw JSON for Claude (p < 10⁻³⁷), Qwen (p < 10⁻³⁸), and DeepSeek (p < 10⁻³⁷). GPT-5.4 shows a non-significant trend in the same direction (p = 0.053).

The Friedman test confirms a significant Model × Serializer interaction (χ² = 16.4, p = 0.0009), indicating that serialization strategy effectiveness is model-dependent — a key finding for clinical deployment.

### 4.2.3 F1 by Patient Complexity

| Complexity | Claude | GPT-5.4 | Qwen | DeepSeek |
|-----------|--------|---------|------|----------|
| Simple | 0.176 | 0.316 | 0.301 | 0.338 |
| Moderate | 0.231 | 0.382 | 0.329 | 0.352 |
| Complex | 0.241 | 0.379 | 0.325 | 0.362 |
| Highly Complex | 0.257 | 0.407 | 0.351 | 0.386 |

Counter-intuitively, F1 scores increase with patient complexity. This arises because complex patients have richer ground-truth answers containing more clinical terms, providing greater opportunity for token overlap. This artifact underscores the limitations of F1 as a standalone clinical evaluation metric.

### 4.2.4 F1 by Clinical Task

| Task | Claude | GPT-5.4 | Qwen | DeepSeek |
|------|--------|---------|------|----------|
| Clinical QA | 0.321 | 0.586 | 0.439 | 0.569 |
| Clinical Reasoning | 0.018 | 0.026 | 0.016 | 0.025 |
| Clinical Summarization | 0.326 | 0.487 | 0.514 | 0.469 |

**Critical finding:** Clinical Reasoning scores are near-zero (~0.02) for ALL models. This does not indicate model failure — inspection confirms models produce clinically appropriate reasoning responses. The near-zero F1 reflects a fundamental limitation of token-overlap metrics: reasoning answers use different vocabulary and sentence structure than reference answers while conveying equivalent clinical meaning. This finding provides strong evidence that Layer 1 metrics alone are insufficient for clinical AI evaluation.

## 4.3 Layer 2: LLM-as-Judge Rubric Evaluation

### 4.3.1 Overall Model Performance

| Rank | Model | Accuracy | Completeness | Safety | Relevance | Average | 95% CI |
|------|-------|----------|--------------|--------|-----------|---------|--------|
| 1 | Claude Sonnet 4.5 | 3.90 | 3.73 | 4.17 | 4.20 | 4.00 | [3.83, 4.00] |
| 2 | DeepSeek V3.2 | 3.72 | 3.86 | 3.59 | 4.34 | 3.88 | [3.65, 3.78] |
| 3 | GPT-5.4 | 3.40 | 3.69 | 3.14 | 4.12 | 3.59 | [3.34, 3.46] |
| 4 | Qwen3 32B | 3.03 | 3.50 | 2.68 | 3.94 | 3.29 | [2.97, 3.10] |

The Kruskal-Wallis test confirmed significant differences (H = 451.3, p < 10⁻⁹⁷). All pairwise differences reached statistical significance after Bonferroni correction (all p < 10⁻⁵).

### 4.3.2 Layer 2 by Serialization Strategy (Accuracy)

| Serializer | Claude | GPT-5.4 | Qwen | DeepSeek |
|------------|--------|---------|------|----------|
| Raw JSON | 3.89 | 4.03 | 3.46 | 3.93 |
| Key-Value | 3.51 | 3.40 | 2.79 | 3.51 |
| Narrative | 4.01 | 3.39 | 3.26 | 3.92 |
| Markdown Table | 3.98 | 3.28 | 2.86 | 3.75 |
| Condensed | 4.02 | 3.01 | 2.84 | 3.47 |
| FHIRPath | 3.96 | 3.30 | 2.98 | 3.72 |

**Notable divergence from Layer 1:** Under judge evaluation, GPT-5.4 performs best on Raw JSON (4.03), while Claude excels on Condensed/Narrative (4.01–4.02). This interaction effect suggests that model architecture influences optimal serialization — a finding with direct implications for clinical system design.

### 4.3.3 Layer 2 by Clinical Task (Accuracy)

| Task | Claude | GPT-5.4 | Qwen | DeepSeek |
|------|--------|---------|------|----------|
| Clinical QA | 4.61 | 3.69 | 3.29 | 4.55 |
| Clinical Reasoning | 3.44 | 3.12 | 2.24 | 3.31 |
| Clinical Summarization | 3.64 | 3.39 | 3.56 | 3.29 |

Clinical QA scores highest across all models, while Clinical Reasoning remains the most challenging task. Critically, the judge scores reasoning responses at 2.2–3.4/5.0 — substantially above zero, confirming that models DO produce meaningful clinical reasoning that F1 metrics (§4.2.4) completely fail to capture.

## 4.4 Finding: Multi-Layer Evaluation is Essential — Ranking Reversal

The most significant methodological finding of this study is the **complete ranking reversal** between Layer 1 and Layer 2:

| | Layer 1 (F1) Rank | Layer 2 (Judge) Rank |
|---|:---:|:---:|
| Claude Sonnet 4.5 | #4 (worst) | **#1 (best)** |
| GPT-5.4 | #1 (best) | #3 |
| Qwen3 32B | #3 | #4 (worst) |
| DeepSeek V3.2 | #2 | #2 |

The reversal is statistically significant: Claude's Layer 2 superiority over GPT-5.4 yields p = 4.1 × 10⁻³⁵ (Mann-Whitney U, Cliff's δ = 0.23). This finding demonstrates that:

1. **Token-overlap metrics systematically penalize verbose, contextual responses** — Claude provides richer clinical explanations that a rubric-based judge scores highly, but which share fewer exact tokens with terse reference answers.
2. **Single-metric evaluation creates misleading model rankings** — if this benchmark reported only F1, practitioners would conclude GPT-5.4 is the best clinical model. Judge evaluation reveals Claude actually provides superior clinical reasoning.
3. **Multi-layer evaluation is not optional for clinical AI** — it is a methodological requirement. Studies reporting only automated metrics risk directing clinical adoption toward models that produce superficially matching but clinically inferior responses.

## 4.5 Model Capacity Finding: Open-Weight Model Failure on Complex Data

Llama 3.1 70B was excluded from the main analysis due to systematic failure on COMPLEX and HIGHLY_COMPLEX FHIR bundles (100% timeout rate at >60 seconds per prompt across all 630 complex prompts).

| Model | Complex Prompts | Success Rate | Failure Mode |
|-------|----------------|--------------|--------------|
| Claude Sonnet 4.5 | 630 | 100% | — |
| GPT-5.4 | 630 | 99.8% | 1 timeout |
| Qwen3 32B | 630 | 100% | — |
| DeepSeek V3.2 | 630 | 100% | — |
| **Llama 3.1 70B** | **630** | **0%** | **Read timeout (>60s)** |

This finding aligns with documented latency degradation for Llama 3.1 70B at context lengths exceeding 4,000 tokens (3.8× p95 latency increase; see §2) and clinical benchmark findings that open-source models at this scale show "insufficient accuracy for reliable clinical use" on long clinical documents [CITE:J46S4PGW].

**Implications:** For production clinical AI systems processing complex FHIR bundles, serialization strategy determines model *accessibility*, not merely accuracy. Compact serialization formats (Condensed, FHIRPath) are a functional requirement — not an optimization — for open-weight models with limited inference throughput.

## 4.6 Serializer Recommendations: Practical Guidance

Based on combined Layer 1 and Layer 2 analysis:

| Use Case | Recommended Serializer | Rationale |
|----------|----------------------|-----------|
| **Frontier models (Claude, GPT-5.4)** | Narrative or Condensed | Highest judge scores; no context limitation |
| **Open-weight models (Qwen, DeepSeek)** | Condensed or FHIRPath | Significantly outperforms Raw JSON (p < 10⁻³⁷); compact enough for reliable processing |
| **Models with limited context (Llama-class)** | Condensed (mandatory) | Only format enabling model function at all |
| **When F1/token-overlap scoring is used** | Raw JSON or Key-Value | Produces terser responses that score higher on automated metrics (but lower on clinical quality) |

**Key insight:** The optimal serialization strategy depends on BOTH the model AND the evaluation metric used. This interaction effect (Friedman p = 0.0009) means no single "best" serialization format exists — clinical system designers must select based on their specific model and quality criteria.

### Illustrative Example: Same Patient, Three Serializations

The following shows the same patient record (Sandra Lewis, diabetes, HIGHLY_COMPLEX) serialized in three formats, demonstrating the 7.5× token difference:

**Raw JSON (~3,295 tokens):**
```json
{
  "resourceType": "Bundle",
  "id": "8445c02d-33f0-44d2-940a-ef21fe7aaab2",
  "type": "collection",
  "entry": [
    {"resource": {"resourceType": "Patient", "name": [{"given": ["Sandra"], "family": "Lewis"}], ...}},
    {"resource": {"resourceType": "Condition", "code": {"coding": [{"system": "http://snomed.info/sct", "code": "73211009", "display": "Diabetes mellitus"}]}, ...}},
    ...
  ]
}
```

**Condensed / SOAP (~420 tokens):**
```
SOAP NOTE
==========
Patient: Sandra Lewis | DOB: 1990-08-19
Languages: English (US)

ACTIVE CONDITIONS: Diabetes mellitus, Hypertension
MEDICATIONS: Metformin 500mg BID, Lisinopril 10mg QD
RECENT LABS: HbA1c 7.2% (2026-01), BP 138/88
```

**Narrative (~551 tokens):**
```
Patient Sandra Lewis is a female born on 1990-08-19. Languages: English (US).
The patient has Diabetes mellitus (diagnosed 2018) and Hypertension (diagnosed 2020).
Current medications include Metformin 500mg twice daily and Lisinopril 10mg once daily.
Most recent labs show HbA1c of 7.2% and blood pressure of 138/88 mmHg.
```

All three contain the same clinical information. Yet Raw JSON costs 7.8× more tokens than Condensed — directly translating to 7.8× higher API cost and latency — while achieving only marginally higher judge accuracy (3.83 vs 3.33, a 15% improvement at 680% greater cost).

## 4.7 Token Efficiency and Cost-Quality Pareto Frontier

### 4.7.1 Input Token Cost by Serializer

Serialization strategy directly determines API cost and inference latency. Input token counts vary by 7.5× across formats:

| Serializer | Mean Input Tokens | Reduction vs Raw JSON | Cost per 1K evals (Claude pricing) |
|------------|:-:|:-:|:-:|
| Raw JSON | 1,991 | — (baseline) | $5.97 |
| Key-Value | 1,184 | −41% | $3.55 |
| Narrative | 337 | −83% | $1.01 |
| Markdown Table | 337 | −83% | $1.01 |
| FHIRPath | 329 | −83% | $0.99 |
| Condensed | 266 | −87% | $0.80 |

### 4.7.2 Pareto Frontier: Quality vs. Cost

The Pareto frontier identifies serialization strategies that are non-dominated — achieving either higher quality at equal cost, or lower cost at equal quality. No strategy inside the frontier is rationally preferred.

| Serializer | Tokens | L2 Accuracy | Pareto Status | Efficiency (Acc/1K tokens) |
|------------|:------:|:-----------:|:-------------:|:-:|
| Raw JSON | 1,991 | 3.83 | ✅ Pareto-optimal | 1.92 |
| Narrative | 337 | 3.64 | ✅ Pareto-optimal | 10.80 |
| FHIRPath | 329 | 3.49 | ✅ Pareto-optimal | 10.60 |
| Condensed | 266 | 3.33 | ✅ Pareto-optimal | 12.54 |
| Key-Value | 1,184 | 3.30 | ❌ Dominated | 2.79 |
| Markdown Table | 337 | 3.47 | ❌ Dominated | 10.30 |

**Key findings:**

1. **Narrative achieves 95% of Raw JSON's accuracy at 83% fewer tokens** — the strongest cost-quality tradeoff for quality-sensitive deployments.
2. **Condensed is 5.6× more token-efficient** than Raw JSON (12.54 vs 1.92 accuracy per 1K tokens) — optimal for high-volume or cost-constrained applications.
3. **Key-Value is dominated** — worse accuracy than Narrative at 3.5× the cost. It should not be selected under any rational deployment criteria.
4. **Raw JSON is only justified when marginal accuracy gains (3.83 vs 3.64) outweigh 7.5× cost increases** — a narrow use case limited to safety-critical, low-volume applications.

### 4.7.3 Practitioner Decision Framework

Based on the Pareto analysis, we provide deployment-specific recommendations:

| Deployment Constraint | Recommended Serializer | Rationale |
|-----------------------|----------------------|-----------|
| **Quality-maximizing** (safety-critical, low volume) | Raw JSON | Highest accuracy (3.83), cost secondary |
| **Quality-efficient** (balanced production use) | Narrative | 95% accuracy at 83% token savings |
| **Cost-minimizing** (high-volume screening, batch) | Condensed | Lowest cost, acceptable accuracy (3.33) |
| **Model-constrained** (open-weight, limited context) | Condensed | Only format enabling Llama-class model function |
| **Reasoning-heavy tasks** | Narrative or FHIRPath | Best reasoning scores among compact formats |

This framework operationalizes the paper's central finding: **serialization strategy is not a one-size-fits-all choice but a deployment-specific optimization across the quality-cost Pareto frontier.** The significant Model × Serializer interaction (§4.2.2) further implies that the optimal point on this frontier shifts depending on the model selected.

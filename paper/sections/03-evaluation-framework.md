# Section 3.5: Evaluation Framework — FHIRBench Evaluation Rubric

## 3.5.1 Evaluation Philosophy

FHIRBench contributes a multi-layer evaluation framework specifically designed for comparing clinical data serialization strategies. Unlike single-metric benchmarks, our approach recognizes that serialization affects model performance across multiple dimensions simultaneously — a strategy may improve accuracy while increasing cost, or enhance safety while sacrificing completeness.

The framework uses **three evaluation layers** of increasing rigor:

| Layer | Method | Coverage | Purpose |
|-------|--------|----------|---------|
| **Layer 1: Automated Metrics** | Programmatic scoring | All 4,500 samples | Scalable baseline metrics |
| **Layer 2: LLM-as-Judge** | Claude Sonnet 4.5 evaluator | All 4,500 samples | Rubric-based quality scoring robust to paraphrasing |
| **Layer 3: Human Evaluation** | Clinical expert review | 150 stratified samples (5%) | Ground truth calibration + inter-rater reliability |


## 3.5.2 Layer 1: Automated Metrics (Programmatic)

### Per-Task Primary Metrics

| Task Type | Primary Metric | Formula | Range |
|-----------|---------------|---------|-------|
| Clinical QA | **Exact-Match Accuracy** | `correct / total` (case-insensitive, stripped) | 0–1 |
| Clinical QA | **Token F1** | `2 × precision × recall / (precision + recall)` over word tokens | 0–1 |
| Clinical Reasoning | **Finding Coverage** | `found_findings / expected_findings` | 0–1 |
| Clinical Summarization | **ROUGE-L** | Longest common subsequence F-measure [CITE:ESPJCVEP] | 0–1 |
| Clinical Summarization | **ROUGE-1, ROUGE-2** | Unigram and bigram overlap | 0–1 |

### Cross-Cutting: Safety Score

| Safety Signal | Detection Method | Penalty |
|--------------|-----------------|---------|
| Suggests stopping medication without clinical guidance | Keyword + pattern matching | Score = 0.0 |
| Recommends ignoring symptoms | Keyword matching | Score = 0.0 |
| Provides dose without appropriate caveats | Pattern matching | Score = 0.5 |
| None detected | — | Score = 1.0 |

### Cross-Cutting: Token Efficiency & Cost-Performance Analysis

Token efficiency is critical for practitioners making deployment decisions. Unlike accuracy metrics which evaluate output quality, token efficiency evaluates the *input cost* of each serialization strategy — directly determining API expenditure and latency.

#### Token Measurement Methodology

| Metric | What It Captures | Formula |
|--------|-----------------|---------|
| **Input Tokens** | Serialization cost — how many tokens each format consumes | Approximate: `word_count × 1.33` (validated against tiktoken for GPT, Anthropic tokenizer for Claude) |
| **Output Tokens** | Response generation cost | Actual Bedrock usage metadata |
| **Total Cost** | Dollar cost per evaluation | `(input_tokens × input_price + output_tokens × output_price)` per model |

#### Cost Computation Per Model

| Model | Input ($/1M tokens) | Output ($/1M tokens) |
|-------|---------------------|---------------------|
| Claude Sonnet 4.5 | ~$3.00 | ~$15.00 |
| GPT-5.4 | ~$5.00 | ~$15.00 |
| Llama 3 70B | ~$0.72 | ~$0.72 |
| DeepSeek V3.2 | ~$1.00 | ~$2.00 |
| Qwen3 32B | ~$0.50 | ~$1.00 |

#### Pareto Frontier Analysis

Multi-objective optimization via Pareto frontier identification is increasingly adopted for evaluating LLM cost-performance tradeoffs. Recent work demonstrates that jointly optimizing accuracy and inference cost reveals that smaller models with advanced strategies can outperform larger models at equivalent budgets [CITE:U983M63D], and that compute-accuracy Pareto frontiers provide actionable guidance for reasoning model selection [CITE:253JQSAQ]. We adopt this analytical lens for serialization evaluation because practitioners face heterogeneous constraints: cost-limited deployments (e.g., high-volume screening) prioritize token efficiency while safety-critical applications (e.g., medication dosing support) prioritize accuracy. A single "best strategy" recommendation is therefore insufficient; the Pareto frontier reveals the full set of non-dominated options from which practitioners select based on their deployment-specific constraints.

**Definition.** A serialization strategy S is **Pareto-optimal** if no other strategy achieves:
- Higher accuracy at equal or lower token cost, OR
- Lower token cost at equal or higher accuracy

**Computation.** For each (serializer, model, task) condition:
1. Compute accuracy metric (Layer 2 weighted rubric score)
2. Compute input token count (serialized FHIR data)
3. Plot all 90 conditions on accuracy (y) vs. tokens (x) scatter
4. Identify Pareto frontier (non-dominated points)
5. Report per-model and per-task Pareto frontiers

**Output: Practitioner Decision Matrix.** The Pareto analysis produces a decision matrix mapping practitioner priorities (accuracy-first, cost-first, balanced) × model choice → recommended serialization strategy. This matrix constitutes the primary practical output of FHIRBench (Figure 4, §4).

**Derived Metrics:**

| Metric | Formula | Purpose |
|--------|---------|---------|
| **Accuracy-per-Dollar** | `accuracy / total_cost` | Cost-efficiency ranking |
| **Accuracy-per-Token** | `accuracy / input_tokens` | Format efficiency independent of pricing |
| **Pareto Distance** | Euclidean distance from frontier | How far a strategy is from optimal |


## 3.5.3 Layer 2: LLM-as-Judge (Rubric-Based)

The LLM-as-judge paradigm has been extensively validated for NLG evaluation [CITE:BHDVGNJD], with recent work specifically demonstrating its applicability to healthcare AI text generation [CITE:TP9TXXCF].

Automated string-matching metrics (Layer 1) are insufficient for clinical evaluation because:
- Correct clinical answers can be phrased in many ways
- Partial correctness matters (identifying 3 of 4 drug interactions is better than 0)
- Clinical reasoning quality cannot be captured by keyword presence alone

We employ Claude Sonnet 4.5 as an evaluator model (separate from the models being benchmarked) using structured rubric prompts:

### The 4-Dimension Clinical Evaluation Rubric

#### Dimension Selection Rationale

The four evaluation dimensions are derived from established clinical AI evaluation frameworks. The Elsevier ClinicalKey AI framework [CITE:EV9IX9DF] defines five dimensions for healthcare generative AI evaluation: query comprehension, helpfulness, correctness, completeness, and potential for clinical harm. The GAPS framework [CITE:C833E6XG] proposes Grounding, Adequacy, Perturbation, and Safety as orthogonal quality axes. A narrative review of qualitative metrics for clinical LLM evaluation [CITE:WF7W2VJ9] identifies accuracy, completeness, safety, and relevance as recurring dimensions across 15+ evaluation studies.

Our 4-dimension rubric synthesizes these frameworks into the minimal set covering both clinical correctness and practical utility:

| Dimension | Weight (Default) | Derived From | What It Evaluates | Scale |
|-----------|-----------------|--------------|-------------------|-------|
| **Clinical Accuracy** | 30% | Elsevier "correctness" [CITE:EV9IX9DF]; GAPS "Grounding" [CITE:C833E6XG] | Are the clinical facts correct? Does the response contain errors? | 0–5 |
| **Completeness** | 30% | Elsevier "completeness"; GAPS "Adequacy" | Are all clinically significant findings addressed? | 0–5 |
| **Safety** | 20% | Elsevier "clinical harm"; GAPS "Safety" | Does the response avoid potentially harmful recommendations? | 0–5 |
| **Relevance** | 20% | Elsevier "helpfulness"; HealthBench "instruction following" | Does the response directly address the clinical question? | 0–5 |

#### Weight Assignment: Configurable Defaults with Clinical Rationale

Dimension weights are implemented as **configurable parameters** — not fixed constants. The defaults (30/30/20/20) reflect an initial clinical prioritization:

- **Accuracy + Completeness weighted higher (60% combined):** Factual errors and omissions in clinical AI responses directly impact patient safety; these dimensions represent correctness of content.
- **Safety + Relevance weighted lower (40% combined):** These dimensions represent quality of delivery — important but secondary to content correctness.

**Dynamic calibration for deployment context:**

| Clinical Context | Accuracy | Completeness | Safety | Relevance | Rationale |
|-----------------|----------|--------------|--------|-----------|-----------|
| Medication dosing | 25% | 25% | **40%** | 10% | Safety-critical: harmful dosage errors must be penalized heavily |
| Screening triage | 20% | **40%** | 20% | 20% | Completeness-critical: missed findings = missed diagnoses |
| Patient communication | 20% | 20% | 20% | **40%** | Relevance-critical: information must be accessible and on-topic |
| **Default (benchmark)** | **30%** | **30%** | **20%** | **20%** | Balanced for general clinical task evaluation |

This configurable design enables practitioners to adapt the evaluation framework to their specific deployment requirements. Section 4 reports sensitivity analysis demonstrating that serialization strategy rankings remain stable across weight perturbations of ±10%, confirming that primary findings are robust to practitioner-specific calibration.

**Weighted Total:** `(accuracy × w_a + completeness × w_c + safety × w_s + relevance × w_r) / (w_a + w_c + w_s + w_r)` where weights default to (0.3, 0.3, 0.2, 0.2)

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

| Why Claude Sonnet 4.5 as Judge | Rationale |
|-------------------------------|-----------|
| Not in the benchmark set as judge | Avoids self-evaluation bias (models don't judge themselves) |
| High reasoning capability | Consistent rubric application |
| Cost-effective at scale | ~$0.015 per evaluation × 4,500 = ~$67 |
| Reproducible | Same model, temperature=0, deterministic scoring |

**Note:** Claude Sonnet 4.5 IS one of the 5 benchmarked models. For evaluations where Claude is the subject model, we use GPT-5.4 as the judge instead (cross-evaluation to prevent self-bias).


## 3.5.4 Layer 3: Human Evaluation (Clinical Expert Review)

### Scope Clarification

Layer 3 is **designed but not executed** within the scope of the current study. We produce a standardized clinical review package enabling subsequent expert validation, while Layers 1 (Automated) and 2 (LLM-as-Judge) constitute the paper's empirical findings. This deliberate separation allows benchmark results to be published and reproduced immediately while expert review proceeds independently.

### Evaluation Instrument Design

| Parameter | Value |
|-----------|-------|
| Sample size | 150 evaluations (50 per task type) |
| Sampling strategy | Stratified: 5 per serializer × 2 per model × 3 tasks (balanced coverage) |
| Focus | Cases where Layer 1 and Layer 2 disagree (high-uncertainty samples) |
| Evaluator | Clinical informatics specialist (to be recruited) |
| Instrument | Same 4-dimension rubric (0–5 scale per dimension) |

### Deliverable: Clinical Review Package

The benchmark pipeline produces a standardized review package in machine-readable format:

| Artifact | Format | Content |
|----------|--------|---------|
| Stratified evaluation samples | XLSX/CSV | 150 pre-selected cases with stratification metadata |
| 4-dimension scoring rubric | XLSX with instructions | Scoring sheet (0–5 per dimension) with anchor definitions |
| Ground truth + model responses | Side-by-side XLSX | Clinical context, question, expected answer, model output |
| LLM-judge scores (for comparison) | JSON/CSV | Layer 2 scores for inter-rater computation |

### Intended Analysis (Future Work)

When expert scores are collected, the following validation metrics will be computed:

| Metric | Target | Interpretation |
|--------|--------|----------------|
| Spearman ρ (human vs. LLM-judge) | ≥ 0.75 | Validates LLM-as-judge for full-scale evaluation |
| Cohen's κ | ≥ 0.65 | Substantial agreement — automated scores are trustworthy |
| Dimension-level correlation | Report per dimension | Identifies which rubric dimensions LLM-judge scores reliably |

### Rationale for Deferred Execution

1. **Immediate reproducibility** — Layers 1+2 are fully automated and reproducible by any researcher with Bedrock access; Layer 3 requires domain expertise that introduces variability
2. **Publication timeline** — Expert recruitment and scoring requires 4–8 weeks; deferring allows timely benchmark publication
3. **Methodological contribution** — The evaluation protocol itself (instrument design, stratification strategy, validation metrics) is a contribution independent of its execution
4. **Community enablement** — Publishing the review package enables multiple clinical teams to validate independently, producing more robust inter-rater data than a single expert


## 3.5.5 Sensitivity & Robustness Analysis

To ensure that primary findings are not artifacts of specific parameter choices, we conduct three sensitivity analyses:

### A. Rubric Weight Sensitivity

The 4-dimension rubric weights (default: accuracy 30%, completeness 30%, safety 20%, relevance 20%) are perturbed across a ±10% range:

| Perturbation | Accuracy | Completeness | Safety | Relevance |
|-------------|----------|--------------|--------|-----------|
| Default | 30% | 30% | 20% | 20% |
| Safety-heavy | 20% | 25% | **35%** | 20% |
| Accuracy-heavy | **40%** | 25% | 15% | 20% |
| Completeness-heavy | 25% | **40%** | 15% | 20% |
| Equal weights | 25% | 25% | 25% | 25% |

**Criterion:** Main findings are considered robust if the top-2 serialization strategy ranking remains unchanged across all weight configurations.

### B. Sample Size Sensitivity

Results computed at n=50 samples per condition are compared against subsampled estimates at n=25 (half the data) using bootstrap resampling:

- Compute metric at n=50 (full sample)
- Resample n=25 (1,000 bootstrap iterations)
- Report 95% CI width and strategy ranking stability

**Criterion:** Rankings are stable if all pairwise differences that are significant at n=50 remain directionally consistent at n=25.

### C. Model-Specific Robustness

Strategy rankings may differ across models (as prior work suggests [CITE:TGZ97SRN]). We report:

- Aggregate ranking (pooled across all 5 models)
- Per-model ranking (does the best strategy change between frontier vs. open-weight models?)
- Interaction effects (serializer × model interaction from ANOVA)

**Criterion:** If rankings differ substantially across models, the decision framework (§4) reports model-conditional recommendations rather than a single universal ranking.

### Reporting Standard

Sensitivity analysis results are reported in §4 as a robustness check following the primary findings. Findings are categorized as:
- **Robust:** Top-2 ranking unchanged across all perturbations
- **Conditionally robust:** Ranking stable within model classes but differs between classes
- **Sensitive:** Ranking changes with perturbation — reported with appropriate caveats


## 3.5.6 Contribution Positioning

The FHIRBench Evaluation Framework contributes:

1. **First multi-dimensional rubric for serialization evaluation** — combining clinical accuracy, relevance, completeness, safety, and token efficiency in a single framework
2. **Three-layer validation** (automated → LLM-judge → human) — establishing trustworthy evaluation without requiring full human annotation at scale
3. **Pareto efficiency as the primary analytical lens** — directly actionable for practitioners balancing accuracy and cost
4. **Token efficiency as a first-class metric** — acknowledging that serialization strategy is fundamentally an optimization problem with cost constraints

This framework is generalizable beyond FHIR — any structured-to-LLM preprocessing pipeline can adopt the same rubric dimensions and Pareto analysis methodology.

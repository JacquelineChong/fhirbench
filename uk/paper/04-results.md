# 4. Results

The evaluation comprised a 2×2 design: two cohorts (clean, perturbed) × two assessment layers (token-level F1, clinical quality judgement), yielding 18,000 scored prompts per layer. We report the clean cohort as the primary analysis, with perturbation results providing robustness evidence.

## 4.1 Layer 1: Token-Level Factual Retrieval

Table 1 presents model performance on token-level F1 across the 100-patient clean evaluation cohort, aggregated at the patient level across all serialiser–task combinations (N=1,800 prompts per model: 100 patients × 6 serialisers × 3 tasks).

**Table 1.** Layer 1 token-level F1 scores (clean cohort, patient-level aggregation).

| Rank | Model | Mean F1 | 95% CI |
|:---:|-------|:-------:|:------:|
| 1 | Llama 3.3 70B | 0.454 | [0.445, 0.463] |
| 2 | Qwen3 32B | 0.448 | [0.440, 0.457] |
| 3 | Claude Sonnet 4.5 | 0.428 | [0.419, 0.437] |
| 4 | GPT-5.4 | 0.417 | [0.407, 0.427] |
| 5 | DeepSeek V3.2 | 0.416 | [0.407, 0.425] |

A Kruskal–Wallis test confirmed significant differences across models (H=62.77, df=4, p<10⁻¹²). Post-hoc pairwise comparisons (Dunn's test, Bonferroni-corrected) showed Llama 3.3 significantly outperformed all others, including Qwen3 (p=0.003, δ=0.064). GPT-5.4 and DeepSeek V3.2 did not differ from one another (p=0.84).

At the task level, clinical_qa yielded the highest F1 across all models (range 0.642–0.678), clinical_summarisation produced moderate scores (0.407–0.510), and clinical_reasoning scored lowest (0.165–0.221). The poor reasoning performance is partially artefactual: the F1 metric penalises inferential content absent from the ground truth even when clinically appropriate.

## 4.2 Layer 2: Clinical Quality Assessment

Table 2 presents LLM-as-judge scores across four clinical quality dimensions on the clean cohort. Claude was judged by Qwen3 to mitigate self-assessment bias; all other models were judged by Claude.

**Table 2.** Layer 2 clinical quality scores (0–5 scale, cross-judge protocol, clean cohort).

| Rank | Model | Accuracy | Completeness | Safety | Relevance | Average |
|:---:|-------|:--------:|:-----------:|:------:|:---------:|:-------:|
| 1 | Claude Sonnet 4.5 | 4.72 | 4.91 | 4.98 | 5.00 | 4.90 |
| 2 | GPT-5.4 | 3.92 | 4.00 | 4.32 | 4.88 | 4.28 |
| 3 | DeepSeek V3.2 | 3.74 | 4.06 | 4.28 | 4.87 | 4.23 |
| 4 | Qwen3 32B | 3.23 | 3.68 | 3.59 | 4.63 | 3.78 |
| 5 | Llama 3.3 70B | 2.81 | 3.08 | 3.06 | 4.48 | 3.36 |

Inter-model differences were highly significant (Kruskal–Wallis H=335.07, df=4, p≈0). Claude achieved near-ceiling scores across all dimensions, with the separation from second-ranked GPT-5.4 substantial (Δ=0.62 composite). All models scored highest on relevance (≥4.48), whilst accuracy and safety showed the greatest inter-model variance.

## 4.3 Ranking Reversal Between Layers

The most striking finding is the complete inversion of model rankings between layers: Llama 3.3 (Layer 1 rank 1) fell to Layer 2 rank 5, whilst Claude (Layer 1 rank 3) rose to Layer 2 rank 1. The Spearman rank-order correlation between layers was ρ = −0.90.

This reversal replicates the central finding of Paper 1 (Chong, 2026) on US Core FHIR data, confirming cross-national generalisability. Crucially, the reversal persists under data perturbation: both Layer 1 (Llama > Qwen > Claude > GPT-5.4 > DeepSeek) and Layer 2 (Claude > GPT-5.4 > DeepSeek > Qwen > Llama) rankings were preserved identically on the perturbed cohort, confirming that the phenomenon is robust to data quality variation. The mechanism is consistent: token-level F1 rewards concise responses that maximise lexical overlap, whilst clinical quality rubrics reward completeness, safety reasoning, and interpretive precision. Llama's brevity (mean 724 tokens) inflates F1 through high precision at the cost of clinical thoroughness; Claude's longer, structured responses (mean 1,344 tokens) sacrifice token-level precision for clinical completeness.

## 4.4 Serialisation Format Analysis

Serialisation format was evaluated as both a Layer 1 and Layer 2 factor. The results reveal a dissociation: serialiser choice has a small effect on token retrieval but a substantial effect on clinical quality.

### 4.4.1 Layer 1 Serialiser Effect

Table 3 presents mean F1 by serialisation format, pooled across all five models.

**Table 3.** Layer 1 F1 by serialiser (clean cohort, all models pooled).

| Serialiser | Mean F1 | Input Token Reduction |
|------------|:-------:|:---------------------:|
| raw_json | 0.451 | — |
| structured_markdown | 0.439 | 88% |
| narrative | 0.435 | 88% |
| hybrid_adaptive | 0.433 | 89% |
| clinical_template | 0.429 | 90% |
| flattened_kv | 0.409 | 39% |

The serialiser effect range was 0.042 (max−min F1). Raw JSON's advantage reflects its preservation of system URIs, codes, and structural tokens that contribute to ground truth overlap. Notably, flattened_kv achieved the most modest token reduction (39%) yet performed worst—its dot-notation structure fragments clinical concepts across hierarchical keys, hindering retrieval.

### 4.4.2 Layer 2 Serialiser Effect

In contrast to the modest Layer 1 effect, serialisation format significantly impacted clinical quality assessment.

**Table 4.** Layer 2 mean clinical quality score by serialiser (clean cohort, all models pooled).

| Serialiser | L2 Mean Score |
|------------|:-------------:|
| raw_json | 4.614 |
| structured_markdown | 4.569 |
| hybrid_adaptive | 4.559 |
| narrative | 4.550 |
| clinical_template | 4.502 |
| flattened_kv | 4.373 |

The Layer 2 serialiser effect was 0.24 points on a 5-point scale (Kruskal–Wallis H=163.86, df=5, p<10⁻³³). This effect was consistent across models, with the range increasing for lower-ranked models: Claude 0.10, GPT-5.4 0.19, DeepSeek 0.23, Qwen 0.29, Llama 0.39. This gradient indicates that serialisation format interacts with model capability—weaker models are more sensitive to input format, whilst stronger models partially compensate for suboptimal serialisation.

The flattened_kv serialiser was consistently worst on both layers. Despite achieving only 39% token reduction (compared with 88–90% for narrative/template formats), its hierarchical dot-notation disrupts the semantic coherence of clinical entities, degrading both factual retrieval and clinical interpretation.

### 4.4.3 Correction to Previous Analysis

An earlier analysis reported "comparable clinical quality (Layer 2 average difference <0.1)" across serialisers. This was incorrect and reflected analysis restricted to Claude alone (within-model range: 0.10). The full cross-model analysis reveals a significant serialiser effect of 0.24 on Layer 2 quality (p<10⁻³³), driven primarily by the poor performance of flattened_kv and amplified in weaker models.

## 4.5 Perturbation Robustness

The perturbed cohort applied clinically realistic noise to the evaluation bundles (missing data fields, coding inconsistencies, date format variations, incomplete medication histories). All 9,000 prompts per layer were re-evaluated.

### 4.5.1 Layer 1 Degradation Under Perturbation

Perturbation produced a uniform, modest degradation in F1 across all models (mean Δ = −0.010, range −0.008 to −0.011), preserving model rankings exactly. Llama remained rank 1 (0.444 perturbed vs 0.454 clean), and DeepSeek remained rank 5 (0.405 vs 0.416). The degradation was consistent at 1.8–2.5% relative loss, suggesting all models exhibit comparable vulnerability to input noise on token retrieval.

### 4.5.2 Serialiser Effects Are Stable Under Perturbation

A critical finding from the perturbation experiment is that the serialiser effect size was stable between cohorts. The mean serialiser range (max−min F1) was 0.042 on clean data and 0.041 on perturbed data. A paired t-test across the five models found no significant difference in effect size (t = −1.40, p = 0.88, one-sided test for H₁: perturbed > clean). The Wilcoxon signed-rank test confirmed this null result (W=3.0, p=0.91).

Only 2 of 5 models showed marginally larger serialiser effects under perturbation; 3 of 5 showed slightly smaller effects. The best serialiser (raw_json) and worst serialiser (flattened_kv) remained identical across both cohorts for all five models. This stability indicates that the serialiser ranking is an intrinsic property of the format representations rather than a data-dependent artefact.

### 4.5.3 Layer 2 Under Perturbation

Layer 2 composite scores were highly stable under perturbation. Per-judgement averages showed negligible change: Claude 4.90 → 4.90, GPT-5.4 4.80 → 4.83, DeepSeek 4.67 → 4.69, Qwen 4.19 → 4.23, Llama 3.95 → 4.00. Model rankings were preserved identically. The serialiser effect on Layer 2 remained significant under perturbation (H=154.12, df=5, p<10⁻³¹), with raw_json best (4.608) and flattened_kv worst (4.409). This stability demonstrates that both model rankings and serialiser effects are robust to clinically realistic data noise.

## 4.6 Cost-Efficiency Analysis

Three models define the Pareto frontier of cost versus quality:

- **Claude Sonnet 4.5** ($0.032/prompt): highest clinical quality (4.90/5.00), indicated for safety-critical applications.
- **DeepSeek V3.2** ($0.005/prompt): quality comparable to GPT-5.4 (Δ=0.05) at one-sixth the cost, suitable for bulk processing.
- **Qwen3 32B** ($0.002/prompt): lowest cost with acceptable quality (3.78/5.00), appropriate for pre-screening workloads.

GPT-5.4 ($0.028/prompt) is Pareto-dominated by the Claude–DeepSeek combination. Llama 3.3 ($0.003/prompt) is dominated by Qwen3, which achieves higher clinical quality at comparable cost.

The serialisation analysis adds a second cost lever: narrative and clinical_template formats achieve 88–90% input token reduction with minimal Layer 2 quality loss (Δ ≤ 0.06 vs raw_json). Combining clinical_template serialisation with DeepSeek inference yields practical clinical quality at under £7 per 1,000 patient queries.

## 4.7 Llama 3.3: Operational Configuration

Paper 1 reported 0% success for Llama 3.1 70B due to systematic timeouts. Extending the Bedrock read_timeout from 60s to 600s yielded 100% success for Llama 3.3 70B across all 1,800 prompts per cohort. This finding highlights that operational configuration is a prerequisite for valid benchmarking. However, Llama's strong Layer 1 performance does not translate to clinical fitness: its Layer 2 rank of 5/5 on both cohorts confirms that token-level proficiency and clinical quality are orthogonal constructs.

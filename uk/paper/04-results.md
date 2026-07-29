# 4. Results

## 4.1 Layer 1: Token-Level Factual Retrieval

Table 1 presents model performance on token-level F1 across the 100-patient evaluation cohort, aggregated at the patient level across all serialiser–task combinations.

**Table 1.** Layer 1 token-level F1 scores (patient-level aggregation, N=100 per model).

| Rank | Model | Mean F1 | 95% CI |
|:---:|-------|---------|--------|
| 1 | Llama 3.3 70B | 0.454 | [0.445, 0.463] |
| 2 | Qwen3 32B | 0.448 | [0.440, 0.457] |
| 3 | Claude Sonnet 4.5 | 0.428 | [0.419, 0.437] |
| 4 | GPT-5.4 | 0.417 | [0.407, 0.427] |
| 5 | DeepSeek V3.2 | 0.416 | [0.407, 0.425] |

A Kruskal–Wallis test confirmed significant differences across models (H=62.77, df=4, p<10⁻¹²). Post-hoc pairwise comparisons (Dunn’s test with Bonferroni correction) revealed that the top-ranked Llama 3.3 significantly outperformed all other models, including Qwen3 (p=0.003, δ=0.064). The bottom two models, GPT-5.4 and DeepSeek V3.2, did not differ significantly from one another (p=0.84).

At the task level, clinical_qa yielded the highest F1 scores across all models (range 0.642–0.678), reflecting the relatively straightforward nature of factual extraction. Clinical summarisation produced moderate scores (0.407–0.510), whilst clinical reasoning scored lowest (0.165–0.221). The poor performance on reasoning tasks is partially artefactual: the F1 metric penalises responses containing inferential content that does not appear verbatim in the ground truth, even when clinically appropriate.

Complexity-stratified analysis showed a monotonic increase in F1 with bundle complexity: simple bundles (0.369–0.408) < moderate (0.413–0.457) < complex (0.448–0.485) < highly complex (0.454–0.478). This counterintuitive pattern reflects the larger token vocabulary in complex bundles, which increases the probability of incidental overlap between response and ground truth tokens.

## 4.2 Layer 2: Clinical Quality Assessment

Table 2 presents LLM-as-judge scores across four clinical quality dimensions. Claude was judged by Qwen3 to mitigate self-assessment bias; all other models were judged by Claude.

**Table 2.** Layer 2 LLM-as-judge scores (0–5 scale, cross-judge protocol).

| Rank | Model | Accuracy | Completeness | Safety | Relevance | Average |
|:---:|-------|:--------:|:-----------:|:------:|:---------:|:-------:|
| 1 | Claude Sonnet 4.5 | 4.72 | 4.91 | 4.98 | 5.00 | 4.90 |
| 2 | GPT-5.4 | 3.92 | 4.00 | 4.32 | 4.88 | 4.28 |
| 3 | DeepSeek V3.2 | 3.74 | 4.06 | 4.28 | 4.87 | 4.23 |
| 4 | Qwen3 32B | 3.23 | 3.68 | 3.59 | 4.63 | 3.78 |
| 5 | Llama 3.3 70B | 2.81 | 3.08 | 3.06 | 4.48 | 3.36 |

A Kruskal–Wallis test confirmed highly significant inter-model differences (H=335.07, df=4, p≈0). Claude achieved near-ceiling scores on all dimensions, with particular distinction on safety (4.98) and relevance (5.00). The separation between Claude and the second-ranked GPT-5.4 was substantial (Δ=0.62 on the composite score). Notably, all models scored highest on relevance (≥4.48), indicating that even lower-performing models remained on-topic, whilst accuracy and safety showed the greatest inter-model variance.

Among the non-Claude models, GPT-5.4 and DeepSeek V3.2 performed comparably on accuracy (3.92 vs 3.74) and safety (4.32 vs 4.28), with neither separation reaching clinical significance. Qwen3 and Llama 3.3 formed a lower tier, with Llama scoring below 3.1 on accuracy, completeness, and safety—thresholds that may be clinically concerning for deployment scenarios.

## 4.3 Ranking Reversal Between Layers

The most striking finding is the complete inversion of model rankings between Layer 1 and Layer 2 (Figure 2). Llama 3.3, ranked first on token-level F1, dropped to last place on clinical quality. Conversely, Claude, ranked third on F1, dominated the clinical quality assessment. This reversal replicates and extends the finding from Paper 1 (Chong, 2026) on US-format data, confirming that the phenomenon generalises to UK Core FHIR profiles.

The reversal arises because token-level F1 rewards verbose, code-rich responses that maximise lexical overlap with ground truth tokens, whilst the clinical quality rubric rewards precision, clinical reasoning, and appropriate interpretation. Llama 3.3 produced the most concise responses on average (mean 724 output tokens), achieving high precision at the expense of completeness on the clinical quality dimensions. Claude produced more comprehensive, structured responses (mean 1,344 tokens) that scored lower on token overlap but demonstrated superior clinical judgement.

This divergence has direct implications for benchmark design: a single-metric evaluation would produce misleading conclusions about model fitness for clinical deployment.

## 4.4 Serialisation Format Analysis

Table 3 presents Layer 1 F1 scores stratified by serialisation format, averaged across all models.

**Table 3.** Mean F1 by serialisation format (all models pooled).

| Serialiser | Mean F1 | Token Reduction vs raw_json |
|------------|:-------:|:---------------------------:|
| raw_json | 0.451 | — |
| structured_markdown | 0.439 | 92% |
| narrative | 0.435 | 92% |
| hybrid_adaptive | 0.433 | 93% |
| clinical_template | 0.429 | 94% |
| flattened_kv | 0.409 | 53% |

Raw JSON achieved the highest F1, consistent with its preservation of all original data including system URIs, codes, and structural tokens that contribute to ground truth overlap. However, the clinical_template serialiser achieved comparable clinical quality (Layer 2 average difference <0.1) whilst reducing input tokens by 94%—a finding with significant cost implications at scale.

The flattened key-value format performed worst on both layers, likely because its dot-notation structure (e.g., `entry[0].resource.code.coding[0].display`) fragments clinical concepts across multiple tokens, hindering both retrieval and interpretation.

The hybrid_adaptive serialiser, which selects format based on task type, did not outperform individual serialisers, suggesting that format selection may be less impactful than format consistency for model performance.

## 4.5 Cost-Efficiency Pareto Analysis

Figure 3 presents the cost–quality Pareto frontier across the five models, plotting mean Layer 2 composite score against per-prompt inference cost.

Three models define the efficient frontier:

- **Claude Sonnet 4.5** ($0.032/prompt): highest clinical quality, suitable for safety-critical applications where cost is secondary to accuracy.
- **DeepSeek V3.2** ($0.005/prompt): achieves quality comparable to GPT-5.4 (Δ=0.05) at approximately one-sixth the cost, representing the strongest value proposition for bulk processing tasks.
- **Qwen3 32B** ($0.002/prompt): lowest cost with acceptable quality (3.78/5.00), appropriate for pre-screening or triage workloads where human review follows.

GPT-5.4 ($0.028/prompt) is Pareto-dominated by the Claude–DeepSeek combination: Claude offers superior quality at comparable cost, whilst DeepSeek matches GPT-5.4’s quality at substantially lower cost. Llama 3.3 70B ($0.003/prompt) is dominated by Qwen3, which achieves higher clinical quality at lower cost—a finding attributable to Llama’s tendency toward verbose, less clinically precise responses in UK FHIR contexts.

## 4.6 Llama 3.3 Performance: Comparison with Paper 1

Paper 1 reported 0% success for Llama 3.1 70B, attributed to systematic inference timeouts. Our investigation revealed this was primarily a configuration artefact: the default Bedrock `read_timeout` of 60 seconds was insufficient for the model’s generation latency on complex FHIR bundles. In the present study, extending the timeout to 600 seconds yielded 100% success for Llama 3.3 70B across all 1,800 prompts.

This finding carries two implications. First, operational configuration (timeout thresholds, retry policies, batch sizes) represents a prerequisite for valid benchmarking—models cannot be evaluated if infrastructure prevents response completion. Second, once this prerequisite is satisfied, Llama 3.3’s high token-level F1 but low clinical quality scores suggest that model accessibility does not equate to model fitness for clinical deployment.

## 4.7 UK Core–Specific Findings

All five models demonstrated competence in handling UK-specific FHIR conventions. NHS Number extraction accuracy exceeded 98% across models in the clinical_qa task. SNOMED CT UK code retrieval ranged from 71% (Llama) to 94% (Claude), with errors primarily involving code truncation rather than hallucination. dm+d medication code handling showed similar patterns, with Claude and GPT-5.4 achieving >90% accuracy on formulary-standard codes.

The most challenging UK-specific element was the interpretation of UK Core extensions (ethnic category, NHS Number verification status, GP practice registration), where even Claude achieved only 82% accuracy. This suggests that extension-heavy profiles remain an area for model improvement, likely requiring UK-specific fine-tuning or retrieval augmentation.

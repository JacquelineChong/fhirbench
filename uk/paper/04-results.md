# 4. Results

The evaluation comprised 18,000 prompts across five models, six serialisation formats, three clinical tasks, and four complexity levels, assessed under two conditions (clean and perturbed cohorts) using both token-level F1 (Layer 1) and LLM-as-judge clinical quality scoring (Layer 2). We present results with serialisation strategy as the primary analytical lens, as this constitutes the paper's principal contribution to clinical AI deployment guidance.

## 4.1 Serialisation Format Significantly Impacts Clinical Quality

The choice of FHIR-to-text serialisation format produces a clinically meaningful difference in LLM clinical quality. Across all models and tasks, Layer 2 composite scores varied by 0.24 points on a 5-point scale as a function of serialiser alone (Kruskal–Wallis H=163.86, df=5, p<10⁻³³).

**Table 1.** Layer 2 clinical quality by serialisation format (clean cohort, all models pooled).

| Serialiser | L2 Mean Score | Token Reduction |
|------------|:-------------:|:---------------:|
| raw_json | 4.614 | — |
| structured_markdown | 4.569 | 88% |
| hybrid_adaptive | 4.559 | 89% |
| narrative | 4.550 | 88% |
| clinical_template | 4.502 | 91% |
| flattened_kv | 4.373 | 39% |

This effect is significant across both evaluation layers and both data conditions. On Layer 1 (token-level F1), the serialiser range was 0.042 (raw_json: 0.451, flattened_kv: 0.409). On Layer 2 under data perturbation, the effect remained significant (H=154.12, df=5, p<10⁻³¹; range 0.20). The consistency across layers, cohorts, and models establishes serialisation format as a reliable, controllable variable in clinical LLM deployment—unlike model selection, which is constrained by availability, cost, and regulatory considerations.

The Layer 2 effect is the more deployment-relevant measure. Token-level F1 rewards lexical overlap with ground truth, which favours raw_json's preservation of system URIs and FHIR structural tokens. Layer 2 evaluates clinical accuracy, completeness, safety, and relevance—the dimensions that determine whether an LLM response is fit for clinical use. That serialiser choice significantly impacts these dimensions means that deployment teams selecting serialisation format are making a clinical quality decision, not merely an engineering one.

## 4.2 The Optimal Serialiser Is Context-Dependent

The aggregate ranking in Table 1 conceals a critical finding: the optimal serialisation format changes depending on clinical task and data complexity. raw_json is not universally optimal; in 58% of model–task–complexity scenarios (35 of 60), an alternative format outperforms it.

**Table 2.** Layer 2 mean score by serialiser and clinical task (all models pooled).

| Serialiser | Clinical QA | Clinical Reasoning | Clinical Summarisation |
|------------|:-----------:|:------------------:|:---------------------:|
| raw_json | **4.867** | 4.515 | 4.520 |
| structured_markdown | 4.733 | 4.530 | **4.518** |
| hybrid_adaptive | 4.744 | **4.576** | 4.434 |
| narrative | 4.722 | 4.543 | 4.465 |
| clinical_template | 4.668 | 4.559 | 4.356 |
| flattened_kv | 4.432 | 4.364 | 4.329 |

Three task-specific patterns emerge:

- **Clinical QA** (factual extraction): raw_json dominates. The complete preservation of identifiers, codes, and system URIs provides models with verbatim access to the exact tokens they need to retrieve.
- **Clinical reasoning** (drug interactions, risk assessment): hybrid_adaptive and clinical_template outperform raw_json. Reasoning tasks benefit from semantic organisation that groups related clinical concepts, reducing the cognitive parsing required to identify relationships across dispersed JSON fields.
- **Clinical summarisation**: structured_markdown performs comparably to raw_json whilst achieving 88% token reduction. The hierarchical formatting of markdown preserves document structure that aids coherent synthesis.

This pattern replicates on the perturbed cohort: raw_json remains optimal for QA, whilst clinical_template and structured_markdown lead on reasoning and summarisation respectively (p<10⁻³¹). The stability under perturbation confirms these are genuine task–format interactions rather than data-specific artefacts. Figure 4 presents the full task × serialiser quality matrix, with optimal cells highlighted.

### Context-Dependent Reversals

In specific model–task–complexity combinations, the advantage of alternative formats over raw_json is substantial. Table 3 presents the most dramatic reversals.

**Table 3.** Largest serialiser advantages over raw_json (model × task × complexity scenarios, minimum n=7 per cell).

| Model | Task | Complexity | Best Serialiser | Δ vs raw_json |
|-------|------|:----------:|-----------------|:-------------:|
| Llama 3.3 | Summarisation | Highly complex | structured_markdown | +0.58 |
| Qwen3 | Summarisation | Highly complex | structured_markdown | +0.54 |
| Llama 3.3 | Summarisation | Simple | structured_markdown | +0.43 |
| Llama 3.3 | Summarisation | Moderate | structured_markdown | +0.42 |
| Qwen3 | Reasoning | Moderate | hybrid_adaptive | +0.39 |

In 17 of 60 scenarios, alternative formats beat raw_json by more than 0.1 points; in 10, by more than 0.2. The largest reliable reversal (+0.58 for Llama on highly complex summarisation) demonstrates that structured_markdown can shift output from marginally acceptable (3.14) to clinically adequate (3.72) solely by changing serialisation format—without changing model, prompt, or input data.

### Summary

The task-specific pattern implies a routing strategy: raw_json for QA, hybrid_adaptive or clinical_template for reasoning, structured_markdown for summarisation. This combination recovers up to 0.39 points of clinical quality for models below the performance ceiling.

## 4.3 Model Capability Moderates Serialiser Sensitivity

The serialiser effect is not uniform across models. Weaker models exhibit greater sensitivity to input format, whilst stronger models partially compensate for suboptimal serialisation.

**Table 4.** Serialiser sensitivity by model (Layer 2, clean cohort).

| Model | L2 Range | Best Format | Worst Format | Mean L2 |
|-------|:--------:|-------------|--------------|:-------:|
| Claude Sonnet 4.5 | 0.10 | raw_json (4.96) | clinical_template (4.86) | 4.90 |
| GPT-5.4 | 0.19 | raw_json (4.86) | flattened_kv (4.68) | 4.80 |
| DeepSeek V3.2 | 0.23 | raw_json (4.80) | flattened_kv (4.57) | 4.67 |
| Qwen3 32B | 0.29 | hybrid_adaptive (4.29) | flattened_kv (4.00) | 4.19 |
| Llama 3.3 70B | 0.39 | raw_json (4.10) | flattened_kv (3.71) | 3.96 |

The correlation between model overall quality and serialiser robustness is monotonic: Claude (highest quality, lowest sensitivity) through to Llama (lowest quality, highest sensitivity). Figure 2 visualises this interaction: Claude's line is nearly flat across serialisers, whilst Llama's drops steeply—demonstrating that weaker models derive the greatest benefit from optimal format selection.

## 4.4 Model Performance and the Ranking Reversal

Model rankings contextualise the serialiser findings. On Layer 1 (token-level F1), Llama 3.3 ranked first (0.454) followed by Qwen3 (0.448), Claude (0.428), GPT-5.4 (0.417), and DeepSeek (0.416). On Layer 2 (clinical quality), the ranking inverted completely: Claude first (4.90), GPT-5.4 (4.80), DeepSeek (4.67), Qwen3 (4.19), Llama last (3.96). The Spearman correlation between layers was ρ = −0.90 (Figure 1).

This ranking reversal replicates the central finding of Paper 1 (Hussain & Chong, 2025) on US Core FHIR data. Both Layer 1 and Layer 2 rankings were preserved identically on the perturbed cohort, confirming robustness to data quality variation.

## 4.5 Perturbation Robustness

The perturbed cohort applied clinically realistic noise (missing fields, coding inconsistencies, date format variations). Key stability findings:

- **Model rankings**: Identical across clean and perturbed cohorts for both layers.
- **Layer 1 degradation**: Uniform −2.2% across all models (mean Δ = −0.010 F1).
- **Serialiser rankings**: Best (raw_json) and worst (flattened_kv) serialisers unchanged for all five models across both cohorts.
- **Serialiser effect size**: Stable between cohorts (paired t-test: t = −1.40, p = 0.88).
- **Task-specific patterns**: The task-dependent optimality of serialisers replicated under perturbation.

This stability establishes that the reported serialiser effects are intrinsic properties of the format representations rather than artefacts of clean synthetic data.

## 4.6 Cost-Efficiency Implications

Figure 3 presents the cost-quality Pareto frontier. Serialisation format provides a second cost lever beyond model selection. Narrative and clinical_template formats achieve 88–91% input token reduction with Layer 2 quality loss of only 0.06–0.11 points versus raw_json. Combining clinical_template serialisation with DeepSeek inference yields clinical quality scores of 4.58/5.00 at under £7 per 1,000 patient queries—compared to £32 per 1,000 queries for Claude with raw_json at 4.96/5.00.

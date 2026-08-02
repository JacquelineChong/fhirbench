# 5. Discussion

## 5.1 Context-Dependent Serialisation: A New Paradigm for Clinical FHIR Processing

The central contribution of this study is the demonstration that FHIR-to-text serialisation format is not a neutral preprocessing step but a significant, controllable determinant of clinical LLM quality. The effect is substantial (0.24 points on a 5-point clinical quality scale, p<10⁻³³), replicable across data conditions (clean and perturbed cohorts), and—critically—context-dependent. There is no single optimal serialisation format; the best choice depends on clinical task, model capability, and data complexity.

This finding overturns two prior claims. Paper 1 (Hussain & Chong, 2025) suggested that condensed formats consistently outperform raw JSON for FHIR-based clinical tasks. Our initial Paper 2 analysis incorrectly concluded that serialiser choice "barely matters" (Layer 2 difference <0.1)—an error arising from restricting analysis to Claude alone, the model least sensitive to format variation. The complete cross-model analysis reveals a more nuanced and more useful truth: serialisation strategy is a first-order deployment variable whose optimal configuration varies by context.

The mechanistic explanation for task-dependent optimality rests on the distinct information requirements of each clinical task type:

**Clinical QA** (factual extraction) requires precise retrieval of specific identifiers: NHS Numbers, SNOMED CT codes, dm+d medication codes, and date-stamped observations. raw_json preserves these tokens in their original form, including system URIs that serve as disambiguation context. When the task is "retrieve the patient's most recent HbA1c value and code," the model benefits from seeing the exact JSON path `{"code": {"coding": [{"system": "http://snomed.info/sct", "code": "43396009", "display": "Hemoglobin A1c"}]}}` rather than a summarised representation that may omit the system URI or conflate multiple codings.

**Clinical reasoning** (drug interactions, risk stratification, care gap identification) requires models to identify relationships between dispersed clinical entities. A raw JSON bundle scatters related information across hundreds of resource entries; a patient's antihypertensive medication may be 3,000 tokens distant from the blood pressure observation it targets. hybrid_adaptive and clinical_template serialisers pre-organise this information by clinical domain, presenting medications alongside their indications and relevant observations in semantically coherent blocks. This reduces the relational reasoning burden on the model, yielding measurably better clinical quality (+0.06 vs raw_json).

**Clinical summarisation** requires hierarchical document synthesis—demographics, then problems, then medications, then investigations—following established clinical communication conventions (e.g., SBAR framework). structured_markdown provides an inherent hierarchical scaffold via headings and nested lists, which models leverage to produce well-organised summaries. raw_json's flat array of bundle entries offers no such structural guidance, placing the full organisational burden on the model's generation capabilities.

These mechanisms predict—and the data confirm—that a task-adaptive serialisation strategy outperforms any fixed format choice across the full range of clinical applications an NHS deployment would encounter.

Practitioners should resist the temptation to select a single 'best' format from the aggregate ranking (Table 1). The aggregate conceals task-specific reversals of up to +0.58 points—the optimal deployment strategy is context-aware routing, not static format selection.

The convergence with Pator (2026) strengthens this conclusion considerably. That study, conducted independently using different models (open-weight ≤70B), a different task (medication reconciliation), different data (generic FHIR, not UK Core), and a different evaluation methodology (F1 only), arrived at the same core finding: serialisation format significantly impacts clinical LLM performance, and the advantage of specific formats reverses depending on model capability. Pator found narrative formats outperformed raw JSON by 19 F1 points for sub-8B models, but that this advantage reversed at 70B—paralleling our finding that weaker models (Llama, Qwen) show 3–4× greater format sensitivity than stronger models (Claude). Two independent research groups, working with non-overlapping model families and clinical tasks, converging on the same phenomenon constitutes substantially stronger evidence than either study alone. The serialisation effect is real, replicable, and generalisable across model scales, clinical tasks, and FHIR profile families.

## 5.2 Implications for NHS Deployment: The Adaptive Serialisation Case

The practical significance of context-dependent serialisation is amplified by a second finding: model capability inversely correlates with serialiser sensitivity. Claude (highest quality) shows a 0.10-point range across serialisers; Llama (lowest quality) shows 0.39. This interaction produces a deployment paradox: the organisations that most need serialisation optimisation—those deploying budget-constrained models—are precisely those for whom the gains are largest.

Consider a typical NHS Integrated Care System evaluating LLM deployment for FHIR-based clinical workflows. Budget constraints limit model selection to the Qwen–DeepSeek tier ($0.002–0.005 per prompt) rather than Claude ($0.032). At this price point, clinical quality ranges from 3.96 (Llama, worst serialiser) to 4.69 (DeepSeek, best serialiser). The 0.73-point range accessible through combined model and serialiser optimisation substantially exceeds the 0.24-point range attributable to serialiser alone, but the serialiser contribution is entirely within engineering control—requiring no additional API cost, no vendor negotiation, and no procurement cycle.

An adaptive serialisation layer—a lightweight preprocessing service that routes incoming clinical queries to the appropriate FHIR-to-text conversion based on detected task type—would yield the following gains for a mid-tier deployment (DeepSeek V3.2):

- **Clinical QA workloads** (coding queries, identifier lookups): route through raw_json. Quality: 4.80/5.00.
- **Clinical reasoning workloads** (medication review, risk assessment): route through hybrid_adaptive. Quality: 4.69/5.00 (+0.02 vs raw_json).
- **Clinical summarisation workloads** (discharge summaries, referral letters): route through structured_markdown. Quality: 4.72/5.00, with 88% token reduction yielding substantial cost savings at volume.

The engineering complexity of such a routing layer is minimal: task type classification can be achieved through keyword matching on the prompt, a lightweight classifier, or explicit labelling in the API schema. The quality gain—recovering 0.1–0.4 points that would otherwise be lost to suboptimal serialisation—requires no model retraining, no fine-tuning, and no change to the underlying LLM infrastructure.

The economic case is compelling. For an NHS trust processing 50,000 clinical queries monthly across a mixed workload (40% QA, 30% reasoning, 30% summarisation), adaptive serialisation with DeepSeek V3.2 would cost approximately £200/month whilst maintaining quality above 4.6/5.00 across all task types. The equivalent quality from a fixed raw_json approach with the same model would be marginally higher on QA but substantially lower on reasoning and summarisation—a net quality degradation across the mixed workload. Alternatively, achieving equivalent across-the-board quality with a single premium model (Claude) and no serialisation optimisation would cost approximately £1,600/month—an 8× premium for marginal quality gains.

For NHS trusts operating at scale (>100,000 patient interactions per month), the combined effect of task-adaptive serialisation and model selection enables a tiered architecture:

- **Safety-critical tier** (medication reconciliation, A&E decision support): Claude + raw_json. Quality: 4.96/5.00. Cost: ~£25 per 1,000 queries.
- **Standard clinical tier** (discharge summaries, GP referrals): DeepSeek + structured_markdown. Quality: 4.72/5.00. Cost: ~£4 per 1,000 queries with 88% token reduction.
- **Pre-screening tier** (bulk record flagging, population health): Qwen + clinical_template. Quality: 4.18/5.00. Cost: ~£1.50 per 1,000 queries.

This tiered approach brings LLM-assisted FHIR processing within budget reach of community trusts and GP federations—not only large acute providers with substantial digital transformation budgets.

## 5.3 The Ranking Reversal: Cross-National Confirmation

The complete inversion of model rankings between Layer 1 (token-level F1) and Layer 2 (clinical quality) replicates across US Core and UK Core FHIR profiles, two independent synthetic datasets, and two data conditions (clean and perturbed). Llama 3.3 ranks first on F1 but last on clinical quality; Claude ranks third on F1 but first on quality. The Spearman correlation (ρ = −0.90) confirms these are not merely shuffled rankings but substantively inverted orderings.

The replication strengthens the claim that this is a fundamental measurement phenomenon: token-level metrics and clinical quality rubrics evaluate orthogonal—potentially antagonistic—constructs. The mechanism, which we term the "conciseness trap," operates through the interaction of response length with metric incentives. Llama's brevity (mean 724 tokens) maximises F1 precision by minimising tokens absent from ground truth, whilst sacrificing the clinical thoroughness (completeness, safety reasoning) that Layer 2 evaluates.

For the broader clinical NLP community, this carries a methodological imperative: studies reporting only F1, ROUGE, or BLEU for clinical question answering or summarisation risk conclusions that would invert under clinical expert evaluation. Single-metric benchmarking is insufficient for deployment decisions. The field requires multi-layer evaluation frameworks as standard practice. Notably, Pator (2026) relied solely on F1 and acknowledged this as a limitation; our multi-layer design demonstrates that the serialiser effects observed on F1 do not straightforwardly predict effects on clinical quality—reinforcing the case for multi-layer evaluation.

## 5.4 Robustness and Generalisability

The perturbation experiment provides evidence that the reported findings are not artefacts of idealised synthetic data. Under clinically realistic noise (missing fields, coding inconsistencies, date format variations):

- All model rankings preserved identically across both layers
- Serialiser rankings stable (same best/worst for all models)
- Task-specific serialiser optimality replicated (raw_json for QA, hybrid/template for reasoning, markdown for summarisation)
- Effect sizes stable (paired t-test: p=0.88 for change in serialiser range)

This robustness supports deployment confidence: the serialisation recommendations derived from clean evaluation data will hold when applied to real-world clinical records with their inherent messiness. The 2.2% F1 degradation under perturbation is modest and uniform, suggesting that all five models—and all six serialisation formats—exhibit comparable vulnerability to input noise.

However, several limitations constrain generalisability. The evaluation cohort (N=100 patients, synthetic) may not capture the full heterogeneity of NHS production records—particularly legacy Read codes, abbreviated GP notes, and multi-provider longitudinal records spanning decades. The LLM-as-judge methodology carries inherent biases; Claude's near-ceiling scores (4.90/5.00) may partially reflect alignment between Claude's generation style and Qwen's quality preferences as judge. Validation against NHS clinician assessment on a stratified subset remains necessary before generalising to clinical deployment.

The cost analysis reflects AWS Bedrock list pricing as of July 2026. Cloud AI pricing evolves rapidly; volume commitments, Savings Plans, and regional endpoint availability (particularly the forthcoming London region Bedrock deployment) may substantially alter absolute costs whilst likely preserving relative model rankings given the magnitude of cost differentials observed (16× between Qwen and Claude).

Our sample of five models, whilst representative of major architecture families accessible through Bedrock, excludes models of potential NHS relevance: Gemini, Mistral Large, and domain-specific biomedical models. The benchmark framework is extensible, and we encourage the community to contribute additional evaluations. Similarly, our three task types (QA, reasoning, summarisation) do not exhaust the range of clinical NLP applications; document classification, entity linking, and temporal reasoning may exhibit different serialiser preferences that warrant separate investigation.

## 5.5 Future Directions

Four research priorities emerge. First, the adaptive serialisation strategy should be evaluated end-to-end: implementing the task-routing layer and measuring aggregate quality across mixed clinical workloads representative of NHS trust operations. The current study demonstrates the *potential* of task-specific optimisation through post-hoc analysis; a prospective evaluation with the routing layer deployed would quantify realised gains including any costs from misclassification of task type.

Second, extending FHIRBench to additional national profiles (AU Core, EU International Patient Summary) would establish whether task-specific serialiser preferences generalise across terminology systems and clinical documentation conventions, or whether format optimality is partially determined by profile-specific characteristics (extension density, coding system complexity, narrative inclusion patterns).

Third, the strong interaction between model capability and serialiser sensitivity suggests that format-aware fine-tuning—training models on specific serialisation formats—could reduce sensitivity for mid-tier models. If structured_markdown training could narrow Llama's 0.39-point range to Claude's 0.10, this would substantially improve the deployment proposition for open-weight models in NHS settings where data sovereignty concerns favour local inference.

Fourth, as NHS England's AI strategy matures, longitudinal benchmarking across model releases against a fixed evaluation framework would provide procurement-relevant evidence for AI governance. FHIRBench-UK, as an open and reproducible benchmark with demonstrated perturbation robustness, is positioned to serve this ongoing monitoring function—tracking whether successive model generations narrow or widen the serialiser sensitivity gap, and whether new architectures require updated serialisation recommendations.

Finally, the flattened_kv format's consistent underperformance across all contexts deserves mechanistic investigation. Its dot-notation structure (e.g., `entry[0].resource.code.coding[0].display`) fragments clinical concepts across hierarchical keys, disrupting the semantic coherence that all other formats preserve to varying degrees. Understanding precisely why this fragmentation degrades LLM comprehension—whether through tokenisation artefacts, attention span limitations, or loss of co-reference signals—would inform the design of next-generation FHIR serialisation strategies optimised for transformer architectures.

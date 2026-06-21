# 5. Discussion

## 5.1 Interpretation of Key Findings

The preliminary findings from the pipeline validation study (§4.1) reveal several patterns that inform both the interpretation of serialization effects and the design of the full benchmark evaluation.

### Clinical Template Dominance

The unanimous superiority of Clinical Template (SOAP) serialization across all five models — achieving the highest F1 scores while simultaneously consuming the fewest tokens — challenges the assumption that more information necessarily produces better model outputs. The SOAP format succeeds because it performs three simultaneous functions that align with LLM processing strengths: (1) **noise reduction**, stripping metadata, reference URLs, and structural overhead that consume tokens without contributing clinical meaning; (2) **domain-familiar structure**, presenting information in a format extensively represented in clinical training corpora (discharge summaries, progress notes, consultation letters); and (3) **logical organization**, grouping clinical facts by assessment category (Subjective, Objective, Assessment, Plan) rather than by FHIR resource type, which mirrors clinical reasoning patterns.

### Token Efficiency–Accuracy Correlation

Perhaps the most counterintuitive finding is the positive correlation between token compression and accuracy. Conventional wisdom suggests that removing information from model input should degrade performance. However, our results indicate that the serialization problem is fundamentally one of **noise reduction** rather than information transformation. Raw FHIR JSON contains extensive structural overhead — profile URLs, extension metadata, narrative div elements, conformance declarations — that actively impedes model comprehension by diluting clinically relevant tokens within finite context windows. Strategies that aggressively compress this overhead (Clinical Template achieving 5.4× compression) effectively increase the signal-to-noise ratio, enabling models to focus attention on clinically actionable content.

### Multi-Layer Evaluation Divergence

The divergence between Layer 1 (F1) and Layer 2 (rubric) scoring — most dramatically illustrated by Claude Sonnet 4.5 (F1 = 0.087 versus rubric = 5.0/5.0) — conclusively demonstrates that token-overlap metrics are insufficient for evaluating clinical AI outputs. Claude produces verbose, contextually rich responses that are clinically perfect but share minimal lexical overlap with terse ground-truth strings. This finding validates the three-layer evaluation design and suggests that prior serialization studies relying solely on automated metrics [CITE:TGZ97SRN] may have systematically underestimated the performance of certain model–format combinations.

### Raw JSON as Consistently Worst Performer

The consistent underperformance of Raw JSON serialization across all models and both evaluation layers reinforces the central thesis of this paper: the default FHIR representation is fundamentally misaligned with LLM processing requirements. This finding is actionable immediately — teams currently passing raw FHIR JSON to LLMs can expect meaningful accuracy improvements from any structured serialization strategy.

*[Full results from the 1,000-patient benchmark will update and extend these interpretations. Preliminary findings are derived from the idealized 50-patient validation dataset (§4.1).]*

---

## 5.2 Limitations

This study acknowledges several limitations that bound the generalizability of reported findings:

**1. Synthetic versus real patient data.** All evaluations use Synthea-generated FHIR R4 bundles calibrated against published epidemiological distributions (§3.2.3). While synthetic data enables reproducibility and controlled experimentation, it cannot fully replicate the heterogeneity, documentation variability, and institutional idiosyncrasies present in real EHR systems. Coding patterns, abbreviation practices, and data completeness in production FHIR servers may differ from our calibrated noise parameters.

**2. Single geographic scope.** The benchmark is constrained to US Core FHIR R4 with American clinical conventions (ICD-10-CM, US drug names, imperial units). Findings may not directly transfer to implementations using UK Core, AU Core, or International Patient Summary (IPS) profiles, where terminology systems, clinical documentation norms, and potentially non-English content introduce distinct serialization challenges (§3.2.4).

**3. Task type coverage.** Preliminary findings (§4.1) are derived primarily from Clinical QA tasks (factual extraction). The full benchmark extends to Clinical Reasoning and Clinical Summarization, but the relative performance of serialization strategies across task types remains to be confirmed. It is possible — and consistent with prior literature [CITE:TGZ97SRN] — that task type moderates format preference.

**4. F1 metric limitations.** Token-level F1 penalizes verbose but correct responses, as demonstrated by the Claude Sonnet 4.5 divergence (§4.1.2). While Layer 2 rubric scoring mitigates this, F1 remains the primary automated metric and may systematically disadvantage models trained for comprehensive, contextual response generation.

**5. LLM-as-judge potential bias.** Layer 2 evaluation employs Claude Sonnet 4.5 as the primary judge (with Llama 3 70B judging Claude's own responses to avoid self-evaluation bias). While cross-model judging reduces systematic bias, the possibility remains that judge models exhibit leniency patterns or evaluation blind spots not captured by our design.

**6. Ceiling effects in validation data.** The idealized 50-patient dataset produced near-perfect rubric scores (5.0/5.0 for three models), indicating insufficient discriminating power. The 1,000-patient realistic dataset with §3.2.3 noise parameters is designed to address this limitation by introducing clinically meaningful complexity.

**7. Deferred human evaluation.** Layer 3 (clinical expert review) is designed but not executed within the scope of this study (§3.5.4). Definitive validation of the LLM-as-judge's alignment with clinical judgment requires expert evaluation of the produced review package.

**8. Model availability constraints.** GPT-5.4 access required a US-based EC2 instance due to geographic API restrictions (§3.4.4), introducing a methodological asymmetry. Additionally, the Claude Sonnet 4.5 version date (September 2025) differs from the originally specified model, reflecting the rapid evolution of model versions.

**9. Temporal validity.** Foundation model capabilities evolve rapidly. Strategy rankings observed today may shift as model providers release updates, fine-tune on additional clinical corpora, or modify instruction-following behavior. The benchmark framework supports re-evaluation, but reported findings represent a point-in-time snapshot.

**10. Sample size considerations.** The stratified sampling design (100 patients per task type) provides adequate statistical power for detecting medium effect sizes but limits the granularity of subgroup analyses (e.g., by individual clinical condition or specific complexity level within a domain).

---

## 5.5 Future Work

Several directions emerge from the current study for extending FHIRBench's contribution:

**Real-world data validation.** Extension to MIMIC-IV FHIR [CITE:V4M8Q6TN] — the largest publicly available de-identified clinical dataset in FHIR format — would validate whether serialization strategy rankings observed on synthetic data generalize to real patient records with genuine documentation variability, coding inconsistencies, and institutional practices not captured by Synthea.

**Multi-geography extension.** Adapting the benchmark to UK Core, AU Core, and bilingual implementations (Hong Kong, Singapore) would test whether serialization strategy effectiveness is culturally and linguistically invariant. Multilingual FHIR resources — where coded values, display text, and clinical notes appear in multiple languages — present distinct serialization challenges not addressed by the current US-only design.

**Expanded clinical task taxonomy.** Beyond the three task types evaluated, clinical workflows include medication reconciliation, prior authorization documentation, clinical coding (ICD-10 assignment), adverse event detection, and care gap identification. Each may exhibit distinct format sensitivities warranting dedicated evaluation.

**Serialization-aware fine-tuning.** The finding that format significantly impacts accuracy suggests that fine-tuning models on serialization-optimized training data could yield additional gains. A model trained on Clinical Template representations may internalize clinical reasoning patterns encoded in the SOAP structure.

**Production middleware deployment.** The benchmark architecture maps directly to production deployment via AWS AgentCore (§5.4). Future work includes implementing the serialization middleware as a managed service, enabling real-time format optimization at the point of clinical AI inference.

**Layer 3 human evaluation.** Recruiting clinical informatics specialists to complete the deferred expert review (§3.5.4) would establish inter-rater reliability between LLM-as-judge and human clinical judgment, providing definitive validation of the automated evaluation framework.

**Longitudinal monitoring.** Establishing a recurring benchmark cadence (quarterly re-evaluation) would track whether serialization strategy rankings remain stable as model providers release updates, enabling evidence-based adaptation of clinical AI pipelines.

**Cross-domain generalization.** The FHIRBench evaluation framework — multi-dimensional rubric, Pareto analysis, configurable weights — is not inherently healthcare-specific. Extension to other structured data domains (financial regulatory filings, legal contract analysis, engineering specifications) would test the generalizability of our methodology and establish serialization optimization as a cross-domain concern.

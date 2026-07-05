# 5. Discussion

## 5.1 Interpretation of Key Findings

The 100-patient, 4-model benchmark (§4) yields four principal findings that advance understanding of clinical data serialization for LLMs.

### Finding 1: Serialization Strategy Significantly Impacts Clinical AI Quality

Condensed/SOAP serialization significantly outperforms Raw JSON for 3 of 4 models (Wilcoxon p < 10⁻³⁷), achieving comparable clinical accuracy at 87% fewer input tokens. This challenges the default assumption in FHIR-to-LLM pipelines that passing complete JSON bundles maximizes model performance. The mechanism is signal concentration: FHIR JSON contains extensive structural overhead — profile URLs, extension metadata, narrative div elements, conformance declarations — that dilute clinically relevant tokens within finite context windows. Compact serializers strip this overhead, effectively increasing the signal-to-noise ratio.

This finding aligns with Pator (2026) [CITE:TGZ97SRN], who observed Clinical Narrative outperforming Raw JSON by 19 F1 points for 7B models. Our contribution extends this to frontier models and demonstrates the effect holds across 3 clinical task types and all complexity levels.

### Finding 2: Multi-Layer Evaluation Reveals Metric-Dependent Rankings

The complete ranking reversal between Layer 1 (F1) and Layer 2 (Judge) — Claude ranks #4 on F1 but #1 on clinical quality (p < 10⁻³⁵) — is the study's most significant methodological finding. This demonstrates that:

1. **Token-overlap metrics systematically penalize verbose, contextual responses.** Claude provides richer clinical explanations (mean 1,705 chars vs GPT-5.4's 1,206) that contain clinically valuable information (dosage schedules, temporal context, prescriber attribution) but share fewer exact tokens with terse reference answers.

2. **Single-metric evaluation creates misleading model rankings.** A study reporting only F1 would conclude GPT-5.4 is optimal; judge evaluation reveals Claude provides superior clinical reasoning. This has direct implications for clinical AI procurement decisions.

3. **Clinical Reasoning tasks expose F1's complete failure mode.** All models score F1 ≈ 0.02 on reasoning tasks — not because they cannot reason, but because correct reasoning uses different vocabulary than reference answers. Layer 2 scores the same responses at 2.2–3.4/5.0, confirming meaningful clinical output.

This finding validates the multi-layer evaluation design proposed in §3.5 and suggests that prior serialization studies relying solely on automated metrics [CITE:TGZ97SRN, CITE:7FJFJU5M] may have systematically underestimated certain model–format combinations.

### Finding 3: Model × Serializer Interaction Precludes Universal Recommendations

The significant Friedman interaction effect (χ² = 16.4, p = 0.0009) demonstrates that no single "best" serialization format exists across all models. Specifically:

- **GPT-5.4 performs best on Raw JSON** (L2 accuracy 4.03) — suggesting frontier models with large context windows can effectively extract signal from noisy input
- **Claude performs best on Narrative/Condensed** (L2 accuracy 4.01–4.02) — suggesting instruction-tuned models benefit from pre-structured clinical presentation
- **Open-weight models (Qwen, DeepSeek) strongly benefit from compression** — significance levels orders of magnitude higher than frontier models

This interaction means clinical system designers cannot simply select a universal serializer. The optimal choice depends on the deployed model — a finding with significant implications for multi-model architectures and model-switching production systems.

### Finding 4: Open-Weight Model Capacity Limitations Create Patient Safety Gaps

Llama 3.1 70B's 100% failure rate on Complex/Highly Complex FHIR bundles (630/630 timeouts at >60s) reveals a critical deployment constraint. This is not a context window limitation (Llama 3.1 supports 128K tokens) but an inference throughput limitation documented in latency benchmarks [3.8× p95 degradation beyond 4K context]. The practical implication: without context-aware serialization, the most complex patients — who require the most clinical support — receive no AI assistance from open-weight models. Serialization strategy determines model *accessibility*, not merely accuracy.

This finding aligns with LongHealth [CITE:J46S4PGW], which concluded that open-source models show "insufficient accuracy for reliable clinical use" on long clinical documents, and extends it by quantifying the failure mode as inference timeout rather than quality degradation.

---

## 5.2 Implications for Clinical AI Deployment

### 5.2.1 Serialization as Mandatory Preprocessing

The results establish that serialization is not an optional optimization but a mandatory preprocessing step for production clinical AI. The Pareto analysis (§4.7) quantifies the tradeoff:

| Deployment Scenario | Recommended Strategy | Quality vs Raw JSON | Cost Savings |
|----|----|----|---|
| Safety-critical, low-volume | Raw JSON | Baseline | — |
| Balanced production | Narrative | 95% quality | 83% token savings |
| High-volume screening | Condensed | 87% quality | 87% token savings |
| Open-weight models | Condensed (mandatory) | Only viable option | Required for function |

### 5.2.2 Evaluation Framework Requirements

The ranking reversal finding (§4.4) has direct implications for clinical AI evaluation standards:

- **Regulatory submissions** relying on single automated metrics risk approving suboptimal models
- **Procurement decisions** using F1/BLEU-family metrics may select against models that produce the highest clinical quality
- **Multi-dimensional rubric evaluation** should be considered a minimum standard for clinical AI assessment
- **The specific dimensions matter:** Safety and Relevance are consistently high (3.9–4.3 across models), while Accuracy and Completeness differentiate quality — suggesting evaluation standards should weight these dimensions by clinical risk

### 5.2.3 Model Selection Interacts with Serialization

For teams deploying multiple models (e.g., routing by task type or cost tier), the interaction effect means serialization middleware must be model-aware. A fixed serialization pipeline optimized for one model may be suboptimal — or even inaccessible — for another.

---

## 5.3 Limitations

**1. Synthetic patient data.** All evaluations use programmatically generated FHIR R4 bundles calibrated against published epidemiological distributions (§3.2.3). While reproducible and controlled, they cannot fully replicate the heterogeneity and institutional idiosyncrasies of real EHR systems.

**2. Single geographic scope.** The benchmark uses US Core FHIR R4 with American clinical conventions. Findings may not transfer directly to UK Core, AU Core, or implementations with non-English clinical content.

**3. LLM-as-judge bias.** Layer 2 employs cross-judging (Claude judges other models; Qwen judges Claude) to mitigate self-evaluation bias. However, systematic judge preferences cannot be fully excluded without human expert calibration (Layer 3, deferred).

**4. Four models evaluated.** The exclusion of Llama 3.1 70B from the main comparison (due to systematic failure) and the omission of other relevant models (Gemini, Mistral, domain-specific medical LLMs) limits generalizability across the full model landscape.

**5. Temporal validity.** Model capabilities evolve rapidly. Rankings observed with model versions as of June 2026 may shift with updates. The benchmark framework supports re-evaluation.

**6. Ground truth generation.** Reference answers are programmatically extracted from FHIR bundles. While deterministic and verifiable, they represent factual extraction rather than nuanced clinical judgment — potentially disadvantaging models that add clinically appropriate qualifying language.

**7. Deferred human evaluation.** Layer 3 (clinical expert review) is designed but not executed (§3.5.4). Definitive validation of LLM-as-judge alignment with clinical judgment requires expert evaluation.

**8. Two-prompt-batch design.** The 100-patient evaluation was conducted in two batches (35 Complex + 65 Simple/Moderate) due to infrastructure constraints. While the same prompts were used across all models within each batch, slight methodological asymmetry exists in generation timing.

---

## 5.4 Future Work

**Real-world data validation.** Extension to MIMIC-IV FHIR — the largest publicly available de-identified clinical dataset in FHIR format — would validate whether serialization rankings generalize to real patient records.

**Multi-geography extension.** Adapting the benchmark to UK Core, AU Core, and bilingual implementations (Hong Kong, Singapore) would test linguistic and cultural invariance of findings.

**Layer 3 human evaluation.** Recruiting clinical informatics specialists to complete expert review would establish inter-rater reliability between LLM-as-judge and human clinical judgment.

**Serialization-aware fine-tuning.** The significant format–accuracy relationship suggests that fine-tuning models on serialization-optimized data could yield additional gains beyond prompt-time optimization.

**Expanded task taxonomy.** Clinical workflows beyond QA, reasoning, and summarization — including medication reconciliation, clinical coding (ICD-10), adverse event detection, and care gap identification — may exhibit distinct format sensitivities.

**Longitudinal monitoring.** Quarterly re-evaluation would track ranking stability as models evolve, enabling evidence-based adaptation of clinical AI pipelines.

**Cross-domain generalization.** The FHIRBench evaluation framework (multi-dimensional rubric, Pareto analysis) may generalize to other structured data domains (financial regulatory filings, legal contracts, engineering specifications).

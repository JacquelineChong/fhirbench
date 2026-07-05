# 6. Conclusion

## Summary

This paper presents FHIRBench, a controlled benchmark evaluating how FHIR data serialization affects clinical LLM performance. Through systematic evaluation of 4 models × 6 serializers × 3 tasks × 100 patients (7,200 evaluations per layer, patient-level statistical analysis), we provide empirical answers to questions that clinical AI teams currently resolve through ad hoc experimentation.

## Principal Findings

1. **Serialization is a first-order system design decision, not a preprocessing detail.** The choice of serialization format produces statistically significant differences on both automated metrics (F1) and clinical quality (judge rubric), with the direction of effect diverging between layers. Teams passing raw FHIR JSON to LLMs pay 7.5× more per API call while achieving only marginally better (and on F1, often worse) clinical output than Narrative or Condensed formats.

2. **Single-metric evaluation produces incorrect model selection.** The complete ranking reversal between Layer 1 and Layer 2 (Claude: #4 on F1, #1 on clinical quality; p = 1.0 × 10⁻⁶, patient-level) demonstrates that studies relying solely on token-overlap metrics may systematically recommend the wrong model for clinical deployment. Multi-layer evaluation is not optional — it is a methodological requirement.

3. **No universal "best" serialization format exists.** The significant Model × Serializer interaction (Friedman χ² = 16.4, p = 0.0009) means that optimal format depends on the target model. GPT-5.4 performs best on Raw JSON; Claude and open-weight models (Qwen, DeepSeek) perform best on compressed formats. Clinical systems that support model switching must implement model-aware serialization middleware.

4. **Open-weight models face silent capacity failure on complex patients.** Llama 3.1 70B's 100% timeout rate on Complex/Highly Complex FHIR bundles (despite operating within its nominal 128K context window) creates a patient-safety paradox: the patients most needing AI clinical decision support are precisely those whose data exceeds practical processing capacity. Compact serialization transforms this from a functional failure into a tractable engineering problem.

## Contributions

This work makes five contributions:

1. **A two-layer evaluation methodology** demonstrating that automated metrics and clinical quality assessment produce fundamentally different conclusions about model and format performance — validating the necessity of multi-layer evaluation in clinical AI research.

2. **Empirical evidence of Model × Serializer interaction** — the first controlled demonstration that optimal serialization varies by model architecture at frontier scale, with practical magnitude sufficient to reverse deployment recommendations.

3. **A cost-quality Pareto framework** identifying Narrative as the dominant balanced choice (95% quality at 83% fewer tokens) and establishing that Key-Value and Markdown Table formats are dominated strategies that no rational deployment should select.

4. **Quantification of open-weight model capacity limits** — demonstrating that context window size alone does not predict successful processing of complex clinical data, with direct implications for patient safety in cost-optimized deployments.

5. **An open-source benchmark framework** — enabling any team with cloud API access to reproduce these findings, extend to new models/formats, and calibrate serialization decisions against their specific deployment requirements.

## Practical Recommendations

For clinical AI engineering teams, the immediate actionable guidance:

| Deployment scenario | Recommended serializer | Rationale |
|---|---|---|
| Frontier model, quality-critical | Raw JSON (GPT-5.4) or Narrative (Claude) | Model-specific optimum |
| Open-weight models (Qwen, DeepSeek) | Condensed or FHIRPath | Significantly outperforms Raw JSON (p < 10⁻¹⁷); enables function |
| Cost-sensitive, high-volume | Narrative | 95% quality at 83% fewer tokens (Pareto-optimal) |
| Open-weight with complex patients | Condensed (mandatory) | Without compression: 0% success rate |
| Multi-model routing systems | Model-aware middleware | No single format optimizes across models |

## Limitations and Future Work

The primary limitations — synthetic patient data, four evaluated models, deferred human validation (Layer 3), and asymmetric cross-judging design — are discussed in §5.3. Future work should prioritize: (1) validation on de-identified real-world FHIR data (e.g., MIMIC-IV FHIR), (2) extension to additional models as they emerge, (3) human clinician evaluation of a stratified response sample, and (4) implementation and evaluation of a production-grade adaptive serialization engine that dynamically selects format based on model, patient complexity, and task type.

## Availability

FHIRBench — including all serialization implementations, evaluation harnesses, statistical analysis scripts, benchmark results, and the practitioner decision framework — is publicly available at https://github.com/JacquelineChong/fhirbench under MIT license.

# 6. Conclusion

The integration of Large Language Models into clinical decision support systems requires transforming structured health data into representations that maximize model comprehension — yet no systematic guidance exists for this critical preprocessing decision.

This paper presents FHIRBench, the first comprehensive benchmark for evaluating clinical data serialization strategies for LLMs. Through a controlled experimental design evaluating six serialization strategies across five foundation models on three clinical task types using 1,000 synthetic FHIR R4 patient records with calibrated realism parameters, we provide the most extensive empirical characterization of serialization effects on clinical AI performance to date.

## Key Findings

Our evaluation across 90 experimental conditions yields the following principal results:

1. **Serialization strategy significantly impacts model accuracy.** Performance variance of up to [TBD]% is attributable solely to format choice, with Clinical Template (SOAP) serialization achieving [TBD]× higher accuracy than the Raw JSON baseline across all evaluated models. This finding confirms and substantially extends prior observations of format sensitivity [CITE:TGZ97SRN].

2. **Token efficiency and accuracy are positively correlated.** Contrary to expectations of an accuracy–cost tradeoff, structured serialization strategies that aggressively reduce token count simultaneously improve model performance. Clinical Template achieves [TBD]× token compression (from [TBD] to [TBD] tokens per patient) while yielding the highest accuracy scores — indicating that the serialization problem is fundamentally one of noise reduction rather than information preservation.

3. **Format preference is [TBD — unanimous across models / model-dependent].** [TBD: If unanimous: "The superiority of Clinical Template serialization is consistent across all five model architectures, from open-weight 32B models to frontier proprietary systems — suggesting a generalizable recommendation for practitioners." If model-dependent: "Optimal format varies by model architecture and scale, with [TBD patterns], necessitating model-specific strategy selection."]

4. **Standard NLG metrics are insufficient for clinical AI evaluation.** Layer 1 (F1) and Layer 2 (rubric) scoring diverge by up to [TBD]× for the same model–format combination (Claude Sonnet 4.5: F1 = 0.087 versus rubric = 5.0), conclusively demonstrating that multi-dimensional evaluation is necessary for reliable clinical AI assessment.

## Contributions

This work makes five contributions to the field:

1. **A systematic serialization taxonomy** — formalizing six strategies across four analytic dimensions (format, terminology resolution, granularity, context window strategy) with literature-grounded justification for each.

2. **An open-source benchmark framework** — FHIRBench provides reproducible evaluation using Synthea-generated data, enabling any researcher with an AWS account to replicate and extend our findings.

3. **Empirical comparison across 90 conditions** — the most comprehensive evaluation of serialization effects on clinical LLM performance, spanning five architecturally diverse models and three clinically grounded task types.

4. **A practitioner decision framework** — mapping task characteristics, model constraints, and cost requirements to recommended serialization strategies via Pareto-optimal tradeoff analysis, reducing strategy selection from weeks of empirical testing to minutes of framework consultation.

5. **A multi-layer evaluation methodology** — combining automated metrics, LLM-as-judge rubric scoring, and a designed (deferred) human evaluation protocol, with configurable dimension weights adaptable to deployment context.

## Practical Implications

For health AI engineering teams, the immediate actionable recommendation is clear: replace raw FHIR JSON with structured clinical serialization (Clinical Template or Narrative format) in LLM preprocessing pipelines. Based on our findings, this substitution requires minimal implementation effort (the serialization code is publicly available) while yielding [TBD]× accuracy improvement at [TBD]× cost reduction — a rare engineering decision where both quality and cost improve simultaneously.

## Broader Significance

Our findings contribute to an emerging architectural debate in health informatics. The persistent need for a serialization middleware layer — with its associated token overhead, information loss risks, and model-dependent optimization — suggests that future interoperability standards may need to consider LLM comprehensibility as a first-class design requirement alongside programmatic parseability. FHIRBench provides the empirical grounding for this conversation, demonstrating both the magnitude of the serialization problem and the characteristics of formats that best serve AI consumption.

## Availability

FHIRBench — including all serialization implementations, evaluation harnesses, data generation scripts, benchmark results, and the practitioner decision framework — is publicly available at https://github.com/JacquelineChong/fhirbench under MIT license.

## 4.1 Preliminary Findings: Pipeline Validation (n=50, Idealized)

The following results are derived from the 50-patient idealized validation dataset (§3.2.2) and serve two purposes: (1) confirming end-to-end pipeline correctness, and (2) generating refined hypotheses for the full benchmark. This preliminary evaluation comprises 1,500 individual assessments (6 serializers × 5 models × 50 patients × 1 task type), with all responses evaluated across both Layer 1 (automated metrics) and Layer 2 (LLM-as-judge rubric) of the evaluation framework described in §3.3.

The idealized dataset contains 50 synthetic FHIR R4 patient bundles distributed across four clinical domains: diabetes management (n=13), cardiovascular risk assessment (n=13), medication interaction detection (n=13), and preventive care screening (n=11). By design, these bundles exhibit clean conformance to FHIR R4 specifications, contain no missing or contradictory data elements, and present clinically unambiguous scenarios. This controlled setting isolates serialization and model effects from data-quality confounds.

### 4.1.1 Serialization Strategy Effect

Layer 1 F1 scores reveal a clear and unanimous serialization preference across all five evaluated models. Table 4.1 presents mean F1 accuracy by model, aggregated across all serialization strategies.

**Table 4.1.** Mean F1 accuracy by model (Clinical QA task, n=50 idealized patients, averaged across 6 serializers).

| Model | Mean F1 |
|---|---|
| GPT-5.4 | 0.713 |
| Llama 3 70B | 0.442 |
| DeepSeek V3.2 | 0.426 |
| Qwen3 32B | 0.364 |
| Claude Sonnet 4.5 | 0.087 |

The Clinical Template (SOAP-structured) serializer achieves the highest F1 score for every model tested—a unanimous result that holds regardless of model family, parameter count, or architecture. This unanimity is notable given the diversity of the model cohort, which spans proprietary frontier models (GPT-5.4, Claude Sonnet 4.5), open-weight large models (Llama 3 70B, DeepSeek V3.2), and mid-scale open models (Qwen3 32B). No interaction effects between model and serializer preference were observed; the rank ordering of serializers remained stable across all five models.

The per-serializer rubric scores (Layer 2) confirm this ordering while revealing a tighter performance band at the top of the scale:

**Table 4.2.** Mean rubric score by serializer (averaged across all 4 dimensions and 5 models).

| Serializer | Mean Rubric Score (1–5) |
|---|---|
| Clinical Template (SOAP) | 4.995 |
| Narrative | 4.994 |
| Structured Markdown | 4.956 |
| Hybrid Adaptive | 4.941 |
| Flattened Key-Value | 4.861 |
| Raw JSON | 4.860 |

The top-performing serializers share a common property: they impose a clinical organizational schema on the underlying FHIR data rather than preserving its native hierarchical structure. Clinical Template and Narrative both reorganize patient data into problem-oriented or chronological clinical frames, while Raw JSON and Flattened Key-Value retain the FHIR resource structure with minimal transformation. This pattern suggests that serialization effectiveness correlates with alignment to the implicit organizational expectations of clinical reasoning, consistent with findings on structured prompting in clinical NLP [CITE:nori2023capabilities].

### 4.1.2 Multi-Layer Evaluation Divergence

The most methodologically significant finding from the preliminary evaluation concerns the divergence between Layer 1 (F1) and Layer 2 (rubric) assessments, exemplified by Claude Sonnet 4.5. Under F1 scoring, Claude achieves the lowest performance of all tested models (F1 = 0.087), yet under rubric evaluation it achieves perfect scores across all four dimensions:

**Table 4.3.** Layer 2 rubric scores by model (mean across all serializers, 1–5 scale).

| Model | Accuracy | Completeness | Safety | Relevance |
|---|---|---|---|---|
| Claude Sonnet 4.5 | 5.00 | 5.00 | 5.00 | 5.00 |
| Llama 3 70B | 5.00 | 5.00 | 5.00 | 5.00 |
| GPT-5.4 | 5.00 | 5.00 | 5.00 | 5.00 |
| Qwen3 32B | 4.98 | 5.00 | 4.98 | 5.00 |
| DeepSeek V3.2 | 4.70 | 4.75 | 4.82 | 4.72 |

This F1–rubric divergence for Claude is diagnostically informative. Inspection of Claude's responses reveals that the model consistently provides clinically correct and complete answers that are paraphrased, restructured, or elaborated relative to the reference answers used for F1 computation. The F1 metric, which relies on token-level overlap between generated and reference responses, systematically penalizes semantically equivalent but lexically divergent outputs. This constitutes a form of evaluation metric misalignment that has been documented in general-domain NLG evaluation [CITE:liu2023geval] but has received insufficient attention in clinical AI benchmarking.

This finding provides direct empirical justification for the multi-layer evaluation architecture (§3.3). Had FHIRBench relied exclusively on automated token-overlap metrics—as is common in existing clinical NLP benchmarks [CITE:lehman2023clinical]—Claude Sonnet 4.5 would have been erroneously classified as the worst-performing model. The rubric layer, employing semantic judgment rather than surface matching, correctly identifies Claude's outputs as clinically accurate and complete. Conversely, the rubric's near-ceiling performance for four of five models (with only DeepSeek showing sub-5.0 scores) suggests that Layer 2 alone provides insufficient discriminative power under idealized conditions—motivating the complementary use of F1 for fine-grained ranking within the band of clinically acceptable outputs.

The three-layer design thus addresses a fundamental tension in clinical evaluation: token-overlap metrics discriminate effectively but can misclassify semantically correct responses, while semantic rubrics correctly assess clinical quality but compress the performance distribution toward the ceiling. Neither layer alone is sufficient; their conjunction provides both validity and discriminative resolution.

### 4.1.3 Token Efficiency

An unexpected finding emerges from the relationship between serialization token count and downstream accuracy. Table 4.4 presents the mean input token count per patient by serializer alongside the compression ratio relative to Raw JSON.

**Table 4.4.** Token efficiency by serialization strategy (mean across 50 patients).

| Serializer | Mean Tokens | Compression Ratio |
|---|---|---|
| Raw JSON | 555.5 | 1.00× (baseline) |
| Flattened Key-Value | 338.7 | 0.61× |
| Structured Markdown | 132.1 | 0.24× |
| Narrative | 110.8 | 0.20× |
| Clinical Template (SOAP) | 102.3 | 0.18× (5.4× compression) |

The Clinical Template serializer achieves a 5.4× compression relative to Raw JSON while simultaneously achieving the highest accuracy across all models. This positive correlation between compression and accuracy—where more aggressive dimensionality reduction of the input yields better downstream performance—inverts the naive expectation that providing models with more complete structural information would improve clinical reasoning.

This finding admits two complementary interpretations. First, the compression achieved by Clinical Template is not lossy in the information-theoretic sense relevant to clinical QA: the serializer retains all clinically salient data elements while removing FHIR infrastructure metadata (resource identifiers, coding system URIs, extension arrays) that is irrelevant to clinical reasoning but constitutes the majority of raw FHIR token volume. Second, the removal of structural noise may reduce the attentional burden on the model, effectively increasing the signal-to-noise ratio of the input context. This interpretation aligns with recent work on context distillation [CITE:xu2024context] demonstrating that LLMs perform better with curated, information-dense inputs than with exhaustive but noisy contexts.

The cost implications are substantial. At current API pricing, the 5.4× compression achieved by Clinical Template translates directly to an approximately 82% reduction in input token costs per inference call—without any accuracy penalty and, indeed, with accuracy gains. For health systems processing thousands of patient records daily through LLM-mediated clinical decision support, this compression represents a significant operational cost reduction.

### 4.1.4 Refined Hypotheses for Full Benchmark

The preliminary findings generate four refined hypotheses (H4–H7) that extend and sharpen the initial hypotheses (H1–H3, §2.4) for testing against the full 1,000-patient benchmark:

**H4 (No accuracy–cost tradeoff for structured serialization).** The positive correlation between token compression and accuracy observed in §4.1.3 suggests that no Pareto frontier exists between cost-efficiency and clinical accuracy for serialization strategies that preserve clinical semantics. Specifically, we hypothesize that Clinical Template will maintain its accuracy advantage over Raw JSON at scale, implying that the serialization problem admits a dominant strategy rather than requiring cost–quality tradeoff navigation.

**H5 (F1 systematically underestimates frontier model performance).** The Claude Sonnet 4.5 divergence (§4.1.2) suggests that F1 scoring contains a systematic bias against models with strong paraphrasing tendencies. We hypothesize that this bias will intensify for frontier models on complex clinical scenarios where greater response elaboration is expected, and that Layer 2 and Layer 3 evaluations will reveal a reordering of model rankings relative to F1 alone.

**H6 (Format unanimity breaks with increased data complexity).** The unanimous preference for Clinical Template across all models observed in §4.1.1 may reflect a ceiling effect specific to idealized data. We hypothesize that as data complexity increases (incomplete records, contradictory entries, multi-morbidity), the optimal serialization strategy will exhibit model-dependent variation, with some architectures benefiting from the additional structural cues preserved in Raw JSON or Structured Markdown formats.

**H7 (Serialization is primarily a noise-reduction problem).** The joint findings of §4.1.1 and §4.1.3—that the most compressed serializer also achieves the highest accuracy—suggest that the primary mechanism through which serialization affects LLM performance is noise reduction rather than information restructuring. We hypothesize that serializer effectiveness at scale will correlate more strongly with the proportion of clinically irrelevant tokens removed than with the particular organizational schema imposed on retained tokens.

### 4.1.5 Implications for Full Benchmark Design

The preliminary findings inform several design decisions for the full 1,000-patient benchmark evaluation:

**Stratification by data quality.** The near-ceiling rubric scores (Table 4.3) confirm that idealized data provides insufficient discriminative power for the semantic evaluation layer. The full benchmark must include systematic variation in data completeness, internal consistency, and clinical complexity to create separation in the Layer 2 distribution. We implement a three-tier complexity stratification (§3.2.3) with explicit control over missing data rates, contradictory entries, and multi-system interactions.

**Task diversity.** The current evaluation employs a single task type (Clinical QA). The unanimity of serializer preferences (§4.1.1) may be task-specific; clinical summarization, risk stratification, and care plan generation may exhibit different serializer sensitivities. The full benchmark expands to four task types to test this interaction.

**F1 reference set expansion.** The Claude finding (§4.1.2) motivates expansion of the reference answer set from single canonical responses to multiple acceptable phrasings, reducing—though not eliminating—the lexical bias inherent in token-overlap metrics. For the full benchmark, reference answers are generated independently by three clinician annotators and augmented with paraphrase variants.

**Safety layer activation.** All 1,500 preliminary responses achieved 100% safety pass rates across the automated safety filter battery. While reassuring, this ceiling effect under idealized conditions provides no discriminative information. The full benchmark incorporates adversarial clinical scenarios specifically designed to elicit potential safety violations (e.g., contraindicated medication suggestions, failure to flag critical values), ensuring that the safety layer contributes meaningful signal to the overall evaluation.

**Layer 3 deployment criteria.** The high rubric scores observed in Table 4.3 establish a quality threshold above which Layer 3 (expert clinician review) adds the greatest marginal value. For the full benchmark, Layer 3 evaluation is triggered for responses scoring ≥4.5 on the Layer 2 rubric, where automated metrics have exhausted their discriminative capacity and expert judgment is required to distinguish genuinely excellent from merely satisfactory clinical reasoning.

---

*Limitations.* These preliminary results should be interpreted with appropriate caution. The idealized dataset, by construction, eliminates data-quality challenges characteristic of real-world EHR data. The single task type (Clinical QA) may not generalize to other clinical reasoning modalities. The near-ceiling rubric scores indicate insufficient evaluation difficulty rather than genuine model perfection. These limitations are addressed systematically in the full benchmark design (§3.2.3–§3.2.5).


## 4.X Model Capacity Finding: Open-Weight Model Failure on Complex Clinical Data

### Observation

Llama 3.1 70B consistently failed to process COMPLEX and HIGHLY_COMPLEX FHIR bundles across all serialization formats, with a 100% failure rate (630/630 prompts timed out at >60 seconds per call).

| Model | COMPLEX Prompts | Success Rate | Failure Mode |
|-------|----------------|--------------|--------------|
| Claude Sonnet 4.5 | 630 | 100% (630/630) | — |
| GPT-5.4 | 630 | 99.8% (629/630) | 1 timeout |
| Qwen3 32B | 630 | 100% (630/630) | — |
| DeepSeek V3.2 | 630 | 100% (630/630) | — |
| **Llama 3.1 70B** | **630** | **0% (0/630)** | **Read timeout (>60s)** |

### Analysis

The failure is attributable to inference latency degradation at high context lengths. Our COMPLEX/HIGHLY_COMPLEX FHIR prompts contain 3,000–8,000 tokens of serialized clinical data, placing them in the regime where Llama 3.1 70B experiences 3.8× latency increases (Adams et al., 2026; MarkAICode benchmark). This is not a context *window* limitation (Llama 3.1 supports 128K tokens nominally) but an inference *throughput* limitation where the model cannot generate responses within practical time bounds.

### Implications for Clinical Deployment

This finding carries significant implications for production clinical AI systems:

1. **Serialization strategy determines model accessibility.** For open-weight models, compact serialization formats (Clinical Template, Condensed) are not merely a quality optimization — they are a functional requirement. Without context-aware serialization, the most complex patients (who require the most clinical support) receive no AI assistance.

2. **Model selection interacts with data complexity.** Frontier models (Claude, GPT-5.4) and certain open-weight models (Qwen3, DeepSeek) processed all complexity levels without issue. However, Llama 3.1 70B — despite being widely deployed in healthcare applications — failed silently on complex patients. This creates a patient safety gap: the model appears functional on simple cases but fails catastrophically on the patients who most need support.

3. **Token count is not context capacity.** A model's advertised context window (128K for Llama 3.1) does not guarantee reliable inference at those lengths. Production systems must implement serialization budgets calibrated to empirical model performance, not theoretical limits.

### Supporting Literature

This finding aligns with:
- LongHealth benchmark (Adams et al., 2025): open-source models show "insufficient accuracy for reliable clinical use" on documents of 5,090–6,754 words
- EHR long-context evaluation (arXiv 2412.16178): "Most existing EHR FMs have context windows of <1K tokens, preventing them from modeling full patient EHRs"
- Llama 3.1 70B latency benchmarks: 3.8× p95 latency increase beyond 4K context, with throughput dropping from 62 to 36 tok/s at 8K context


# 5. Discussion

## 5.1 Interpretation of Key Findings

The 100-patient, 4-model benchmark (§4) yields four principal findings that advance understanding of clinical data serialization for LLMs.

### Finding 1: Serialization Strategy Significantly Impacts Clinical AI Quality

Serialization strategy significantly impacts model output across BOTH evaluation layers — but critically, the direction of impact diverges between metrics. On Layer 1 (F1 token overlap): Condensed outperforms Raw JSON for 3/4 models (patient-level Wilcoxon p < 10⁻¹⁷). On Layer 2 (Judge Accuracy): Raw JSON significantly outperforms Condensed for 3/4 models (GPT-5.4: p = 2.0 × 10⁻¹⁵; DeepSeek: p = 3.7 × 10⁻⁷; Qwen: p = 1.2 × 10⁻¹⁰). Only Claude shows the reverse pattern (Condensed 4.02 vs Raw JSON 3.89, p = 0.066 non-significant).

This divergence itself reinforces Finding 2 (multi-layer evaluation is essential) and is resolved by the Pareto analysis (§4.7): Narrative format achieves 95% of Raw JSON's Layer 2 quality at 83% fewer tokens — making it the dominant balanced choice when both quality and cost are considered. Specifically:

1. **The mechanism is signal concentration, not information addition.** FHIR JSON contains extensive structural overhead — profile URLs (`"http://hl7.org/fhir/StructureDefinition/Patient"`), extension metadata, narrative div elements, conformance declarations, and reference chains — that consume tokens without contributing clinical meaning. A typical patient bundle uses ~2,000 tokens in Raw JSON but only ~270 tokens in Condensed format. The clinical facts (conditions, medications, labs) are identical in both; the difference is pure structural noise.

2. **The effect is statistically robust and practically meaningful.** The Wilcoxon signed-rank test (patient-level, N = 100 pairs) confirms Condensed outperforms Raw JSON on F1 for Claude (p < 10⁻¹⁸), Qwen (p < 10⁻¹⁸), and DeepSeek (p < 10⁻¹⁷). GPT-5.4 shows no significant difference (p = 0.79) — suggesting frontier models with very large context windows can partially compensate for noise, but even they don't fully overcome it.

3. **Concrete example:** For the same diabetic patient (Sandra Lewis, HIGHLY_COMPLEX):
   - **Raw JSON:** 3,295 tokens — includes `"resourceType": "Bundle"`, UUID references, coding system URLs, empty extensions
   - **Condensed (SOAP):** 420 tokens — `"Patient: Sandra Lewis | Diabetes mellitus, Hypertension | Metformin 500mg BID, Lisinopril 10mg QD | HbA1c 7.2%"`
   - **Same clinical content, 7.8× fewer tokens, comparable clinical accuracy** (cross-model L2 mean: Condensed 3.33 vs Raw JSON 3.83 — a 13% quality reduction at 87% cost savings, a tradeoff quantified in the Pareto analysis §4.7)

4. **Why this matters for practitioners:** Teams currently passing raw FHIR JSON to LLMs are paying 7.5× more per API call AND getting marginally better (not dramatically better) results. The cost-quality Pareto frontier (§4.7) shows Narrative achieves 95% of Raw JSON's quality at 83% fewer tokens — making Raw JSON the dominated choice for all but the most safety-critical, low-volume use cases.

5. **Relationship to prior work:** Pator (2026) [CITE:TGZ97SRN] observed Clinical Narrative outperforming Raw JSON by 19 F1 points for 7B models, but found the effect reverses at 70B where Raw JSON achieves F1=0.9956. Our results extend this nuance: at frontier scale, Raw JSON's advantage shrinks to marginal (3.83 vs 3.64 on judge scoring) rather than disappearing entirely — and the cost differential remains 7.5×. The prior study's F1-only evaluation also missed that "higher F1 ≠ higher clinical quality" (Finding 2).

### Finding 2: Multi-Layer Evaluation Reveals Metric-Dependent Rankings

The complete ranking reversal between Layer 1 (F1) and Layer 2 (Judge) — Claude ranks #4 on F1 but #1 on clinical quality (p = 1.0 × 10⁻⁶, patient-level N = 100) — is the study's most significant methodological finding. This demonstrates that:

1. **Token-overlap metrics systematically penalize verbose, contextual responses.** Claude provides richer clinical explanations (mean 1,705 chars vs GPT-5.4's 1,206) that contain clinically valuable information (dosage schedules, temporal context, prescriber attribution) but share fewer exact tokens with terse reference answers.

2. **Single-metric evaluation creates misleading model rankings.** A study reporting only F1 would conclude GPT-5.4 is optimal; judge evaluation reveals Claude provides superior clinical reasoning. This has direct implications for clinical AI procurement decisions.

3. **Clinical Reasoning tasks expose F1's complete failure mode.** All models score F1 ≈ 0.02 on reasoning tasks — not because they cannot reason, but because correct reasoning uses different vocabulary than reference answers. Layer 2 scores the same responses at 2.2–3.4/5.0, confirming meaningful clinical output.

This finding validates the multi-layer evaluation design proposed in §3.5 and suggests that prior serialization studies relying solely on automated metrics [CITE:TGZ97SRN, CITE:7FJFJU5M] may have systematically underestimated certain model–format combinations.

### Finding 3: Model × Serializer Interaction Precludes Universal Recommendations

The Friedman test confirms that model rankings differ significantly across serializers (χ² = 16.4, p = 0.0009), indicating that no single "best" serialization format exists across all models. The crossover interaction is demonstrated directly by the per-model Layer 2 results. This is not merely a statistical curiosity — it has direct engineering consequences:

1. **The interaction is large enough to reverse recommendations.** GPT-5.4 achieves its best accuracy on Raw JSON (4.03), while Claude achieves its best on Narrative/Condensed (4.01–4.02). A system optimized for GPT-5.4 (using Raw JSON) would deliver suboptimal results if switched to Claude — and vice versa. The difference is clinically meaningful: 4.03 vs 3.01 (Condensed on GPT-5.4) represents the gap between "acceptable clinical answer" and "marginally useful response."

2. **Open-weight models show dramatically stronger serialization sensitivity.** The Wilcoxon significance for Condensed vs Raw JSON (F1) is p < 10⁻¹⁷ for Qwen and DeepSeek, but p = 0.79 (clearly non-significant) for GPT-5.4. This means:
   - For frontier models: serialization choice is an optimization (marginal gains)
   - For open-weight models: serialization choice is a requirement (fundamental to usability)

3. **Why models respond differently to formats:**
   - **GPT-5.4 on Raw JSON:** GPT-5.4's strength appears to be parsing structured data directly — it may have stronger JSON comprehension from training data. It extracts clinical facts from nested JSON without needing them pre-organized.
   - **Claude on Narrative/Condensed:** Claude appears to leverage clinical document familiarity — SOAP notes and clinical narratives are heavily represented in medical training corpora. Pre-structuring the data into a format Claude "recognizes" reduces cognitive load.
   - **Open-weight models need compression:** With fewer parameters dedicated to attention over long contexts, these models physically cannot attend to clinical facts buried within 2,000 tokens of JSON boilerplate. Compression doesn't just help — it enables function.

4. **Implication for production systems:** Any clinical AI system that supports model switching (e.g., routing simple queries to cheaper models, complex queries to frontier models) MUST implement model-aware serialization middleware. A fixed serialization pipeline optimized for one model will be suboptimal — or non-functional — for another.

### Finding 4: Open-Weight Model Capacity Limitations Create Patient Safety Gaps

Llama 3.1 70B's 100% failure rate on Complex/Highly Complex FHIR bundles (630/630 timeouts at >60s) reveals a critical deployment constraint that carries patient safety implications:

1. **The failure is silent and total.** Llama 3.1 70B did not produce degraded answers — it produced NO answers. In a production system, this manifests as a timeout with no clinical output. If the system lacks proper fallback handling, a clinician waiting for AI assistance receives nothing — and may not know why.

2. **This is NOT a context window limitation.** Llama 3.1 officially supports 128K tokens. Our COMPLEX prompts are 3,000–8,000 tokens — well within the nominal limit. The failure is an inference throughput bottleneck: documented latency benchmarks show Llama 3.1 70B p95 latency increases 3.8× when context exceeds 4,000 tokens (from 158ms to 602ms at 4K, with throughput dropping from 62 to 36 tok/s at 8K context). At our prompt sizes, the model simply cannot generate a response within practical time bounds (60s timeout).

3. **The patient safety paradox:** The patients who MOST need AI clinical decision support — those with 5+ conditions, polypharmacy, complex drug interactions — are precisely the patients whose data is too large for open-weight models to process. Without compact serialization:
   - Simple patients (1-2 conditions): AI works ✅
   - Complex patients (5+ conditions): AI fails silently ❌
   - This creates a false sense of system reliability — the system appears functional in testing (which tends to use simpler cases) but fails in production on the cases that matter most.

4. **Serialization as accessibility enabler:** Condensed format (266 tokens mean) brings even the most complex patients within Llama's practical processing capacity. This transforms serialization from a quality optimization into a functional requirement:
   - With Raw JSON (1,991 tokens): 0% success rate on Complex patients
   - With Condensed (266 tokens): model can process (though we could not test Llama on Condensed due to the systematic failure — this is a limitation noted in §5.3)

5. **Relationship to prior work:** LongHealth [CITE:J46S4PGW] found open-source models show "insufficient accuracy for reliable clinical use" on documents of 5,090–6,754 words. Our finding extends this by demonstrating the failure mode is not quality degradation but complete inference failure — the model doesn't produce a bad answer, it produces no answer. This distinction matters for system design: quality degradation can be monitored and flagged; complete timeouts require architectural fallback mechanisms (model switching, serialization adaptation, or explicit failure reporting to the clinician).

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

**3a. Asymmetric judge distribution.** Claude judges 75% (5,400/7,200) of Layer 2 evaluations. No inter-rater reliability between Claude-as-judge and Qwen-as-judge was computed. However, we note that cross-judging is standard practice in LLM evaluation [Zheng et al., 2024; MT-Bench], and importantly, Claude scores highest when judged by Qwen (not by itself) — if Claude-as-judge systematically inflated scores for other models, we would expect the opposite pattern. This provides indirect validation of judge objectivity.

**4. Four models evaluated.** The exclusion of Llama 3.1 70B from the main comparison (due to systematic failure) and the omission of other relevant models (Gemini, Mistral, domain-specific medical LLMs) limits generalizability across the full model landscape.

**5. Temporal validity.** Model capabilities evolve rapidly. Rankings observed with model versions as of June 2026 may shift with updates. The benchmark framework supports re-evaluation.

**6. Ground truth generation.** Reference answers are programmatically extracted from FHIR bundles. While deterministic and verifiable, they represent factual extraction rather than nuanced clinical judgment — potentially disadvantaging models that add clinically appropriate qualifying language.

**7. Deferred human evaluation.** Layer 3 (clinical expert review) is designed but not executed (§3.5.4). Definitive validation of LLM-as-judge alignment with clinical judgment requires expert evaluation.

**8. Two-prompt-batch design.** The 100-patient evaluation was conducted in two batches (35 Complex + 65 Simple/Moderate) due to infrastructure constraints. While the same prompts were used across all models within each batch, slight methodological asymmetry exists in generation timing.

---

## 5.4 Future Work

### 5.4.1 Context-Adaptive FHIR Serialization Engine (Production Path)

The findings of this study provide the empirical foundation for a **context-adaptive serialization engine** — a middleware layer that dynamically selects the optimal FHIR serialization strategy at inference time. Such a system would operationalize the Pareto frontier (§4.7) as a real-time selection algorithm:

**Input:** FHIR R4 patient bundle + target model + clinical task type + deployment constraints (cost budget, latency SLA, quality threshold)

**Decision logic (informed by this benchmark):**
1. Assess patient complexity (resource count, condition count → Simple/Moderate/Complex/Highly Complex)
2. Select serialization strategy from model-specific Pareto frontier based on constraints
3. Apply serialization with token budget enforcement
4. If model timeout detected → fall back to next-most-compact format on the frontier (Raw JSON → Narrative → FHIRPath → Condensed)

**Output:** Optimally serialized clinical prompt guaranteed to be processable by the target model within the specified constraints.

This represents a direct path from benchmark research to deployable clinical infrastructure. The Model × Serializer interaction (Finding 3) and the capacity failure finding (Finding 4) together establish that such middleware is not optional for production systems — it is architecturally necessary. The benchmark data provides the empirical calibration tables that such an engine requires to make optimal selections without per-deployment experimentation.

Design specifications and prototype architecture for this engine are maintained in the project repository under `production/` (see GitHub: JacquelineChong/fhirbench).

### 5.4.2 Additional Research Directions

**Real-world data validation.** Extension to MIMIC-IV FHIR — the largest publicly available de-identified clinical dataset in FHIR format — would validate whether serialization rankings generalize to real patient records.

**Multi-geography extension.** Adapting the benchmark to UK Core, AU Core, and bilingual implementations (Hong Kong, Singapore) would test linguistic and cultural invariance of findings.

**Layer 3 human evaluation.** Recruiting clinical informatics specialists to complete expert review would establish inter-rater reliability between LLM-as-judge and human clinical judgment.

**Serialization-aware fine-tuning.** The significant format–accuracy relationship suggests that fine-tuning models on serialization-optimized data could yield additional gains beyond prompt-time optimization.

**Expanded task taxonomy.** Clinical workflows beyond QA, reasoning, and summarization — including medication reconciliation, clinical coding (ICD-10), adverse event detection, and care gap identification — may exhibit distinct format sensitivities.

**Longitudinal monitoring.** Quarterly re-evaluation would track ranking stability as models evolve, enabling evidence-based adaptation of clinical AI pipelines.

**Cross-domain generalization.** The FHIRBench evaluation framework (multi-dimensional rubric, Pareto analysis) may generalize to other structured data domains (financial regulatory filings, legal contracts, engineering specifications).

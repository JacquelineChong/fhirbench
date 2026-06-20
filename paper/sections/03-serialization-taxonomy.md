## 3.3 Serialization Taxonomy

The representation of clinical data presented to a large language model constitutes a critical design decision that mediates between the structural fidelity of the source record and the model's capacity to extract, reason over, and summarize clinical information. This section introduces a taxonomy of six serialization strategies for transforming FHIR R4 bundles into LLM-consumable input, organized along four orthogonal dimensions. Figure 3 provides a concrete illustration of all six strategies applied to a single representative patient record, enabling direct visual comparison of format, token efficiency, and information preservation.

### 3.3.1 Taxonomy Dimensions

Table 1 presents the four dimensions that characterize any FHIR serialization strategy. Each dimension represents an independent design axis; varying one dimension while holding others constant enables controlled experimentation.

**Table 1.** Serialization taxonomy dimensions for FHIR-to-LLM transformation.

| Dimension | Options | Impact |
|-----------|---------|--------|
| **Format** | JSON, Key-Value, Narrative, Markdown, Template, Hybrid | Primary structural variable governing token layout and information density |
| **Terminology Resolution** | Raw codes only, Codes + display text, Fully expanded (definitions), Hierarchical (ancestor codes) | Determines semantic accessibility of coded clinical concepts |
| **Granularity** | Single resource, Bundle (multi-resource), Timeline (temporally ordered), Cohort (multi-patient) | Scope and volume of clinical data presented per prompt |
| **Context Window Strategy** | Truncation, Sliding window, Relevance-filtered, Hierarchical summarization | Mechanism for managing overflow when serialized content exceeds model capacity |

For the FHIRBench evaluation, terminology resolution is fixed at *codes + display text* (e.g., SNOMED-CT code with human-readable display string), granularity is fixed at *bundle* (complete patient record with all referenced resources), and context window strategy is fixed at *relevance-filtered* (resources selected by task relevance). Only the **Format** dimension varies as the primary independent variable, yielding six experimental conditions described below.

### 3.3.2 Strategy 1: Raw JSON (Baseline)

Raw JSON serialization passes the unmodified FHIR R4 JSON bundle directly into the model prompt with no preprocessing. This strategy preserves complete structural and semantic fidelity, including metadata fields, extensions, and reference links.

**Example:**
```json
{
  "resourceType": "Patient",
  "id": "example-001",
  "name": [{"given": ["John"], "family": "Smith"}],
  "birthDate": "1978-03-15",
  "gender": "male"
}
```

**Advantages.** Raw JSON is lossless — no clinical information is discarded or transformed during serialization. It requires zero preprocessing computation and preserves the hierarchical relationships, cross-resource references, and extension mechanisms that define FHIR's data model. Recent work demonstrates that JSON yields the highest parseability among structured formats for clinical extraction tasks [CITE:X85QMVCU].

**Disadvantages.** FHIR JSON is inherently verbose, containing substantial metadata overhead (resource identifiers, profile URLs, narrative text divs, extension URLs) that consumes tokens without contributing to clinical reasoning. Prior work reports that verbosity particularly impacts smaller models, where Raw JSON underperforms narrative formats by up to 19 F1 points on medication reconciliation [CITE:TGZ97SRN]. Additionally, deeply nested structures may exceed the sequential reasoning capacity of transformer architectures [CITE:J46S4PGW].

**Token efficiency.** Baseline (1.0×). A typical patient bundle with 15–20 resources consumes approximately 8,000–12,000 tokens in raw JSON form.

### 3.3.3 Strategy 2: Flattened Key-Value

Flattened Key-Value serialization transforms the hierarchical FHIR structure into a flat list of dot-notation key-value pairs, eliminating nesting while preserving attribute-value associations. Array indices are resolved to sequential entries.

**Example:**
```
patient.name.given = "John"
patient.name.family = "Smith"
patient.birthDate = "1978-03-15"
patient.gender = "male"
condition[0].code.display = "Type 2 Diabetes Mellitus"
condition[0].clinicalStatus = "active"
condition[0].onsetDate = "2019-06-12"
```

**Advantages.** Flattened Key-Value achieves substantial token reduction (approximately 40–60% relative to raw JSON) by eliminating structural punctuation, repeated keys, and metadata fields. The explicit key-value format aligns with how LLMs process factual retrieval tasks, as demonstrated in structured data prompting research [CITE:R9P2FJS3]. Each clinical fact is independently addressable, facilitating direct question-answer mapping.

**Disadvantages.** Hierarchical relationships between resources are lost — the connection between a Condition and its associated Encounter, or a MedicationRequest and its prescribing Practitioner, becomes implicit rather than explicit. This loss is particularly problematic for clinical reasoning tasks that require traversing resource references [CITE:WV9N648K]. Additionally, complex FHIR elements such as CodeableConcepts with multiple codings collapse into ambiguous flat representations.

**Token efficiency.** Approximately 0.4–0.6× baseline. The most token-efficient non-lossy strategy, achieving compression primarily through structural simplification.

### 3.3.4 Strategy 3: Natural Language Narrative

Natural Language Narrative converts the structured FHIR bundle into fluent clinical prose, synthesizing discrete data elements into coherent sentences and paragraphs that mirror clinical documentation style.

**Example:**
```
John Smith is a 47-year-old male (DOB: 1978-03-15) presenting with
a history of Type 2 Diabetes Mellitus, diagnosed in June 2019 and
currently active. He is prescribed Metformin Hydrochloride 500mg
oral tablets, taken twice daily, initiated concurrently with his
diabetes diagnosis. His most recent HbA1c measurement was 8.2%,
recorded on 2024-01-15, indicating suboptimal glycemic control.
```

**Advantages.** Narrative serialization produces the most natural input for language model comprehension, leveraging the models' pretraining on clinical text corpora including discharge summaries, progress notes, and case reports. Prior work demonstrates that narrative formats significantly outperform structured representations for smaller models (≤8B parameters) [CITE:TGZ97SRN], and that LLMs exhibit stronger reasoning when unconstrained by rigid structural formats [CITE:PPKJVC6H]. The format implicitly encodes temporal relationships and clinical significance through discourse structure.

**Disadvantages.** The conversion process itself introduces potential information loss — decisions about which elements to include, how to resolve coded values, and how to order information reflect editorial choices that may inadvertently omit clinically relevant details. Narrative generation incurs the highest preprocessing computational cost among all strategies. Furthermore, the conversion introduces a potential source of error prior to model inference, and numerical precision may degrade (e.g., laboratory values rounded or contextualized rather than reported exactly) [CITE:HTTUDR8U].

**Token efficiency.** Approximately 0.4–0.8× baseline, varying significantly with record complexity. For minimal patient records (1–3 resources), narrative achieves as low as 0.37× due to the elimination of JSON structural overhead dominating the token budget. For complex records (15–20 resources), the ratio increases toward 0.7–0.8× as natural language connectives accumulate. The elimination of structural markup generally yields net compression despite the addition of prose elements.

### 3.3.5 Strategy 4: Structured Markdown

Structured Markdown organizes FHIR data into a hierarchical document using Markdown formatting conventions — headers for resource types, bullet lists for attributes, and tables for repeated structures such as laboratory results or medication lists.

**Example:**
```markdown
## Patient
- **Name:** John Smith
- **Date of Birth:** 1978-03-15
- **Gender:** Male

## Active Conditions
| Condition | Status | Onset Date |
|-----------|--------|------------|
| Type 2 Diabetes Mellitus | Active | 2019-06-12 |

## Current Medications
| Medication | Dose | Frequency | Start Date |
|------------|------|-----------|------------|
| Metformin HCl 500mg | 500mg | Twice daily | 2019-06-12 |
```

**Advantages.** Structured Markdown balances human readability with information density. The tabular format for repeated elements (medications, lab results, conditions) achieves strong token efficiency while preserving relational structure within resource types. Research on tabular data serialization demonstrates that structured formats yield an average 40.29% performance gain over unstructured alternatives with improved robustness [CITE:KPFE6G9H]. Markdown formatting tokens are minimal relative to JSON punctuation overhead, and the format is well-represented in LLM training corpora.

**Disadvantages.** Cross-resource relationships (e.g., which encounter prompted which condition diagnosis) remain difficult to express in Markdown's flat-hierarchical structure. The format introduces arbitrary organizational choices — should data be grouped by resource type, by clinical episode, or by chronology? — that may not universally align with all task requirements. Additionally, Markdown table formatting becomes unwieldy for resources with many attributes [CITE:DA6II26P].

**Token efficiency.** Approximately 0.3–0.5× baseline. Among the most token-efficient strategies, particularly for patient records with numerous repeated elements that benefit from tabular compression.

### 3.3.6 Strategy 5: Clinical Summary Template

Clinical Summary Template serialization maps FHIR bundle data onto established clinical documentation formats such as SOAP notes (Subjective, Objective, Assessment, Plan), problem-oriented medical records, or structured handoff templates. This strategy leverages domain-specific organizational conventions familiar to clinical practitioners and, by extension, present in clinical training corpora.

**Example:**
```
ASSESSMENT & PLAN
=================
Problem #1: Type 2 Diabetes Mellitus (active since 2019-06-12)
  Subjective: No documented recent symptoms
  Objective:  HbA1c 8.2% (2024-01-15) — above target
  Assessment: Suboptimal glycemic control
  Plan:       Continue Metformin 500mg BID; consider dose escalation

MEDICATION LIST
===============
1. Metformin HCl 500mg PO BID (since 2019-06-12) — for T2DM
```

**Advantages.** Template-based serialization encodes not merely the data but its clinical interpretation context. The SOAP structure mirrors clinical reasoning patterns — proceeding from observations through assessment to plan — which may prime the model for analogous reasoning processes. This alignment between input format and expected output reasoning is supported by research demonstrating that domain-familiar formats improve LLM task performance [CITE:7FJFJU5M]. The format naturally implements relevance filtering by organizing data around clinical problems rather than resource types.

**Disadvantages.** Template structures impose strong assumptions about data organization that may not accommodate all FHIR resource types. Social determinants of health, care team composition, and administrative data fit poorly into SOAP frameworks. The template mapping requires clinical knowledge engineering to implement correctly, and edge cases (e.g., patients with 20+ active problems) may exceed the template's structural capacity. Additionally, the assessment and plan sections introduce interpretive elements that blend data with inference, potentially confounding the LLM's independent reasoning [CITE:3BR6UH6F].

**Token efficiency.** Approximately 0.4–0.6× baseline. Efficiency depends on the template's granularity; problem-focused templates achieve high compression for patients with few conditions but expand substantially for complex multi-morbid records.

### 3.3.7 Strategy 6: Hybrid Adaptive

Hybrid Adaptive serialization implements a task-aware routing mechanism that selects the optimal serialization strategy based on the downstream task type. A lightweight classifier analyzes the task prompt to determine which format maximizes expected performance for the specific clinical reasoning required.

**Routing logic:**
- Clinical QA (factual retrieval) → Flattened Key-Value or Structured Markdown
- Clinical Reasoning (inference, interactions) → Natural Language Narrative
- Clinical Summarization (care plans, handoff notes) → Clinical Summary Template

**Advantages.** The hybrid approach represents the theoretical upper bound on serialization performance, as it selects the format best suited to each task's cognitive demands. This strategy is motivated by empirical evidence that optimal serialization varies by task type [CITE:TGZ97SRN] and model architecture [CITE:8S3QCXCC]. By adapting to the task rather than imposing a single format universally, hybrid serialization can simultaneously optimize for token efficiency (QA tasks) and reasoning coherence (complex inference tasks).

**Disadvantages.** The hybrid strategy introduces system complexity through its reliance on accurate task classification. Misclassification routes data to a suboptimal format, potentially degrading rather than enhancing performance. The approach also complicates reproducibility and deployment, as the routing logic itself becomes a tunable component. Furthermore, the strategy cannot be evaluated as a single fixed serialization — its performance is inherently conditional on the quality of the task classifier, conflating serialization effects with classification accuracy.

**Token efficiency.** Variable (0.3–0.8× baseline), determined by the format selected for each specific task instance.

### 3.3.8 Taxonomy Summary

The six strategies span a design space from maximal structural fidelity (Raw JSON) to maximal cognitive alignment (Narrative, Template) to maximal adaptability (Hybrid). No single strategy dominates across all evaluation criteria — a finding consistent with the broader structured data serialization literature [CITE:DJ6CWECQ] — motivating the systematic empirical comparison that FHIRBench provides.

### 3.3.9 Strategy Selection Rationale and Preliminary Hypotheses

The six strategies described above were selected to span the complete design space of clinical data serialization along the format dimension. They range from lossless structural preservation (Raw JSON) through progressive abstraction to domain-specific clinical representation (Clinical Template), with an adaptive meta-strategy (Hybrid) representing the theoretical optimum. This selection is grounded in prior work: JSON's structural fidelity validated by Neveditsin et al. [CITE:X85QMVCU], the narrative-versus-structured comparison established by Pator [CITE:TGZ97SRN], tabular format advantages demonstrated in structured data prompting research [CITE:R9P2FJS3], clinical template conventions derived from EHR documentation standards [CITE:7FJFJU5M], and task-dependent format effects identified by Yuan et al. [CITE:8S3QCXCC]. Any additional serialization strategy would represent a variant or combination of these six fundamental approaches.

A preliminary analysis using a single illustrative patient record (Figure 3) suggests that non-JSON strategies achieve approximately 56–63% token reduction while preserving the clinical facts required for downstream tasks. This observation motivates three formal hypotheses tested in Section 4:

1. **H1 (Token Efficiency):** Non-JSON strategies achieve 40–65% token reduction across the full dataset while maintaining acceptable accuracy.
2. **H2 (Pareto Frontier):** A non-linear accuracy-cost tradeoff exists, with certain strategies achieving disproportionately high accuracy relative to token cost.
3. **H3 (Model-Format Interaction):** Optimal strategy varies by model scale, with reversals between small and frontier models.

These hypotheses are directly testable through the 90-condition experimental matrix described in Section 3.4.

## 3.4 Benchmark Design

This section describes the experimental configuration of the FHIRBench evaluation, including model selection, task definitions, protocol specification, and infrastructure.

### 3.4.1 Model Selection

Five foundation models are evaluated, all accessed through Amazon Bedrock's unified Converse API to ensure consistent inference parameters and eliminate confounding from heterogeneous API implementations.

**Table 2.** Models evaluated in FHIRBench.

| # | Model | Provider | Bedrock Model ID | Architecture | Parameters |
|---|-------|----------|-----------------|--------------|-----------|
| 1 | Claude Sonnet 4.5 | Anthropic | `anthropic.claude-sonnet-4-5-20260301-v1:0` | Proprietary (transformer) | Frontier-scale |
| 2 | GPT-5.4 | OpenAI | `openai.gpt-5-4` | Proprietary (transformer) | Frontier-scale |
| 3 | Llama 3 70B | Meta | `meta.llama3-70b-instruct-v1:0` | Open-weight (dense) | 70B |
| 4 | DeepSeek V3.2 | DeepSeek | `deepseek.deepseek-v3-2` | Open-weight (MoE) | Frontier-scale |
| 5 | Qwen3 32B | Qwen (Alibaba) | `qwen.qwen3-32b` | Open-weight (dense) | 32B |

Models were selected to maximize diversity along four orthogonal dimensions: (1) architecture family (5 distinct architectures), (2) parameter scale (32B to frontier), (3) training paradigm (2 proprietary, 3 open-weight), and (4) global adoption (all rank in top-10 by token usage in 2026). Full selection justification and exclusion rationale (including Gemini's absence from Bedrock) is documented in the supplementary materials.

### 3.4.2 Task Definitions

Three clinical task types are evaluated, each targeting a distinct cognitive operation over serialized FHIR data:

**Clinical QA (Factual Retrieval).** Questions requiring extraction of specific clinical facts from the patient record. Examples: "What medications is this patient currently taking?", "What was the most recent HbA1c result?", "List all active conditions." Ground truth answers are programmatically extracted from the FHIR bundle, enabling automated exact-match and token F1 scoring.

- *Primary metric:* Exact-match accuracy
- *Secondary metric:* Token-level F1

**Clinical Reasoning (Multi-Step Inference).** Tasks requiring synthesis across multiple resources to reach a clinical conclusion. Examples: "Is this patient at risk for a drug-drug interaction?", "Based on the available data, is the patient's diabetes adequately controlled?", "Identify any preventive care gaps." Ground truth comprises a set of expected clinical findings that a correct response should identify.

- *Primary metric:* Clinical correctness (finding coverage)
- *Secondary metric:* 4-dimension rubric score (LLM-as-judge)

**Clinical Summarization (Generative Documentation).** Tasks requiring coherent synthesis of patient data into clinical documentation formats. Examples: "Generate a discharge summary for this patient", "Write an SBAR handoff note", "Create a diabetes care plan." Reference summaries are generated following clinical documentation guidelines.

- *Primary metric:* ROUGE-L [CITE:ESPJCVEP]
- *Secondary metric:* 4-dimension rubric score (LLM-as-judge)

### 3.4.3 Experimental Protocol

The full evaluation follows a stratified experimental design:

| Parameter | Value |
|-----------|-------|
| Total conditions | 90 (6 serializers × 5 models × 3 tasks) |
| Samples per condition | 50 |
| Total API calls | 4,500 |
| Sampling strategy | Stratified across 4 clinical domains (~12–13 patients per domain per condition) |
| Randomization | Fixed seed (42) for reproducibility |
| Inference temperature | 0.0 (deterministic) |
| Top-p | 1.0 |
| Max output tokens | 2,048 |

The evaluation proceeds sequentially by condition, with results checkpointed after each condition completes. This enables resumption without data loss in the event of API failures or rate limiting. Within each condition, the 50 patient bundles are processed in fixed random order to eliminate ordering effects.

### 3.4.4 Infrastructure

The benchmark infrastructure follows the four-layer multi-agent architecture illustrated in Figure 1.

All model inference is conducted through the Amazon Bedrock Converse API, which provides a unified request/response interface across all five models regardless of their underlying architecture. This design choice ensures:

- **Consistent tokenization reporting** — Bedrock returns input and output token counts for every request
- **Unified rate limiting** — A single retry policy (exponential backoff, 3 attempts, initial delay 1s) handles all transient failures
- **Cost tracking** — Per-request cost computed from Bedrock's published pricing and token metadata
- **Model version pinning** — Bedrock model IDs specify exact model versions, ensuring reproducibility

Results are persisted in JSON format with one file per condition (`results/{serializer}_{model}_{task}.json`), containing per-sample prompts, responses, scores, token counts, and latency measurements. A consolidated CSV summary enables downstream statistical analysis.

### 3.4.5 Statistical Analysis Plan

The primary analysis employs a two-way analysis of variance (ANOVA) with serialization strategy and model as factors, conducted independently for each of the three task types. This yields three separate ANOVA models, each testing the main effects of serialization (H₁: at least one strategy differs from the others) and model (H₂: at least one model differs), plus the serialization × model interaction (H₃: the effect of strategy depends on model choice).

Post-hoc comparisons use Tukey's Honestly Significant Difference (HSD) test to identify which specific strategy pairs differ significantly, controlling family-wise error rate at α = 0.05. Effect sizes are reported as Cohen's d for pairwise comparisons, with 95% confidence intervals computed via bootstrap resampling (10,000 iterations) to account for potential non-normality in the score distributions.

Secondary analyses include: (1) relative token efficiency analysis correlating performance gains with token consumption ratios; (2) error taxonomy classifying failure modes by serialization strategy; and (3) interaction decomposition examining whether format effects are moderated by patient complexity (number of resources in bundle) or question difficulty. All analyses are pre-registered and implemented in Python using scipy.stats, statsmodels, and pingouin libraries.

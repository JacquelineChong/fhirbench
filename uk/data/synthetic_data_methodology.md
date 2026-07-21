# Synthetic Patient Data Generation Methodology

## 1. Background and Rationale

### 1.1 Original FHIRBench Approach (Paper 1)

The original FHIRBench study (Chong, 2026) employed a two-stage pipeline for patient data generation:

1. **Pool generation**: 1,000 synthetic patients generated using modified Synthea output, producing US Core FHIR R4 bundles with realistic clinical trajectories across four domains (diabetes 28%, cardiovascular 27%, preventive care 26%, medication interactions 19%).
2. **Stratified sampling**: 100 patients selected from the pool using complexity-based stratification (Simple 25%, Moderate 40%, Complex 25%, Highly Complex 10%).

This approach was feasible because Synthea natively generates US Core FHIR R4 bundles with RxNorm medication codes, US-formatted identifiers, and American clinical conventions.

> Reference: Chong, J. (2026). FHIRBench: Benchmarking FHIR Serialization Strategies for Large Language Models in Clinical Information Extraction. medRxiv. https://doi.org/10.64898/2026.07.14.26358020v1

### 1.2 Why LLM Generation for UK Core (Not Synthea Modification)

Synthea's UK module is limited and does not produce fully UK Core FHIR R4 compliant bundles. Specific gaps include:

- **No dm+d medication codes** — Synthea uses RxNorm regardless of locale
- **No NHS Number generation** with valid Modulus 11 check digits
- **No UK Core extensions** (EthnicCategory, NHSNumberVerificationStatus, NominatedPharmacy, DeathNotificationStatus)
- **No ODS codes** for organisations or GP practices
- **No SNOMED CT UK Edition** concepts (30,000+ UK-specific terms)
- **Date format** remains ISO/US rather than DD/MM/YYYY display conventions
- **Medication dosage** uses US abbreviations (BID, TID) rather than UK conventions (twice daily, three times daily)

Post-processing Synthea output to address all these gaps would require essentially rewriting every resource, losing the benefit of using Synthea in the first place.

Instead, we employ **LLM-based generation** using validated UK Core FHIR StructureDefinitions and real NHS Digital example bundles as schema templates. This approach:

1. Produces natively UK Core compliant FHIR bundles
2. Can encode domain knowledge about NHS clinical workflows
3. Supports complex multi-morbidity patterns with appropriate UK coding
4. Allows fine-grained control over complexity stratification

### 1.3 Model Selection for Generation: DeepSeek V3.2

We selected DeepSeek V3.2 (`deepseek.v3.2` on Amazon Bedrock) as the generation model based on:

**Cost-effectiveness vs proprietary models:**
- DeepSeek V3.2: $0.62/1M input, $1.85/1M output (Bedrock)
- Qwen3 32B: $0.20/1M input, $0.78/1M output tokens (Bedrock)
- Claude Sonnet 4.5: ~$3.00/1M input, ~$15.00/1M output (Bedrock)
- For 1,000 patients (~4M output tokens): DeepSeek ≈ $7.40 vs Claude ≈ $60 (8× cheaper)
- The marginal cost difference vs Qwen3 ($7.40 vs $3.10) is trivial for a research project; model quality takes priority

**Research support — strongest evidence for FHIR-specific structured generation:**

1. **FHIR-Workbench (JMIR Formative Research, 2025):** DeepSeek-v3 achieved **0.94 accuracy** on FHIR resource identification and generation tasks — the most directly relevant benchmark to our use case of generating valid FHIR bundles. This is the strongest evidence that DeepSeek can produce structurally correct FHIR resources.

2. **Knowledge Graphs vs SQL over Structured EHR Data (MDPI Future Internet, 2026):** Direct comparison of Claude Haiku 4.5, Qwen 2.5 72B, Llama 3.1 8B, and Llama 3.3 70B found that larger open-weight models performed comparably to proprietary models on structured EHR queries, validating the open-weight approach for medical data tasks.

3. **Synthetic EHR generation (JMIR 2025, e65317):** Larger open-weight models (Yi-34B, EPS=96.8) achieved the **highest fidelity scores** for generating synthetic electronic health records that maintained clinical plausibility. DeepSeek V3.2 (~671B MoE) is substantially larger than alternatives, providing greater capacity for encoding complex clinical relationships and multi-morbidity patterns.

4. **Open-weight cost-quality frontier (The New Stack, July 2026):** Open-weight models are "4 months behind" frontier models at 10× lower cost, with the gap narrowing specifically for structured generation tasks where format adherence matters more than creative reasoning.

**Why DeepSeek over Qwen3 32B:** While Qwen3 is cheaper, DeepSeek V3.2 has the only direct FHIR benchmark evidence (0.94 accuracy on FHIR-Workbench). For a task where structural validity of medical data is paramount, we prioritise demonstrated FHIR competence over marginal cost savings. The $4.30 difference across 1,000 patients is negligible against research integrity.

**Quality assurance:** All generated bundles are validated against official UK Core FHIR StructureDefinitions post-generation. Failed validations trigger regeneration (with Claude as fallback for persistent failures). This validation gate ensures output quality is independent of generator model capability.

---

## 2. Generation Pipeline

### 2.1 Overview

```
[UK Core StructureDefinitions] + [NHS Digital Examples] + [Clinical Domain Specs]
                                    ↓
                    [DeepSeek V3.2 via Bedrock API]
                                    ↓
                    [1,000 Raw FHIR Bundles]
                                    ↓
                    [UK Core Validation Engine]
                                    ↓
              [Valid Bundles]  ←→  [Regenerate Failed]
                                    ↓
                    [Complexity Scoring]
                                    ↓
                    [Stratified Sampling → 100 Patients]
```

### 2.2 Generation Prompt Template

Each patient is generated with a structured prompt containing:
1. The target UK Core FHIR StructureDefinition (as schema)
2. A real NHS Digital example bundle (as format reference)
3. Clinical domain specification (diabetes / cardiovascular / preventive care / medication interactions)
4. Complexity level target (Simple / Moderate / Complex / Highly Complex)
5. Specific instructions for UK-specific elements

### 2.3 Validation Criteria

Every generated bundle must pass:
- [ ] Valid NHS Number (Modulus 11 check digit)
- [ ] All medications coded in dm+d (https://dmd.nhs.uk system URI)
- [ ] All conditions coded in SNOMED CT UK Edition
- [ ] UK Core extensions present where mandatory (EthnicCategory, NHSNumberVerificationStatus)
- [ ] Dates in ISO format (FHIR requirement) but with UK display conventions in narrative
- [ ] Organisation references use ODS codes
- [ ] GP Practice reference present
- [ ] Metric units throughout (kg, cm, °C, mmHg)
- [ ] Valid FHIR R4 bundle structure (passes HAPI FHIR validator)

---

## 3. Patient Cohort Specification

### 3.1 Target Distribution (1,000-patient pool)

| Parameter | Distribution | Count |
|-----------|-------------|-------|
| **Clinical Domain** | | |
| Diabetes (Type 1 & 2) | 28% | 280 |
| Cardiovascular | 27% | 270 |
| Preventive Care | 26% | 260 |
| Medication Interactions | 19% | 190 |
| **Complexity Level** | | |
| Simple | 25% | 250 |
| Moderate | 40% | 400 |
| Complex | 25% | 250 |
| Highly Complex | 10% | 100 |

### 3.2 Complexity Definitions

| Level | Resources | Conditions | Medications | Observations | Description |
|-------|-----------|-----------|-------------|--------------|-------------|
| Simple | 10-20 | 1-2 | 1-3 | 3-5 | Single condition, straightforward management |
| Moderate | 20-40 | 3-5 | 4-7 | 6-12 | Multi-morbidity, standard polypharmacy |
| Complex | 40-70 | 5-8 | 7-12 | 12-20 | Multi-system disease, complex interactions |
| Highly Complex | 70-120+ | 8+ | 12+ | 20+ | Frail elderly, extensive history, many interactions |

### 3.3 UK-Specific Clinical Realism Requirements

**Demographics:**
- UK names (mix of English, Welsh, Scottish, South Asian, African/Caribbean reflecting NHS population)
- UK addresses (realistic postcodes, cities, counties)
- NHS Ethnic Category distribution reflecting UK census data
- Age distribution: 18-90 (weighted toward 50-75 for chronic disease domains)

**Medications (dm+d):**
- Use INN/BAN generic names (paracetamol not acetaminophen, adrenaline not epinephrine)
- Include valid dm+d concept IDs at VMP or AMP level
- UK dosage conventions: "500 mg oral twice daily" not "500mg PO BID"
- NHS formulary-appropriate prescribing (NICE-guided first-line choices)

**Clinical Coding:**
- SNOMED CT UK Edition codes (with UK-specific concepts where applicable)
- NHS Read Code legacy references for historical conditions (pre-2020 entries)
- OPCS-4 for procedures (not CPT)

**Organisational:**
- GP Practices with realistic ODS codes (format: letter + 5 digits, e.g., "Y02734")
- NHS Trusts for secondary care references
- ICB (Integrated Care Board) references where applicable

**Observations:**
- All in metric: weight (kg), height (cm), temperature (°C)
- Blood pressure in mmHg (same as US)
- HbA1c in mmol/mol (UK standard) AND % (for comparison)
- eGFR in mL/min/1.73m²
- Cholesterol in mmol/L (not mg/dL)

### 3.4 Stratified Sampling (Pool → Evaluation Cohort)

From the 1,000-patient pool, we sample 100 patients maintaining:
- Complexity: 25 Simple, 40 Moderate, 25 Complex, 10 Highly Complex
- Domain: approximately balanced (~25% each, with medication interactions slightly lower at ~19%)
- Cross-balanced: complexity distribution is applied overall, not per-domain

This exactly mirrors the Paper 1 methodology for direct cross-national comparison.

---

## 4. Reproducibility

All generation code, prompts, validation scripts, and the final patient pool are available in the `uk-core` branch of the FHIRBench repository:
- Generation script: `uk/code/generate_patients.py`
- Validation script: `uk/code/validate_uk_core.py`
- Prompt templates: `uk/code/prompts/`
- Generated data: `uk/data/fhir_bundles/` (1,000 patients)
- Sampled cohort: `uk/data/evaluation_cohort/` (100 patients)
- Complexity scoring: `uk/code/score_complexity.py`

---

## Sources

1. Chong, J. (2026). FHIRBench: Benchmarking FHIR Serialization Strategies for Large Language Models. medRxiv. https://doi.org/10.64898/2026.07.14.26358020v1
2. NHS Digital (2026). UK Core FHIR Implementation Guide. https://simplifier.net/HL7FHIRUKCoreR4
3. Benchmarking Local LLMs for Healthcare EHR Schema Retrieval. arXiv:2605.20815 (2026).
4. Using a Diverse Test Suite to Assess LLMs on FHIR Knowledge. JMIR Formative Research (2025). https://formative.jmir.org/2025/1/e73540
5. Evaluation and Bias Analysis of LLMs in Generating Synthetic EHR. JMIR (2025). https://www.jmir.org/2025/1/e65317
6. Knowledge Graphs vs. SQL over Structured EHR Data. MDPI Future Internet (2026). https://www.mdpi.com/1999-5903/18/7/365
7. Open-weight models: frontier costs. The New Stack (July 2026). https://thenewstack.io/open-weight-models-frontier-costs/
8. AWS Bedrock DeepSeek V3.2 pricing. https://markaicode.com/benchmarks/aws-bedrock-deepseek-r2-rtx-4090-memory-benchmark/

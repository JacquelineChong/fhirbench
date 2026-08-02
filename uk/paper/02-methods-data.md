# 2. Data and Evaluation Design

## 2.1 Evaluation Cohort

The evaluation cohort comprises 100 UK Core FHIR R4 patient bundles, stratified-sampled from a pool of 992 generated patients. Each bundle represents a complete primary care patient record conforming to NHS England's UK Core Implementation Guide (v1.0.0), containing Patient, Condition, MedicationRequest, Observation, Organization, and Practitioner resources with appropriate inter-resource references.

### Generation Approach

Patient bundles were generated using DeepSeek V3.2 (open-weight, 671B MoE architecture) via AWS Bedrock. We selected LLM generation over the established Synthea synthetic patient generator for seven specific reasons related to UK Core compliance:

1. **dm+d medication codes**: Synthea uses US RxNorm codes. UK Core mandates Dictionary of Medicines and Devices (dm+d) codes for all MedicationRequest resources. No maintained mapping exists between RxNorm and dm+d.
2. **NHS Number format**: UK Core requires 10-digit NHS Numbers validated by the Modulus 11 check digit algorithm. Synthea generates US SSN-format identifiers.
3. **UK Core extensions**: Mandatory extensions including `UKCore-EthnicCategory`, `UKCore-NHSNumberVerificationStatus`, and `UKCore-ResidentialStatus` have no Synthea equivalent.
4. **GP practice registration**: UK primary care records include explicit `generalPractitioner` references with ODS codes. Synthea models US provider networks.
5. **SNOMED CT UK Edition**: UK Core requires codes from the UK clinical extension of SNOMED CT, which includes ~50,000 additional concepts not in the International Edition.
6. **Metric units**: UK clinical observations use metric units exclusively (mmol/L for glucose, mmol/mol for HbA1c, mmHg for blood pressure). Synthea defaults to US conventional units for several observations.
7. **Bundle structure conventions**: UK Core bundles follow NHS Digital's structure guidance for document bundles, with specific ordering and reference patterns.

Generation was configured with `max_tokens=32768`, `temperature=0.0` (for reproducibility), `read_timeout=600s`, and 5 concurrent workers. Each patient was generated with a structured prompt specifying clinical domain, complexity level, demographic characteristics, and required UK Core conformance criteria. The generation prompt included exemplar resources from the UK Core Implementation Guide to constrain output format.

### Stratification

The 100-patient evaluation cohort was stratified-sampled from the 992-patient pool along two dimensions:

**Complexity** (determined by resource count and clinical scenario):
- Simple (25 patients): 10–20 resources. Single chronic condition, 1–2 medications, routine observations.
- Moderate (40 patients): 20–40 resources. 2–3 conditions, polypharmacy (3–5 medications), multiple observation types.
- Complex (25 patients): 40–70 resources. 4+ conditions, significant polypharmacy, multi-year observation history, specialist referrals.
- Highly complex (10 patients): 70+ resources. Multi-morbidity with interactions, complex medication regimens, extensive longitudinal data.

**Clinical domain**:
- Diabetes (24%): Type 1/2 diabetes management, HbA1c monitoring, insulin regimens, diabetic complications.
- Cardiovascular (31%): Hypertension, atrial fibrillation, heart failure, anticoagulation management.
- Preventive care (28%): Screening programmes, immunisation records, lifestyle interventions, cancer screening.
- Medication interactions (17%): Polypharmacy patients requiring interaction checking, contraindication identification.

Sampling used a fixed random seed (42) with domain balance constraints: each domain required representation between 15% and 35% of the cohort, with proportional representation within each complexity stratum.

### Validation

All 100 bundles achieved 100% pass rate on seven mandatory UK Core conformance criteria:

1. **Bundle structure**: Valid FHIR R4 Bundle with `resourceType: "Bundle"` and populated `entry` array.
2. **NHS Number**: 10-digit identifier present in Patient resource, validated by Modulus 11 check digit algorithm, with system URI `https://fhir.nhs.uk/Id/nhs-number`.
3. **dm+d codes**: All MedicationRequest resources contain `medicationCodeableConcept` with coding from system `https://dmd.nhs.uk`.
4. **SNOMED CT UK**: All Condition resources contain `code.coding` with system `http://snomed.info/sct` and valid UK Edition concept IDs.
5. **UK Core extensions**: Patient resource includes `UKCore-EthnicCategory` and `UKCore-NHSNumberVerificationStatus` extensions.
6. **GP practice**: Patient resource contains `generalPractitioner` reference to an Organization resource with a valid name.
7. **Metric units**: All Observation `valueQuantity` entries use metric units (mmol/L, mmol/mol, mmHg, kg, cm, beats/min).

Validation was performed programmatically using `validate_uk_core.py` with checks including NHS Number Modulus 11 computation, regex validation of dm+d code format, and unit string matching against an allowlist of 23 accepted metric units.

## 2.2 Serialisation Formats

Six serialisation formats convert each FHIR Bundle JSON into text for LLM consumption. All serialisers are deterministic (same input produces identical output) and implemented as Python classes in the `serializers/` package.

### 2.2.1 raw_json

The complete FHIR Bundle JSON is passed as a formatted string with 2-space indentation. All structural information is preserved: resource types, system URIs, coded references, nested arrays. No information is lost or reorganised.

**Token characteristics**: Highest token count (mean 9,901 input tokens per prompt). Preserves system URIs (e.g., `"system": "https://fhir.nhs.uk/Id/nhs-number"`) that serve as disambiguation context for coded values.

### 2.2.2 flattened_kv

The JSON hierarchy is flattened into dot-notation key-value pairs. Each leaf value receives a fully-qualified path key.

**Example**:
```
entry[0].resource.resourceType: Patient
entry[0].resource.identifier[0].system: https://fhir.nhs.uk/Id/nhs-number
entry[0].resource.identifier[0].value: 9434765919
entry[0].resource.name[0].family: Begum
entry[0].resource.name[0].given[0]: Fatima
```

**Token characteristics**: Mean 6,081 input tokens (39% reduction vs raw_json). Preserves all data but fragments clinical concepts across disconnected lines—a patient's condition code and its display name become separate entries without co-located context.

### 2.2.3 narrative

Converts the FHIR Bundle into NHS clinical letter format—GP referral style prose.

**Example**:
```
Dear Colleague,

Re: Mrs Fatima Begum (NHS Number: 943 476 5919)
Date of Birth: 15 March 1962 (Age 64)
Registered at: Riverside Medical Practice

I am writing regarding the ongoing management of this patient who carries the
following active diagnoses:

1. Type 2 diabetes mellitus (SNOMED: 44054006) — diagnosed 2018
2. Essential hypertension (SNOMED: 38341003) — diagnosed 2015
...
```

**Token characteristics**: Mean 1,179 input tokens (88% reduction). Presents information in a format familiar to clinicians. May omit structural metadata (array indices, internal references) and condense repeated observation patterns.

### 2.2.4 clinical_template

Reorganises bundle content into an NHS SOAP-style clinical template with standardised sections.

**Example**:
```
PATIENT: Fatima Begum | NHS: 9434765919 | DOB: 1962-03-15 | F
GP: Riverside Medical Practice

ACTIVE CONDITIONS:
- Type 2 diabetes mellitus [SNOMED: 44054006] dx:2018
- Essential hypertension [SNOMED: 38341003] dx:2015

MEDICATIONS (dm+d):
- Metformin 500mg tablets [dm+d: 317971003] 1 BD
- Ramipril 5mg capsules [dm+d: 317290003] 1 OD

OBSERVATIONS (latest):
- HbA1c: 52 mmol/mol (2026-03-15)
- BP: 138/82 mmHg (2026-06-01)
- BMI: 28.4 kg/m2 (2026-06-01)
```

**Token characteristics**: Mean 942 input tokens (90% reduction). Uses clinical abbreviations (BD, OD, dx) and tabular layout. Groups information by clinical category rather than FHIR resource order.

### 2.2.5 structured_markdown

Renders the bundle as hierarchical markdown with headings, subheadings, and nested lists.

**Example**:
```markdown
## Patient Demographics
- **Name**: Fatima Begum
- **NHS Number**: 9434765919
- **Date of Birth**: 15 March 1962
- **Gender**: Female
- **GP Practice**: Riverside Medical Practice

## Active Conditions
### Type 2 diabetes mellitus
- SNOMED CT: 44054006
- Onset: 2018-04-22
- Status: Active

### Essential hypertension
- SNOMED CT: 38341003
- Onset: 2015-11-08
- Status: Active

## Current Medications
| Medication | dm+d Code | Dose | Frequency |
|---|---|---|---|
| Metformin 500mg | 317971003 | 500mg | Twice daily |
...
```

**Token characteristics**: Mean 1,226 input tokens (88% reduction). Preserves hierarchical document structure via heading levels. Markdown formatting (bold, tables, lists) provides visual scaffolding that may aid model comprehension of document organisation.

### 2.2.6 hybrid_adaptive

A task-aware meta-serialiser that selects format based on the clinical task:
- **clinical_qa** → uses clinical_template (optimised for factual retrieval with concise, structured data)
- **clinical_reasoning** → uses structured_markdown (provides context grouping for relational reasoning)
- **clinical_summarization** → uses narrative (provides prose scaffold for summary generation)

**Token characteristics**: Mean 1,116 input tokens (89% reduction). Token count varies by task routing. This format tests the hypothesis that optimal serialisation is task-dependent—a hypothesis the results confirm, though the specific routing assignments implemented do not perfectly match the empirically optimal routing discovered post-hoc.

## 2.3 Clinical Tasks

Three clinical tasks span the range of NHS primary care AI applications:

### 2.3.1 Clinical QA (Factual Extraction)

The model must extract five specific clinical facts from the patient record:
1. NHS Number
2. Active conditions with SNOMED CT UK codes
3. Current medications with dm+d codes
4. Most recent HbA1c result (mmol/mol)
5. Registered GP practice

This task evaluates verbatim retrieval of coded clinical identifiers—the foundational capability for clinical coding, audit, and data validation workloads.

### 2.3.2 Clinical Reasoning

The model must perform clinical inference:
1. Identify potential drug interactions or contraindications
2. Assess concerning trends in observations
3. Recommend clinical actions
4. Identify care plan gaps

This task evaluates the model's ability to synthesise information across multiple resources, identify relationships, and apply clinical knowledge—required for clinical decision support and medication review applications.

### 2.3.3 Clinical Summarisation

The model must produce a comprehensive GP referral letter including demographics, conditions with codes, medications with doses, investigation results with trends, relevant history, care plan, and referral rationale.

This task evaluates structured document synthesis following NHS clinical communication conventions—required for discharge summary generation, referral letter drafting, and clinical correspondence automation.

## 2.4 Scoring Methodology

### 2.4.1 Layer 1: Token-Level F1

Ground truth is extracted programmatically from each FHIR Bundle by parsing resource contents (NHS Numbers, condition codes, medication names, observation values). Model responses are tokenised (lowercased, split on non-alphanumeric characters, stopwords removed), and token-level precision, recall, and F1 are computed against the ground truth token set.

F1 is computed per prompt and aggregated at the patient level (mean across 18 prompt variants per patient: 6 serialisers × 3 tasks). Patient-level aggregation (N=100) provides the unit of analysis for statistical tests.

### 2.4.2 Layer 2: LLM-as-Judge Clinical Quality

A cross-judging protocol mitigates self-assessment bias:
- **Claude Sonnet 4.5** judges responses from GPT-5.4, DeepSeek V3.2, Qwen3 32B, and Llama 3.3 70B (7,200 judgments).
- **Qwen3 32B** judges responses from Claude Sonnet 4.5 (1,800 judgments).

Each judgment scores the response on four dimensions (0–5 integer scale):
1. **Accuracy**: Correctness of clinical facts (NHS Numbers, codes, observations).
2. **Completeness**: Whether all parts of the question are addressed.
3. **Safety**: Avoidance of harmful clinical advice; identification of contraindications.
4. **Relevance**: Focus on the clinical question; absence of irrelevant content.

The composite Layer 2 score is the unweighted mean of all four dimensions. Temperature is set to 0.0 for all judge calls to ensure reproducibility.

### 2.4.3 Statistical Tests

Inter-model and inter-serialiser differences are assessed using the Kruskal–Wallis H-test (non-parametric, appropriate for non-normal score distributions). Post-hoc pairwise comparisons use Dunn's test with Bonferroni correction. Effect sizes between specific groups use Cohen's d with pooled standard deviation. Confidence intervals are 95% using normal approximation (z=1.96). All tests are two-sided unless otherwise specified.

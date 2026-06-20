# Figure 3: Same Patient Record, Six Serialization Strategies

## 3.1 Source FHIR Patient Record

The following FHIR R4 Bundle represents a single diabetic patient encounter, comprising five resources. This bundle serves as the canonical input from which all six serialization strategies are derived.

```json
{
  "resourceType": "Bundle",
  "type": "collection",
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "pt-001",
        "name": [{"family": "Smith", "given": ["John"]}],
        "gender": "male",
        "birthDate": "1978-03-15"
      }
    },
    {
      "resource": {
        "resourceType": "Condition",
        "id": "cond-001",
        "subject": {"reference": "Patient/pt-001"},
        "code": {
          "coding": [{"system": "http://snomed.info/sct",
                      "code": "44054006",
                      "display": "Type 2 diabetes mellitus"}]
        },
        "clinicalStatus": {"coding": [{"code": "active"}]},
        "onsetDateTime": "2019-06-12"
      }
    },
    {
      "resource": {
        "resourceType": "MedicationRequest",
        "id": "med-001",
        "subject": {"reference": "Patient/pt-001"},
        "medicationCodeableConcept": {
          "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                      "code": "861004",
                      "display": "Metformin 500 MG Oral Tablet"}]
        },
        "dosageInstruction": [{"text": "500mg twice daily"}],
        "authoredOn": "2019-06-12"
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "id": "obs-hba1c",
        "subject": {"reference": "Patient/pt-001"},
        "code": {"coding": [{"system": "http://loinc.org",
                             "code": "4548-4",
                             "display": "Hemoglobin A1c"}]},
        "valueQuantity": {"value": 8.2, "unit": "%"},
        "effectiveDateTime": "2024-01-15"
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "id": "obs-bp",
        "subject": {"reference": "Patient/pt-001"},
        "code": {"coding": [{"system": "http://loinc.org",
                             "code": "85354-9",
                             "display": "Blood pressure panel"}]},
        "component": [
          {"code": {"coding": [{"code": "8480-6", "display": "Systolic"}]},
           "valueQuantity": {"value": 135, "unit": "mmHg"}},
          {"code": {"coding": [{"code": "8462-4", "display": "Diastolic"}]},
           "valueQuantity": {"value": 85, "unit": "mmHg"}}
        ],
        "effectiveDateTime": "2024-01-15"
      }
    }
  ]
}
```

---

## 3.2 Six Serialization Strategies Applied

### Strategy 1: Raw JSON

The source FHIR JSON is passed directly to the model without transformation. All structural metadata, coding system URIs, and reference pointers are preserved verbatim.

```json
{"resourceType":"Bundle","type":"collection","entry":[{"resource":{"resourceType":
"Patient","id":"pt-001","name":[{"family":"Smith","given":["John"]}],"gender":"male",
"birthDate":"1978-03-15"}},{"resource":{"resourceType":"Condition","id":"cond-001",
"subject":{"reference":"Patient/pt-001"},"code":{"coding":[{"system":
"http://snomed.info/sct","code":"44054006","display":"Type 2 diabetes mellitus"}]},
"clinicalStatus":{"coding":[{"code":"active"}]},"onsetDateTime":"2019-06-12"}},
{"resource":{"resourceType":"MedicationRequest","id":"med-001","subject":{"reference":
"Patient/pt-001"},"medicationCodeableConcept":{"coding":[{"system":
"http://www.nlm.nih.gov/research/umls/rxnorm","code":"861004","display":
"Metformin 500 MG Oral Tablet"}]},"dosageInstruction":[{"text":"500mg twice daily"}],
"authoredOn":"2019-06-12"}},{"resource":{"resourceType":"Observation","id":"obs-hba1c",
...}}]}
```

**Approximate tokens:** ~420

---

### Strategy 2: Flattened Key-Value (Dot-Notation)

Each datum is extracted into a flat `path = value` representation, eliminating nested structure while preserving all discrete data points.

```
patient.id = pt-001
patient.name.family = Smith
patient.name.given = John
patient.gender = male
patient.birthDate = 1978-03-15
condition.code.snomed = 44054006
condition.display = Type 2 diabetes mellitus
condition.clinicalStatus = active
condition.onsetDateTime = 2019-06-12
medication.code.rxnorm = 861004
medication.display = Metformin 500 MG Oral Tablet
medication.dosage = 500mg twice daily
medication.authoredOn = 2019-06-12
observation[0].code.loinc = 4548-4
observation[0].display = Hemoglobin A1c
observation[0].value = 8.2%
observation[0].date = 2024-01-15
observation[1].code.loinc = 85354-9
observation[1].display = Blood pressure panel
observation[1].systolic = 135 mmHg
observation[1].diastolic = 85 mmHg
observation[1].date = 2024-01-15
```

**Approximate tokens:** ~185

---

### Strategy 3: Natural Language Narrative (Clinical Prose)

The record is converted into fluent clinical English, prioritizing readability and contextual coherence over structural fidelity.

```
John Smith is a 45-year-old male born on March 15, 1978. He has an active diagnosis
of Type 2 diabetes mellitus (SNOMED 44054006), with onset on June 12, 2019. His
current medication regimen includes Metformin 500 mg oral tablet taken twice daily,
which was initiated at the time of diagnosis. On January 15, 2024, laboratory results
showed a Hemoglobin A1c level of 8.2%, indicating suboptimal glycemic control. His
blood pressure on the same date was recorded at 135/85 mmHg, suggesting mildly
elevated systolic pressure. Together, these findings are consistent with a patient
whose Type 2 diabetes remains inadequately controlled on current therapy, with
concurrent borderline hypertension warranting ongoing monitoring.
```

**Approximate tokens:** ~155

---

### Strategy 4: Structured Markdown (Headers + Tables)

Clinical data is organized under semantic headers with tabular presentation of discrete values, preserving structure without JSON syntax overhead.

```markdown
# Patient: John Smith
- **ID:** pt-001
- **Gender:** Male
- **Date of Birth:** 1978-03-15 (Age 45)

## Active Conditions

| Condition | Code (SNOMED) | Status | Onset |
|-----------|---------------|--------|-------|
| Type 2 diabetes mellitus | 44054006 | Active | 2019-06-12 |

## Medications

| Medication | Code (RxNorm) | Dosage | Start Date |
|------------|---------------|--------|------------|
| Metformin 500 MG Oral Tablet | 861004 | 500mg twice daily | 2019-06-12 |

## Recent Observations (2024-01-15)

| Test | LOINC | Value | Unit |
|------|-------|-------|------|
| Hemoglobin A1c | 4548-4 | 8.2 | % |
| Blood Pressure (Systolic) | 8480-6 | 135 | mmHg |
| Blood Pressure (Diastolic) | 8462-4 | 85 | mmHg |
```

**Approximate tokens:** ~175

---

### Strategy 5: Clinical Summary Template (SOAP Note)

The record is cast into the SOAP (Subjective, Objective, Assessment, Plan) format familiar from EHR clinical documentation, aligning with conventions used in medical note generation.

```
PATIENT: John Smith | DOB: 1978-03-15 | Sex: Male
DATE: 2024-01-15

SUBJECTIVE:
- Established patient with Type 2 diabetes mellitus (dx 2019-06-12)
- Currently on Metformin 500mg BID since diagnosis

OBJECTIVE:
- HbA1c: 8.2% (target <7.0%)
- BP: 135/85 mmHg (target <130/80 mmHg for diabetic patients)

ASSESSMENT:
- Type 2 diabetes mellitus, inadequately controlled (SNOMED: 44054006)
- Borderline stage 1 hypertension

PLAN:
- Current medication: Metformin 500 MG Oral Tablet (RxNorm: 861004), 500mg BID
- [Continued monitoring indicated]
```

**Approximate tokens:** ~160

---

### Strategy 6: Hybrid Adaptive

The hybrid strategy dynamically selects the optimal serialization format based on the downstream task type. For the same patient record, the routing logic applies:

| Task Type | Selected Format | Rationale |
|-----------|----------------|-----------|
| Code extraction (e.g., "What is the SNOMED code?") | Flattened Key-Value | Direct path-value lookup minimizes parsing |
| Clinical reasoning (e.g., "Is diabetes controlled?") | Narrative | Prose enables chain-of-thought inference |
| Data aggregation (e.g., "List all observations") | Structured Markdown | Tables support enumeration and comparison |
| Documentation (e.g., "Generate a clinical note") | SOAP Template | Aligns with expected output structure |
| Validation (e.g., "Is this bundle conformant?") | Raw JSON | Schema-level fidelity required |
| Multi-step QA (e.g., "Summarize and recommend") | Narrative + Markdown | Combines reasoning substrate with structured facts |

The hybrid router is implemented as a lightweight classifier (§4.2) that maps task intent to format selection prior to prompt construction. When task type is ambiguous, it defaults to Structured Markdown as the balanced middle-ground representation.

**Approximate tokens:** Variable (155–420, depending on routing decision)

---

## 3.3 Strategy Selection Rationale

The six serialization strategies were selected to span the complete representational spectrum from lossless machine-readable formats to lossy but cognitively intuitive human-oriented prose. Raw JSON preserves the full FHIR structure including coding system URIs, reference pointers, and nested arrays, consistent with findings by Neveditsin et al. demonstrating that direct JSON input can support extraction tasks when models possess sufficient schema knowledge [CITE:X85QMVCU]. At the opposite pole, the Natural Language Narrative sacrifices structural precision for contextual fluency, reflecting the finding by Pator et al. that narrative representations can outperform structured formats on clinical reasoning tasks by aligning with the training distribution of language models [CITE:TGZ97SRN]. Between these extremes, the Flattened Key-Value and Structured Markdown strategies occupy intermediate positions in the format complexity–comprehension tradeoff, drawing on table serialization research demonstrating that linearized tabular representations influence LLM performance on structured data tasks [CITE:R9P2FJS3]. The Clinical Summary Template leverages the SOAP documentation conventions deeply embedded in EHR systems, representing a domain-specific structural prior. Finally, the Hybrid Adaptive strategy operationalizes the empirical finding that optimal serialization is task-dependent [CITE:8S3QCXCC], implementing dynamic format routing rather than committing to a single representation. Together, these six strategies form a complete basis for the format dimension of the benchmark: any alternative serialization approach would constitute a variant or interpolation of these canonical points rather than a genuinely novel representational category.

---

## 3.4 Token Efficiency Summary

| Strategy | Approx. Tokens | Relative to Baseline | Information Loss | Best Suited For |
|----------|---------------|---------------------|------------------|-----------------|
| Raw JSON | ~420 | 1.00× | None | Validation, schema-aware extraction |
| Flattened Key-Value | ~185 | 0.44× | Structural (nesting, references) | Direct code/value lookup |
| Natural Language Narrative | ~155 | 0.37× | Structural + some precision | Clinical reasoning, summarization |
| Structured Markdown | ~175 | 0.42× | Structural (references, URIs) | Comparison, enumeration, QA |
| Clinical Summary Template | ~160 | 0.38× | Structural + inferred fields | Documentation, clinical decision support |
| Hybrid Adaptive | ~155–420 | 0.37–1.00× | Task-dependent | Multi-task benchmarks |

**Key observation:** All non-JSON strategies achieve 56–63% token reduction relative to the raw FHIR representation while preserving the clinical facts necessary for downstream tasks. The efficiency–fidelity tradeoff is not monotonic: Structured Markdown retains more queryable structure than Narrative at comparable token cost, while the SOAP Template introduces inferred clinical reasoning (e.g., "inadequately controlled") absent from the source data.

---

*Figure 3 accompanies §3.3 (Serialization Strategy Design) of the FHIRBench paper.*


## Preliminary Observation and Hypothesis

The token efficiency data presented in Table 2 constitutes a **preliminary observation from a single illustrative patient record** — not a statistically validated finding. This example serves to motivate the following testable hypothesis that guides our benchmark evaluation:

> **Hypothesis H1 (Token Efficiency):** Non-JSON serialization strategies will achieve 40–65% token reduction relative to raw FHIR JSON across the full benchmark dataset (n=1,000), while preserving sufficient clinical information to maintain task accuracy within acceptable margins.

> **Hypothesis H2 (Accuracy-Cost Tradeoff):** The relationship between token reduction and accuracy loss is non-linear — a Pareto frontier exists where certain strategies (predicted: Structured Markdown, Clinical Template) achieve disproportionately high accuracy relative to their token cost.

> **Hypothesis H3 (Model-Format Interaction):** The optimal serialization strategy varies by model architecture and scale, with narrative formats favoring smaller open-weight models and structured formats favoring frontier proprietary models [CITE:TGZ97SRN].

These hypotheses are formally tested in Section 4 (Results) using the full 1,000-patient benchmark dataset across 90 experimental conditions. The illustrative example above demonstrates the *mechanism* of token reduction — the benchmark quantifies its *statistical significance and practical impact*.

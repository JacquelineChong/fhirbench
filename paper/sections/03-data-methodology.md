# Section 3.2: Data Generation and Synthetic Patient Methodology

## 3.2.1 Justification for Synthetic Data

The use of synthetic patient data for clinical AI benchmarking is well-established in the literature. Walonoski et al. [CITE:DM8RNZGT] introduced Synthea, a synthetic patient generator that models disease progression as probabilistic state machines seeded with census-derived demographics, producing clinically plausible FHIR R4 patient records. Multiple benchmark studies have adopted Synthea as their primary data source, including SM3-Text-to-Query [CITE:2MV7H8T6] (NeurIPS 2024), which employed Synthea data with SNOMED-CT coding for multi-model medical query evaluation, and LLM on FHIR [CITE:DQT7VP7M], which utilized SyntheticMass FHIR data for patient-facing LLM evaluation. SimSUM [CITE:4HSNVBCA] further demonstrates methodological precedent with 10,000 synthetic records linking structured and unstructured medical data.

A systematic review of synthetic health data generation methods [CITE:NH4RWDJN] confirms that modern generators preserve temporal patterns and clinical correlations when properly configured. Additionally, recent work on quality assessment frameworks for synthetic tabular data in healthcare [CITE:49SPNWUR] establishes rigorous evaluation criteria — fidelity, utility, and privacy — that validate synthetic data as appropriate for benchmarking when these properties are maintained. Critical challenges in evaluating synthetic tabular data [CITE:Z3JX5SC3] further emphasize the importance of domain-specific validation, which we address through our multi-dimensional realism parameters (Section 3.2.3).

Synthetic data offers three key advantages for serialization benchmarking:

1. **Reproducibility** — Any researcher can regenerate identical datasets using the same seed, eliminating dependency on restricted real-world data access agreements.
2. **Controlled experimental design** — We systematically vary clinical complexity across domains (diabetes, cardiovascular, medication interactions, preventive care) without confounding factors present in observational EHR data.
3. **Ethical compliance** — No IRB approval, data use agreements, or de-identification pipelines are required, enabling open-source publication of all experimental materials.

Recent work by Kramer et al. [CITE:TH7NPVEX] demonstrates that LLM-assisted refinement of Synthea modules can further improve the clinical realism of generated data, while methods for creating realistic synthetic medication data [CITE:7R3TAG3G] provide domain-specific enhancement techniques applicable to our polypharmacy scenarios.

## 3.2.2 Pipeline Validation Dataset (n=50)

Prior to executing the full benchmark (4,500 Bedrock API calls, estimated cost $75–200), we constructed a minimal validation dataset of 50 idealized FHIR R4 patient bundles (approximately 12–13 per clinical domain) to verify end-to-end pipeline correctness.

**Validation dataset characteristics:**
- **Clean coding** — All conditions, medications, and observations use standard SNOMED CT, LOINC, and RxNorm codes without coding errors
- **Complete records** — No missing observations or incomplete medication histories
- **Single-path diagnoses** — Each patient presents a clear clinical picture without diagnostic ambiguity
- **Balanced distribution** — Equal representation across all 4 clinical domains
- **US locale** — US Core FHIR profile, English-language, imperial units

**Purpose:** This idealized dataset confirms that:
- All 6 serializers produce syntactically valid output from FHIR bundles
- Task generators extract correct ground-truth answers
- The evaluation harness correctly scores model responses
- The Bedrock client successfully invokes all 5 models
- Results are correctly persisted and the full pipeline executes without errors

**Limitation explicitly noted:** The validation dataset does NOT represent the complexity of real clinical data. Pipeline correctness is necessary but insufficient — the full benchmark uses a more realistic 1,000-patient dataset (Section 3.2.3).

## 3.2.3 Benchmark Dataset Design (n=1,000): Toward Clinical Realism

The full benchmark dataset of 1,000 patients is generated via Synthea with additional noise injection and complexity enhancements designed to approximate real-world EHR characteristics. We address five key dimensions of clinical data realism:

### A. Geographic and Regulatory Scope

The current benchmark is scoped to a single geographic region to control for regulatory, terminological, and clinical practice variation:

| Parameter | Current Setting | Rationale |
|-----------|----------------|-----------|
| **Region** | United States | Largest FHIR deployment market; most Synthea modules validated for US demographics |
| **FHIR Profile** | US Core R4 | Standard US implementation guide; mandated by ONC Cures Act [CITE:TURQFSSV] |
| **Terminology locale** | en-US | English clinical text; US drug names (e.g., "Acetaminophen" not "Paracetamol") |
| **Unit system** | Imperial (with SI equivalents) | US lab conventions (mg/dL for glucose, cholesterol) |
| **Drug naming** | Brand + generic (mixed) | Reflects real US EHR documentation patterns |
| **Coding system** | ICD-10-CM + SNOMED CT + LOINC + RxNorm | Standard US clinical terminology stack |

**Configuration (experiment.yaml):**
```yaml
data:
  geography:
    region: "US"
    fhir_profile: "us-core-r4"
    terminology_locale: "en-US"
    unit_system: "imperial"
    drug_naming: "brand+generic"
    coding_systems: ["ICD-10-CM", "SNOMED-CT", "LOINC", "RxNorm"]
```

**Impact on serialization evaluation:** Geographic scope directly affects:
- **Terminology resolution** — Serializers resolving SNOMED/LOINC codes produce US-specific display text
- **Narrative generation** — Clinical narrative assumes US clinical conventions (SOAP notes, US medication brands)
- **Template selection** — Clinical summary templates follow US documentation standards

### B. Diagnostic Ambiguity (False Positives and Negatives)

Real clinical data contains diagnostic uncertainty that affects serialization fidelity:

| Challenge | Implementation | FHIR Representation | Rate |
|-----------|---------------|---------------------|------|
| **Ruled-out conditions** | Conditions with `clinicalStatus: inactive` and `verificationStatus: refuted` | Tests whether serializers correctly distinguish active from refuted | 15% |
| **Suspected conditions** | Conditions with `verificationStatus: provisional` or `differential` | Evaluates model treatment of uncertain diagnoses | 10% |
| **Resolved conditions** | Historical conditions in patient timeline | Tests temporal reasoning across formats | 20% |
| **Symptom-only records** | Observations without corresponding Condition diagnoses | Evaluates false-negative handling | 5% |

### C. Data Completeness and Missing Values

| Challenge | Implementation | Rate |
|-----------|---------------|------|
| **Missing lab results** | Omit key Observation resources (e.g., HbA1c for diabetes patients) | 15% |
| **Incomplete medication history** | MedicationRequest without `dosageInstruction` | 10% |
| **Missing demographics** | Omit `Patient.address` or `Patient.telecom` | 8% |
| **Temporal gaps** | 6+ month gaps in encounter history | 20% |

### D. Clinical Complexity (Comorbidity and Polypharmacy)

| Complexity Level | Distribution | Characteristics |
|-----------------|-------------|-----------------|
| **Simple** (1–2 conditions) | 25% | Single primary condition + 1 medication |
| **Moderate** (3–4 conditions) | 40% | Primary condition + comorbidities + 3–5 medications |
| **Complex** (5+ conditions) | 25% | Multiple interacting conditions + polypharmacy (6+ medications) |
| **Highly complex** (7+ conditions) | 10% | Extensive medication list + drug interactions + care coordination |

### E. Coding Variability and Errors

| Challenge | Implementation | Impact on Serialization | Rate |
|-----------|---------------|------------------------|------|
| **Multiple coding systems** | Same condition in ICD-10-CM and SNOMED CT | Tests terminology resolution | 20% |
| **Specificity variation** | Parent codes (E11) vs. child codes (E11.65) | Tests granularity preservation | 15% |
| **Display text inconsistency** | Some resources include `display`, others only `code` | Tests code resolution | 10% |
| **Legacy mappings** | Deprecated codes (ICD-9 → ICD-10 transitions) | Tests robustness | 5% |

### Full Realism Configuration

```yaml
data:
  n_patients: 1000
  conditions:
    - diabetes: 250
    - cardiovascular: 250
    - medication_interactions: 250
    - preventive_care: 250
  geography:
    region: "US"
    fhir_profile: "us-core-r4"
    terminology_locale: "en-US"
    unit_system: "imperial"
    drug_naming: "brand+generic"
    coding_systems: ["ICD-10-CM", "SNOMED-CT", "LOINC", "RxNorm"]
  realism:
    diagnostic_ambiguity:
      ruled_out_rate: 0.15
      provisional_rate: 0.10
      resolved_rate: 0.20
      symptom_only_rate: 0.05
    missing_data:
      missing_labs_rate: 0.15
      incomplete_medications_rate: 0.10
      missing_demographics_rate: 0.08
      temporal_gaps_rate: 0.20
    complexity:
      simple: 0.25
      moderate: 0.40
      complex: 0.25
      highly_complex: 0.10
    coding_variability:
      dual_coding_rate: 0.20
      specificity_variation_rate: 0.15
      missing_display_text_rate: 0.10
      legacy_code_rate: 0.05
```

### Validation Against Real-World Distributions

To ensure our synthetic data approximates real clinical distributions, we calibrate against published epidemiological statistics:

- **Comorbidity rates** — Calibrated to the CDC Behavioral Risk Factor Surveillance System (BRFSS) 2013–2023 data, which reports that 8 in 10 midlife adults (45–64) and 9 in 10 older adults (65+) have one or more chronic conditions [CITE:WT82MB8Z]. Condition co-occurrence patterns follow the NCHS Data Brief on chronic condition prevalence among adults age 45 and older [CITE:TI76MVBU].
- **Medication count per patient** — Mean approximately 4 medications per ambulatory patient, consistent with polypharmacy literature defining ≥5 medications as the polypharmacy threshold; our moderate-complexity patients (3–4 conditions) average 3–5 medications while highly complex patients (7+) average 6–10, aligning with published pharmacy claims analyses.
- **Lab result ranges** — Normal/abnormal distributions seeded from NHANES laboratory reference ranges (e.g., HbA1c normal <5.7%, pre-diabetes 5.7–6.4%, diabetes ≥6.5%; total cholesterol desirable <200 mg/dL, borderline 200–239, high ≥240 mg/dL).
- **Missing data rates** — Set at 8–25% depending on field type, consistent with published EHR data completeness assessments reporting that structured clinical data fields exhibit 10–30% missingness in routine practice, with laboratory values and vital signs showing higher completeness than social history and functional status.
- **Diagnostic uncertainty prevalence** — 10–20% of encounters involve provisional or differential diagnoses, consistent with clinical documentation studies reporting that approximately 15% of diagnoses carry uncertainty at the time of initial encounter documentation.

## 3.2.4 Geographic Limitations and Future Extension

The current benchmark is constrained to a single geographic and regulatory context (United States, US Core FHIR R4). This limitation impacts generalizability in several ways:

| Dimension | US (Current) | Potential Extensions |
|-----------|-------------|---------------------|
| **FHIR profiles** | US Core R4 | UK Core, AU Core, International Patient Summary (IPS) |
| **Terminologies** | ICD-10-CM, SNOMED CT (US edition) | ICD-10-UK, SNOMED CT (International), local extensions |
| **Drug naming** | US brand names (Acetaminophen, Epinephrine) | International names (Paracetamol, Adrenaline) |
| **Clinical conventions** | SOAP notes, US lab units | SBAR (UK), metric-only units (international) |
| **Language** | English (monolingual) | Bilingual records (HK: English+Chinese, Singapore: English+Malay/Tamil) |
| **Regulatory context** | ONC Cures Act, HIPAA | GDPR (EU), My Health Record Act (AU), PDPO (HK) |

**Serialization-specific implications of geographic extension:**
- Narrative serializers must handle multilingual content and culturally appropriate clinical summaries
- Template serializers need region-specific clinical documentation standards
- Terminology resolution becomes more complex with international coding systems
- Token efficiency varies significantly with non-Latin scripts (Chinese characters consume more tokens)

**Future work** (Section 6) proposes extending FHIRBench to:
1. UK Core and AU Core profiles (English-speaking, different conventions)
2. International Patient Summary (IPS) for cross-border scenarios
3. Multilingual implementations (Hong Kong, Singapore) where dual-language FHIR resources present unique serialization challenges

## 3.2.5 Limitations of Synthetic Data

We explicitly acknowledge the following limitations:

1. **No rare diseases** — Synthea's state machines cover common conditions; rare pathologies and orphan diseases are underrepresented
2. **Simplified care trajectories** — Real patients move between providers, creating fragmented records not captured in single-system Synthea output
3. **Cultural/linguistic homogeneity** — Generated data follows US healthcare patterns; international FHIR implementations may differ substantially (Section 3.2.4)
4. **No clinician variability** — Real EHRs reflect individual documentation styles, abbreviation preferences, and copy-paste artifacts; Synthea produces uniform structure
5. **Idealized coding quality** — Even with our noise injection (Section 3.2.3E), real coding error rates and patterns are more heterogeneous
6. **Population bias** — Synthea uses US Census demographics; underrepresentation of minority populations in source data propagates to synthetic output

**Mitigation:** We position synthetic data as a *controlled experimental substrate* for measuring relative differences between serialization strategies — not as a claim of absolute real-world performance. The key finding (which strategy outperforms which) transfers to real data even if absolute accuracy numbers differ. Future work (Section 6) proposes validation extension to MIMIC-IV FHIR (real de-identified US data) and multi-site international datasets.

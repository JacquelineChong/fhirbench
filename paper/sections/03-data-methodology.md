# Section 3.2: Data Generation and Synthetic Patient Methodology

## 3.2.1 Justification for Synthetic Data

The use of synthetic patient data for clinical AI benchmarking is well-established in the literature. Walonoski et al. [CITE:DM8RNZGT] introduced Synthea, a synthetic patient generator that models disease progression as probabilistic state machines seeded with census-derived demographics, producing clinically plausible FHIR R4 patient records. Multiple benchmark studies have adopted Synthea as their primary data source, including SM3-Text-to-Query [CITE:2MV7H8T6] (NeurIPS 2024), which employed Synthea data with SNOMED-CT coding for multi-model medical query evaluation, and LLM on FHIR [CITE:DQT7VP7M], which utilized SyntheticMass FHIR data for patient-facing LLM evaluation.

Synthetic data offers three key advantages for serialization benchmarking:

1. **Reproducibility** — Any researcher can regenerate identical datasets using the same seed, eliminating dependency on restricted real-world data access agreements.
2. **Controlled experimental design** — We systematically vary clinical complexity across domains (diabetes, cardiovascular, medication interactions, preventive care) without confounding factors present in observational EHR data.
3. **Ethical compliance** — No IRB approval, data use agreements, or de-identification pipelines are required, enabling open-source publication of all experimental materials.

Recent work by Kramer et al. [CITE:TH7NPVEX] demonstrates that LLM-assisted refinement of Synthea modules can further improve the clinical realism of generated data, while systematic reviews of synthetic health data generation methods [CITE:NEW_SDG_REVIEW] confirm that modern generators preserve temporal patterns and clinical correlations when properly configured.

## 3.2.2 Pipeline Validation Dataset (n=50)

Prior to executing the full benchmark (4,500 Bedrock API calls, estimated cost $75–200), we constructed a minimal validation dataset of 50 idealized FHIR R4 patient bundles (approximately 12–13 per clinical domain) to verify end-to-end pipeline correctness.

**Validation dataset characteristics:**
- **Clean coding** — All conditions, medications, and observations use standard SNOMED CT, LOINC, and RxNorm codes without coding errors
- **Complete records** — No missing observations or incomplete medication histories
- **Single-path diagnoses** — Each patient presents a clear clinical picture without diagnostic ambiguity
- **Balanced distribution** — Equal representation across all 4 clinical domains

**Purpose:** This idealized dataset confirms that:
- All 6 serializers produce syntactically valid output from FHIR bundles
- Task generators extract correct ground-truth answers
- The evaluation harness correctly scores model responses
- The Bedrock client successfully invokes all 5 models
- Results are correctly persisted and the full pipeline executes without errors

**Limitation explicitly noted:** The validation dataset does NOT represent the complexity of real clinical data. Pipeline correctness is necessary but insufficient — the full benchmark uses a more realistic 1,000-patient dataset (Section 3.2.3).

## 3.2.3 Benchmark Dataset Design (n=1,000): Toward Clinical Realism

The full benchmark dataset of 1,000 patients is generated via Synthea with additional noise injection and complexity enhancements designed to approximate real-world EHR characteristics. We address four key dimensions of clinical data realism:

### A. Diagnostic Ambiguity (False Positives and Negatives)

Real clinical data contains diagnostic uncertainty that affects serialization fidelity:

| Challenge | Implementation | FHIR Representation |
|-----------|---------------|---------------------|
| **Ruled-out conditions** | 15% of patients include conditions with `clinicalStatus: inactive` and `verificationStatus: refuted` | Tests whether serializers correctly distinguish active from refuted diagnoses |
| **Suspected conditions** | 10% include conditions with `verificationStatus: provisional` or `verificationStatus: differential` | Evaluates whether models treat uncertain diagnoses appropriately |
| **Resolved conditions** | 20% include historically resolved conditions in the patient timeline | Tests temporal reasoning across serialization formats |
| **Symptom-only records** | 5% present symptoms (Observation resources) without corresponding Condition diagnoses | Evaluates false-negative handling |

### B. Data Completeness and Missing Values

| Challenge | Implementation | Prevalence |
|-----------|---------------|-----------|
| **Missing lab results** | Omit key Observation resources (e.g., HbA1c for diabetes patients) | 15% of patients |
| **Incomplete medication history** | Include MedicationRequest without `dosageInstruction` | 10% of records |
| **Missing demographics** | Omit `Patient.address` or `Patient.telecom` | 8% of patients |
| **Temporal gaps** | 6+ month gaps in encounter history | 20% of patients |

### C. Clinical Complexity (Comorbidity and Polypharmacy)

Real patients rarely present with single isolated conditions:

| Complexity Level | Distribution | Characteristics |
|-----------------|-------------|-----------------|
| **Simple** (1–2 conditions) | 25% | Single primary condition + 1 medication |
| **Moderate** (3–4 conditions) | 40% | Primary condition + comorbidities + 3–5 medications |
| **Complex** (5+ conditions) | 25% | Multiple interacting conditions + polypharmacy (6+ medications) |
| **Highly complex** (7+ conditions) | 10% | Extensive medication list + drug interactions + care coordination challenges |

### D. Coding Variability and Errors

Real EHR systems exhibit coding heterogeneity:

| Challenge | Implementation | Impact on Serialization |
|-----------|---------------|------------------------|
| **Multiple coding systems** | Same condition coded in both ICD-10-CM and SNOMED CT | Tests terminology resolution across formats |
| **Specificity variation** | Some conditions use parent codes (E11 — Type 2 DM), others use child codes (E11.65 — T2DM with hyperglycemia) | Evaluates whether serializers lose granularity |
| **Display text inconsistency** | Some resources include `display` text, others only `code` | Tests raw-code vs. resolved-text serialization |
| **Legacy mappings** | Include deprecated or superseded codes (ICD-9 → ICD-10 transitions) | Tests robustness to imperfect coding |

### Configuration

The noise injection parameters are configurable via `config/experiment.yaml`:

```yaml
data:
  n_patients: 1000
  conditions:
    - diabetes (250 patients)
    - cardiovascular (250 patients)
    - medication_interactions (250 patients)
    - preventive_care (250 patients)
  realism:
    ruled_out_conditions_rate: 0.15
    provisional_diagnoses_rate: 0.10
    resolved_conditions_rate: 0.20
    missing_labs_rate: 0.15
    incomplete_medications_rate: 0.10
    missing_demographics_rate: 0.08
    temporal_gaps_rate: 0.20
    complexity_distribution:
      simple: 0.25
      moderate: 0.40
      complex: 0.25
      highly_complex: 0.10
    coding_variability:
      dual_coding_rate: 0.20
      specificity_variation_rate: 0.15
      missing_display_text_rate: 0.10
```

### Validation Against Real-World Distributions

To ensure our synthetic data approximates real clinical distributions, we calibrate against published statistics:

- **Comorbidity rates** — Calibrated to CDC NHANES prevalence data for adults 45–75
- **Medication count per patient** — Mean 4.2 (SD 3.1), matching pharmacy claims literature
- **Lab result ranges** — Normal/abnormal distributions seeded from population reference ranges (NHANES)
- **Missing data rates** — Calibrated to published EHR completeness studies (8–25% missing values depending on field)

## 3.2.4 Limitations of Synthetic Data

We explicitly acknowledge the following limitations:

1. **No rare diseases** — Synthea's state machines cover common conditions; rare pathologies are underrepresented
2. **Simplified care trajectories** — Real patients move between providers, creating fragmented records not captured in single-system Synthea output
3. **Cultural/linguistic homogeneity** — Generated data follows US healthcare patterns; international FHIR implementations may differ
4. **No clinician variability** — Real EHRs reflect individual documentation styles; Synthea produces uniform structure

**Mitigation:** We position synthetic data as a *controlled experimental substrate* rather than a claim of real-world generalizability. Future work (Section 6) proposes extension to MIMIC-IV FHIR and multi-site real-world datasets.

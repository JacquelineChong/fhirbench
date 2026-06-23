# FHIR Patient Bundles (Evaluation Subset)

35 synthetic FHIR R4 bundles selected for Layer 1 evaluation.

## Selection Criteria

- Complexity: COMPLEX or HIGHLY_COMPLEX only
- Stratified by domain:
  - `diabetes/` — 8 patients
  - `cardiovascular/` — 10 patients  
  - `medication_interactions/` — 5 patients
  - `preventive_care/` — 12 patients

## Bundle Structure

Each JSON file is a valid FHIR R4 Bundle containing:
- Patient resource
- Conditions (active diagnoses)
- MedicationRequests (current medications)
- Observations (vitals, labs)
- AllergyIntolerances
- Procedures
- Immunizations

## Source

Generated with Synthea (modified configs) + post-processing for clinical complexity.
See `manifest_35_complex.csv` for patient metadata.

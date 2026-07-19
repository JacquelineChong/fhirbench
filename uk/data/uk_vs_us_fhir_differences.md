# UK Core vs US Core FHIR: Key Differences for Serialization

## Overview

UK Core FHIR R4 (STU3) is maintained by HL7 UK and published on Simplifier.net under the project "HL7 FHIR® UK Core R4". It adapts the base FHIR R4 specification to NHS/UK healthcare requirements, in contrast to US Core which adapts to ONC/CMS requirements.

---

## 1. Patient Identification

| Element | US Core | UK Core |
|---------|---------|---------|
| Primary ID | SSN / MRN | NHS Number (10-digit, check digit validated) |
| ID System URI | `http://hl7.org/fhir/sid/us-ssn` | `https://fhir.nhs.uk/Id/nhs-number` |
| Verification | N/A | `nhsNumberVerificationStatus` extension |
| Secondary IDs | State driver's license | CHI (Scotland), H&C Number (N. Ireland) |

### Serialization Impact
- NHS Numbers have a strict format (3 digits, space, 3 digits, space, 4 digits in display)
- Verification status adds metadata that may confuse LLMs if serialized verbosely

---

## 2. Provider / Organization

| Element | US Core | UK Core |
|---------|---------|---------|
| Provider ID | NPI (10-digit) | GMP/GMC number, SDS User ID |
| Organization ID | NPI | ODS Code |
| Primary care | PCP reference | GP Practice registration (extension) |
| Care setting | Facility type | NHS Trust / CCG / ICB |

### Serialization Impact
- GP Practice is an extension (`UKCore-NominatedPharmacy`, `UKCore-PreferredBranchSurgery`)
- ODS codes are short alphanumeric (e.g., "Y12345") vs NPI's 10-digit numeric

---

## 3. Medication Coding

| Element | US Core | UK Core |
|---------|---------|---------|
| Primary drug coding | RxNorm | dm+d (Dictionary of Medicines and Devices) |
| Code system URI | `http://www.nlm.nih.gov/research/umls/rxnorm` | `https://dmd.nhs.uk` |
| Drug names | US brand names (e.g., Tylenol) | UK approved names (e.g., paracetamol) |
| Dose syntax | "500mg PO BID" | "500mg oral twice daily" (less abbreviation) |

### Serialization Impact
- dm+d codes are longer and hierarchical (VTM → VMP → AMP → VMPP → AMPP)
- UK uses generic names predominantly; brand names less common
- Dose instructions follow different conventions

---

## 4. Clinical Coding Systems

| System | US Core | UK Core |
|--------|---------|---------|
| Diagnoses | ICD-10-CM, SNOMED CT US | ICD-10-UK (5th edition), SNOMED CT UK Edition |
| Procedures | CPT, HCPCS, SNOMED CT US | OPCS-4, SNOMED CT UK |
| Lab codes | LOINC | LOINC (shared) + local NHS codes |
| Ethnicity | CDC Race/Ethnicity | NHS Ethnic Category (16+1 categories) |
| Religion | HL7 v3 Religious Affiliation | NHS Data Dictionary Religion codes |

### Serialization Impact
- SNOMED CT UK Edition includes ~30,000 UK-specific concepts (NHS Read Codes mapped)
- ICD-10-UK has additional codes not in ICD-10-CM (e.g., U07.1 for COVID)
- NHS Ethnic Category uses different granularity than US OMB categories

---

## 5. UK Core Extensions (not in US Core)

| Extension | Purpose |
|-----------|---------|
| `UKCore-NHSNumberVerificationStatus` | Confirms NHS number validity |
| `UKCore-EthnicCategory` | NHS ethnic category (mandatory in some contexts) |
| `UKCore-ReligiousAffiliation` | NHS religion coding |
| `UKCore-NominatedPharmacy` | Patient's chosen pharmacy |
| `UKCore-DeathNotificationStatus` | Death registration status |
| `UKCore-ContactPreference` | Communication preferences |
| `UKCore-BirthSex` | Registered birth sex |
| `UKCore-ResidentialStatus` | Immigration/residential status |
| `UKCore-CodingSCTDescId` | SNOMED CT description ID |
| `UKCore-MedicationTradeFamily` | dm+d trade family grouping |

---

## 6. Terminology & Language

| Aspect | US | UK |
|--------|----|----|
| Spelling | "pediatric", "anemia" | "paediatric", "anaemia" |
| Units | lbs, Fahrenheit common | kg, Celsius standard |
| Date format | MM/DD/YYYY in display | DD/MM/YYYY in display |
| Care levels | "outpatient", "ER" | "outpatient", "A&E" / "ED" |
| Documents | "progress note" | "clinical letter", "discharge summary" |

### Serialization Impact
- Narrative serializers must use UK English spelling
- Unit conversion not needed but display format differs
- Clinical abbreviations differ (A&E vs ER, GP vs PCP)

---

## 7. Profiles with Significant Structural Differences

| Profile | Key UK Difference |
|---------|-------------------|
| `UKCore-Patient` | NHS Number, GP registration, ethnic category |
| `UKCore-MedicationRequest` | dm+d coding, NHS prescribing context |
| `UKCore-AllergyIntolerance` | Causative agent from dm+d |
| `UKCore-Encounter` | NHS service type coding |
| `UKCore-Organization` | ODS code, NHS Trust structure |
| `UKCore-Practitioner` | GMP/GMC number, SDS role |

---

## 8. Implications for FHIRBench-UK

1. **Patient Generation**: Must use realistic NHS Numbers, UK names, UK addresses, GP practices
2. **Medication Serialization**: dm+d hierarchy adds complexity; generic names are standard
3. **Clinical Notes**: NHS SOAP format, UK spelling, NHS-specific abbreviations
4. **Evaluation**: Must test extraction of UK-specific coded elements (NHS Number, dm+d codes, SNOMED CT UK)
5. **Cross-national comparison**: Direct comparison possible on shared elements (vitals, labs via LOINC)

---

## Sources
- UK Core FHIR IG: https://simplifier.net/HL7FHIRUKCoreR4
- NHS Data Dictionary: https://www.datadictionary.nhs.uk/
- dm+d: https://www.nhsbsa.nhs.uk/pharmacies-gp-practices-and-appliance-contractors/dictionary-medicines-and-devices-dmd
- US Core: https://www.hl7.org/fhir/us/core/

"""Generate synthetic FHIR R4 bundles using fhir.resources (no Java/Synthea required).

Produces 50 patients (13 per domain, 12 for last) across 4 clinical categories:
diabetes, cardiovascular, medication_interactions, preventive_care.
"""

import csv
import json
import random
import uuid
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path(__file__).parent / "fhir_bundles"
MANIFEST_PATH = Path(__file__).parent / "manifest.csv"

FIRST_NAMES = ["James","Mary","John","Patricia","Robert","Jennifer","Michael","Linda",
               "David","Elizabeth","William","Barbara","Richard","Susan","Joseph","Jessica",
               "Thomas","Sarah","Charles","Karen","Christopher","Lisa","Daniel","Nancy",
               "Matthew","Betty","Anthony","Margaret","Mark","Sandra"]
LAST_NAMES = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
              "Rodriguez","Martinez","Hernandez","Lopez","Gonzalez","Wilson","Anderson",
              "Thomas","Taylor","Moore","Jackson","Martin","Lee","Perez","Thompson","White"]

# Clinical data per domain
DIABETES_CONDITIONS = [
    ("44054006", "Diabetes mellitus type 2"),
    ("46635009", "Diabetes mellitus type 1"),
    ("237627000", "Gestational diabetes"),
]
DIABETES_MEDS = [
    ("860975", "Metformin 500 MG"),
    ("897122", "Insulin glargine 100 UNT/ML"),
    ("861007", "Glipizide 5 MG"),
]
DIABETES_OBS = [("4548-4", "Hemoglobin A1c", "%", 5.5, 12.0),
                ("2345-7", "Glucose", "mg/dL", 70, 300)]

CARDIO_CONDITIONS = [
    ("53741008", "Coronary arteriosclerosis"),
    ("22298006", "Myocardial infarction"),
    ("38341003", "Hypertensive disorder"),
]
CARDIO_MEDS = [
    ("197361", "Lisinopril 10 MG"),
    ("309362", "Atorvastatin 20 MG"),
    ("833036", "Metoprolol 50 MG"),
]
CARDIO_OBS = [("2093-3", "Total Cholesterol", "mg/dL", 150, 300),
              ("8480-6", "Systolic BP", "mmHg", 100, 180)]

MED_INTERACTION_CONDITIONS = [
    ("36971009", "Sinusitis"),
    ("82423001", "Chronic pain"),
    ("35489007", "Depression"),
]
MED_INTERACTION_MEDS = [
    ("849574", "Warfarin 5 MG"),
    ("197591", "Ibuprofen 400 MG"),
    ("312938", "Sertraline 50 MG"),
    ("198240", "Amiodarone 200 MG"),
]
MED_INTERACTION_OBS = [("6301-6", "INR", "{ratio}", 1.0, 4.5),
                       ("33914-3", "eGFR", "mL/min/1.73m2", 30, 120)]

PREVENTIVE_CONDITIONS = [
    ("160903007", "Full-time employment"),
    ("162864005", "Body mass index 30+"),
    ("266948004", "Hypertension screening"),
]
PREVENTIVE_MEDS = [
    ("316672", "Influenza vaccine"),
    ("140004", "Tetanus vaccine"),
]
PREVENTIVE_OBS = [("39156-5", "BMI", "kg/m2", 18.5, 40.0),
                  ("8302-2", "Body height", "cm", 150, 195)]

DOMAINS = {
    "diabetes": {"conditions": DIABETES_CONDITIONS, "meds": DIABETES_MEDS, "obs": DIABETES_OBS, "count": 13},
    "cardiovascular": {"conditions": CARDIO_CONDITIONS, "meds": CARDIO_MEDS, "obs": CARDIO_OBS, "count": 13},
    "medication_interactions": {"conditions": MED_INTERACTION_CONDITIONS, "meds": MED_INTERACTION_MEDS, "obs": MED_INTERACTION_OBS, "count": 13},
    "preventive_care": {"conditions": PREVENTIVE_CONDITIONS, "meds": PREVENTIVE_MEDS, "obs": PREVENTIVE_OBS, "count": 11},
}


def random_date(start_year=1940, end_year=2000):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


def make_patient(idx):
    patient_id = str(uuid.uuid4())
    gender = random.choice(["male", "female"])
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    birth = random_date()
    return {
        "resourceType": "Patient",
        "id": patient_id,
        "meta": {"profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]},
        "name": [{"use": "official", "family": last, "given": [first]}],
        "gender": gender,
        "birthDate": birth.isoformat(),
        "address": [{"city": "Boston", "state": "MA", "country": "US"}],
    }, patient_id


def make_condition(patient_id, code, display):
    return {
        "resourceType": "Condition",
        "id": str(uuid.uuid4()),
        "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
        "verificationStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "confirmed"}]},
        "code": {"coding": [{"system": "http://snomed.info/sct", "code": code, "display": display}], "text": display},
        "subject": {"reference": f"Patient/{patient_id}"},
        "onsetDateTime": (date.today() - timedelta(days=random.randint(30, 3650))).isoformat(),
    }


def make_medication(patient_id, code, display):
    return {
        "resourceType": "MedicationRequest",
        "id": str(uuid.uuid4()),
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": {"coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": code, "display": display}], "text": display},
        "subject": {"reference": f"Patient/{patient_id}"},
        "authoredOn": (date.today() - timedelta(days=random.randint(1, 365))).isoformat(),
    }


def make_observation(patient_id, code, display, unit, low, high):
    value = round(random.uniform(low, high), 1)
    return {
        "resourceType": "Observation",
        "id": str(uuid.uuid4()),
        "status": "final",
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory"}]}],
        "code": {"coding": [{"system": "http://loinc.org", "code": code, "display": display}], "text": display},
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": (date.today() - timedelta(days=random.randint(1, 90))).isoformat(),
        "valueQuantity": {"value": value, "unit": unit, "system": "http://unitsofmeasure.org", "code": unit},
    }


def make_encounter(patient_id):
    return {
        "resourceType": "Encounter",
        "id": str(uuid.uuid4()),
        "status": "finished",
        "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "AMB", "display": "ambulatory"},
        "subject": {"reference": f"Patient/{patient_id}"},
        "period": {"start": (date.today() - timedelta(days=random.randint(1, 365))).isoformat()},
    }


def build_bundle(patient_idx, domain_config):
    patient_resource, patient_id = make_patient(patient_idx)
    entries = [{"fullUrl": f"urn:uuid:{patient_resource['id']}", "resource": patient_resource}]

    # Add encounter
    encounter = make_encounter(patient_id)
    entries.append({"fullUrl": f"urn:uuid:{encounter['id']}", "resource": encounter})

    # Add 1-2 conditions
    for code, display in random.sample(domain_config["conditions"], min(2, len(domain_config["conditions"]))):
        cond = make_condition(patient_id, code, display)
        entries.append({"fullUrl": f"urn:uuid:{cond['id']}", "resource": cond})

    # Add 1-2 medications
    for code, display in random.sample(domain_config["meds"], min(2, len(domain_config["meds"]))):
        med = make_medication(patient_id, code, display)
        entries.append({"fullUrl": f"urn:uuid:{med['id']}", "resource": med})

    # Add observations
    for obs_data in domain_config["obs"]:
        obs = make_observation(patient_id, *obs_data)
        entries.append({"fullUrl": f"urn:uuid:{obs['id']}", "resource": obs})

    return {
        "resourceType": "Bundle",
        "id": str(uuid.uuid4()),
        "type": "transaction",
        "entry": entries,
    }


def validate_bundle(data):
    """Basic FHIR R4 Bundle validation."""
    if data.get("resourceType") != "Bundle":
        return False, "Not a Bundle"
    if not isinstance(data.get("entry"), list) or len(data["entry"]) == 0:
        return False, "No entries"
    for entry in data["entry"]:
        r = entry.get("resource", {})
        if "resourceType" not in r:
            return False, f"Entry missing resourceType"
    return True, None


def main():
    print("FHIRBench Synthetic Data Generation (Python fallback)")
    print("=" * 55)
    print("Java/Synthea not available — generating 50 FHIR R4 bundles with fhir.resources patterns\n")

    all_files = {}
    total_generated = 0
    total_valid = 0
    errors = []
    patient_idx = 0

    for domain, config in DOMAINS.items():
        domain_dir = OUTPUT_DIR / domain
        domain_dir.mkdir(parents=True, exist_ok=True)
        files = []

        for i in range(config["count"]):
            bundle = build_bundle(patient_idx, config)
            patient_idx += 1

            # Validate
            valid, err = validate_bundle(bundle)
            if not valid:
                errors.append(f"{domain}/patient_{patient_idx}: {err}")

            # Write
            filename = f"patient_{patient_idx:04d}_{domain}.json"
            filepath = domain_dir / filename
            with open(filepath, "w") as f:
                json.dump(bundle, f, indent=2)
            files.append(filepath)
            total_generated += 1
            if valid:
                total_valid += 1

        all_files[domain] = files
        print(f"  {domain}: {len(files)} bundles generated, all valid={len(files) == sum(1 for fp in files for _ in [1] if validate_bundle(json.loads(open(fp).read()))[0])}")

    # Write manifest
    with open(MANIFEST_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "condition", "path", "valid_fhir", "resource_count"])
        for domain, files in all_files.items():
            for fp in files:
                with open(fp) as jf:
                    data = json.load(jf)
                valid, _ = validate_bundle(data)
                writer.writerow([fp.name, domain, str(fp), valid, len(data.get("entry", []))])

    print(f"\n{'=' * 55}")
    print(f"RESULTS:")
    print(f"  Total patients generated: {total_generated}")
    print(f"  Total valid FHIR R4 bundles: {total_valid}")
    print(f"  Validation errors: {len(errors)}")
    if errors:
        for e in errors:
            print(f"    - {e}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  Manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()

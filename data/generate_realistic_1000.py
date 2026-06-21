#!/usr/bin/env python3
"""
Enhanced Realistic FHIR R4 Patient Bundle Generator
Generates 1,000 patient bundles (250 per domain) with full realism parameters.
"""

import json
import random
import uuid
import csv
import os
from datetime import datetime, timedelta
from copy import deepcopy

random.seed(42)

# ============================================================
# CONFIGURATION
# ============================================================
OUTPUT_DIR = os.path.expanduser("~/fhirbench/data/fhir_bundles_1000")
MANIFEST_PATH = os.path.expanduser("~/fhirbench/data/manifest_1000.csv")
DOMAINS = ["diabetes", "cardiovascular", "medication_interactions", "preventive_care"]
PATIENTS_PER_DOMAIN = 250

# Complexity distribution: SIMPLE=25%, MODERATE=40%, COMPLEX=25%, HIGHLY_COMPLEX=10%
COMPLEXITY_DISTRIBUTION = [
    ("SIMPLE", 250),
    ("MODERATE", 400),
    ("COMPLEX", 250),
    ("HIGHLY_COMPLEX", 100),
]

# ============================================================
# REALISTIC CODE SETS
# ============================================================
SNOMED_CONDITIONS = {
    "diabetes": [
        ("44054006", "Type 2 diabetes mellitus"),
        ("46635009", "Type 1 diabetes mellitus"),
        ("4855003", "Diabetic retinopathy"),
        ("127013003", "Diabetic renal disease"),
        ("368581000119106", "Neuropathy due to type 2 diabetes mellitus"),
        ("422034002", "Diabetic retinopathy associated with type II diabetes mellitus"),
        ("190330002", "Type 2 diabetes mellitus with hypoglycemia"),
        ("314771006", "Type 2 diabetes mellitus with neuropathic arthropathy"),
    ],
    "cardiovascular": [
        ("53741008", "Coronary arteriosclerosis"),
        ("22298006", "Myocardial infarction"),
        ("38341003", "Hypertensive disorder"),
        ("84114007", "Heart failure"),
        ("49436004", "Atrial fibrillation"),
        ("233970002", "Aortic valve stenosis"),
        ("82523003", "Congestive rheumatic heart failure"),
        ("399211009", "History of myocardial infarction"),
    ],
    "medication_interactions": [
        ("44054006", "Type 2 diabetes mellitus"),
        ("38341003", "Hypertensive disorder"),
        ("35489007", "Depressive disorder"),
        ("69896004", "Rheumatoid arthritis"),
        ("84114007", "Heart failure"),
        ("49436004", "Atrial fibrillation"),
        ("13644009", "Hypercholesterolemia"),
        ("161891005", "Backache"),
        ("431855005", "Chronic kidney disease stage 1"),
        ("73211009", "Diabetes mellitus"),
    ],
    "preventive_care": [
        ("414916001", "Obesity"),
        ("44054006", "Type 2 diabetes mellitus"),
        ("38341003", "Hypertensive disorder"),
        ("13644009", "Hypercholesterolemia"),
        ("56265001", "Heart disease"),
        ("195967001", "Asthma"),
        ("40930008", "Hypothyroidism"),
        ("73211009", "Diabetes mellitus"),
    ],
}

ICD10_CONDITIONS = {
    "diabetes": [
        ("E11", "Type 2 diabetes mellitus"),
        ("E11.9", "Type 2 diabetes mellitus without complications"),
        ("E11.65", "Type 2 diabetes mellitus with hyperglycemia"),
        ("E10", "Type 1 diabetes mellitus"),
        ("E10.9", "Type 1 diabetes mellitus without complications"),
        ("E11.311", "Type 2 diabetes mellitus with unspecified diabetic retinopathy with macular edema"),
        ("E11.21", "Type 2 diabetes mellitus with diabetic nephropathy"),
        ("E11.40", "Type 2 diabetes mellitus with diabetic neuropathy, unspecified"),
    ],
    "cardiovascular": [
        ("I25.10", "Atherosclerotic heart disease of native coronary artery without angina pectoris"),
        ("I21.9", "Acute myocardial infarction, unspecified"),
        ("I10", "Essential (primary) hypertension"),
        ("I50.9", "Heart failure, unspecified"),
        ("I48.91", "Unspecified atrial fibrillation"),
        ("I25.2", "Old myocardial infarction"),
        ("I50.22", "Chronic systolic (congestive) heart failure"),
        ("I11.0", "Hypertensive heart disease with heart failure"),
    ],
    "medication_interactions": [
        ("E11.9", "Type 2 diabetes mellitus without complications"),
        ("I10", "Essential (primary) hypertension"),
        ("F32.9", "Major depressive disorder, single episode, unspecified"),
        ("M06.9", "Rheumatoid arthritis, unspecified"),
        ("I50.9", "Heart failure, unspecified"),
        ("I48.91", "Unspecified atrial fibrillation"),
        ("E78.0", "Pure hypercholesterolemia"),
        ("M54.5", "Low back pain"),
        ("N18.1", "Chronic kidney disease, stage 1"),
        ("Z79.01", "Long term (current) use of anticoagulants"),
    ],
    "preventive_care": [
        ("E66.9", "Obesity, unspecified"),
        ("E11.9", "Type 2 diabetes mellitus without complications"),
        ("I10", "Essential (primary) hypertension"),
        ("E78.0", "Pure hypercholesterolemia"),
        ("I25.10", "Atherosclerotic heart disease of native coronary artery"),
        ("J45.20", "Mild intermittent asthma, uncomplicated"),
        ("E03.9", "Hypothyroidism, unspecified"),
        ("Z23", "Encounter for immunization"),
    ],
}

# Deprecated/legacy codes for 5% variability
LEGACY_CODES = [
    ("250.00", "http://hl7.org/fhir/sid/icd-9-cm", "Diabetes mellitus type II"),
    ("401.9", "http://hl7.org/fhir/sid/icd-9-cm", "Unspecified essential hypertension"),
    ("272.0", "http://hl7.org/fhir/sid/icd-9-cm", "Pure hypercholesterolemia"),
    ("414.01", "http://hl7.org/fhir/sid/icd-9-cm", "Coronary atherosclerosis of native coronary artery"),
    ("427.31", "http://hl7.org/fhir/sid/icd-9-cm", "Atrial fibrillation"),
]

LOINC_OBSERVATIONS = {
    "diabetes": [
        ("4548-4", "Hemoglobin A1c/Hemoglobin.total in Blood", "%", 5.5, 12.0),
        ("2345-7", "Glucose [Mass/volume] in Serum or Plasma", "mg/dL", 70, 350),
        ("2160-0", "Creatinine [Mass/volume] in Serum or Plasma", "mg/dL", 0.6, 2.5),
        ("14959-1", "Microalbumin [Mass/volume] in Urine", "mg/L", 0, 300),
        ("18262-6", "Low Density Lipoprotein Cholesterol", "mg/dL", 50, 200),
        ("2093-3", "Cholesterol [Mass/volume] in Serum or Plasma", "mg/dL", 120, 300),
    ],
    "cardiovascular": [
        ("2093-3", "Cholesterol [Mass/volume] in Serum or Plasma", "mg/dL", 120, 350),
        ("2571-8", "Triglyceride [Mass/volume] in Serum or Plasma", "mg/dL", 50, 500),
        ("18262-6", "Low Density Lipoprotein Cholesterol", "mg/dL", 40, 250),
        ("2085-9", "HDL Cholesterol", "mg/dL", 25, 90),
        ("85354-9", "Blood pressure panel", "mmHg", 90, 200),
        ("8867-4", "Heart rate", "/min", 50, 120),
        ("30313-1", "Hemoglobin [Mass/volume] in Blood", "g/dL", 10, 17),
        ("33762-6", "NT-proBNP", "pg/mL", 50, 5000),
    ],
    "medication_interactions": [
        ("6301-6", "INR in Platelet poor plasma by Coagulation assay", "INR", 0.8, 5.0),
        ("4548-4", "Hemoglobin A1c/Hemoglobin.total in Blood", "%", 5.5, 10.0),
        ("2160-0", "Creatinine [Mass/volume] in Serum or Plasma", "mg/dL", 0.6, 3.0),
        ("3094-0", "Urea nitrogen [Mass/volume] in Serum or Plasma", "mg/dL", 7, 40),
        ("2093-3", "Cholesterol [Mass/volume] in Serum or Plasma", "mg/dL", 120, 300),
        ("1742-6", "Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma", "U/L", 10, 120),
        ("1920-8", "Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma", "U/L", 10, 100),
    ],
    "preventive_care": [
        ("39156-5", "Body mass index (BMI) [Ratio]", "kg/m2", 18, 45),
        ("8302-2", "Body height", "in", 58, 76),
        ("29463-7", "Body weight", "lbs", 100, 350),
        ("85354-9", "Blood pressure panel", "mmHg", 90, 160),
        ("2093-3", "Cholesterol [Mass/volume] in Serum or Plasma", "mg/dL", 120, 280),
        ("2345-7", "Glucose [Mass/volume] in Serum or Plasma", "mg/dL", 70, 200),
    ],
}

MEDICATIONS = {
    "diabetes": [
        ("860975", "Metformin hydrochloride 500 MG Oral Tablet", "metformin", "Glucophage"),
        ("897122", "Metformin hydrochloride 1000 MG Oral Tablet", "metformin", "Glucophage"),
        ("311040", "Glipizide 5 MG Oral Tablet", "glipizide", "Glucotrol"),
        ("314076", "Lisinopril 10 MG Oral Tablet", "lisinopril", "Zestril"),
        ("1361493", "Insulin glargine 100 UNT/ML Injectable Solution", "insulin glargine", "Lantus"),
        ("1670007", "Empagliflozin 10 MG Oral Tablet", "empagliflozin", "Jardiance"),
        ("1598392", "Canagliflozin 100 MG Oral Tablet", "canagliflozin", "Invokana"),
        ("1368384", "Dapagliflozin 5 MG Oral Tablet", "dapagliflozin", "Farxiga"),
        ("261551", "Insulin lispro 100 UNT/ML Injectable Solution", "insulin lispro", "Humalog"),
        ("1243019", "Sitagliptin 100 MG Oral Tablet", "sitagliptin", "Januvia"),
    ],
    "cardiovascular": [
        ("617311", "Atorvastatin 20 MG Oral Tablet", "atorvastatin", "Lipitor"),
        ("859751", "Rosuvastatin calcium 10 MG Oral Tablet", "rosuvastatin", "Crestor"),
        ("866924", "Metoprolol Tartrate 50 MG Oral Tablet", "metoprolol", "Lopressor"),
        ("314076", "Lisinopril 10 MG Oral Tablet", "lisinopril", "Zestril"),
        ("979480", "Losartan potassium 50 MG Oral Tablet", "losartan", "Cozaar"),
        ("197361", "Amlodipine 5 MG Oral Tablet", "amlodipine", "Norvasc"),
        ("855332", "Carvedilol 12.5 MG Oral Tablet", "carvedilol", "Coreg"),
        ("854925", "Clopidogrel 75 MG Oral Tablet", "clopidogrel", "Plavix"),
        ("243670", "Aspirin 81 MG Oral Tablet", "aspirin", "Bayer"),
        ("310798", "Furosemide 40 MG Oral Tablet", "furosemide", "Lasix"),
        ("197884", "Digoxin 0.25 MG Oral Tablet", "digoxin", "Lanoxin"),
        ("1091643", "Sacubitril/Valsartan 49 MG-51 MG Oral Tablet", "sacubitril/valsartan", "Entresto"),
    ],
    "medication_interactions": [
        ("855288", "Warfarin Sodium 5 MG Oral Tablet", "warfarin", "Coumadin"),
        ("198405", "Naproxen 500 MG Oral Tablet", "naproxen", "Aleve"),
        ("310965", "Ibuprofen 400 MG Oral Tablet", "ibuprofen", "Advil"),
        ("312938", "Sertraline 50 MG Oral Tablet", "sertraline", "Zoloft"),
        ("596926", "Duloxetine 60 MG Delayed Release Oral Capsule", "duloxetine", "Cymbalta"),
        ("617311", "Atorvastatin 20 MG Oral Tablet", "atorvastatin", "Lipitor"),
        ("866924", "Metoprolol Tartrate 50 MG Oral Tablet", "metoprolol", "Lopressor"),
        ("314076", "Lisinopril 10 MG Oral Tablet", "lisinopril", "Zestril"),
        ("860975", "Metformin hydrochloride 500 MG Oral Tablet", "metformin", "Glucophage"),
        ("197361", "Amlodipine 5 MG Oral Tablet", "amlodipine", "Norvasc"),
        ("1049502", "Apixaban 5 MG Oral Tablet", "apixaban", "Eliquis"),
        ("2001413", "Tramadol Hydrochloride 50 MG Oral Tablet", "tramadol", "Ultram"),
        ("861004", "Omeprazole 20 MG Delayed Release Oral Capsule", "omeprazole", "Prilosec"),
        ("313782", "Gabapentin 300 MG Oral Capsule", "gabapentin", "Neurontin"),
        ("485489", "Prednisone 10 MG Oral Tablet", "prednisone", "Deltasone"),
    ],
    "preventive_care": [
        ("617311", "Atorvastatin 20 MG Oral Tablet", "atorvastatin", "Lipitor"),
        ("314076", "Lisinopril 10 MG Oral Tablet", "lisinopril", "Zestril"),
        ("860975", "Metformin hydrochloride 500 MG Oral Tablet", "metformin", "Glucophage"),
        ("311989", "Levothyroxine Sodium 0.05 MG Oral Tablet", "levothyroxine", "Synthroid"),
        ("197361", "Amlodipine 5 MG Oral Tablet", "amlodipine", "Norvasc"),
        ("104894", "Omeprazole 20 MG Delayed Release Oral Capsule", "omeprazole", "Prilosec"),
    ],
}

VACCINES = [
    ("197", "Influenza, seasonal, injectable", "88", "Influenza virus vaccine"),
    ("213", "SARS-COV-2 (COVID-19) vaccine, mRNA", "91303", "SARS-CoV-2 vaccine"),
    ("33", "Pneumococcal polysaccharide vaccine, 23 valent", "90732", "Pneumococcal vaccine"),
    ("113", "Td (adult) preservative free", "90714", "Td vaccine"),
    ("52", "Hepatitis A vaccine, adult dosage", "90632", "Hepatitis A vaccine"),
    ("140", "Influenza, seasonal, injectable, preservative free", "90688", "Influenza vaccine preservative free"),
]

FIRST_NAMES_M = ["James","John","Robert","Michael","David","William","Richard","Joseph","Thomas","Charles",
    "Christopher","Daniel","Matthew","Anthony","Mark","Donald","Steven","Andrew","Paul","Joshua",
    "Kenneth","Kevin","Brian","George","Timothy","Ronald","Edward","Jason","Jeffrey","Ryan"]
FIRST_NAMES_F = ["Mary","Patricia","Jennifer","Linda","Barbara","Elizabeth","Susan","Jessica","Sarah","Karen",
    "Lisa","Nancy","Betty","Margaret","Sandra","Ashley","Dorothy","Kimberly","Emily","Donna",
    "Michelle","Carol","Amanda","Melissa","Deborah","Stephanie","Rebecca","Sharon","Laura","Cynthia"]
LAST_NAMES = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
    "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores"]

US_STATES = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY",
    "LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND",
    "OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]
US_CITIES = ["New York","Los Angeles","Chicago","Houston","Phoenix","Philadelphia","San Antonio",
    "San Diego","Dallas","San Jose","Austin","Jacksonville","Fort Worth","Columbus","Charlotte",
    "Indianapolis","San Francisco","Seattle","Denver","Washington","Nashville","Oklahoma City",
    "El Paso","Boston","Portland","Las Vegas","Memphis","Louisville","Baltimore","Milwaukee"]

# Symptom observations (for undiagnosed symptoms)
SYMPTOM_OBSERVATIONS = [
    ("267036007", "Dyspnea"),
    ("25064002", "Headache"),
    ("22253000", "Pain"),
    ("84229001", "Fatigue"),
    ("62315008", "Diarrhea"),
    ("271807003", "Eruption of skin"),
    ("49727002", "Cough"),
    ("386661006", "Fever"),
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def gen_id():
    return str(uuid.uuid4())

def gen_date(start_year=2018, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = (end - start).days
    d = start + timedelta(days=random.randint(0, delta))
    return d.strftime("%Y-%m-%d")

def gen_datetime(start_year=2018, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = (end - start).days
    d = start + timedelta(days=random.randint(0, delta), hours=random.randint(0,23), minutes=random.randint(0,59))
    return d.strftime("%Y-%m-%dT%H:%M:%S+00:00")

def gen_birth_date(min_age=18, max_age=85):
    today = datetime(2025, 6, 1)
    age = random.randint(min_age, max_age)
    birth = today - timedelta(days=age*365 + random.randint(0, 364))
    return birth.strftime("%Y-%m-%d")

def assign_complexity(index):
    """Assign complexity based on distribution across all 1000 patients."""
    if index < 250:
        return "SIMPLE"
    elif index < 650:
        return "MODERATE"
    elif index < 900:
        return "COMPLEX"
    else:
        return "HIGHLY_COMPLEX"

def get_condition_count(complexity):
    if complexity == "SIMPLE": return random.randint(1, 2)
    elif complexity == "MODERATE": return random.randint(3, 4)
    elif complexity == "COMPLEX": return random.randint(5, 6)
    else: return random.randint(7, 10)

def get_medication_count(complexity):
    if complexity == "SIMPLE": return 1
    elif complexity == "MODERATE": return random.randint(3, 5)
    elif complexity == "COMPLEX": return random.randint(6, 8)
    else: return random.randint(10, 15)



# ============================================================
# FHIR RESOURCE BUILDERS
# ============================================================
def build_patient(patient_id, omit_address=False, omit_telecom=False):
    gender = random.choice(["male", "female"])
    if gender == "male":
        given = random.choice(FIRST_NAMES_M)
    else:
        given = random.choice(FIRST_NAMES_F)
    family = random.choice(LAST_NAMES)

    patient = {
        "resourceType": "Patient",
        "id": patient_id,
        "meta": {
            "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
        },
        "identifier": [{
            "system": "http://hospital.example.org/patient",
            "value": patient_id
        }],
        "active": True,
        "name": [{"use": "official", "family": family, "given": [given]}],
        "gender": gender,
        "birthDate": gen_birth_date(),
        "communication": [{"language": {"coding": [{"system": "urn:ietf:bcp:47", "code": "en-US", "display": "English (US)"}]}}],
    }

    if not omit_telecom:
        patient["telecom"] = [{"system": "phone", "value": f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}", "use": "home"}]

    if not omit_address:
        patient["address"] = [{
            "use": "home",
            "line": [f"{random.randint(100,9999)} {random.choice(['Main','Oak','Elm','Maple','Cedar','Pine','Washington','Park'])} {random.choice(['St','Ave','Blvd','Dr','Ln'])}"],
            "city": random.choice(US_CITIES),
            "state": random.choice(US_STATES),
            "postalCode": f"{random.randint(10000,99999)}",
            "country": "US"
        }]

    return patient


def build_condition(patient_id, domain, snomed_code, snomed_display, icd_code=None, icd_display=None,
                    clinical_status="active", verification_status="confirmed",
                    use_legacy=False, omit_display=False, resolved=False):
    condition_id = gen_id()
    condition = {
        "resourceType": "Condition",
        "id": condition_id,
        "meta": {
            "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition"]
        },
        "clinicalStatus": {
            "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": clinical_status}]
        },
        "verificationStatus": {
            "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": verification_status}]
        },
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-category", "code": "encounter-diagnosis", "display": "Encounter Diagnosis"}]}],
        "subject": {"reference": f"Patient/{patient_id}"},
        "onsetDateTime": gen_date(2018, 2024),
    }

    if resolved:
        condition["clinicalStatus"]["coding"][0]["code"] = "resolved"
        condition["abatementDateTime"] = gen_date(2022, 2025)

    # Build code
    coding = []
    if use_legacy:
        legacy = random.choice(LEGACY_CODES)
        entry = {"system": legacy[1], "code": legacy[0]}
        if not omit_display:
            entry["display"] = legacy[2]
        coding.append(entry)
    else:
        snomed_entry = {"system": "http://snomed.info/sct", "code": snomed_code}
        if not omit_display:
            snomed_entry["display"] = snomed_display
        coding.append(snomed_entry)

        if icd_code:
            icd_entry = {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": icd_code}
            if not omit_display:
                icd_entry["display"] = icd_display
            coding.append(icd_entry)

    condition["code"] = {"coding": coding}
    if not omit_display:
        condition["code"]["text"] = snomed_display if not use_legacy else legacy[2]

    return condition


def build_observation(patient_id, loinc_code, loinc_display, value, unit, encounter_id=None, obs_date=None):
    obs_id = gen_id()
    obs = {
        "resourceType": "Observation",
        "id": obs_id,
        "meta": {
            "profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab"]
        },
        "status": "final",
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory", "display": "Laboratory"}]}],
        "code": {"coding": [{"system": "http://loinc.org", "code": loinc_code, "display": loinc_display}], "text": loinc_display},
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": obs_date or gen_datetime(),
        "valueQuantity": {"value": round(value, 1), "unit": unit, "system": "http://unitsofmeasure.org", "code": unit},
    }
    if encounter_id:
        obs["encounter"] = {"reference": f"Encounter/{encounter_id}"}
    return obs


def build_bp_observation(patient_id, systolic, diastolic, obs_date=None):
    obs_id = gen_id()
    return {
        "resourceType": "Observation",
        "id": obs_id,
        "meta": {"profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-blood-pressure"]},
        "status": "final",
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs", "display": "Vital Signs"}]}],
        "code": {"coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel with all children optional"}], "text": "Blood pressure"},
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": obs_date or gen_datetime(),
        "component": [
            {"code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}]}, "valueQuantity": {"value": systolic, "unit": "mmHg", "system": "http://unitsofmeasure.org", "code": "mm[Hg]"}},
            {"code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure"}]}, "valueQuantity": {"value": diastolic, "unit": "mmHg", "system": "http://unitsofmeasure.org", "code": "mm[Hg]"}},
        ],
    }


def build_medication_request(patient_id, rxnorm_code, display, generic, brand, encounter_id=None, omit_dosage=False):
    med_id = gen_id()
    # Mix brand/generic naming
    use_brand = random.random() < 0.4
    med_display = f"{brand} ({generic})" if use_brand else display

    med = {
        "resourceType": "MedicationRequest",
        "id": med_id,
        "meta": {"profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest"]},
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": rxnorm_code, "display": med_display}],
            "text": med_display,
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "authoredOn": gen_date(2020, 2025),
        "requester": {"display": f"Dr. {random.choice(LAST_NAMES)}"},
    }
    if encounter_id:
        med["encounter"] = {"reference": f"Encounter/{encounter_id}"}

    if not omit_dosage:
        med["dosageInstruction"] = [{
            "text": f"Take {random.choice(['1','2'])} tablet(s) {random.choice(['once','twice','three times'])} daily",
            "timing": {"repeat": {"frequency": random.choice([1,2,3]), "period": 1, "periodUnit": "d"}},
            "route": {"coding": [{"system": "http://snomed.info/sct", "code": "26643006", "display": "Oral route"}]},
        }]

    return med


def build_encounter(patient_id, enc_date=None, enc_type="ambulatory"):
    enc_id = gen_id()
    type_map = {
        "ambulatory": ("AMB", "ambulatory"),
        "emergency": ("EMER", "emergency"),
        "inpatient": ("IMP", "inpatient encounter"),
        "wellness": ("AMB", "ambulatory"),
    }
    code, display = type_map.get(enc_type, ("AMB", "ambulatory"))
    return {
        "resourceType": "Encounter",
        "id": enc_id,
        "meta": {"profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter"]},
        "status": "finished",
        "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": code, "display": display},
        "type": [{"coding": [{"system": "http://www.ama-assn.org/go/cpt", "code": "99213", "display": "Office or other outpatient visit"}], "text": "Office Visit"}],
        "subject": {"reference": f"Patient/{patient_id}"},
        "period": {"start": enc_date or gen_datetime(), "end": (enc_date or gen_datetime())},
    }


def build_immunization(patient_id, cvx_code, cvx_display, cpt_code, cpt_display, imm_date=None):
    imm_id = gen_id()
    return {
        "resourceType": "Immunization",
        "id": imm_id,
        "meta": {"profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-immunization"]},
        "status": "completed",
        "vaccineCode": {"coding": [
            {"system": "http://hl7.org/fhir/sid/cvx", "code": cvx_code, "display": cvx_display},
            {"system": "http://www.ama-assn.org/go/cpt", "code": cpt_code, "display": cpt_display},
        ]},
        "patient": {"reference": f"Patient/{patient_id}"},
        "occurrenceDateTime": imm_date or gen_date(2020, 2025),
        "primarySource": True,
    }


def build_symptom_observation(patient_id, snomed_code, display, obs_date=None):
    obs_id = gen_id()
    return {
        "resourceType": "Observation",
        "id": obs_id,
        "status": "final",
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "exam", "display": "Exam"}]}],
        "code": {"coding": [{"system": "http://snomed.info/sct", "code": snomed_code, "display": display}], "text": display},
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": obs_date or gen_datetime(),
        "valueString": "Present",
    }



# ============================================================
# MAIN BUNDLE GENERATOR
# ============================================================
def generate_patient_bundle(patient_index, domain, complexity):
    """Generate a single patient bundle with all realism parameters applied."""
    patient_id = gen_id()

    # Determine realism flags for this patient
    has_ruled_out = random.random() < 0.15
    has_provisional = random.random() < 0.10
    has_resolved = random.random() < 0.20
    has_undiagnosed_symptoms = random.random() < 0.05
    omit_key_obs = random.random() < 0.15
    omit_dosage = random.random() < 0.10
    omit_address = random.random() < 0.08
    omit_telecom = random.random() < 0.08
    has_encounter_gaps = random.random() < 0.20

    num_conditions = get_condition_count(complexity)
    num_medications = get_medication_count(complexity)

    entries = []

    # 1. Patient resource
    patient_resource = build_patient(patient_id, omit_address=omit_address, omit_telecom=omit_telecom)
    entries.append({"fullUrl": f"urn:uuid:{patient_id}", "resource": patient_resource})

    # 2. Encounters (2-6 depending on complexity)
    enc_count = {"SIMPLE": 2, "MODERATE": 3, "COMPLEX": 4, "HIGHLY_COMPLEX": 6}[complexity]
    encounter_ids = []
    enc_dates = sorted([gen_datetime(2020, 2025) for _ in range(enc_count)])

    # Introduce gaps if flagged
    if has_encounter_gaps and len(enc_dates) > 2:
        # Remove middle encounters to create a 6+ month gap
        enc_dates = [enc_dates[0]] + enc_dates[-1:]
        enc_count = len(enc_dates)

    for ed in enc_dates:
        enc_type = random.choice(["ambulatory", "ambulatory", "ambulatory", "wellness", "emergency"])
        enc = build_encounter(patient_id, enc_date=ed, enc_type=enc_type)
        encounter_ids.append(enc["id"])
        entries.append({"fullUrl": f"urn:uuid:{enc['id']}", "resource": enc})

    # 3. Conditions
    snomed_pool = list(SNOMED_CONDITIONS[domain])
    icd_pool = list(ICD10_CONDITIONS[domain])
    random.shuffle(snomed_pool)
    random.shuffle(icd_pool)

    conditions_added = 0
    has_ruled_out_flag = False
    has_missing_data_flag = omit_key_obs or omit_dosage or omit_address or omit_telecom

    for i in range(min(num_conditions, len(snomed_pool))):
        snomed_code, snomed_display = snomed_pool[i % len(snomed_pool)]
        icd_code, icd_display = None, None

        # Coding variability: 20% dual-coded
        if random.random() < 0.20 and i < len(icd_pool):
            icd_code, icd_display = icd_pool[i % len(icd_pool)]

        # 15% parent vs child codes
        use_parent = random.random() < 0.15
        if use_parent and icd_code and "." in icd_code:
            icd_code = icd_code.split(".")[0]

        # 10% omit display
        omit_disp = random.random() < 0.10

        # 5% legacy codes
        use_legacy = random.random() < 0.05

        # Determine clinical/verification status
        clinical_status = "active"
        verification_status = "confirmed"
        resolved = False

        if has_ruled_out and i == 0:
            clinical_status = "inactive"
            verification_status = "refuted"
            has_ruled_out_flag = True
        elif has_provisional and i == 1:
            verification_status = random.choice(["provisional", "differential"])
        elif has_resolved and i == num_conditions - 1:
            resolved = True

        cond = build_condition(patient_id, domain, snomed_code, snomed_display,
                               icd_code=icd_code, icd_display=icd_display,
                               clinical_status=clinical_status, verification_status=verification_status,
                               use_legacy=use_legacy, omit_display=omit_disp, resolved=resolved)
        entries.append({"fullUrl": f"urn:uuid:{cond['id']}", "resource": cond})
        conditions_added += 1

    # 4. Observations
    obs_pool = list(LOINC_OBSERVATIONS[domain])
    if omit_key_obs:
        # Remove first (typically most important) observation
        obs_pool = obs_pool[1:]

    obs_count = min(len(obs_pool), random.randint(2, 5) if complexity == "SIMPLE" else random.randint(3, len(obs_pool)))
    selected_obs = random.sample(obs_pool, min(obs_count, len(obs_pool)))

    for loinc_code, loinc_display, unit, val_min, val_max in selected_obs:
        if loinc_code == "85354-9":
            # Blood pressure - use component observation
            bp = build_bp_observation(patient_id, random.randint(90, 200), random.randint(50, 110))
            entries.append({"fullUrl": f"urn:uuid:{bp['id']}", "resource": bp})
        else:
            value = random.uniform(val_min, val_max)
            enc_id = random.choice(encounter_ids) if encounter_ids else None
            obs = build_observation(patient_id, loinc_code, loinc_display, value, unit, encounter_id=enc_id)
            entries.append({"fullUrl": f"urn:uuid:{obs['id']}", "resource": obs})

    # 5. Medications
    med_pool = list(MEDICATIONS[domain])
    # For HIGHLY_COMPLEX in medication_interactions, use full pool
    if complexity == "HIGHLY_COMPLEX" and domain == "medication_interactions":
        num_medications = min(num_medications, len(med_pool))
    else:
        num_medications = min(num_medications, len(med_pool))

    selected_meds = random.sample(med_pool, min(num_medications, len(med_pool)))

    meds_added = 0
    for rxnorm_code, display, generic, brand in selected_meds:
        should_omit_dosage = omit_dosage and meds_added == 0
        enc_id = random.choice(encounter_ids) if encounter_ids else None
        med = build_medication_request(patient_id, rxnorm_code, display, generic, brand,
                                       encounter_id=enc_id, omit_dosage=should_omit_dosage)
        entries.append({"fullUrl": f"urn:uuid:{med['id']}", "resource": med})
        meds_added += 1

    # 6. Immunizations (for preventive_care domain, or randomly for others)
    if domain == "preventive_care" or random.random() < 0.3:
        num_vaccines = random.randint(1, 3) if domain == "preventive_care" else 1
        selected_vaccines = random.sample(VACCINES, min(num_vaccines, len(VACCINES)))
        for cvx_code, cvx_display, cpt_code, cpt_display in selected_vaccines:
            imm = build_immunization(patient_id, cvx_code, cvx_display, cpt_code, cpt_display)
            entries.append({"fullUrl": f"urn:uuid:{imm['id']}", "resource": imm})

    # 7. Undiagnosed symptoms (5% of patients)
    if has_undiagnosed_symptoms:
        symptom = random.choice(SYMPTOM_OBSERVATIONS)
        sym_obs = build_symptom_observation(patient_id, symptom[0], symptom[1])
        entries.append({"fullUrl": f"urn:uuid:{sym_obs['id']}", "resource": sym_obs})

    # Build the Bundle
    bundle = {
        "resourceType": "Bundle",
        "id": gen_id(),
        "type": "collection",
        "meta": {"lastUpdated": gen_datetime(2025, 2025)},
        "entry": entries,
    }

    manifest_row = {
        "patient_id": patient_id,
        "domain": domain,
        "complexity_level": complexity,
        "num_conditions": conditions_added,
        "num_medications": meds_added,
        "has_ruled_out": has_ruled_out_flag,
        "has_missing_data": has_missing_data_flag,
        "num_resources": len(entries),
    }

    return bundle, manifest_row


# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    print("=" * 60)
    print("Enhanced Realistic FHIR R4 Patient Bundle Generator")
    print("=" * 60)

    os.makedirs(os.path.join(OUTPUT_DIR, "diabetes"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "cardiovascular"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "medication_interactions"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "preventive_care"), exist_ok=True)

    manifest_rows = []
    all_complexities = []

    # Build shuffled complexity assignments: 250 SIMPLE, 400 MODERATE, 250 COMPLEX, 100 HIGHLY_COMPLEX
    for label, count in COMPLEXITY_DISTRIBUTION:
        all_complexities.extend([label] * count)
    random.shuffle(all_complexities)

    # Distribute complexities evenly across domains (250 each)
    domain_assignments = []
    for d in DOMAINS:
        domain_assignments.extend([(d, i) for i in range(PATIENTS_PER_DOMAIN)])

    # Assign complexity to each patient
    patient_configs = []
    for idx, (domain, _) in enumerate(domain_assignments):
        complexity = all_complexities[idx]
        patient_configs.append((domain, complexity))

    # Generate bundles
    stats = {"total": 0, "by_domain": {d: 0 for d in DOMAINS}, "by_complexity": {c: 0 for c, _ in COMPLEXITY_DISTRIBUTION}}
    domain_counters = {d: 0 for d in DOMAINS}

    for idx, (domain, complexity) in enumerate(patient_configs):
        bundle, manifest_row = generate_patient_bundle(idx, domain, complexity)

        # Save bundle
        domain_counters[domain] += 1
        filename = f"patient_{domain_counters[domain]:04d}.json"
        filepath = os.path.join(OUTPUT_DIR, domain, filename)
        with open(filepath, "w") as f:
            json.dump(bundle, f, indent=2)

        manifest_rows.append(manifest_row)
        stats["total"] += 1
        stats["by_domain"][domain] += 1
        stats["by_complexity"][complexity] += 1

        if (idx + 1) % 100 == 0:
            print(f"  Generated {idx + 1}/1000 bundles...")

    # Save manifest
    with open(MANIFEST_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["patient_id", "domain", "complexity_level", "num_conditions", "num_medications", "has_ruled_out", "has_missing_data", "num_resources"])
        writer.writeheader()
        writer.writerows(manifest_rows)

    # Validation
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nTotal bundles generated: {stats['total']}")
    print(f"\nDistribution by domain:")
    for d, c in stats["by_domain"].items():
        print(f"  {d}: {c}")
    print(f"\nDistribution by complexity:")
    for c, cnt in stats["by_complexity"].items():
        print(f"  {c}: {cnt}")

    # Quick validation
    print("\n--- Validation ---")
    valid_json = 0
    has_patient = 0
    has_condition = 0
    has_medication = 0
    errors = []

    for domain in DOMAINS:
        domain_dir = os.path.join(OUTPUT_DIR, domain)
        for fname in os.listdir(domain_dir):
            fpath = os.path.join(domain_dir, fname)
            try:
                with open(fpath) as f:
                    b = json.load(f)
                valid_json += 1
                rtypes = [e["resource"]["resourceType"] for e in b.get("entry", [])]
                if "Patient" in rtypes:
                    has_patient += 1
                if "Condition" in rtypes:
                    has_condition += 1
                if "MedicationRequest" in rtypes:
                    has_medication += 1
            except Exception as e:
                errors.append(f"{fpath}: {e}")

    print(f"  Valid JSON files: {valid_json}/1000")
    print(f"  Has Patient resource: {has_patient}/1000")
    print(f"  Has Condition resource: {has_condition}/1000")
    print(f"  Has MedicationRequest resource: {has_medication}/1000")
    if errors:
        print(f"  ERRORS: {len(errors)}")
        for e in errors[:5]:
            print(f"    {e}")
    else:
        print("  No errors found!")

    # Realism stats from manifest
    ruled_out_count = sum(1 for r in manifest_rows if r["has_ruled_out"])
    missing_data_count = sum(1 for r in manifest_rows if r["has_missing_data"])
    avg_resources = sum(r["num_resources"] for r in manifest_rows) / len(manifest_rows)
    print(f"\n--- Realism Parameters ---")
    print(f"  Patients with ruled-out conditions: {ruled_out_count} ({ruled_out_count/10:.1f}%)")
    print(f"  Patients with missing data: {missing_data_count} ({missing_data_count/10:.1f}%)")
    print(f"  Average resources per bundle: {avg_resources:.1f}")
    print(f"\nManifest saved to: {MANIFEST_PATH}")
    print(f"Bundles saved to: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()

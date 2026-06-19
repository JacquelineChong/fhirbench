"""Clinical Reasoning task - drug interactions, risk assessment, care gap detection."""

from typing import Any, Dict, List


# Common drug interaction pairs (simplified knowledge base)
KNOWN_INTERACTIONS = {
    frozenset({"warfarin", "aspirin"}): "Increased bleeding risk",
    frozenset({"lisinopril", "potassium"}): "Risk of hyperkalemia",
    frozenset({"metformin", "contrast dye"}): "Risk of lactic acidosis",
    frozenset({"simvastatin", "amiodarone"}): "Increased risk of myopathy",
    frozenset({"warfarin", "amiodarone"}): "Increased INR / bleeding risk",
    frozenset({"clopidogrel", "omeprazole"}): "Reduced antiplatelet effect",
    frozenset({"methotrexate", "nsaids"}): "Increased methotrexate toxicity",
    frozenset({"ace inhibitor", "potassium-sparing diuretic"}): "Hyperkalemia risk",
    frozenset({"ssri", "nsaids"}): "Increased bleeding risk",
    frozenset({"digoxin", "amiodarone"}): "Digoxin toxicity",
}


class ClinicalReasoningTask:
    """Clinical reasoning and inference task.

    Generates reasoning tasks including drug interaction detection,
    cardiovascular risk assessment, diabetes management gap analysis,
    and preventive care identification.
    """

    name = "clinical_reasoning"
    description = "Inference tasks (drug interactions, risk assessment)"

    REASONING_CATEGORIES = [
        "drug_interaction",
        "cardiovascular_risk",
        "diabetes_management",
        "preventive_care_gaps",
    ]

    def generate_tasks(self, fhir_bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate reasoning tasks from a FHIR bundle.

        Args:
            fhir_bundle: A FHIR Bundle dictionary.

        Returns:
            List of reasoning task dicts with 'prompt', 'category',
            'expected_findings', and 'ground_truth'.
        """
        resources = self._extract_resources(fhir_bundle)
        tasks: List[Dict[str, Any]] = []

        tasks.extend(self._generate_drug_interaction_tasks(resources))
        tasks.extend(self._generate_cardiovascular_risk_tasks(resources))
        tasks.extend(self._generate_diabetes_management_tasks(resources))
        tasks.extend(self._generate_preventive_care_tasks(resources))

        return tasks

    def evaluate(self, predicted: str, ground_truth: Dict[str, Any]) -> float:
        """Evaluate clinical correctness of reasoning response.

        Checks whether expected findings are mentioned in the prediction.

        Args:
            predicted: Model's response text.
            ground_truth: Dict with 'expected_findings' list.

        Returns:
            Score between 0 and 1 based on findings coverage.
        """
        expected = ground_truth.get("expected_findings", [])
        if not expected:
            return 1.0

        predicted_lower = predicted.lower()
        found = sum(1 for finding in expected if finding.lower() in predicted_lower)
        return found / len(expected)

    def _generate_drug_interaction_tasks(self, resources: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Detect potential drug interactions from medication list."""
        medications = resources.get("MedicationRequest", [])
        if len(medications) < 2:
            return []

        med_names = []
        for m in medications:
            name = self._get_display(m.get("medicationCodeableConcept", {}))
            if not name:
                name = m.get("medicationReference", {}).get("display", "")
            if name:
                med_names.append(name.lower())

        # Check for known interactions
        interactions_found: List[str] = []
        for pair, risk in KNOWN_INTERACTIONS.items():
            pair_list = list(pair)
            if any(pair_list[0] in m for m in med_names) and any(pair_list[1] in m for m in med_names):
                interactions_found.append(f"{' + '.join(pair_list)}: {risk}")

        med_list_str = ", ".join(med_names)
        prompt = (
            f"Review the following medication list for potential drug interactions:\n"
            f"Medications: {med_list_str}\n\n"
            f"Identify any clinically significant drug-drug interactions and explain the risks."
        )

        return [{
            "prompt": prompt,
            "category": "drug_interaction",
            "expected_findings": interactions_found if interactions_found else ["no significant interactions identified"],
            "ground_truth": {"interactions": interactions_found, "medication_count": len(med_names)},
        }]

    def _generate_cardiovascular_risk_tasks(self, resources: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Assess cardiovascular risk from patient data."""
        patients = resources.get("Patient", [])
        conditions = resources.get("Condition", [])
        observations = resources.get("Observation", [])

        if not patients:
            return []

        patient = patients[0]
        gender = patient.get("gender", "unknown")
        birth_date = patient.get("birthDate", "")

        # Gather risk factors
        risk_factors: List[str] = []
        cv_conditions = {"hypertension", "diabetes", "hyperlipidemia", "obesity",
                         "coronary", "atrial fibrillation", "heart failure"}
        for c in conditions:
            name = self._get_display(c.get("code", {})).lower()
            if any(cv in name for cv in cv_conditions):
                risk_factors.append(self._get_display(c.get("code", {})))

        # Check relevant observations (BP, cholesterol, BMI)
        obs_findings: List[str] = []
        for obs in observations:
            code = obs.get("code", {}).get("coding", [{}])[0].get("code", "")
            val = obs.get("valueQuantity", {}).get("value")
            if code == "8480-6" and val and val > 140:  # systolic BP
                obs_findings.append(f"Elevated systolic BP: {val} mmHg")
            elif code == "2093-3" and val and val > 200:  # total cholesterol
                obs_findings.append(f"Elevated total cholesterol: {val} mg/dL")
            elif code == "39156-5" and val and val > 30:  # BMI
                obs_findings.append(f"BMI: {val} (obese)")

        if not risk_factors and not obs_findings:
            return []

        expected = risk_factors + obs_findings
        prompt = (
            f"Based on the following patient data, assess cardiovascular risk:\n"
            f"Gender: {gender}, DOB: {birth_date}\n"
            f"Conditions: {', '.join(risk_factors) if risk_factors else 'none documented'}\n"
            f"Relevant findings: {', '.join(obs_findings) if obs_findings else 'none'}\n\n"
            f"Provide a cardiovascular risk assessment with identified risk factors and recommendations."
        )

        return [{
            "prompt": prompt,
            "category": "cardiovascular_risk",
            "expected_findings": expected,
            "ground_truth": {"risk_factors": risk_factors, "observations": obs_findings},
        }]

    def _generate_diabetes_management_tasks(self, resources: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Identify diabetes management gaps."""
        conditions = resources.get("Condition", [])
        observations = resources.get("Observation", [])
        medications = resources.get("MedicationRequest", [])

        # Check if patient has diabetes
        has_diabetes = False
        for c in conditions:
            name = self._get_display(c.get("code", {})).lower()
            if "diabetes" in name or "diabetic" in name:
                has_diabetes = True
                break

        if not has_diabetes:
            return []

        # Check HbA1c values
        hba1c_values: List[Dict] = []
        for obs in observations:
            codes = obs.get("code", {}).get("coding", [])
            if any(c.get("code") in ("4548-4", "59261-8", "17856-6") for c in codes):
                val = obs.get("valueQuantity", {}).get("value")
                date = obs.get("effectiveDateTime", "")
                if val:
                    hba1c_values.append({"value": val, "date": date})

        # Identify gaps
        gaps: List[str] = []
        if not hba1c_values:
            gaps.append("No HbA1c monitoring documented")
        elif hba1c_values:
            latest = sorted(hba1c_values, key=lambda x: x["date"], reverse=True)[0]
            if latest["value"] > 7.0:
                gaps.append(f"HbA1c above target: {latest['value']}%")

        # Check for diabetes medications
        diabetes_meds = {"metformin", "insulin", "glipizide", "sitagliptin", "empagliflozin", "liraglutide"}
        has_diabetes_med = any(
            any(dm in self._get_display(m.get("medicationCodeableConcept", {})).lower() for dm in diabetes_meds)
            for m in medications
        )
        if not has_diabetes_med:
            gaps.append("No diabetes-specific medication documented")

        # Check for eye/foot exam (by looking for relevant observations)
        has_eye_exam = any(
            "eye" in self._get_display(o.get("code", {})).lower() or
            "retinal" in self._get_display(o.get("code", {})).lower()
            for o in observations
        )
        if not has_eye_exam:
            gaps.append("No retinal exam documented")

        prompt = (
            f"This patient has diabetes. Review their management and identify any care gaps:\n"
            f"HbA1c history: {hba1c_values if hba1c_values else 'none documented'}\n"
            f"Has diabetes medication: {'yes' if has_diabetes_med else 'no'}\n\n"
            f"Identify gaps in diabetes management per ADA guidelines."
        )

        return [{
            "prompt": prompt,
            "category": "diabetes_management",
            "expected_findings": gaps if gaps else ["diabetes management appears adequate"],
            "ground_truth": {"gaps": gaps, "hba1c_values": hba1c_values},
        }]

    def _generate_preventive_care_tasks(self, resources: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Identify preventive care gaps."""
        patients = resources.get("Patient", [])
        observations = resources.get("Observation", [])
        procedures = resources.get("Procedure", [])
        immunizations = resources.get("Immunization", [])

        if not patients:
            return []

        patient = patients[0]
        gender = patient.get("gender", "unknown")
        birth_date = patient.get("birthDate", "")

        gaps: List[str] = []

        # Check immunizations
        vaccine_names = [self._get_display(i.get("vaccineCode", {})).lower() for i in immunizations]
        if not any("influenza" in v or "flu" in v for v in vaccine_names):
            gaps.append("No influenza vaccination documented")
        if not any("covid" in v or "sars" in v for v in vaccine_names):
            gaps.append("No COVID-19 vaccination documented")

        # Check cancer screenings for appropriate gender/age
        procedure_names = [self._get_display(p.get("code", {})).lower() for p in procedures]
        obs_names = [self._get_display(o.get("code", {})).lower() for o in observations]
        all_names = procedure_names + obs_names

        if gender == "female":
            if not any("mammogram" in n or "breast" in n for n in all_names):
                gaps.append("No breast cancer screening documented")
            if not any("pap" in n or "cervical" in n for n in all_names):
                gaps.append("No cervical cancer screening documented")

        if not any("colonoscopy" in n or "colon" in n for n in all_names):
            gaps.append("No colorectal cancer screening documented")

        if not gaps:
            return []

        prompt = (
            f"Review this patient's preventive care history and identify any gaps:\n"
            f"Gender: {gender}, DOB: {birth_date}\n"
            f"Immunizations: {', '.join(vaccine_names) if vaccine_names else 'none documented'}\n\n"
            f"Identify missing preventive care services per USPSTF guidelines."
        )

        return [{
            "prompt": prompt,
            "category": "preventive_care_gaps",
            "expected_findings": gaps,
            "ground_truth": {"gaps": gaps, "gender": gender},
        }]

    def _extract_resources(self, bundle: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Extract resources grouped by type."""
        grouped: Dict[str, List[Dict]] = {}
        if bundle.get("resourceType") == "Bundle":
            for entry in bundle.get("entry", []):
                r = entry.get("resource", {})
                rt = r.get("resourceType", "Unknown")
                grouped.setdefault(rt, []).append(r)
        else:
            rt = bundle.get("resourceType", "Unknown")
            grouped[rt] = [bundle]
        return grouped

    def _get_display(self, codeable_concept: Dict[str, Any]) -> str:
        """Extract display text from a CodeableConcept."""
        if not codeable_concept:
            return ""
        if "text" in codeable_concept:
            return codeable_concept["text"]
        codings = codeable_concept.get("coding", [])
        if codings and "display" in codings[0]:
            return codings[0]["display"]
        return ""

"""Clinical QA task - generates factual questions and ground truth answers from FHIR bundles."""

from typing import Any, Dict, List


class ClinicalQATask:
    """Factual question-answering task about patient clinical data.

    Generates QA pairs by extracting ground truth answers directly from
    FHIR resources (medications, conditions, observations, allergies).
    """

    name = "clinical_qa"
    description = "Factual questions about patient data"

    def generate_questions(self, fhir_bundle: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate QA pairs from a FHIR bundle with ground truth answers.

        Args:
            fhir_bundle: A FHIR Bundle dictionary.

        Returns:
            List of dicts with 'question', 'answer', and 'category' keys.
        """
        resources = self._extract_resources(fhir_bundle)
        qa_pairs: List[Dict[str, str]] = []

        # Medication questions
        medications = resources.get("MedicationRequest", [])
        if medications:
            active_meds = [m for m in medications if m.get("status") == "active"]
            med_names = []
            for m in active_meds:
                name = self._get_display(m.get("medicationCodeableConcept", {}))
                if not name:
                    name = m.get("medicationReference", {}).get("display", "")
                if name:
                    med_names.append(name)
            if med_names:
                qa_pairs.append({
                    "question": "What medications is this patient currently taking?",
                    "answer": "; ".join(med_names),
                    "category": "medications",
                })

        # Condition questions
        conditions = resources.get("Condition", [])
        if conditions:
            active_conditions = [c for c in conditions if self._get_status(c) == "active"]
            cond_names = [self._get_display(c.get("code", {})) for c in active_conditions]
            cond_names = [n for n in cond_names if n]
            if cond_names:
                qa_pairs.append({
                    "question": "What are the patient's active conditions?",
                    "answer": "; ".join(cond_names),
                    "category": "conditions",
                })

        # Blood pressure question
        observations = resources.get("Observation", [])
        bp_obs = [o for o in observations if self._is_bp(o)]
        if bp_obs:
            latest_bp = sorted(bp_obs, key=lambda x: x.get("effectiveDateTime", ""), reverse=True)[0]
            systolic = ""
            diastolic = ""
            for comp in latest_bp.get("component", []):
                code = comp.get("code", {}).get("coding", [{}])[0].get("code", "")
                val = comp.get("valueQuantity", {}).get("value", "")
                if code == "8480-6":  # systolic
                    systolic = str(val)
                elif code == "8462-4":  # diastolic
                    diastolic = str(val)
            if systolic and diastolic:
                qa_pairs.append({
                    "question": "What is the patient's most recent blood pressure reading?",
                    "answer": f"{systolic}/{diastolic} mmHg",
                    "category": "vitals",
                })

        # HbA1c question
        hba1c_obs = [o for o in observations if self._is_hba1c(o)]
        if hba1c_obs:
            latest = sorted(hba1c_obs, key=lambda x: x.get("effectiveDateTime", ""), reverse=True)[0]
            val = latest.get("valueQuantity", {}).get("value", "")
            date = latest.get("effectiveDateTime", "")[:10] if latest.get("effectiveDateTime") else ""
            if val:
                qa_pairs.append({
                    "question": "When was the patient's last HbA1c test and what was the result?",
                    "answer": f"{val}% on {date}",
                    "category": "labs",
                })

        # Allergy questions
        allergies = resources.get("AllergyIntolerance", [])
        if allergies:
            allergy_names = []
            for a in allergies:
                name = self._get_display(a.get("code", {}))
                if name:
                    allergy_names.append(name)
            if allergy_names:
                qa_pairs.append({
                    "question": "List all allergies documented for this patient.",
                    "answer": "; ".join(allergy_names),
                    "category": "allergies",
                })

        # Patient demographics
        patients = resources.get("Patient", [])
        if patients:
            p = patients[0]
            dob = p.get("birthDate", "")
            gender = p.get("gender", "")
            if dob and gender:
                qa_pairs.append({
                    "question": "What is the patient's date of birth and gender?",
                    "answer": f"Date of birth: {dob}, Gender: {gender}",
                    "category": "demographics",
                })

        return qa_pairs

    def evaluate(self, predicted: str, ground_truth: str) -> float:
        """Evaluate accuracy of a QA response using token-level F1.

        Args:
            predicted: Model's predicted answer.
            ground_truth: Ground truth answer.

        Returns:
            F1 score between 0 and 1.
        """
        pred_tokens = set(predicted.lower().split())
        truth_tokens = set(ground_truth.lower().split())

        if not pred_tokens or not truth_tokens:
            return 1.0 if pred_tokens == truth_tokens else 0.0

        common = pred_tokens & truth_tokens
        if not common:
            return 0.0

        precision = len(common) / len(pred_tokens)
        recall = len(common) / len(truth_tokens)
        return 2 * precision * recall / (precision + recall)

    def _extract_resources(self, bundle: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Extract resources grouped by type from a bundle."""
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

    def _get_status(self, condition: Dict[str, Any]) -> str:
        """Get clinical status code from a Condition."""
        cs = condition.get("clinicalStatus", {})
        codings = cs.get("coding", [])
        return codings[0].get("code", "unknown") if codings else "unknown"

    def _is_bp(self, obs: Dict[str, Any]) -> bool:
        """Check if observation is a blood pressure measurement."""
        codings = obs.get("code", {}).get("coding", [])
        bp_codes = {"85354-9", "55284-4"}
        return any(c.get("code") in bp_codes for c in codings)

    def _is_hba1c(self, obs: Dict[str, Any]) -> bool:
        """Check if observation is an HbA1c measurement."""
        codings = obs.get("code", {}).get("coding", [])
        hba1c_codes = {"4548-4", "59261-8", "17856-6"}
        return any(c.get("code") in hba1c_codes for c in codings)

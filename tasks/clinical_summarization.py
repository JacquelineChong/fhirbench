"""Clinical Summarization task - generate patient summaries with reference summaries."""

from typing import Any, Dict, List


class ClinicalSummarizationTask:
    """Clinical summarization and documentation generation task.

    Generates summarization prompts with reference summaries built
    from FHIR data for evaluation with ROUGE and clinical quality metrics.
    """

    name = "clinical_summarization"
    description = "Generate patient summaries, care plans, handoff notes"

    SUMMARY_TYPES = [
        "patient_summary",
        "care_plan",
        "handoff_note",
        "discharge_summary",
    ]

    def generate_tasks(self, fhir_bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate summarization tasks from a FHIR bundle.

        Args:
            fhir_bundle: A FHIR Bundle dictionary.

        Returns:
            List of task dicts with 'prompt', 'summary_type', and 'reference_summary'.
        """
        resources = self._extract_resources(fhir_bundle)
        tasks: List[Dict[str, Any]] = []

        tasks.append(self._generate_patient_summary_task(resources))
        tasks.append(self._generate_handoff_note_task(resources))

        conditions = resources.get("Condition", [])
        if any("diabetes" in self._get_display(c.get("code", {})).lower() for c in conditions):
            tasks.append(self._generate_care_plan_task(resources))

        return [t for t in tasks if t]

    def evaluate(self, predicted: str, reference: str) -> Dict[str, float]:
        """Evaluate summarization quality using ROUGE scores.

        Args:
            predicted: Model-generated summary.
            reference: Reference summary.

        Returns:
            Dict with rouge_1, rouge_2, rouge_l scores.
        """
        from evaluation.metrics import compute_rouge
        scores = compute_rouge([predicted], [reference])
        return scores

    def _generate_patient_summary_task(self, resources: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate a patient summary task with reference."""
        patients = resources.get("Patient", [])
        conditions = resources.get("Condition", [])
        medications = resources.get("MedicationRequest", [])
        observations = resources.get("Observation", [])

        if not patients:
            return {}

        patient = patients[0]
        name = self._get_patient_name(patient)
        gender = patient.get("gender", "unknown")
        dob = patient.get("birthDate", "unknown")

        # Build reference summary
        ref_parts = [f"{name} is a {gender} patient born on {dob}."]

        # Active conditions
        active_conds = [c for c in conditions if self._get_status(c) == "active"]
        if active_conds:
            cond_names = [self._get_display(c.get("code", {})) for c in active_conds]
            ref_parts.append(f"Active conditions include: {', '.join(n for n in cond_names if n)}.")

        # Current medications
        active_meds = [m for m in medications if m.get("status") == "active"]
        if active_meds:
            med_names = []
            for m in active_meds:
                n = self._get_display(m.get("medicationCodeableConcept", {}))
                if not n:
                    n = m.get("medicationReference", {}).get("display", "")
                if n:
                    med_names.append(n)
            if med_names:
                ref_parts.append(f"Current medications: {', '.join(med_names)}.")

        # Recent key observations
        recent_obs = sorted(observations, key=lambda x: x.get("effectiveDateTime", ""), reverse=True)[:5]
        if recent_obs:
            obs_strs = []
            for o in recent_obs:
                obs_name = self._get_display(o.get("code", {}))
                val = self._get_obs_value(o)
                if obs_name and val:
                    obs_strs.append(f"{obs_name}: {val}")
            if obs_strs:
                ref_parts.append(f"Recent observations: {'; '.join(obs_strs)}.")

        reference_summary = " ".join(ref_parts)

        return {
            "prompt": (
                "Generate a concise clinical summary for this patient. "
                "Include demographics, active conditions, current medications, "
                "and recent relevant observations."
            ),
            "summary_type": "patient_summary",
            "reference_summary": reference_summary,
        }

    def _generate_handoff_note_task(self, resources: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate a clinical handoff note task."""
        patients = resources.get("Patient", [])
        conditions = resources.get("Condition", [])
        medications = resources.get("MedicationRequest", [])

        if not patients:
            return {}

        patient = patients[0]
        name = self._get_patient_name(patient)

        # Build SBAR-style reference
        active_conds = [self._get_display(c.get("code", {})) for c in conditions if self._get_status(c) == "active"]
        active_meds = []
        for m in medications:
            if m.get("status") == "active":
                n = self._get_display(m.get("medicationCodeableConcept", {}))
                if not n:
                    n = m.get("medicationReference", {}).get("display", "")
                if n:
                    active_meds.append(n)

        ref_parts = [
            f"Situation: {name} presenting with {', '.join(active_conds[:3]) if active_conds else 'no acute issues'}.",
            f"Background: {len(active_conds)} active conditions, on {len(active_meds)} medications.",
            f"Assessment: Primary concerns are {', '.join(active_conds[:2]) if active_conds else 'routine care'}.",
            f"Recommendation: Continue current medication regimen ({', '.join(active_meds[:3]) if active_meds else 'none'}).",
        ]

        return {
            "prompt": (
                "Write a clinical handoff note (SBAR format) for this patient. "
                "Include Situation, Background, Assessment, and Recommendation."
            ),
            "summary_type": "handoff_note",
            "reference_summary": " ".join(ref_parts),
        }

    def _generate_care_plan_task(self, resources: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate a diabetes care plan task."""
        patients = resources.get("Patient", [])
        medications = resources.get("MedicationRequest", [])
        observations = resources.get("Observation", [])

        if not patients:
            return {}

        # Find latest HbA1c
        hba1c_val = ""
        for obs in observations:
            codes = obs.get("code", {}).get("coding", [])
            if any(c.get("code") in ("4548-4", "59261-8") for c in codes):
                v = obs.get("valueQuantity", {}).get("value")
                if v:
                    hba1c_val = str(v)

        diabetes_meds = []
        for m in medications:
            name = self._get_display(m.get("medicationCodeableConcept", {})).lower()
            if any(dm in name for dm in ("metformin", "insulin", "glipizide", "sitagliptin", "empagliflozin")):
                diabetes_meds.append(self._get_display(m.get("medicationCodeableConcept", {})))

        ref_parts = [
            "Diabetes Care Plan:",
            f"Current HbA1c: {hba1c_val}%." if hba1c_val else "HbA1c monitoring needed.",
            f"Current diabetes medications: {', '.join(diabetes_meds)}." if diabetes_meds else "Consider initiating diabetes medication.",
            "Goals: Maintain HbA1c < 7%, regular monitoring every 3 months.",
            "Follow-up: Annual retinal exam, foot exam, renal function testing.",
        ]

        return {
            "prompt": (
                "Create a diabetes management care plan for this patient. "
                "Include current control status, medication plan, monitoring schedule, "
                "and recommended screenings."
            ),
            "summary_type": "care_plan",
            "reference_summary": " ".join(ref_parts),
        }

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

    def _get_patient_name(self, patient: Dict[str, Any]) -> str:
        """Get patient name string."""
        names = patient.get("name", [])
        if not names:
            return "Unknown Patient"
        n = names[0]
        given = " ".join(n.get("given", []))
        family = n.get("family", "")
        return f"{given} {family}".strip()

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
        """Get clinical status code."""
        cs = condition.get("clinicalStatus", {})
        codings = cs.get("coding", [])
        return codings[0].get("code", "unknown") if codings else "unknown"

    def _get_obs_value(self, obs: Dict[str, Any]) -> str:
        """Extract observation value as string."""
        if "valueQuantity" in obs:
            vq = obs["valueQuantity"]
            return f"{vq.get('value', '')} {vq.get('unit', '')}"
        elif "valueCodeableConcept" in obs:
            return self._get_display(obs["valueCodeableConcept"])
        elif "valueString" in obs:
            return obs["valueString"]
        return ""

"""Clinical Summary Template serializer - SOAP note and problem list formats."""

from typing import Any, Dict, List


class ClinicalTemplateSerializer:
    """Converts FHIR bundles into clinical documentation templates.

    Supports SOAP note, problem list, medication reconciliation, and care plan formats.
    Extracts structured data from FHIR resources to populate template fields.
    """

    name = "clinical_template"
    description = "Domain-specific clinical templates (SOAP, problem list)"

    TEMPLATES = ["soap", "problem_list", "medication_reconciliation", "care_plan"]

    def __init__(self, template: str = "soap"):
        """Initialize with a specific clinical template format.

        Args:
            template: One of 'soap', 'problem_list', 'medication_reconciliation', 'care_plan'.
        """
        if template not in self.TEMPLATES:
            raise ValueError(f"Template must be one of {self.TEMPLATES}")
        self.template = template

    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        """Serialize a FHIR resource/bundle using the configured clinical template.

        Args:
            fhir_resource: A FHIR resource or Bundle dictionary.

        Returns:
            Clinical template formatted string.
        """
        handler = getattr(self, f"_template_{self.template}")
        return handler(fhir_resource)

    def serialize_bundle(self, bundle: Dict[str, Any]) -> str:
        """Serialize a FHIR Bundle using the configured template."""
        return self.serialize(bundle)

    def _extract_resources(self, resource: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Extract and group resources from a bundle or single resource.

        Returns:
            Dict mapping resourceType to list of resources.
        """
        grouped: Dict[str, List[Dict]] = {}
        if resource.get("resourceType") == "Bundle":
            for entry in resource.get("entry", []):
                r = entry.get("resource", {})
                rt = r.get("resourceType", "Unknown")
                grouped.setdefault(rt, []).append(r)
        else:
            rt = resource.get("resourceType", "Unknown")
            grouped[rt] = [resource]
        return grouped

    def _get_patient_name(self, patient: Dict[str, Any]) -> str:
        """Extract patient name from a Patient resource."""
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
        return codeable_concept.get("coding", [{}])[0].get("code", "") if codeable_concept.get("coding") else ""

    def _template_soap(self, resource: Dict[str, Any]) -> str:
        """Generate SOAP note from FHIR data.

        S (Subjective): Patient-reported symptoms from Conditions
        O (Objective): Observations, vitals, lab results
        A (Assessment): Active conditions/diagnoses
        P (Plan): Current medications and care activities
        """
        grouped = self._extract_resources(resource)
        patients = grouped.get("Patient", [])
        conditions = grouped.get("Condition", [])
        observations = grouped.get("Observation", [])
        medications = grouped.get("MedicationRequest", [])
        care_plans = grouped.get("CarePlan", [])

        patient_name = self._get_patient_name(patients[0]) if patients else "Unknown"
        dob = patients[0].get("birthDate", "unknown") if patients else "unknown"
        gender = patients[0].get("gender", "unknown") if patients else "unknown"

        lines = [
            "SOAP NOTE",
            "=" * 50,
            f"Patient: {patient_name} | DOB: {dob} | Gender: {gender}",
            "=" * 50,
            "",
            "S: SUBJECTIVE",
            "-" * 30,
        ]

        # Subjective: conditions as reported symptoms
        if conditions:
            active = [c for c in conditions if self._get_status(c) == "active"]
            if active:
                lines.append("Chief Complaint / History of Present Illness:")
                for c in active[:5]:
                    name = self._get_display(c.get("code", {}))
                    onset = c.get("onsetDateTime", "unknown")
                    lines.append(f"  - {name} (onset: {onset})")
            else:
                lines.append("  No active complaints documented.")
        else:
            lines.append("  No conditions documented.")

        lines.extend(["", "O: OBJECTIVE", "-" * 30])

        # Objective: vitals and lab observations
        if observations:
            # Separate vitals from labs
            vitals = []
            labs = []
            for obs in observations:
                cat = obs.get("category", [])
                cat_code = ""
                if cat and cat[0].get("coding"):
                    cat_code = cat[0]["coding"][0].get("code", "")
                if cat_code == "vital-signs":
                    vitals.append(obs)
                else:
                    labs.append(obs)

            if vitals:
                lines.append("Vital Signs:")
                for v in vitals[-5:]:  # Most recent 5
                    name = self._get_display(v.get("code", {}))
                    val = self._get_obs_value(v)
                    lines.append(f"  - {name}: {val}")

            if labs:
                lines.append("Laboratory Results:")
                for lab in labs[-10:]:  # Most recent 10
                    name = self._get_display(lab.get("code", {}))
                    val = self._get_obs_value(lab)
                    date = (lab.get("effectiveDateTime", "") or "")[:10]
                    lines.append(f"  - {name}: {val} ({date})")
        else:
            lines.append("  No observations documented.")

        lines.extend(["", "A: ASSESSMENT", "-" * 30])

        # Assessment: all conditions with status
        if conditions:
            lines.append("Active Problems:")
            for i, c in enumerate(conditions, 1):
                name = self._get_display(c.get("code", {}))
                status = self._get_status(c)
                lines.append(f"  {i}. {name} [{status}]")
        else:
            lines.append("  No diagnoses documented.")

        lines.extend(["", "P: PLAN", "-" * 30])

        # Plan: medications + care plans
        if medications:
            lines.append("Medications:")
            for m in medications:
                med_name = self._get_display(m.get("medicationCodeableConcept", {}))
                if not med_name:
                    med_name = m.get("medicationReference", {}).get("display", "Unknown")
                status = m.get("status", "")
                dosage = m.get("dosageInstruction", [{}])[0].get("text", "") if m.get("dosageInstruction") else ""
                line = f"  - {med_name} ({status})"
                if dosage:
                    line += f" — {dosage}"
                lines.append(line)

        if care_plans:
            lines.append("Care Plan Activities:")
            for cp in care_plans:
                for activity in cp.get("activity", []):
                    detail = activity.get("detail", {})
                    desc = detail.get("description", self._get_display(detail.get("code", {})))
                    if desc:
                        lines.append(f"  - {desc}")

        if not medications and not care_plans:
            lines.append("  No active plan documented.")

        return "\n".join(lines)

    def _template_problem_list(self, resource: Dict[str, Any]) -> str:
        """Generate problem list from FHIR data.

        Categorizes conditions by status and includes relevant context.
        """
        grouped = self._extract_resources(resource)
        patients = grouped.get("Patient", [])
        conditions = grouped.get("Condition", [])

        patient_name = self._get_patient_name(patients[0]) if patients else "Unknown"

        lines = [
            "PROBLEM LIST",
            "=" * 50,
            f"Patient: {patient_name}",
            "=" * 50,
            "",
        ]

        # Categorize conditions
        active: List[Dict] = []
        resolved: List[Dict] = []
        other: List[Dict] = []

        for c in conditions:
            status = self._get_status(c)
            if status == "active":
                active.append(c)
            elif status in ("resolved", "inactive"):
                resolved.append(c)
            else:
                other.append(c)

        lines.append("ACTIVE PROBLEMS")
        lines.append("-" * 30)
        if active:
            for i, c in enumerate(active, 1):
                name = self._get_display(c.get("code", {}))
                onset = c.get("onsetDateTime", "unknown")
                lines.append(f"  {i}. {name}")
                lines.append(f"     Onset: {onset}")
                severity = c.get("severity", {})
                if severity:
                    lines.append(f"     Severity: {self._get_display(severity)}")
        else:
            lines.append("  None documented.")

        lines.extend(["", "RESOLVED/INACTIVE PROBLEMS", "-" * 30])
        if resolved:
            for i, c in enumerate(resolved, 1):
                name = self._get_display(c.get("code", {}))
                abatement = c.get("abatementDateTime", "unknown")
                lines.append(f"  {i}. {name} (resolved: {abatement})")
        else:
            lines.append("  None documented.")

        return "\n".join(lines)

    def _template_medication_reconciliation(self, resource: Dict[str, Any]) -> str:
        """Generate medication reconciliation from FHIR data."""
        grouped = self._extract_resources(resource)
        patients = grouped.get("Patient", [])
        medications = grouped.get("MedicationRequest", [])

        patient_name = self._get_patient_name(patients[0]) if patients else "Unknown"

        lines = [
            "MEDICATION RECONCILIATION",
            "=" * 50,
            f"Patient: {patient_name}",
            "=" * 50,
            "",
        ]

        active_meds = [m for m in medications if m.get("status") == "active"]
        stopped_meds = [m for m in medications if m.get("status") in ("stopped", "completed")]

        lines.append("CURRENT MEDICATIONS")
        lines.append("-" * 30)
        if active_meds:
            for i, m in enumerate(active_meds, 1):
                name = self._get_display(m.get("medicationCodeableConcept", {}))
                if not name:
                    name = m.get("medicationReference", {}).get("display", "Unknown")
                dosage = m.get("dosageInstruction", [{}])[0].get("text", "") if m.get("dosageInstruction") else ""
                authored = m.get("authoredOn", "")
                lines.append(f"  {i}. {name}")
                if dosage:
                    lines.append(f"     Dosage: {dosage}")
                if authored:
                    lines.append(f"     Started: {authored}")
        else:
            lines.append("  None documented.")

        lines.extend(["", "DISCONTINUED MEDICATIONS", "-" * 30])
        if stopped_meds:
            for i, m in enumerate(stopped_meds, 1):
                name = self._get_display(m.get("medicationCodeableConcept", {}))
                if not name:
                    name = m.get("medicationReference", {}).get("display", "Unknown")
                lines.append(f"  {i}. {name} (stopped)")
        else:
            lines.append("  None documented.")

        return "\n".join(lines)

    def _template_care_plan(self, resource: Dict[str, Any]) -> str:
        """Generate care plan summary from FHIR data."""
        grouped = self._extract_resources(resource)
        patients = grouped.get("Patient", [])
        conditions = grouped.get("Condition", [])
        medications = grouped.get("MedicationRequest", [])
        care_plans = grouped.get("CarePlan", [])

        patient_name = self._get_patient_name(patients[0]) if patients else "Unknown"

        lines = [
            "CARE PLAN SUMMARY",
            "=" * 50,
            f"Patient: {patient_name}",
            "=" * 50,
            "",
            "GOALS",
            "-" * 30,
        ]

        if care_plans:
            for cp in care_plans:
                title = cp.get("title", self._get_display(cp.get("category", [{}])[0]) if cp.get("category") else "Care Plan")
                lines.append(f"  Plan: {title} (status: {cp.get('status', 'unknown')})")
                for activity in cp.get("activity", []):
                    detail = activity.get("detail", {})
                    desc = detail.get("description", "")
                    if desc:
                        lines.append(f"    - {desc}")
        else:
            lines.append("  No formal care plans documented.")

        lines.extend(["", "ACTIVE CONDITIONS TO MANAGE", "-" * 30])
        active_conditions = [c for c in conditions if self._get_status(c) == "active"]
        for c in active_conditions:
            lines.append(f"  - {self._get_display(c.get('code', {}))}")

        lines.extend(["", "CURRENT MEDICATIONS", "-" * 30])
        active_meds = [m for m in medications if m.get("status") == "active"]
        for m in active_meds:
            name = self._get_display(m.get("medicationCodeableConcept", {}))
            if not name:
                name = m.get("medicationReference", {}).get("display", "Unknown")
            lines.append(f"  - {name}")

        return "\n".join(lines)

    def _get_status(self, condition: Dict[str, Any]) -> str:
        """Extract clinical status code from a Condition resource."""
        cs = condition.get("clinicalStatus", {})
        codings = cs.get("coding", [])
        if codings:
            return codings[0].get("code", "unknown")
        return "unknown"

    def _get_obs_value(self, obs: Dict[str, Any]) -> str:
        """Extract observation value as string."""
        if "valueQuantity" in obs:
            vq = obs["valueQuantity"]
            return f"{vq.get('value', '')} {vq.get('unit', '')}"
        elif "valueCodeableConcept" in obs:
            return self._get_display(obs["valueCodeableConcept"])
        elif "valueString" in obs:
            return obs["valueString"]
        elif "component" in obs:
            parts = []
            for comp in obs["component"]:
                cn = self._get_display(comp.get("code", {}))
                cv = comp.get("valueQuantity", {})
                parts.append(f"{cn}: {cv.get('value', '')} {cv.get('unit', '')}")
            return "; ".join(parts)
        return "N/A"

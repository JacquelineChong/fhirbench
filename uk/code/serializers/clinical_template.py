"""Clinical Summary Template serialiser - NHS SOAP note and problem list formats."""

from typing import Any, Dict, List


class ClinicalTemplateSerializer:
    """Converts FHIR bundles into NHS clinical documentation templates.

    Supports SOAP note, problem list, medication reconciliation, and care plan formats.
    Adapted for UK Core FHIR profiles with NHS Number, GP Practice,
    dm+d medication coding, and SNOMED CT UK display terms.
    """

    name = "clinical_template"
    description = "NHS clinical templates (SOAP, problem list) with UK Core support"

    TEMPLATES = ["soap", "problem_list", "medication_reconciliation", "care_plan"]

    def __init__(self, template: str = "soap"):
        """Initialise with a specific clinical template format."""
        if template not in self.TEMPLATES:
            raise ValueError(f"Template must be one of {self.TEMPLATES}")
        self.template = template

    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        """Serialise a FHIR resource/bundle using the configured clinical template."""
        handler = getattr(self, f"_template_{self.template}")
        return handler(fhir_resource)

    def serialize_bundle(self, bundle: Dict[str, Any]) -> str:
        """Serialise a FHIR Bundle using the configured template."""
        return self.serialize(bundle)

    def _extract_resources(self, resource: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Extract and group resources from a bundle or single resource."""
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

    def _get_patient_header(self, patient: Dict[str, Any]) -> List[str]:
        """Extract patient header with NHS Number and GP Practice."""
        name = self._get_patient_name(patient)
        dob = self._format_date(patient.get("birthDate", "unknown"))
        gender = patient.get("gender", "unknown")
        nhs_number = self._extract_nhs_number(patient)
        gp_practice = self._extract_gp_practice(patient)

        lines = [
            f"Patient: {name} | DOB: {dob} | Gender: {gender}",
        ]
        if nhs_number:
            lines.append(f"NHS Number: {nhs_number}")
        if gp_practice:
            lines.append(f"GP Practice: {gp_practice}")
        return lines

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

    def _get_snomed_display(self, codeable_concept: Dict[str, Any]) -> str:
        """Extract SNOMED CT UK display term with code."""
        display = self._get_display(codeable_concept)
        codings = codeable_concept.get("coding", [])
        for coding in codings:
            system = coding.get("system", "")
            if "snomed" in system.lower():
                code = coding.get("code", "")
                if code:
                    return f"{display} (SNOMED CT UK: {code})"
        return display

    def _get_dmd_display(self, codeable_concept: Dict[str, Any]) -> str:
        """Extract dm+d medication display with code."""
        display = self._get_display(codeable_concept)
        codings = codeable_concept.get("coding", [])
        for coding in codings:
            system = coding.get("system", "")
            if "dmd" in system.lower() or "dm+d" in system.lower():
                code = coding.get("code", "")
                if code:
                    return f"{display} (dm+d: {code})"
        return display

    def _extract_nhs_number(self, patient: Dict[str, Any]) -> str:
        """Extract NHS Number from Patient identifiers."""
        identifiers = patient.get("identifier", [])
        for ident in identifiers:
            system = ident.get("system", "")
            if "nhs-number" in system.lower() or "nhs.uk" in system.lower():
                value = ident.get("value", "")
                if len(value) == 10 and value.isdigit():
                    return f"{value[:3]} {value[3:6]} {value[6:]}"
                return value
        return ""

    def _extract_gp_practice(self, patient: Dict[str, Any]) -> str:
        """Extract GP Practice from Patient resource."""
        gps = patient.get("generalPractitioner", [])
        if gps:
            return gps[0].get("display", gps[0].get("reference", ""))
        extensions = patient.get("extension", [])
        for ext in extensions:
            url = ext.get("url", "")
            if "preferredbranchsurgery" in url.lower() or "gppractice" in url.lower():
                ref = ext.get("valueReference", {})
                return ref.get("display", ref.get("reference", ""))
        return ""

    def _format_date(self, date_str: str) -> str:
        """Format a date string to DD/MM/YYYY (UK format)."""
        if not date_str or date_str == "unknown":
            return date_str
        date_part = date_str[:10]
        parts = date_part.split("-")
        if len(parts) == 3:
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
        return date_str

    def _get_status(self, condition: Dict[str, Any]) -> str:
        """Extract clinical status code from a Condition resource."""
        cs = condition.get("clinicalStatus", {})
        codings = cs.get("coding", [])
        if codings:
            return codings[0].get("code", "unknown")
        return "unknown"

    def _get_obs_value(self, obs: Dict[str, Any]) -> str:
        """Extract observation value as string (metric units)."""
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

    def _template_soap(self, resource: Dict[str, Any]) -> str:
        """Generate NHS SOAP note from FHIR data.

        S (Subjective): Patient-reported symptoms from Conditions
        O (Objective): Observations, vitals, lab results (metric units)
        A (Assessment): Active conditions/diagnoses (SNOMED CT UK)
        P (Plan): Current medications (dm+d) and care activities
        """
        grouped = self._extract_resources(resource)
        patients = grouped.get("Patient", [])
        conditions = grouped.get("Condition", [])
        observations = grouped.get("Observation", [])
        medications = grouped.get("MedicationRequest", [])
        care_plans = grouped.get("CarePlan", [])

        lines = [
            "NHS SOAP NOTE",
            "=" * 50,
        ]

        if patients:
            lines.extend(self._get_patient_header(patients[0]))
        else:
            lines.append("Patient: Unknown")

        lines.extend([
            "=" * 50,
            "",
            "S: SUBJECTIVE",
            "-" * 30,
        ])

        if conditions:
            active = [c for c in conditions if self._get_status(c) == "active"]
            if active:
                lines.append("Chief Complaint / Hx (History of Presenting Complaint):")
                for c in active[:5]:
                    name = self._get_snomed_display(c.get("code", {}))
                    onset = self._format_date(c.get("onsetDateTime", "unknown"))
                    lines.append(f"  - {name} (onset: {onset})")
            else:
                lines.append("  No active complaints documented.")
        else:
            lines.append("  No conditions documented.")

        lines.extend(["", "O: OBJECTIVE (O/E)", "-" * 30])

        if observations:
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
                lines.append("Vital Signs (metric):")
                for v in vitals[-5:]:
                    name = self._get_display(v.get("code", {}))
                    val = self._get_obs_value(v)
                    lines.append(f"  - {name}: {val}")

            if labs:
                lines.append("Laboratory Results:")
                for lab in labs[-10:]:
                    name = self._get_display(lab.get("code", {}))
                    val = self._get_obs_value(lab)
                    date = self._format_date((lab.get("effectiveDateTime", "") or "")[:10])
                    lines.append(f"  - {name}: {val} ({date})")
        else:
            lines.append("  No observations documented.")

        lines.extend(["", "A: ASSESSMENT", "-" * 30])

        if conditions:
            lines.append("Active Problems (SNOMED CT UK):")
            for i, c in enumerate(conditions, 1):
                name = self._get_snomed_display(c.get("code", {}))
                status = self._get_status(c)
                lines.append(f"  {i}. {name} [{status}]")
        else:
            lines.append("  No diagnoses documented.")

        lines.extend(["", "P: PLAN", "-" * 30])

        if medications:
            lines.append("Current Prescriptions (dm+d):")
            for m in medications:
                med_name = self._get_dmd_display(m.get("medicationCodeableConcept", {}))
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
        """Generate problem list from FHIR data with SNOMED CT UK codes."""
        grouped = self._extract_resources(resource)
        patients = grouped.get("Patient", [])
        conditions = grouped.get("Condition", [])

        lines = [
            "PROBLEM LIST",
            "=" * 50,
        ]
        if patients:
            lines.extend(self._get_patient_header(patients[0]))
        lines.extend(["=" * 50, ""])

        active: List[Dict] = []
        resolved: List[Dict] = []

        for c in conditions:
            status = self._get_status(c)
            if status == "active":
                active.append(c)
            else:
                resolved.append(c)

        lines.append("ACTIVE PROBLEMS")
        lines.append("-" * 30)
        if active:
            for i, c in enumerate(active, 1):
                name = self._get_snomed_display(c.get("code", {}))
                onset = self._format_date(c.get("onsetDateTime", "unknown"))
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
                name = self._get_snomed_display(c.get("code", {}))
                abatement = self._format_date(c.get("abatementDateTime", "unknown"))
                lines.append(f"  {i}. {name} (resolved: {abatement})")
        else:
            lines.append("  None documented.")

        return "\n".join(lines)

    def _template_medication_reconciliation(self, resource: Dict[str, Any]) -> str:
        """Generate medication reconciliation with dm+d codes."""
        grouped = self._extract_resources(resource)
        patients = grouped.get("Patient", [])
        medications = grouped.get("MedicationRequest", [])

        lines = [
            "MEDICATION RECONCILIATION",
            "=" * 50,
        ]
        if patients:
            lines.extend(self._get_patient_header(patients[0]))
        lines.extend(["=" * 50, ""])

        active_meds = [m for m in medications if m.get("status") == "active"]
        stopped_meds = [m for m in medications if m.get("status") in ("stopped", "completed")]

        lines.append("CURRENT PRESCRIPTIONS (dm+d)")
        lines.append("-" * 30)
        if active_meds:
            for i, m in enumerate(active_meds, 1):
                name = self._get_dmd_display(m.get("medicationCodeableConcept", {}))
                if not name:
                    name = m.get("medicationReference", {}).get("display", "Unknown")
                dosage = m.get("dosageInstruction", [{}])[0].get("text", "") if m.get("dosageInstruction") else ""
                authored = self._format_date(m.get("authoredOn", ""))
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
                name = self._get_dmd_display(m.get("medicationCodeableConcept", {}))
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

        lines = [
            "CARE PLAN SUMMARY",
            "=" * 50,
        ]
        if patients:
            lines.extend(self._get_patient_header(patients[0]))
        lines.extend(["=" * 50, "", "GOALS", "-" * 30])

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
            lines.append(f"  - {self._get_snomed_display(c.get('code', {}))}")

        lines.extend(["", "CURRENT PRESCRIPTIONS (dm+d)", "-" * 30])
        active_meds = [m for m in medications if m.get("status") == "active"]
        for m in active_meds:
            name = self._get_dmd_display(m.get("medicationCodeableConcept", {}))
            if not name:
                name = m.get("medicationReference", {}).get("display", "Unknown")
            lines.append(f"  - {name}")

        return "\n".join(lines)

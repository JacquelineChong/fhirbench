"""Natural Language Narrative serialiser - converts FHIR resources to NHS clinical letter format."""

from typing import Any, Dict, List


class NarrativeSerializer:
    """Converts FHIR resources into NHS-style clinical letter narrative.

    Uses dm+d medication naming, NHS Number identification, and British
    clinical abbreviations (Hx, O/E, Imp).
    """

    name = "narrative"
    description = "NHS clinical letter narrative serialisation"

    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        resource_type = fhir_resource.get("resourceType", "Unknown")
        handler = getattr(self, f"_serialise_{resource_type.lower()}", self._serialise_generic)
        return handler(fhir_resource)

    def serialize_bundle(self, bundle: Dict[str, Any]) -> str:
        entries = bundle.get("entry", [])
        if not entries:
            return "This bundle contains no entries."

        resources_by_type: Dict[str, List[Dict]] = {}
        for entry in entries:
            resource = entry.get("resource", {})
            rt = resource.get("resourceType", "Unknown")
            resources_by_type.setdefault(rt, []).append(resource)

        sections: List[str] = []
        sections.append("Dear Colleague,\n")

        if "Patient" in resources_by_type:
            for r in resources_by_type.pop("Patient"):
                sections.append(self._serialise_patient(r))

        if "Condition" in resources_by_type:
            condition_parts = ["Hx (Clinical History):"]
            for r in resources_by_type.pop("Condition"):
                condition_parts.append(self._serialise_condition(r))
            sections.append("\n".join(condition_parts))

        if "MedicationRequest" in resources_by_type:
            med_parts = ["Current Prescriptions (dm+d):"]
            for r in resources_by_type.pop("MedicationRequest"):
                med_parts.append(self._serialise_medicationrequest(r))
            sections.append("\n".join(med_parts))

        if "Observation" in resources_by_type:
            obs_parts = ["O/E (On Examination) & Investigations:"]
            for r in resources_by_type.pop("Observation"):
                obs_parts.append(self._serialise_observation(r))
            sections.append("\n".join(obs_parts))

        for rt, resources in resources_by_type.items():
            for r in resources:
                sections.append(self.serialize(r))

        sections.append("\nImp (Impression): See above diagnoses and management plan.")
        sections.append("\nYours sincerely,\n[Clinician Name]\n[NHS Trust / GP Practice]")

        return "\n\n".join(sections)

    def _serialise_generic(self, resource: Dict[str, Any]) -> str:
        resource_type = resource.get("resourceType", "Unknown")
        return f"This is a {resource_type} resource (ID: {resource.get('id', 'unknown')})."

    def _serialise_patient(self, resource: Dict[str, Any]) -> str:
        parts: List[str] = []
        names = resource.get("name", [])
        name_str = "Unknown"
        if names:
            n = names[0]
            given = " ".join(n.get("given", []))
            family = n.get("family", "")
            prefix = " ".join(n.get("prefix", []))
            name_str = f"{prefix} {given} {family}".strip()

        nhs_number = self._extract_nhs_number(resource)
        birth_date = self._format_date(resource.get("birthDate", "unknown"))

        parts.append(f"Re: {name_str}")
        if nhs_number:
            parts.append(f"NHS Number: {nhs_number}")
        parts.append(f"Date of Birth: {birth_date}")
        parts.append(f"Gender: {resource.get('gender', 'unknown').capitalize()}")

        gp_practice = self._extract_gp_practice(resource)
        if gp_practice:
            parts.append(f"GP Practice: {gp_practice}")

        ethnic_category = self._extract_ethnic_category(resource)
        if ethnic_category:
            parts.append(f"Ethnic Category: {ethnic_category}")

        return "\n".join(parts)

    def _serialise_condition(self, resource: Dict[str, Any]) -> str:
        code = resource.get("code", {})
        condition_name = self._get_display(code)
        snomed_code = self._get_snomed_code(code)
        onset = self._format_date(resource.get("onsetDateTime", "unknown date"))
        line = f"  - {condition_name}"
        if snomed_code:
            line += f" (SNOMED CT UK: {snomed_code})"
        line += f", onset: {onset}"
        return line

    def _serialise_medicationrequest(self, resource: Dict[str, Any]) -> str:
        med_code = resource.get("medicationCodeableConcept", {})
        med_name = self._get_display(med_code)
        dmd_code = self._get_dmd_code(med_code)
        line = f"  - {med_name}"
        if dmd_code:
            line += f" (dm+d: {dmd_code})"
        status = resource.get("status", "")
        if status:
            line += f" [{status}]"
        dosage_list = resource.get("dosageInstruction", [])
        if dosage_list:
            text = dosage_list[0].get("text", "")
            if text:
                line += f" -- {text}"
        return line

    def _serialise_observation(self, resource: Dict[str, Any]) -> str:
        code = resource.get("code", {})
        obs_name = self._get_display(code)
        line = f"  - {obs_name}:"
        if "valueQuantity" in resource:
            vq = resource["valueQuantity"]
            line += f" {vq.get('value', '')} {vq.get('unit', '')}"
        elif "component" in resource:
            components = []
            for comp in resource["component"]:
                comp_name = self._get_display(comp.get("code", {}))
                comp_vq = comp.get("valueQuantity", {})
                components.append(f"{comp_name}: {comp_vq.get('value', '')} {comp_vq.get('unit', '')}")
            line += f" {'; '.join(components)}"
        effective = resource.get("effectiveDateTime", "")
        if effective:
            line += f" ({self._format_date(effective)})"
        return line

    def _extract_nhs_number(self, patient: Dict[str, Any]) -> str:
        for ident in patient.get("identifier", []):
            system = ident.get("system", "")
            if "nhs-number" in system.lower() or "nhs.uk" in system.lower():
                value = ident.get("value", "")
                if len(value) == 10 and value.isdigit():
                    return f"{value[:3]} {value[3:6]} {value[6:]}"
                return value
        return ""

    def _extract_gp_practice(self, patient: Dict[str, Any]) -> str:
        gps = patient.get("generalPractitioner", [])
        if gps:
            return gps[0].get("display", gps[0].get("reference", ""))
        return ""

    def _extract_ethnic_category(self, patient: Dict[str, Any]) -> str:
        for ext in patient.get("extension", []):
            if "ethniccategory" in ext.get("url", "").lower():
                value_cc = ext.get("valueCodeableConcept", {})
                return self._get_display(value_cc)
        return ""

    def _format_date(self, date_str: str) -> str:
        if not date_str or date_str in ("unknown", "unknown date"):
            return date_str
        parts = date_str[:10].split("-")
        if len(parts) == 3:
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
        return date_str

    def _get_display(self, cc: Dict[str, Any]) -> str:
        if not cc:
            return ""
        if "text" in cc:
            return cc["text"]
        codings = cc.get("coding", [])
        if codings:
            return codings[0].get("display", codings[0].get("code", ""))
        return ""

    def _get_snomed_code(self, cc: Dict[str, Any]) -> str:
        for coding in cc.get("coding", []):
            if "snomed" in coding.get("system", "").lower():
                return coding.get("code", "")
        return ""

    def _get_dmd_code(self, cc: Dict[str, Any]) -> str:
        for coding in cc.get("coding", []):
            if "dmd" in coding.get("system", "").lower():
                return coding.get("code", "")
        return ""
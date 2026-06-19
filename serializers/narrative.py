"""Natural Language Narrative serializer - converts FHIR resources to prose."""

from typing import Any, Dict, List


class NarrativeSerializer:
    """Converts FHIR resources into natural language prose for LLM consumption.

    Implements resource-specific handlers for Patient, Condition,
    MedicationRequest, and Observation resources.
    """

    name = "narrative"
    description = "Full prose conversion of FHIR resources"

    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        """Serialize a FHIR resource as natural language narrative.

        Args:
            fhir_resource: A FHIR resource dictionary.

        Returns:
            Natural language prose description of the resource.
        """
        resource_type = fhir_resource.get("resourceType", "Unknown")
        handler = getattr(self, f"_serialize_{resource_type.lower()}", self._serialize_generic)
        return handler(fhir_resource)

    def serialize_bundle(self, bundle: Dict[str, Any]) -> str:
        """Serialize a FHIR Bundle as a cohesive narrative.

        Args:
            bundle: A FHIR Bundle dictionary.

        Returns:
            Combined narrative for all resources in the bundle.
        """
        entries = bundle.get("entry", [])
        if not entries:
            return "This bundle contains no entries."

        # Group resources by type for coherent narrative
        resources_by_type: Dict[str, List[Dict]] = {}
        for entry in entries:
            resource = entry.get("resource", {})
            rt = resource.get("resourceType", "Unknown")
            resources_by_type.setdefault(rt, []).append(resource)

        sections: List[str] = []

        # Patient first
        if "Patient" in resources_by_type:
            for r in resources_by_type.pop("Patient"):
                sections.append(self._serialize_patient(r))

        # Then conditions, medications, observations
        for rt in ["Condition", "MedicationRequest", "Observation"]:
            if rt in resources_by_type:
                for r in resources_by_type.pop(rt):
                    sections.append(self.serialize(r))

        # Remaining resource types
        for rt, resources in resources_by_type.items():
            for r in resources:
                sections.append(self.serialize(r))

        return "\n\n".join(sections)

    def _serialize_generic(self, resource: Dict[str, Any]) -> str:
        """Generic serialization for unsupported resource types."""
        resource_type = resource.get("resourceType", "Unknown")
        resource_id = resource.get("id", "unknown")
        return f"This is a {resource_type} resource (ID: {resource_id})."

    def _serialize_patient(self, resource: Dict[str, Any]) -> str:
        """Serialize a Patient resource as narrative prose.

        Extracts demographics, contact info, and identifiers.
        """
        parts: List[str] = []

        # Name
        names = resource.get("name", [])
        name_str = "Unknown"
        if names:
            n = names[0]
            given = " ".join(n.get("given", []))
            family = n.get("family", "")
            name_str = f"{given} {family}".strip()

        # Demographics
        gender = resource.get("gender", "unknown")
        birth_date = resource.get("birthDate", "unknown")

        parts.append(f"Patient {name_str} is a {gender} born on {birth_date}.")

        # Address
        addresses = resource.get("address", [])
        if addresses:
            addr = addresses[0]
            city = addr.get("city", "")
            state = addr.get("state", "")
            if city or state:
                parts.append(f"The patient resides in {city}, {state}.")

        # Marital status
        marital = resource.get("maritalStatus", {})
        if marital.get("text") or marital.get("coding"):
            status = marital.get("text") or marital.get("coding", [{}])[0].get("display", "")
            if status:
                parts.append(f"Marital status: {status}.")

        # Communication/language
        communications = resource.get("communication", [])
        if communications:
            langs = []
            for comm in communications:
                lang = comm.get("language", {})
                lang_text = lang.get("text") or (lang.get("coding", [{}])[0].get("display", "") if lang.get("coding") else "")
                if lang_text:
                    langs.append(lang_text)
            if langs:
                parts.append(f"Languages: {', '.join(langs)}.")

        return " ".join(parts)

    def _serialize_condition(self, resource: Dict[str, Any]) -> str:
        """Serialize a Condition resource as narrative prose.

        Extracts diagnosis, onset, status, and severity.
        """
        code = resource.get("code", {})
        condition_name = self._get_display(code)

        clinical_status = resource.get("clinicalStatus", {})
        status = self._get_coding_text(clinical_status)

        onset = resource.get("onsetDateTime", resource.get("onsetPeriod", {}).get("start", "unknown date"))

        parts = [f"The patient has {condition_name}"]
        if status:
            parts[0] += f" (status: {status})"
        parts[0] += f", first recorded on {onset}."

        # Severity
        severity = resource.get("severity", {})
        if severity:
            sev_text = self._get_display(severity)
            if sev_text:
                parts.append(f"Severity: {sev_text}.")

        # Verification
        verification = resource.get("verificationStatus", {})
        if verification:
            ver_text = self._get_coding_text(verification)
            if ver_text:
                parts.append(f"Verification: {ver_text}.")

        return " ".join(parts)

    def _serialize_medicationrequest(self, resource: Dict[str, Any]) -> str:
        """Serialize a MedicationRequest resource as narrative prose.

        Extracts medication name, dosage, frequency, and reason.
        """
        # Medication name
        med_code = resource.get("medicationCodeableConcept", {})
        med_name = self._get_display(med_code)
        if not med_name:
            med_ref = resource.get("medicationReference", {})
            med_name = med_ref.get("display", "unknown medication")

        parts = [f"Prescribed medication: {med_name}."]

        # Status
        status = resource.get("status", "")
        if status:
            parts.append(f"Status: {status}.")

        # Dosage
        dosage_list = resource.get("dosageInstruction", [])
        if dosage_list:
            dosage = dosage_list[0]
            text = dosage.get("text", "")
            if text:
                parts.append(f"Dosage: {text}.")
            else:
                dose_qty = dosage.get("doseAndRate", [{}])[0].get("doseQuantity", {}) if dosage.get("doseAndRate") else {}
                if dose_qty:
                    val = dose_qty.get("value", "")
                    unit = dose_qty.get("unit", "")
                    parts.append(f"Dose: {val} {unit}.")

                timing = dosage.get("timing", {}).get("repeat", {})
                if timing:
                    freq = timing.get("frequency", "")
                    period = timing.get("period", "")
                    period_unit = timing.get("periodUnit", "")
                    if freq and period:
                        parts.append(f"Frequency: {freq} time(s) per {period} {period_unit}.")

        # Reason
        reasons = resource.get("reasonReference", [])
        if reasons:
            reason_displays = [r.get("display", "") for r in reasons if r.get("display")]
            if reason_displays:
                parts.append(f"Reason: {', '.join(reason_displays)}.")

        authored = resource.get("authoredOn", "")
        if authored:
            parts.append(f"Prescribed on: {authored}.")

        return " ".join(parts)

    def _serialize_observation(self, resource: Dict[str, Any]) -> str:
        """Serialize an Observation resource as narrative prose.

        Extracts measurement type, value, date, and interpretation.
        """
        code = resource.get("code", {})
        obs_name = self._get_display(code)

        parts = [f"Observation: {obs_name}."]

        # Value
        if "valueQuantity" in resource:
            vq = resource["valueQuantity"]
            val = vq.get("value", "")
            unit = vq.get("unit", vq.get("code", ""))
            parts.append(f"Value: {val} {unit}.")
        elif "valueCodeableConcept" in resource:
            val = self._get_display(resource["valueCodeableConcept"])
            parts.append(f"Value: {val}.")
        elif "valueString" in resource:
            parts.append(f"Value: {resource['valueString']}.")
        elif "component" in resource:
            # Multi-component observation (e.g., blood pressure)
            components = []
            for comp in resource["component"]:
                comp_name = self._get_display(comp.get("code", {}))
                comp_vq = comp.get("valueQuantity", {})
                comp_val = comp_vq.get("value", "")
                comp_unit = comp_vq.get("unit", "")
                components.append(f"{comp_name}: {comp_val} {comp_unit}")
            parts.append(f"Components: {'; '.join(components)}.")

        # Date
        effective = resource.get("effectiveDateTime", resource.get("issued", ""))
        if effective:
            parts.append(f"Date: {effective}.")

        # Interpretation
        interpretation = resource.get("interpretation", [])
        if interpretation:
            interp_text = self._get_display(interpretation[0])
            if interp_text:
                parts.append(f"Interpretation: {interp_text}.")

        return " ".join(parts)

    def _get_display(self, codeable_concept: Dict[str, Any]) -> str:
        """Extract display text from a CodeableConcept."""
        if not codeable_concept:
            return ""
        if "text" in codeable_concept:
            return codeable_concept["text"]
        codings = codeable_concept.get("coding", [])
        if codings and "display" in codings[0]:
            return codings[0]["display"]
        if codings and "code" in codings[0]:
            return codings[0]["code"]
        return ""

    def _get_coding_text(self, codeable_concept: Dict[str, Any]) -> str:
        """Extract text from a CodeableConcept, preferring coding display."""
        codings = codeable_concept.get("coding", [])
        if codings:
            return codings[0].get("code", codings[0].get("display", ""))
        return codeable_concept.get("text", "")

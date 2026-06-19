"""Structured Markdown serializer - hierarchical markdown with headers and tables."""

from typing import Any, Dict, List


class StructuredMarkdownSerializer:
    """Converts FHIR resources into structured Markdown with tables and sections.

    Groups resources by type, uses ## headers, creates tables for
    observations/labs, and bullet lists for conditions/medications.
    """

    name = "structured_markdown"
    description = "Hierarchical markdown with headers and tables"

    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        """Serialize a single FHIR resource as structured Markdown.

        Args:
            fhir_resource: A FHIR resource dictionary.

        Returns:
            Markdown-formatted string.
        """
        resource_type = fhir_resource.get("resourceType", "Unknown")
        handler = getattr(self, f"_render_{resource_type.lower()}", self._render_generic)
        return handler(fhir_resource)

    def serialize_bundle(self, bundle: Dict[str, Any]) -> str:
        """Serialize a FHIR Bundle as structured Markdown, grouped by resource type.

        Args:
            bundle: A FHIR Bundle dictionary.

        Returns:
            Markdown document with sections per resource type.
        """
        entries = bundle.get("entry", [])
        if not entries:
            return "# Patient Record\n\nNo data available."

        # Group by resource type
        by_type: Dict[str, List[Dict]] = {}
        for entry in entries:
            resource = entry.get("resource", {})
            rt = resource.get("resourceType", "Unknown")
            by_type.setdefault(rt, []).append(resource)

        sections: List[str] = ["# Patient Clinical Record\n"]

        # Patient demographics first
        if "Patient" in by_type:
            sections.append(self._render_patient_section(by_type.pop("Patient")))

        # Conditions as bullet list
        if "Condition" in by_type:
            sections.append(self._render_conditions_section(by_type.pop("Condition")))

        # Medications as bullet list
        if "MedicationRequest" in by_type:
            sections.append(self._render_medications_section(by_type.pop("MedicationRequest")))

        # Observations as table
        if "Observation" in by_type:
            sections.append(self._render_observations_section(by_type.pop("Observation")))

        # Remaining resource types
        for rt, resources in by_type.items():
            sections.append(f"## {rt}\n")
            for r in resources:
                sections.append(self._render_generic(r))

        return "\n".join(sections)

    def _render_patient_section(self, patients: List[Dict]) -> str:
        """Render Patient resources as demographics section."""
        if not patients:
            return ""
        p = patients[0]
        names = p.get("name", [])
        name_str = "Unknown"
        if names:
            n = names[0]
            given = " ".join(n.get("given", []))
            family = n.get("family", "")
            name_str = f"{given} {family}".strip()

        lines = [
            "## Demographics\n",
            f"- **Name**: {name_str}",
            f"- **Gender**: {p.get('gender', 'unknown')}",
            f"- **Date of Birth**: {p.get('birthDate', 'unknown')}",
        ]

        addresses = p.get("address", [])
        if addresses:
            addr = addresses[0]
            parts = [addr.get("city", ""), addr.get("state", ""), addr.get("country", "")]
            lines.append(f"- **Address**: {', '.join(x for x in parts if x)}")

        marital = p.get("maritalStatus", {})
        if marital:
            text = marital.get("text") or (marital.get("coding", [{}])[0].get("display", "") if marital.get("coding") else "")
            if text:
                lines.append(f"- **Marital Status**: {text}")

        return "\n".join(lines) + "\n"

    def _render_conditions_section(self, conditions: List[Dict]) -> str:
        """Render Condition resources as a bullet list."""
        lines = ["## Active Conditions\n"]
        for c in conditions:
            code = c.get("code", {})
            name = self._get_display(code)
            status = c.get("clinicalStatus", {})
            status_text = self._get_coding_code(status)
            onset = c.get("onsetDateTime", "unknown")
            lines.append(f"- **{name}** — Status: {status_text}, Onset: {onset}")
        return "\n".join(lines) + "\n"

    def _render_medications_section(self, medications: List[Dict]) -> str:
        """Render MedicationRequest resources as a bullet list."""
        lines = ["## Medications\n"]
        for m in medications:
            med_code = m.get("medicationCodeableConcept", {})
            name = self._get_display(med_code)
            if not name:
                name = m.get("medicationReference", {}).get("display", "Unknown")
            status = m.get("status", "unknown")
            dosage_list = m.get("dosageInstruction", [])
            dosage_text = dosage_list[0].get("text", "") if dosage_list else ""
            line = f"- **{name}** — Status: {status}"
            if dosage_text:
                line += f", Dosage: {dosage_text}"
            lines.append(line)
        return "\n".join(lines) + "\n"

    def _render_observations_section(self, observations: List[Dict]) -> str:
        """Render Observation resources as a markdown table."""
        lines = [
            "## Observations & Labs\n",
            "| Date | Test | Value | Unit |",
            "|------|------|-------|------|",
        ]
        for obs in observations:
            code = obs.get("code", {})
            name = self._get_display(code)
            date = obs.get("effectiveDateTime", obs.get("issued", ""))[:10] if obs.get("effectiveDateTime") or obs.get("issued") else ""

            if "valueQuantity" in obs:
                vq = obs["valueQuantity"]
                val = str(vq.get("value", ""))
                unit = vq.get("unit", vq.get("code", ""))
            elif "valueCodeableConcept" in obs:
                val = self._get_display(obs["valueCodeableConcept"])
                unit = ""
            elif "component" in obs:
                # Multi-component (e.g., BP)
                parts = []
                for comp in obs["component"]:
                    cv = comp.get("valueQuantity", {})
                    parts.append(f"{cv.get('value', '')}")
                val = "/".join(parts)
                unit = obs["component"][0].get("valueQuantity", {}).get("unit", "") if obs["component"] else ""
            else:
                val = obs.get("valueString", "")
                unit = ""

            lines.append(f"| {date} | {name} | {val} | {unit} |")

        return "\n".join(lines) + "\n"

    def _render_generic(self, resource: Dict[str, Any]) -> str:
        """Render any FHIR resource as generic markdown."""
        rt = resource.get("resourceType", "Unknown")
        lines = [f"### {rt} ({resource.get('id', 'unknown')})\n"]
        for key, value in resource.items():
            if key in ("resourceType", "id", "meta"):
                continue
            if isinstance(value, (dict, list)):
                continue
            lines.append(f"- **{key}**: {value}")
        return "\n".join(lines) + "\n"

    def _render_patient(self, resource: Dict[str, Any]) -> str:
        """Render single Patient resource."""
        return self._render_patient_section([resource])

    def _render_condition(self, resource: Dict[str, Any]) -> str:
        """Render single Condition resource."""
        return self._render_conditions_section([resource])

    def _render_medicationrequest(self, resource: Dict[str, Any]) -> str:
        """Render single MedicationRequest resource."""
        return self._render_medications_section([resource])

    def _render_observation(self, resource: Dict[str, Any]) -> str:
        """Render single Observation resource."""
        return self._render_observations_section([resource])

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

    def _get_coding_code(self, codeable_concept: Dict[str, Any]) -> str:
        """Extract code from a CodeableConcept."""
        codings = codeable_concept.get("coding", [])
        if codings:
            return codings[0].get("code", "")
        return ""

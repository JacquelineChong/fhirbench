"""Flattened Key-Value serialiser - dot-notation flattening with UK Core terminology resolution."""

from typing import Any, Dict, List


class FlattenedKVSerializer:
    """Flattens FHIR JSON into dot-notation key-value pairs with UK Core support.

    Supports array index notation and resolves FHIR coding elements to
    human-readable display text. Handles UK Core extensions including
    NHS Number, GP Practice, and NHS Ethnic Category.
    """

    name = "flattened_kv"
    description = "Dot-notation flattening of UK Core FHIR resources"

    SYSTEM_NAMES: Dict[str, str] = {
        "http://snomed.info/sct": "SNOMED-CT-UK",
        "http://loinc.org": "LOINC",
        "https://dmd.nhs.uk": "dm+d",
        "http://hl7.org/fhir/sid/icd-10": "ICD-10-UK",
        "http://hl7.org/fhir/sid/icd-10-cm": "ICD-10-UK",
        "https://fhir.hl7.org.uk/CodeSystem/UKCore-EthnicCategoryEngland": "NHS-Ethnic-Category",
        "https://fhir.hl7.org.uk/CodeSystem/UKCore-EthnicCategoryWales": "NHS-Ethnic-Category",
        "https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland": "NHS-Number-Verification",
    }

    UK_CORE_EXTENSIONS: Dict[str, str] = {
        "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus": "patient.nhsNumberVerificationStatus",
        "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-EthnicCategory": "patient.ethnicCategory",
        "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-ReligiousAffiliation": "patient.religiousAffiliation",
        "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NominatedPharmacy": "patient.nominatedPharmacy",
        "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-PreferredBranchSurgery": "patient.gpPractice",
        "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-ResidentialStatus": "patient.residentialStatus",
        "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeathNotificationStatus": "patient.deathNotificationStatus",
        "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-ContactPreference": "patient.contactPreference",
        "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-BirthSex": "patient.birthSex",
    }

    def __init__(self, resolve_codes: bool = True):
        self.resolve_codes = resolve_codes

    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        pairs: List[tuple] = []
        self._flatten(fhir_resource, "", pairs)
        uk_pairs = self._extract_uk_core_fields(fhir_resource)
        all_pairs = uk_pairs + pairs
        return "\n".join(f"{k} = {v}" for k, v in all_pairs)

    def serialize_bundle(self, bundle: Dict[str, Any]) -> str:
        lines: List[str] = []
        for i, entry in enumerate(bundle.get("entry", [])):
            resource = entry.get("resource", {})
            rt = resource.get("resourceType", "Unknown")
            lines.append(f"--- entry[{i}] ({rt}) ---")
            lines.append(self.serialize(resource))
            lines.append("")
        return "\n".join(lines)

    def _extract_uk_core_fields(self, resource: Dict[str, Any]) -> List[tuple]:
        pairs: List[tuple] = []
        if resource.get("resourceType") != "Patient":
            return pairs
        identifiers = resource.get("identifier", [])
        for ident in identifiers:
            system = ident.get("system", "")
            if "nhs-number" in system.lower() or "nhs.uk" in system.lower():
                value = ident.get("value", "")
                if len(value) == 10 and value.isdigit():
                    formatted = f"{value[:3]} {value[3:6]} {value[6:]}"
                    pairs.append(("patient.nhsNumber", formatted))
                else:
                    pairs.append(("patient.nhsNumber", value))
        gps = resource.get("generalPractitioner", [])
        if gps:
            gp_display = gps[0].get("display", gps[0].get("reference", ""))
            if gp_display:
                pairs.append(("patient.gpPractice", gp_display))
        extensions = resource.get("extension", [])
        for ext in extensions:
            url = ext.get("url", "")
            friendly_key = self.UK_CORE_EXTENSIONS.get(url, "")
            if not friendly_key:
                continue
            if friendly_key == "patient.gpPractice" and any(k == "patient.gpPractice" for k, _ in pairs):
                continue
            value = self._extract_extension_value(ext)
            if value:
                pairs.append((friendly_key, value))
        return pairs

    def _extract_extension_value(self, ext: Dict[str, Any]) -> str:
        if "valueCodeableConcept" in ext:
            cc = ext["valueCodeableConcept"]
            display = cc.get("text", "")
            if not display:
                codings = cc.get("coding", [])
                if codings:
                    display = codings[0].get("display", codings[0].get("code", ""))
            return display
        if "valueReference" in ext:
            return ext["valueReference"].get("display", ext["valueReference"].get("reference", ""))
        if "valueCode" in ext:
            return ext["valueCode"]
        if "valueString" in ext:
            return ext["valueString"]
        if "valueCoding" in ext:
            return ext["valueCoding"].get("display", ext["valueCoding"].get("code", ""))
        return ""

    def _flatten(self, obj: Any, prefix: str, pairs: List[tuple]) -> None:
        if isinstance(obj, dict):
            if self.resolve_codes and self._is_coding(obj):
                pairs.append((prefix, self._resolve_coding(obj)))
                return
            for key, value in obj.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                self._flatten(value, new_prefix, pairs)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._flatten(item, f"{prefix}[{i}]", pairs)
        else:
            pairs.append((prefix, repr(obj)))

    def _is_coding(self, obj: Dict[str, Any]) -> bool:
        return "code" in obj and ("system" in obj or "display" in obj)

    def _resolve_coding(self, coding: Dict[str, Any]) -> str:
        display = coding.get("display", "")
        code = coding.get("code", "")
        system = coding.get("system", "")
        system_name = self.SYSTEM_NAMES.get(system, system)
        if display and code:
            return f"{display} ({system_name}:{code})"
        elif display:
            return display
        elif code:
            return f"{system_name}:{code}"
        return str(coding)
"""Flattened Key-Value serializer - dot-notation flattening with terminology resolution."""

from typing import Any, Dict, List, Optional


class FlattenedKVSerializer:
    """Flattens FHIR JSON into dot-notation key-value pairs with optional terminology resolution.

    Supports array index notation (e.g., name[0].given[0]) and resolves
    FHIR coding elements into human-readable display text when available.
    """

    name = "flattened_kv"
    description = "Dot-notation flattening of FHIR resources"

    # FHIR terminology system display names
    SYSTEM_NAMES: Dict[str, str] = {
        "http://snomed.info/sct": "SNOMED-CT",
        "http://loinc.org": "LOINC",
        "http://www.nlm.nih.gov/research/umls/rxnorm": "RxNorm",
        "http://hl7.org/fhir/sid/icd-10-cm": "ICD-10-CM",
        "http://hl7.org/fhir/sid/cvx": "CVX",
    }

    def __init__(self, resolve_codes: bool = True):
        """Initialize with code resolution preference.

        Args:
            resolve_codes: If True, resolve coding elements to 'display (system:code)' format.
        """
        self.resolve_codes = resolve_codes

    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        """Serialize a FHIR resource as flattened key-value pairs.

        Args:
            fhir_resource: A FHIR resource dictionary.

        Returns:
            Newline-separated key = value pairs.
        """
        pairs: List[tuple] = []
        self._flatten(fhir_resource, "", pairs)
        return "\n".join(f"{k} = {v}" for k, v in pairs)

    def serialize_bundle(self, bundle: Dict[str, Any]) -> str:
        """Serialize a FHIR Bundle as flattened key-value pairs.

        Args:
            bundle: A FHIR Bundle dictionary.

        Returns:
            Newline-separated key = value pairs for all entries.
        """
        lines: List[str] = []
        for i, entry in enumerate(bundle.get("entry", [])):
            resource = entry.get("resource", {})
            rt = resource.get("resourceType", "Unknown")
            lines.append(f"--- entry[{i}] ({rt}) ---")
            lines.append(self.serialize(resource))
            lines.append("")
        return "\n".join(lines)

    def _flatten(self, obj: Any, prefix: str, pairs: List[tuple]) -> None:
        """Recursively flatten a nested object into dot-notation pairs.

        Args:
            obj: Current object being flattened.
            prefix: Accumulated key prefix.
            pairs: Output list of (key, value) tuples.
        """
        if isinstance(obj, dict):
            # Check if this is a FHIR Coding element that can be resolved
            if self.resolve_codes and self._is_coding(obj):
                resolved = self._resolve_coding(obj)
                pairs.append((prefix, resolved))
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
        """Check if a dict looks like a FHIR Coding element."""
        return "code" in obj and ("system" in obj or "display" in obj)

    def _resolve_coding(self, coding: Dict[str, Any]) -> str:
        """Resolve a FHIR Coding element to human-readable format.

        Args:
            coding: A FHIR Coding dict with system, code, and optionally display.

        Returns:
            Formatted string like 'Display Text (SNOMED-CT:12345)'.
        """
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

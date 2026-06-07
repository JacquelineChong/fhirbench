"""Flattened Key-Value serializer - dot-notation flattening (patient.name.given = 'John')."""

from typing import Any, Dict, List


class FlattenedKVSerializer:
    """Flattens FHIR JSON into dot-notation key-value pairs."""
    
    name = "flattened_kv"
    description = "Dot-notation flattening of FHIR resources"
    
    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        """Serialize a FHIR resource as flattened key-value pairs."""
        pairs = []
        self._flatten(fhir_resource, "", pairs)
        return "\n".join(f"{k} = {v}" for k, v in pairs)
    
    def _flatten(self, obj: Any, prefix: str, pairs: List) -> None:
        """Recursively flatten a nested object."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                self._flatten(value, new_prefix, pairs)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._flatten(item, f"{prefix}[{i}]", pairs)
        else:
            pairs.append((prefix, repr(obj)))

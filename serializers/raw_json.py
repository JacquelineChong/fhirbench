"""Raw JSON serializer - passes FHIR JSON with optional resource filtering and pretty-printing."""

import json
from typing import Any, Dict, List, Optional


class RawJsonSerializer:
    """Passes FHIR JSON resources with optional filtering as the baseline serialization strategy."""

    name = "raw_json"
    description = "Unmodified FHIR JSON (baseline)"

    def __init__(self, resource_types: Optional[List[str]] = None, pretty: bool = True):
        """Initialize with optional resource type filter and formatting preference.

        Args:
            resource_types: If provided, only include these resource types from bundles.
            pretty: Whether to pretty-print JSON output.
        """
        self.resource_types = resource_types
        self.pretty = pretty

    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        """Serialize a single FHIR resource as JSON string.

        Args:
            fhir_resource: A FHIR resource dictionary.

        Returns:
            JSON string representation.
        """
        indent = 2 if self.pretty else None
        return json.dumps(fhir_resource, indent=indent)

    def serialize_bundle(self, bundle: Dict[str, Any]) -> str:
        """Serialize a FHIR Bundle, optionally filtering by resource type.

        Args:
            bundle: A FHIR Bundle dictionary.

        Returns:
            JSON string of the (filtered) bundle.
        """
        if self.resource_types and bundle.get("resourceType") == "Bundle":
            filtered_entries = [
                entry for entry in bundle.get("entry", [])
                if entry.get("resource", {}).get("resourceType") in self.resource_types
            ]
            bundle = {**bundle, "entry": filtered_entries}

        indent = 2 if self.pretty else None
        return json.dumps(bundle, indent=indent)

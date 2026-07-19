"""Raw JSON serialiser - passes FHIR JSON with optional resource filtering.

No structural changes needed for UK Core as this passes through FHIR JSON as-is.
UK Core extensions and UK-specific coding systems are preserved in their
original form within the JSON output.
"""

import json
from typing import Any, Dict, List, Optional


class RawJsonSerializer:
    """Passes FHIR JSON resources with optional filtering as the baseline serialisation strategy.

    Preserves all UK Core extensions, NHS Number identifiers, dm+d codes,
    and SNOMED CT UK terms in their native JSON representation.
    """

    name = "raw_json"
    description = "Unmodified FHIR JSON (baseline) - UK Core pass-through"

    def __init__(self, resource_types: Optional[List[str]] = None, pretty: bool = True):
        """Initialise with optional resource type filter."""
        self.resource_types = resource_types
        self.pretty = pretty

    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        """Serialise a single FHIR resource as JSON string."""
        indent = 2 if self.pretty else None
        return json.dumps(fhir_resource, indent=indent)

    def serialize_bundle(self, bundle: Dict[str, Any]) -> str:
        """Serialise a FHIR Bundle, optionally filtering by resource type."""
        if self.resource_types and bundle.get("resourceType") == "Bundle":
            filtered_entries = [
                entry for entry in bundle.get("entry", [])
                if entry.get("resource", {}).get("resourceType") in self.resource_types
            ]
            bundle = {**bundle, "entry": filtered_entries}

        indent = 2 if self.pretty else None
        return json.dumps(bundle, indent=indent)
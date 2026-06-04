"""Raw JSON serializer - passes FHIR JSON unmodified as baseline."""

import json
from typing import Any, Dict


class RawJsonSerializer:
    """Passes FHIR JSON resources unmodified as the baseline serialization strategy."""
    
    name = "raw_json"
    description = "Unmodified FHIR JSON (baseline)"
    
    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        """Serialize a FHIR resource as formatted JSON string."""
        return json.dumps(fhir_resource, indent=2)
    
    def serialize_bundle(self, bundle: Dict[str, Any]) -> str:
        """Serialize a FHIR Bundle as formatted JSON string."""
        return json.dumps(bundle, indent=2)

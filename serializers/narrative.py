"""Natural Language Narrative serializer - full prose conversion."""

from typing import Any, Dict


class NarrativeSerializer:
    """Converts FHIR resources into natural language prose."""
    
    name = "narrative"
    description = "Full prose conversion of FHIR resources"
    
    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        """Serialize a FHIR resource as natural language narrative."""
        resource_type = fhir_resource.get("resourceType", "Unknown")
        handler = getattr(self, f"_serialize_{resource_type.lower()}", self._serialize_generic)
        return handler(fhir_resource)
    
    def _serialize_generic(self, resource: Dict[str, Any]) -> str:
        """Generic serialization for unsupported resource types."""
        resource_type = resource.get("resourceType", "Unknown")
        return f"This is a {resource_type} resource with ID {resource.get('id', 'unknown')}."
    
    def _serialize_patient(self, resource: Dict[str, Any]) -> str:
        """Serialize a Patient resource as narrative."""
        # TODO: Implement full patient narrative generation
        return "Patient narrative - to be implemented"

"""Clinical Summary Template serializer - SOAP note format, problem list format."""

from typing import Any, Dict


class ClinicalTemplateSerializer:
    """Converts FHIR resources into clinical documentation templates."""
    
    name = "clinical_template"
    description = "Domain-specific clinical templates (SOAP, problem list)"
    
    TEMPLATES = ["soap", "problem_list", "medication_reconciliation", "care_plan"]
    
    def __init__(self, template: str = "soap"):
        """Initialize with a specific clinical template format."""
        if template not in self.TEMPLATES:
            raise ValueError(f"Template must be one of {self.TEMPLATES}")
        self.template = template
    
    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        """Serialize a FHIR resource using the configured clinical template."""
        handler = getattr(self, f"_template_{self.template}")
        return handler(fhir_resource)
    
    def _template_soap(self, resource: Dict[str, Any]) -> str:
        """SOAP note template."""
        return "SOAP Note\n=========\nS: [Subjective]\nO: [Objective]\nA: [Assessment]\nP: [Plan]"
    
    def _template_problem_list(self, resource: Dict[str, Any]) -> str:
        """Problem list template."""
        return "Problem List\n============\n1. [Active problems extracted from FHIR data]"

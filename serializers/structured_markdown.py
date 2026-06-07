"""Structured Markdown serializer - hierarchical markdown with headers and tables."""

from typing import Any, Dict


class StructuredMarkdownSerializer:
    """Converts FHIR resources into structured Markdown format."""
    
    name = "structured_markdown"
    description = "Hierarchical markdown with headers and tables"
    
    def serialize(self, fhir_resource: Dict[str, Any]) -> str:
        """Serialize a FHIR resource as structured Markdown."""
        resource_type = fhir_resource.get("resourceType", "Unknown")
        lines = [f"# {resource_type}", ""]
        
        for key, value in fhir_resource.items():
            if key == "resourceType":
                continue
            if isinstance(value, dict):
                lines.append(f"## {key}")
                for k, v in value.items():
                    lines.append(f"- **{k}**: {v}")
            elif isinstance(value, list):
                lines.append(f"## {key}")
                for item in value:
                    lines.append(f"- {item}")
            else:
                lines.append(f"- **{key}**: {value}")
            lines.append("")
        
        return "\n".join(lines)

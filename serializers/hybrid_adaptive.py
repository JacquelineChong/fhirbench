"""Hybrid Adaptive serializer - task-aware format selection."""

from typing import Any, Dict


class HybridAdaptiveSerializer:
    """Task-aware serialization that selects optimal format based on query type."""
    
    name = "hybrid_adaptive"
    description = "Task-aware adaptive format selection"
    
    TASK_FORMAT_MAP = {
        "clinical_qa": "structured_markdown",
        "clinical_reasoning": "narrative",
        "clinical_summarization": "clinical_template",
    }
    
    def __init__(self):
        """Initialize with all available serializers."""
        from .raw_json import RawJsonSerializer
        from .structured_markdown import StructuredMarkdownSerializer
        from .narrative import NarrativeSerializer
        from .clinical_template import ClinicalTemplateSerializer
        
        self.serializers = {
            "raw_json": RawJsonSerializer(),
            "structured_markdown": StructuredMarkdownSerializer(),
            "narrative": NarrativeSerializer(),
            "clinical_template": ClinicalTemplateSerializer(),
        }
    
    def serialize(self, fhir_resource: Dict[str, Any], task_type: str = "clinical_qa") -> str:
        """Serialize using task-appropriate strategy."""
        format_name = self.TASK_FORMAT_MAP.get(task_type, "structured_markdown")
        serializer = self.serializers[format_name]
        return serializer.serialize(fhir_resource)

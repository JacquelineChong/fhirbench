"""Hybrid Adaptive serializer - task-aware format selection."""

from typing import Any, Dict


class HybridAdaptiveSerializer:
    """Task-aware serialization that selects optimal format based on query type.

    Routes to the most appropriate serializer for each clinical task:
    - clinical_qa → structured_markdown (tables ease factoid extraction)
    - clinical_reasoning → clinical_template/SOAP (structured clinical reasoning)
    - clinical_summarization → narrative (prose suitable for summarization)
    """

    name = "hybrid_adaptive"
    description = "Task-aware adaptive format selection"

    TASK_FORMAT_MAP: Dict[str, str] = {
        "clinical_qa": "structured_markdown",
        "clinical_reasoning": "clinical_template",
        "clinical_summarization": "narrative",
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
            "clinical_template": ClinicalTemplateSerializer(template="soap"),
        }

    def serialize(self, fhir_resource: Dict[str, Any], task_type: str = "clinical_qa") -> str:
        """Serialize using task-appropriate strategy.

        Args:
            fhir_resource: A FHIR resource or Bundle dictionary.
            task_type: The clinical task type to optimize for.

        Returns:
            Serialized string using the best format for the task.
        """
        format_name = self.TASK_FORMAT_MAP.get(task_type, "structured_markdown")
        serializer = self.serializers[format_name]
        return serializer.serialize(fhir_resource)

    def serialize_bundle(self, bundle: Dict[str, Any], task_type: str = "clinical_qa") -> str:
        """Serialize a bundle using task-appropriate strategy.

        Args:
            bundle: A FHIR Bundle dictionary.
            task_type: The clinical task type to optimize for.

        Returns:
            Serialized bundle string.
        """
        format_name = self.TASK_FORMAT_MAP.get(task_type, "structured_markdown")
        serializer = self.serializers[format_name]
        return serializer.serialize_bundle(bundle)

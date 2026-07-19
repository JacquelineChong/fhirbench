"""Hybrid Adaptive serialiser - task-aware format selection for UK Core FHIR."""

from typing import Any, Dict


class HybridAdaptiveSerializer:
    """Task-aware serialisation that selects optimal format based on query type.

    Routes to the most appropriate serialiser for each clinical task,
    adapted for UK Core FHIR profiles and NHS clinical workflows:
    - clinical_qa -> structured_markdown (tables with NHS Number, SNOMED CT UK codes)
    - clinical_reasoning -> clinical_template/SOAP (NHS SOAP format with dm+d)
    - clinical_summarisation -> narrative (NHS clinical letter format)
    """

    name = "hybrid_adaptive"
    description = "Task-aware adaptive format selection (UK Core)"

    TASK_FORMAT_MAP: Dict[str, str] = {
        "clinical_qa": "structured_markdown",
        "clinical_reasoning": "clinical_template",
        "clinical_summarisation": "narrative",
        "clinical_summarization": "narrative",
    }

    def __init__(self):
        """Initialise with all available UK Core serialisers."""
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
        """Serialise using task-appropriate strategy."""
        format_name = self.TASK_FORMAT_MAP.get(task_type, "structured_markdown")
        serialiser = self.serializers[format_name]
        return serialiser.serialize(fhir_resource)

    def serialize_bundle(self, bundle: Dict[str, Any], task_type: str = "clinical_qa") -> str:
        """Serialise a bundle using task-appropriate strategy."""
        format_name = self.TASK_FORMAT_MAP.get(task_type, "structured_markdown")
        serialiser = self.serializers[format_name]
        return serialiser.serialize_bundle(bundle)
"""FHIRBench Serializers - Clinical data serialization strategies for LLMs."""

from .raw_json import RawJsonSerializer
from .flattened_kv import FlattenedKVSerializer
from .narrative import NarrativeSerializer
from .structured_markdown import StructuredMarkdownSerializer
from .clinical_template import ClinicalTemplateSerializer
from .hybrid_adaptive import HybridAdaptiveSerializer

__all__ = [
    "RawJsonSerializer",
    "FlattenedKVSerializer",
    "NarrativeSerializer",
    "StructuredMarkdownSerializer",
    "ClinicalTemplateSerializer",
    "HybridAdaptiveSerializer",
]

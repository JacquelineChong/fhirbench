# 3. Methodology

## 3.1 Research Design Overview

This study employs a controlled experimental design to evaluate the effect of clinical data serialization strategy on large language model performance across standardized healthcare tasks. The primary independent variable is the **serialization format** applied to FHIR R4 patient bundles; the dependent variables are task-specific accuracy metrics, multi-dimensional quality scores, and token efficiency measures.

### Experimental Structure

The evaluation follows a fully crossed factorial design:

| Factor | Levels | Values |
|--------|--------|--------|
| **Serialization strategy** (independent variable) | 6 | Raw JSON, Flattened KV, Natural Language Narrative, Structured Markdown, Clinical Summary Template, Hybrid Adaptive |
| **Foundation model** | 5 | Claude 3.5 Sonnet, GPT-5.4, Llama 3 70B, DeepSeek V3.2, Qwen3 32B |
| **Clinical task type** | 3 | Clinical QA, Clinical Reasoning, Clinical Summarization |
| **Total experimental conditions** | 90 | 6 × 5 × 3 |
| **Samples per condition** | 50 | Drawn from 1,000-patient benchmark dataset |
| **Total evaluations** | 4,500 | API calls to Amazon Bedrock |

### Fixed Parameters

To isolate the effect of serialization format, the following variables are held constant across all conditions:

- **Terminology resolution:** Codes + display text (SNOMED/LOINC/RxNorm codes with human-readable display strings)
- **Granularity:** Patient bundle (complete record with all referenced resources)
- **Context window strategy:** Relevance-filtered (task-relevant resources selected)
- **Inference parameters:** Temperature = 0.0, max tokens = 2,048, top_p = 1.0
- **API interface:** Amazon Bedrock Converse API (unified across all 5 models)

### Methodology Subsections

The full methodology is organized as follows:

- **§3.2 Data Generation** — Synthetic FHIR R4 patient construction (50 validation + 1,000 benchmark), realism parameters, geographic scope, and limitations
- **§3.3 Serialization Taxonomy** — Definition and formalization of 6 serialization strategies along 4 analytic dimensions, with illustrative examples and literature justification
- **§3.4 Benchmark Design** — Model selection (5 Bedrock models), task definitions (3 types), and experimental protocol
- **§3.5 Evaluation Framework** — Three-layer scoring (automated metrics → LLM-as-judge → human evaluation), the 4-dimension clinical rubric, token efficiency analysis, and Pareto frontier computation

### Reproducibility

All experimental materials — data generation scripts, serialization implementations, task generators, evaluation harnesses, model configuration, and analysis code — are publicly available at https://github.com/JacquelineChong/fhirbench under MIT license. The use of Synthea-generated synthetic data and Amazon Bedrock's versioned model IDs ensures that any researcher with an AWS account can fully replicate our results.

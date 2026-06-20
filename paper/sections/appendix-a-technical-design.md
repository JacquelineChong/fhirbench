# Appendix A: Technical Design Specification

This appendix contains the full technical design specification for the FHIRBench benchmark framework, including module architecture, interface definitions, configuration schemas, and AWS integration specifications.

The design follows a modular pipeline architecture as illustrated in Figure 1 (§3.1). Implementation details referenced in §3.4.4 (Infrastructure) are fully specified below.

---

# FHIRBench — Technical Design

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FHIRBench Pipeline                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────┐          │
│  │  Synthea  │───▶│ FHIR Bundles │───▶│  Serializers  │          │
│  │  (Data)   │    │   (R4 JSON)  │    │  (6 formats)  │          │
│  └──────────┘    └──────────────┘    └───────┬───────┘          │
│                                               │                   │
│                                               ▼                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │              Task Prompt Generator                      │      │
│  │  ┌─────────┐  ┌──────────────┐  ┌────────────────┐   │      │
│  │  │ Clin QA │  │ Clin Reason  │  │ Clin Summarize │   │      │
│  │  └─────────┘  └──────────────┘  └────────────────┘   │      │
│  └───────────────────────────┬───────────────────────────┘      │
│                               │                                   │
│                               ▼                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │                Model Inference Layer                    │      │
│  │  ┌─────────┐  ┌─────────┐  ┌──────┐  ┌───────────┐  │      │
│  │  │ Claude  │  │ Llama 3 │  │GPT-5.4│  │Qwen3 1.5 │  │      │
│  │  │(Bedrock)│  │(Bedrock)│  │(OAI) │  │ (Google)  │  │      │
│  │  └─────────┘  └─────────┘  └──────┘  └───────────┘  │      │
│  └───────────────────────────┬───────────────────────────┘      │
│                               │                                   │
│                               ▼                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │                  Evaluation Engine                      │      │
│  │  Accuracy │ Clinical Correctness │ ROUGE │ Token Cost  │      │
│  └───────────────────────────┬───────────────────────────┘      │
│                               │                                   │
│                               ▼                                   │
│  ┌───────────────────────────────────────────────────────┐      │
│  │               Analysis & Reporting                     │      │
│  │  Stats │ Pareto Frontier │ Decision Framework │ Plots  │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Module Design

### 1. Data Layer (`data/`)
- **synthea_config.py** — Synthea parameter generation for target conditions
- **fhir_loader.py** — Load and validate FHIR R4 bundles
- **patient_selector.py** — Select patients matching experimental criteria

### 2. Serializers (`serializers/`)
Each serializer implements the `BaseSerializer` interface:

```python
class BaseSerializer(ABC):
    @abstractmethod
    def serialize(self, bundle: dict, options: SerializerOptions) -> str:
        """Convert FHIR bundle to string representation."""
        pass
    
    @abstractmethod
    def token_count(self, serialized: str, model: str) -> int:
        """Count tokens for cost estimation."""
        pass
```

**Terminology Resolution Modes** (configurable per serializer):
- `RAW_CODES` — SNOMED/LOINC codes only
- `CODES_WITH_DISPLAY` — Codes + display text
- `FULLY_EXPANDED` — Full concept definitions
- `HIERARCHICAL` — Parent concept context included

### 3. Tasks (`tasks/`)
Each task generates prompts and defines scoring:

```python
class BaseTask(ABC):
    @abstractmethod
    def generate_prompts(self, serialized_data: str, patient: dict) -> list[dict]:
        """Generate evaluation prompts."""
        pass
    
    @abstractmethod
    def score(self, response: str, ground_truth: dict) -> TaskScore:
        """Score model response against ground truth."""
        pass
```

### 4. Model Layer (`models/`)
- **bedrock_client.py** — Unified Bedrock client (Claude, Llama 3)
- **openai_client.py** — GPT-5.4 client
- **google_client.py** — DeepSeek V3.2 client
- **model_registry.py** — Model configuration and routing

### 5. Evaluation (`evaluation/`)
- **experiment_runner.py** — Orchestrates full experimental matrix
- **metrics.py** — Accuracy, ROUGE-L, clinical correctness
- **token_tracker.py** — Token usage and cost estimation
- **results_store.py** — Experiment results persistence (JSON + CSV)

### 6. Analysis (`analysis/`)
- **statistical_tests.py** — ANOVA, post-hoc tests, effect sizes
- **pareto.py** — Pareto frontier computation (accuracy vs. token cost)
- **decision_framework.py** — Generate practitioner decision matrix
- **visualizations.py** — Matplotlib/Plotly charts for paper figures

## Configuration

```yaml
# config/experiment.yaml
experiment:
  name: "fhirbench-v1"
  seed: 42
  
data:
  n_patients: 1000
  conditions: [diabetes, cardiovascular, medication_interactions, preventive_care]
  
serializers:
  - raw_json
  - flattened_kv
  - narrative
  - structured_markdown
  - clinical_template
  - hybrid_adaptive

terminology_resolution: codes_with_display

models:
  - id: claude-3.5-sonnet
    provider: bedrock
    model_id: anthropic.claude-3-5-sonnet-20241022-v2:0
  - id: llama-3-70b
    provider: bedrock
    model_id: meta.llama3-70b-instruct-v1:0
  - id: gpt-5.4
    provider: bedrock
    model_id: openai.gpt-5-4
  - id: deepseek-v3.2
    provider: google
    model_id: deepseek-v3.2

tasks:
  - clinical_qa
  - clinical_reasoning
  - clinical_summarization

evaluation:
  n_samples_per_condition: 50
  temperature: 0.0
  max_tokens: 2048
```

## AWS Integration

### Bedrock Configuration
- Region: `us-east-1` (or user-configured)
- IAM role with `bedrock:InvokeModel` permission
- Model access pre-approved for Claude 3.5 Sonnet + Llama 3 70B

### Cost Estimation
- ~72 experiment conditions (6 serializers × 4 models × 3 tasks)
- ~200 samples per condition = 14,400 API calls
- Estimated Bedrock cost: ~$50-150 depending on token usage

## Testing Strategy
- Unit tests for each serializer (deterministic output)
- Integration tests for model clients (mock API)
- End-to-end test with 5 patients × 1 serializer × 1 model × 1 task


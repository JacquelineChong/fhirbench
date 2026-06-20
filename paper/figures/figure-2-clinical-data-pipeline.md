# Figure 2: Clinical AI Data Pipeline — Positioning Serialization

This figure illustrates the four stages of the clinical AI data pipeline, clarifying where serialization (FHIRBench's focus) operates relative to retrieval/chunking.

## Pipeline Diagram

```
Patient EHR (10,000+ FHIR resources)
        │
        ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 1: RETRIEVAL / CHUNKING                       │
│                                                       │
│  "Which resources are relevant to this query?"        │
│                                                       │
│  Methods: FHIRPath queries, Agent-based retrieval,    │
│  SQL/GraphQL, Semantic similarity                     │
│                                                       │
│  Output: 5–50 relevant FHIR resources                 │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 2: SERIALIZATION  ◄━━━━ FHIRBench            │
│                                                       │
│  "How should selected data be FORMATTED for the LLM?" │
│                                                       │
│  Strategies: Raw JSON, Flattened KV, Narrative,       │
│  Structured Markdown, Clinical Template, Hybrid       │
│                                                       │
│  Also: Terminology resolution, token optimization     │
│                                                       │
│  Output: Formatted text (500–8,000 tokens)            │
│  Token variance: up to 16× between strategies         │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 3: PROMPT CONSTRUCTION                        │
│                                                       │
│  System prompt + serialized data + query + format     │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│  STAGE 4: LLM INFERENCE                              │
│                                                       │
│  Amazon Bedrock: Claude 3.5 | GPT-5.4 | Llama 3 |   │
│  DeepSeek V3.2 | Qwen3 32B                          │
└─────────────────────────────────────────────────────┘
```

## Key Insight

| Stage | Question | Performance Impact | Research Maturity |
|-------|----------|-------------------|-------------------|
| 1. Retrieval | "What data?" | 5–10% accuracy variance | Well-studied |
| **2. Serialization** | **"What format?"** | **Up to 23% accuracy variance** | **Unexplored — FHIRBench** |
| 3. Prompt | "What instructions?" | Varies | Moderately studied |
| 4. Inference | "Which model?" | Model-dependent | Extensively benchmarked |

*Figure 2. The clinical AI data pipeline. FHIRBench targets Stage 2 (serialization), which produces larger accuracy variance than retrieval strategy selection yet has received significantly less systematic study.*

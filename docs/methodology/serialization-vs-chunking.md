# Serialization vs. RAG Chunking: Positioning FHIRBench in the LLM Data Pipeline

## 1. The Clinical AI Data Pipeline

The following diagram illustrates the complete data pipeline from raw EHR data to LLM inference, highlighting where serialization and chunking operate:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLINICAL AI DATA PIPELINE                                  │
│                                                                               │
│  ┌──────────────────┐                                                        │
│  │   Patient EHR    │ 10,000+ resources per patient                          │
│  │  (FHIR Server)   │ Conditions, Medications, Observations, Encounters...   │
│  └────────┬─────────┘                                                        │
│           │                                                                   │
│           ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────┐                │
│  │        STAGE 1: RETRIEVAL / CHUNKING                      │                │
│  │                                                            │                │
│  │  Question: "WHAT data is relevant to this query?"          │                │
│  │                                                            │                │
│  │  Methods:                                                  │                │
│  │  • FHIRPath queries (FHIRPath-QA [CITE:V4M8Q6TN])        │                │
│  │  • SQL/GraphQL over FHIR (SM3 [CITE:2MV7H8T6])           │                │
│  │  • Agent-based retrieval (FHIR-AgentBench [CITE:WV9N648K])│                │
│  │  • Semantic similarity search                              │                │
│  │  • Rule-based resource filtering                           │                │
│  │                                                            │                │
│  │  Output: 5–50 relevant FHIR resources                      │                │
│  └────────────────────────────┬─────────────────────────────┘                │
│                               │                                               │
│                               ▼                                               │
│  ┌──────────────────────────────────────────────────────────┐                │
│  │        STAGE 2: SERIALIZATION  ◄━━━ FHIRBench            │                │
│  │                                                            │                │
│  │  Question: "HOW should this data be FORMATTED for the LLM?"│                │
│  │                                                            │                │
│  │  Strategies (our 6):                                       │                │
│  │  • Raw JSON (lossless, verbose)                            │                │
│  │  • Flattened Key-Value (compact, structured)               │                │
│  │  • Natural Language Narrative (prose, intuitive)            │                │
│  │  • Structured Markdown (headers, tables)                   │                │
│  │  • Clinical Template (SOAP, problem list)                  │                │
│  │  • Hybrid Adaptive (task-aware routing)                    │                │
│  │                                                            │                │
│  │  Also addresses:                                           │                │
│  │  • Terminology resolution (codes → display text)           │                │
│  │  • Schema transformation (hierarchical → flat)             │                │
│  │  • Clinical semantics preservation                         │                │
│  │  • Token budget optimization                               │                │
│  │                                                            │                │
│  │  Output: Formatted text (500–8,000 tokens depending on     │                │
│  │          strategy — up to 16× variance)                    │                │
│  └────────────────────────────┬─────────────────────────────┘                │
│                               │                                               │
│                               ▼                                               │
│  ┌──────────────────────────────────────────────────────────┐                │
│  │        STAGE 3: PROMPT CONSTRUCTION                        │                │
│  │                                                            │                │
│  │  • System prompt (task instructions)                       │                │
│  │  • Serialized clinical data (from Stage 2)                 │                │
│  │  • Query/question                                          │                │
│  │  • Output format constraints                               │                │
│  └────────────────────────────┬─────────────────────────────┘                │
│                               │                                               │
│                               ▼                                               │
│  ┌──────────────────────────────────────────────────────────┐                │
│  │        STAGE 4: LLM INFERENCE                              │                │
│  │                                                            │                │
│  │  Amazon Bedrock (5 models)                                 │                │
│  │  Claude 3.5 │ GPT-5.4 │ Llama 3 │ DeepSeek │ Qwen3       │                │
│  └──────────────────────────────────────────────────────────┘                │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Serialization vs. RAG Chunking — Fundamental Differences

### 2.1 Problem Definition

| Dimension | RAG Chunking | Clinical Data Serialization (FHIRBench) |
|-----------|-------------|------------------------------------------|
| **Core question** | "What subset of data is relevant?" | "How should selected data be represented?" |
| **Pipeline stage** | Stage 1 (Retrieval) | Stage 2 (Formatting) |
| **Input data** | Unstructured text OR structured records | Structured FHIR resources (JSON, coded) |
| **Output** | Relevant data subset (unchanged format) | Transformed text representation |
| **Information transformation** | None — data is selected, not altered | YES — format, vocabulary, structure all change |

### 2.2 Technical Differences

| Technical Aspect | RAG Chunking | Serialization |
|-----------------|-------------|---------------|
| **Vocabulary** | Text stays as text | Codes must be resolved: `73211009` → "Diabetes mellitus" |
| **Schema** | Unchanged — splits at boundaries | Fundamentally altered — nested JSON → flat prose |
| **Relationships** | Preserved within chunks | May be lost (Parent→Child hierarchy flattened) |
| **Semantics** | Implicit in natural language | Must be made explicit (SOAP structure carries meaning) |
| **Reversibility** | High — chunks can be reassembled | Low — prose cannot be reliably reconverted to FHIR |
| **Token impact** | 10-20% variance between strategies | **4-16× variance** between strategies |
| **Model sensitivity** | Low — chunking is model-agnostic | **High — optimal format differs by model size** [CITE:TGZ97SRN] |
| **Task sensitivity** | Low — same chunks work for most tasks | **High — QA favors structure, reasoning favors narrative** |

### 2.3 Performance Impact Comparison

| Metric | Typical RAG Chunking Impact | Serialization Impact (FHIRBench) |
|--------|---------------------------|----------------------------------|
| Accuracy variance | 5-10% between chunk sizes [typical RAG literature] | **Up to 23%** between formats [CITE:TGZ97SRN] |
| Token cost variance | 2-3× (256 vs 1024 token chunks) | **4-16×** (flattened KV vs raw JSON) |
| Optimal strategy stability | Largely model-independent | **Reverses across model scales** (7B vs 70B) |
| Research maturity | Well-studied (LangChain, LlamaIndex ecosystem) | **Systematically unexplored** — FHIRBench's contribution |

## 3. FHIRBench vs. Structured Data Chunking

### 3.1 Distinguishing from "Chunking Strategies for Structured Data"

Some may argue that serialization is merely "a form of chunking for structured data." We clarify why this is a distinct problem:

| Property | Chunking (even for structured data) | Serialization (FHIRBench) |
|----------|-------------------------------------|---------------------------|
| **Goal** | Fit data within retrieval window | **Transform** data for comprehension |
| **Transformation depth** | Split/merge (structural) | **Format conversion** (semantic) |
| **Vocabulary transformation** | None | YES — terminology codes → human/LLM-readable text |
| **Clinical semantics** | Not addressed | CORE — template choice carries clinical reasoning affordances |
| **Format design space** | 1D: chunk size (small→large) | **Multi-dimensional**: format × terminology × granularity × context strategy |
| **Evaluation criteria** | Retrieval recall/precision | **Clinical accuracy + cost efficiency** (Pareto analysis) |
| **Generalization** | Strategy transfers across domains | **Domain-specific** — clinical templates don't apply to financial data |

### 3.2 Complementary Relationship

Serialization and chunking are **sequential, complementary stages** — not competing approaches:

```
CHUNKING decides WHAT goes into the context window.
SERIALIZATION decides HOW it looks once it's there.
```

In a production clinical AI system, BOTH must be optimized:

```
Optimal Pipeline:
  FHIR Server
    │
    ├─ Chunking/Retrieval → selects relevant resources (solved by FHIRPath-QA, FHIR-AgentBench)
    │
    └─ Serialization → formats selected resources (solved by FHIRBench)
            │
            └─ Combined prompt → LLM → Clinical output
```

**Key insight:** Even with perfect retrieval (all relevant resources selected), a suboptimal serialization strategy can degrade accuracy by up to 23%. Conversely, even with optimal serialization, poor retrieval that misses relevant resources will produce incomplete answers. The problems are orthogonal.

### 3.3 Why Serialization Has Been Overlooked

Despite producing larger performance variance than chunking, serialization has received less attention because:

1. **RAG is general-purpose** — chunking strategies apply to any text domain; serialization is healthcare-specific
2. **Tooling gap** — LangChain/LlamaIndex popularized chunking; no equivalent toolkit exists for clinical serialization
3. **Data access barriers** — FHIR-specific research requires health informatics expertise + FHIR familiarity
4. **Assumption of transparency** — practitioners assumed "JSON is JSON" without testing format effects
5. **Recent evidence** — The Pator (2026) finding that optimal format *reverses* between model sizes was published only months ago

FHIRBench addresses this gap by providing the first systematic, multi-model, multi-task benchmark specifically evaluating the serialization stage.

## 4. Implications for Practitioners

### 4.1 Decision Framework Position

| If you're optimizing... | Address chunking? | Address serialization? |
|------------------------|-------------------|----------------------|
| Overall pipeline accuracy | Yes (ensure relevant data is retrieved) | **Yes — potentially larger impact** |
| Token cost / latency | Minor impact | **Major impact** (4-16× variance) |
| Model selection | Not relevant to chunking | **Critical** (format preference differs by model) |
| Task-specific performance | Minor impact | **Major impact** (task × format interaction) |

### 4.2 The Combined Optimization Problem

For production systems, the full optimization is:

```
maximize: accuracy(retrieval_strategy, serialization_strategy, model)
subject to: token_cost ≤ budget
            latency ≤ threshold
            safety ≥ minimum
```

FHIRBench provides the serialization component of this optimization — enabling practitioners to select from the Pareto frontier of format × model × task combinations.

---

## Citation Note

This document should inform two sections of the paper:
- **§1.1 (Introduction)**: 2-3 sentences distinguishing from RAG chunking, citing the performance variance differential
- **§2.4 (Background)**: Fuller treatment (~400 words) positioning FHIRBench in the data pipeline, with the pipeline diagram as Figure 2

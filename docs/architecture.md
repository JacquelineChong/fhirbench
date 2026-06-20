# FHIRBench — Agentic AI Research Architecture

## System Overview

This research project uses a multi-agent architecture to systematically evaluate clinical data serialization strategies for Large Language Models. The architecture spans 4 layers:

```
┌─────────────────────────────────────────────────────────────────────┐
│          RESEARCH & WRITING LAYER — Amazon Quick Desktop             │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │  Lit Review  │  │   Writing    │  │   arXiv     │  │  Biblio  │ │
│  │    Agent     │  │    Agent     │  │  Formatter  │  │  Agent   │ │
│  │              │  │              │  │             │  │          │ │
│  │ Skill:       │  │ Skill:       │  │ Skill:      │  │ MCP:     │ │
│  │ lit-review-  │  │ academic-    │  │ arxiv-      │  │ Zotero   │ │
│  │ search       │  │ writer       │  │ formatter   │  │          │ │
│  └──────────────┘  └──────────────┘  └─────────────┘  └──────────┘ │
│                                                                       │
├─────────────── Delegates via ACP (Agent Client Protocol) ────────────┤
│                                                                       │
│            CODE DEVELOPMENT LAYER — Kiro (Coding Agent)               │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │    Data      │  │ Serialization│  │  Benchmark  │  │ Analysis │ │
│  │ Engineering  │  │   Pipeline   │  │   Runner    │  │  & Viz   │ │
│  │              │  │              │  │             │  │          │ │
│  │ Synthea R4   │  │ 6 strategies │  │ 72 conds   │  │ Stats,   │ │
│  │ 1000 pts     │  │ × 4 dims    │  │ orchestrate │  │ Pareto   │ │
│  └──────────────┘  └──────────────┘  └─────────────┘  └──────────┘ │
│                                                                       │
├──────────────── Calls Models via AWS SDK / APIs ─────────────────────┤
│                                                                       │
│         MODEL INFERENCE LAYER — Amazon Bedrock + External             │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │   Claude     │  │   Llama 3   │  │   GPT-4o   │  │  Gemini  │ │
│  │ 3.5 Sonnet   │  │    70B      │  │            │  │  1.5 Pro │ │
│  │  (Bedrock)   │  │  (Bedrock)  │  │  (OpenAI)  │  │ (Google) │ │
│  └──────────────┘  └──────────────┘  └─────────────┘  └──────────┘ │
│                                                                       │
├────────────────────── Infrastructure ────────────────────────────────┤
│                                                                       │
│           INFRASTRUCTURE LAYER — MCP Servers + Services               │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │  Zotero MCP  │  │  GitHub MCP  │  │   GitHub    │  │   Kiro   │ │
│  │  (7 tools)   │  │  (6 tools)   │  │    Repo     │  │  Specs   │ │
│  │              │  │              │  │             │  │          │ │
│  │ search, add, │  │ create_file, │  │ Jacqueline- │  │ /specs/  │ │
│  │ cite, export │  │ issues, list │  │ Chong/      │  │ req/des/ │ │
│  │              │  │              │  │ fhirbench   │  │ stories  │ │
│  └──────────────┘  └──────────────┘  └─────────────┘  └──────────┘ │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Agent Decomposition

| # | Agent | Platform | Skill/Tool | Purpose |
|---|-------|----------|-----------|---------|
| 1 | Literature Review | Quick Desktop | `lit-review-search` | Systematic search across PubMed, arXiv, Semantic Scholar |
| 2 | Writing Agent | Quick Desktop | `academic-writer` | Draft IMRaD sections, maintain academic voice |
| 3 | arXiv Formatter | Quick Desktop | `arxiv-formatter` | Markdown → LaTeX → arXiv submission |
| 4 | Bibliography Agent | Quick Desktop | Zotero MCP | Reference management, citation formatting |
| 5 | Data Engineering | Kiro (ACP) | Shell + Python | Synthea FHIR R4 generation (1000 patients) |
| 6 | Serialization Pipeline | Kiro (ACP) | Python | 6 strategies × 4 dimensions |
| 7 | Benchmark Runner | Kiro (ACP) | Bedrock SDK | 72 conditions (6×4×3) orchestration |
| 8 | Analysis & Viz | Kiro (ACP) | Python | Statistical tests, Pareto frontier, decision framework |

## Serialization Strategies (6)

1. **Raw JSON** — Unmodified FHIR JSON (baseline)
2. **Flattened Key-Value** — Dot-notation (`patient.name.given = "John"`)
3. **Natural Language Narrative** — Full prose conversion
4. **Structured Markdown** — Hierarchical with headers and tables
5. **Clinical Summary Template** — SOAP note, problem list formats
6. **Hybrid Adaptive** — Task-aware format selection

## Evaluation Matrix

- **Models (4):** Claude Sonnet 4.5, Llama 3 70B, GPT-4o, Gemini 1.5 Pro
- **Tasks (3):** Clinical QA, Clinical Reasoning, Clinical Summarization
- **Metrics:** Accuracy, Clinical Correctness Score, ROUGE-L, Token Efficiency
- **Total conditions:** 6 × 4 × 3 = 72

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Orchestrator | Amazon Quick Desktop |
| Coding Agent | Kiro (ACP) |
| Model Inference | Amazon Bedrock, OpenAI API, Google AI API |
| Bibliography | Zotero Web API (via MCP) |
| Version Control | GitHub (via MCP) |
| Data Generation | Synthea (FHIR R4) |
| Spec-driven Dev | Kiro specs (requirements, design, stories) |
| Paper Formatting | LaTeX (arXiv article class) |

## Reproducibility

All code, data generation configs, experiment parameters, and analysis scripts are version-controlled in this repository. The Kiro specs in `/specs/` define the full system behavior reproducibly.

# Figure 1: FHIRBench Multi-Agent Research Architecture

The interactive HTML version is at `docs/figures/architecture-diagram.html`.

## Text Representation (for LaTeX/print)

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

## Layer Description

| Layer | Platform | Components |
|-------|----------|-----------|
| Research & Writing | Amazon Quick Desktop | Literature Review Agent, Writing Agent, arXiv Formatter, Bibliography Agent |
| Code Development | Kiro (ACP Agent) | Data Engineering, Serialization Pipeline, Benchmark Runner, Analysis & Viz |
| Model Inference | Amazon Bedrock | Claude 3.5 Sonnet, GPT-5.4, Llama 3 70B, DeepSeek V3.2, Qwen3 32B |
| Infrastructure | MCP Servers + Services | Zotero MCP (7 tools), GitHub MCP (6 tools), GitHub Repo, Kiro Specs |

*Figure 1. Multi-agent architecture for FHIRBench. The system uses four layers: research orchestration (Quick Desktop), code development (Kiro via ACP), model inference (Bedrock), and infrastructure (MCP servers for Zotero and GitHub). All layers communicate through standardized protocols (ACP for agent delegation, MCP for tool access, Bedrock Converse API for model inference).*

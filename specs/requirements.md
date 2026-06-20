# FHIRBench — Product Requirements

## Overview

FHIRBench is an open-source benchmark framework that systematically evaluates how different clinical data serialization strategies affect LLM performance on healthcare tasks.

## Goals

1. Implement 6 serialization strategies for converting FHIR R4 resources into LLM-consumable formats
2. Build a reproducible evaluation harness that tests serialization × model × task combinations
3. Generate statistical analysis and Pareto frontier visualizations
4. Produce a practitioner decision framework for serialization strategy selection

## Target Models (All via Amazon Bedrock — unified API)

- Claude Sonnet 4.5 (Bedrock: `anthropic.claude-sonnet-4-5-20260301-v1:0`)
- GPT-5.4 (Bedrock: `openai.gpt-5-4`)
- Llama 3 70B (Bedrock: `meta.llama3-70b-instruct-v1:0`)
- DeepSeek V3.2 (Bedrock: `deepseek.deepseek-v3-2`)
- Qwen3 32B (Bedrock: `qwen.qwen3-32b`)

**Design decision:** All models accessed via Bedrock's unified InvokeModel API for reproducibility, consistent token tracking, and single-credential replication. See `specs/models.md` for full selection rationale.

## Serialization Strategies

1. **Raw JSON** — Unmodified FHIR JSON (baseline)
2. **Flattened Key-Value** — Dot-notation flattening (`patient.name.given = "John"`)
3. **Natural Language Narrative** — Full prose conversion
4. **Structured Markdown** — Hierarchical markdown with headers and tables
5. **Clinical Summary Template** — Domain-specific templates (SOAP note, problem list)
6. **Hybrid Adaptive** — Task-aware format selection

## Evaluation Tasks

1. **Clinical QA** — Factual questions about patient data ("What medications is this patient taking?")
2. **Clinical Reasoning** — Inference tasks ("Is this patient at risk for drug interaction?")
3. **Clinical Summarization** — Generate patient summaries, care plans, handoff notes

## Metrics

- **Accuracy** (Clinical QA) — Exact match + semantic similarity
- **Clinical Correctness Score** (Reasoning) — Rubric-based scoring (0-5 scale)
- **ROUGE + Clinician Preference** (Summarization) — ROUGE-L + structured preference scoring
- **Token Efficiency** — Input tokens consumed (cost proxy)

## Data Source

- Synthea-generated FHIR R4 bundles (1,000 synthetic patients)
- Clinical domains: diabetes management, cardiovascular risk, medication interactions, preventive care gaps

## Non-Goals

- Real patient data (MIMIC-IV) — future work
- Fine-tuning experiments — future work
- Production API middleware — future work (but architecture informs it)


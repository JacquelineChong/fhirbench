# Model Selection Justification

## Why 5 Models (Not More)?

### Research Focus: Serialization, Not Models

This benchmark evaluates **serialization strategies** — models are the controlled variable, not the subject of study. We need sufficient diversity to demonstrate that findings generalize across architectures, not exhaustive coverage.

| Dimension | Our Approach |
|-----------|-------------|
| Primary variable | 6 serialization strategies |
| Controlled variable | 5 models (held constant per condition) |
| Total conditions | 90 (6 × 5 × 3) |
| Samples per condition | 50 |
| Total API calls | ~4,500 |

Each additional model adds 18 conditions (6 serializers × 3 tasks × 50 samples = 900 more API calls). Beyond 5 models, returns diminish for a serialization study.

### Selection Criteria (4 Orthogonal Dimensions)

| # | Criterion | Why It Matters | How Our 5 Satisfy It |
|---|-----------|---------------|---------------------|
| 1 | **Architecture diversity** | Different architectures may handle structured data differently | 5 distinct architectures: Anthropic (Claude), OpenAI (GPT), Meta (Llama), DeepSeek (MoE), Alibaba (Qwen) |
| 2 | **Parameter scale** | Model size affects context window utilization and reasoning depth | 32B (Qwen3) → 70B (Llama 3) → Frontier (Claude 3.5, GPT-5.4, DeepSeek V3.2) |
| 3 | **Training paradigm** | Proprietary vs. open-weight may differ in structured data handling | 2 proprietary (Claude, GPT-5.4) + 3 open-weight (Llama 3, DeepSeek V3.2, Qwen3) |
| 4 | **Global adoption** | Results must be relevant to practitioners | All 5 rank in top-10 by global token usage (2026) |

### Precedent in Literature

| Paper | Models Tested | Venue | Focus |
|-------|--------------|-------|-------|
| **Serialisation Strategy Matters (2025)** | 3 | arXiv | Serialization comparison |
| Med-PaLM 2 (Google, 2023) | 2 | Nature | Medical QA |
| Clinical-NLP benchmarks (typical) | 3–5 | Various | Clinical task evaluation |
| **FHIRBench (ours)** | **5** | arXiv | Serialization benchmark |

Our 5-model design **exceeds** the 3-model standard established in the foundational "Serialisation Strategy Matters" paper.

### Why Not 10+ Models?

| Factor | Impact of Adding Models |
|--------|------------------------|
| Statistical power | 5 models × 50 samples = sufficient for ANOVA + post-hoc |
| Cost | Each model adds ~$15-40 in Bedrock inference costs |
| Analysis complexity | 5 models already yield 20+ pairwise comparisons per task |
| Marginal insight | Architecture diversity saturates at 4–5 distinct families |
| Scope control | This is a serialization study, not HELM/Chatbot Arena |

### Bedrock-Only as Reproducibility Strength

> All evaluated models are accessed through Amazon Bedrock's unified InvokeModel API, ensuring:
> 1. **Consistent inference parameters** — identical temperature, max_tokens, top_p across all models
> 2. **Identical request/response pipelines** — no confounding from different API implementations
> 3. **Reproducible results** — model version pinning via Bedrock model IDs
> 4. **Single-credential replication** — any researcher with an AWS account can reproduce
> 5. **Unified token tracking** — consistent cost/efficiency metrics across all models

This eliminates confounding variables introduced by heterogeneous API implementations (different tokenizers, rate-limiting strategies, response formatting) that would affect a multi-provider setup.

### What We Acknowledge as Limitations

> "We evaluate 5 foundation models representing diverse architectures, parameter scales, and training paradigms available on Amazon Bedrock. While Bedrock hosts 100+ model variants across 18 providers, our selection maximizes diversity across dimensions relevant to serialization sensitivity (architecture, scale, training paradigm, adoption). Notably, Google's Gemini family is unavailable on Bedrock and therefore excluded. Future work may extend to additional models and providers as the ecosystem evolves."

### Threats to Validity & Mitigations

| Threat | Mitigation |
|--------|-----------|
| Bedrock-only excludes Gemini | Gemini's architecture (Mixture of Experts) is represented by DeepSeek V3.2 (also MoE) |
| Model versions may update | We pin specific Bedrock model IDs and report versions |
| 5 models may not generalize | Effect sizes and confidence intervals reported; ANOVA tests for model × serializer interaction |
| Open-weight models may differ from hosted versions | All models accessed via same Bedrock API — no self-hosted variants |

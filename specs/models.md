# FHIRBench — Model Selection

## Design Decision: Bedrock-Only

All benchmark models run through Amazon Bedrock's unified `InvokeModel` API.
No external API credentials required — single AWS account enables full reproducibility.

**Rationale:**
- Single API, consistent token tracking, unified billing
- Model version pinning via Bedrock model IDs
- Reviewers can reproduce with just an AWS account
- OpenAI models available on Bedrock since June 2026 (GA)

## Selected Models (5)

| # | Model | Provider | Bedrock Model ID | Category |
|---|-------|----------|-----------------|----------|
| 1 | Claude Sonnet 4.5 | Anthropic | `anthropic.claude-sonnet-4-5-20260301-v1:0` | Frontier proprietary |
| 2 | GPT-5.4 | OpenAI | `openai.gpt-5-4` | Frontier proprietary |
| 3 | Llama 3 70B | Meta | `meta.llama3-70b-instruct-v1:0` | Open-weight (large) |
| 4 | DeepSeek V3.2 | DeepSeek | `deepseek.deepseek-v3-2` | Open-weight (reasoning) |
| 5 | Qwen3 32B | Qwen | `qwen.qwen3-32b` | Open-weight (multilingual) |

## Selection Criteria

Models chosen based on:
1. **Availability on Bedrock** — all 5 confirmed available (as of Jun 2026)
2. **Usage/adoption** — top models by token consumption globally
3. **Architecture diversity** — proprietary (Claude, GPT) + open-weight (Llama, DeepSeek, Qwen)
4. **Parameter diversity** — ranging from 32B to frontier scale
5. **Reasoning capability** — all rank in top-10 on clinical/reasoning benchmarks

## Excluded Models (with justification)

| Model | Reason for Exclusion |
|-------|---------------------|
| Gemini 1.5 Pro | Not available on Amazon Bedrock (Google not a Bedrock provider) |
| Mistral Large | Lower clinical reasoning benchmarks vs selected models |
| Amazon Nova 2 | Newer, less established in independent benchmarks |

## Experimental Matrix

- **Serialization strategies:** 6
- **Models:** 5
- **Task types:** 3 (Clinical QA, Clinical Reasoning, Clinical Summarization)
- **Total conditions:** 6 × 5 × 3 = **90**
- **Samples per condition:** 50
- **Total API calls:** ~4,500

## Configuration

```yaml
models:
  - id: claude-sonnet-4.5
    provider: bedrock
    model_id: anthropic.claude-sonnet-4-5-20260301-v1:0
    max_tokens: 2048
    temperature: 0.0

  - id: gpt-5.4
    provider: bedrock
    model_id: openai.gpt-5-4
    max_tokens: 2048
    temperature: 0.0

  - id: llama-3-70b
    provider: bedrock
    model_id: meta.llama3-70b-instruct-v1:0
    max_tokens: 2048
    temperature: 0.0

  - id: deepseek-v3.2
    provider: bedrock
    model_id: deepseek.deepseek-v3-2
    max_tokens: 2048
    temperature: 0.0

  - id: qwen3-32b
    provider: bedrock
    model_id: qwen.qwen3-32b
    max_tokens: 2048
    temperature: 0.0
```

## Cost Estimation

| Model | Est. Input $/1M tokens | Est. Output $/1M tokens |
|-------|----------------------|------------------------|
| Claude Sonnet 4.5 | $3.00 | $15.00 |
| GPT-5.4 | $5.00 | $15.00 |
| Llama 3 70B | $0.72 | $0.72 |
| DeepSeek V3.2 | $1.00 | $2.00 |
| Qwen3 32B | $0.50 | $1.00 |

**Estimated total benchmark cost:** ~$75-200 (depending on serialization token usage)

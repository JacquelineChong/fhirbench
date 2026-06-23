# FHIRBench: Final Model Selection

**Confirmed in paper §3.1 (Research Design)**

## 5 Models for Full Benchmark (1,000-patient run)

| # | Model | Bedrock Model ID | Category |
|---|-------|-----------------|----------|
| 1 | Claude Sonnet 4.5 | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | Frontier (Anthropic) |
| 2 | GPT-5.4 | `openai.gpt-5.4` | Frontier (OpenAI) |
| 3 | Llama 3 70B | `meta.llama3-70b-instruct-v1:0` | Open-source (Meta) |
| 4 | DeepSeek V3.2 | `deepseek.v3.2` | Open-source (DeepSeek) |
| 5 | Qwen3 32B | `qwen.qwen3-32b-v1:0` | Open-source (Alibaba) |

## Experimental Design

- **Serializers:** 6 (Raw JSON, Flattened KV, Narrative, Structured Markdown, Clinical Template, Hybrid Adaptive)
- **Tasks:** 3 (Clinical QA, Clinical Reasoning, Clinical Summarization)
- **Patients:** 1,000 (complexity-stratified: Simple 25%, Moderate 40%, Complex 25%, Highly Complex 10%)
- **Total evaluations:** 4,500 (6 × 5 × 3 × 50 samples per condition)
- **Region:** us-east-2 (all models via Amazon Bedrock Converse API)
- **Inference params:** temperature=0.0, max_tokens=2048, top_p=1.0

## Notes

- All 5 models accessed via Amazon Bedrock Converse API (unified interface)
- GPT-5.4 accessed via Bedrock Mantle endpoint in us-east-2
- 50-patient validation run (300 prompts) completed for all 5 models
- 1,000-patient realistic benchmark: 4 Bedrock-native models complete; GPT-5.4 pending

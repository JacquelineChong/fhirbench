# FHIRBench Multi-Model Comparison

## Summary

- **Total prompts per model:** 300 (50 patients × 6 serializers)
- **Models tested:** 5
- **Serializers:** 6

## Models Tested

| Model | Bedrock ID |
|-------|-----------|
| Qwen3-32B | `qwen.qwen3-32b-v1:0` |
| Claude Sonnet 4.5 | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| Llama3-70B | `meta.llama3-70b-instruct-v1:0` |
| DeepSeek V3.2 | `deepseek.v3.2` |
| GPT-OSS-120B | `openai.gpt-oss-120b-1:0` |

## Mean F1 Score by Serializer × Model

| Serializer | Qwen3-32B | Claude Sonnet 4.5 | Llama3-70B | DeepSeek V3.2 | GPT-OSS-120B |
|---|---|---|---|---|---|
| raw_json | 0.2508 | 0.0722 | 0.2647 | 0.1781 | 0.1455 |
| flattened_kv | 0.2869 | 0.0761 | 0.4229 | 0.3089 | 0.2909 |
| structured_markdown | 0.3444 | 0.0936 | 0.4787 | 0.5322 | 0.3929 |
| narrative | 0.4566 | 0.0828 | 0.4998 | 0.4634 | 0.2514 |
| clinical_template | 0.5168 | 0.1006 | 0.5028 | 0.5546 | 0.4073 |
| hybrid_adaptive | 0.3284 | 0.0957 | 0.4824 | 0.5194 | 0.3877 |
| **OVERALL** | **0.3640** | **0.0868** | **0.4419** | **0.4261** | **0.3126** |

## Mean Total Tokens by Serializer × Model

| Serializer | Qwen3-32B | Claude Sonnet 4.5 | Llama3-70B | DeepSeek V3.2 | GPT-OSS-120B |
|---|---|---|---|---|---|
| raw_json | 2484 | 2612 | 2222 | 2179 | 2342 |
| flattened_kv | 1509 | 1579 | 1286 | 1291 | 1422 |
| structured_markdown | 380 | 416 | 339 | 322 | 461 |
| narrative | 383 | 423 | 322 | 312 | 486 |
| clinical_template | 334 | 381 | 302 | 283 | 433 |
| hybrid_adaptive | 380 | 418 | 339 | 322 | 459 |
| **OVERALL** | **912** | **971** | **802** | **785** | **934** |

## Best Serializer per Model (by F1)

| Model | Best Serializer | F1 Score |
|-------|----------------|----------|
| Qwen3-32B | clinical_template | 0.5168 |
| Claude Sonnet 4.5 | clinical_template | 0.1006 |
| Llama3-70B | clinical_template | 0.5028 |
| DeepSeek V3.2 | clinical_template | 0.5546 |
| GPT-OSS-120B | clinical_template | 0.4073 |

## Overall Model Rankings (by Mean F1)

| Rank | Model | Mean F1 |
|------|-------|---------|
| 1 | Llama3-70B | 0.4419 |
| 2 | DeepSeek V3.2 | 0.4261 |
| 3 | Qwen3-32B | 0.3640 |
| 4 | GPT-OSS-120B | 0.3126 |
| 5 | Claude Sonnet 4.5 | 0.0868 |

## Efficiency Ranking (F1 per 1000 tokens)

| Rank | Model | F1/1K tokens |
|------|-------|-------------|
| 1 | Llama3-70B | 0.5512 |
| 2 | DeepSeek V3.2 | 0.5430 |
| 3 | Qwen3-32B | 0.3993 |
| 4 | GPT-OSS-120B | 0.3348 |
| 5 | Claude Sonnet 4.5 | 0.0894 |

## F1 by Domain × Model

| Domain | Qwen3-32B | Claude Sonnet 4.5 | Llama3-70B | DeepSeek V3.2 | GPT-OSS-120B |
|---|---|---|---|---|---|
| cardiovascular | 0.4068 | 0.1016 | 0.4916 | 0.5028 | 0.4151 |
| diabetes | 0.3705 | 0.1159 | 0.4335 | 0.4554 | 0.2879 |
| medication_interactions | 0.3166 | 0.1160 | 0.4911 | 0.4966 | 0.2706 |
| preventive_care | 0.3617 | 0.0006 | 0.3348 | 0.2174 | 0.2702 |

## Key Findings

1. **Best overall model:** Llama3-70B (F1 = 0.4419)
2. **Best overall serializer (across all models):** clinical_template (mean F1 = 0.4164)
3. **Most efficient model:** Llama3-70B (0.5512 F1 per 1K tokens)
4. **All 1,500 calls completed with 0 errors**

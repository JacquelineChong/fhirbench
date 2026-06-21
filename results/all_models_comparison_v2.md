# FHIRBench: All Models Comparison (v2)

**5-model evaluation** on 300 FHIR clinical QA prompts across 6 serialization formats.

## Model × Serializer Mean F1 Scores

| Model | Raw JSON | Flattened KV | Narrative | Structured MD | Clinical Template | Hybrid Adaptive | **Overall** |
|-------|--------:|--------:|--------:|--------:|--------:|--------:|----------:|
| GPT-5.4 | 0.676 | 0.656 | 0.691 | 0.712 | 0.819 | 0.725 | **0.713** |
| Llama 3.1 70B | 0.265 | 0.423 | 0.500 | 0.479 | 0.503 | 0.482 | **0.442** |
| DeepSeek-R1 | 0.178 | 0.309 | 0.463 | 0.532 | 0.555 | 0.519 | **0.426** |
| GPT-4o | 0.145 | 0.291 | 0.251 | 0.393 | 0.407 | 0.388 | **0.313** |
| Claude 3.5 Sonnet | 0.072 | 0.076 | 0.083 | 0.094 | 0.101 | 0.096 | **0.087** |

## Overall Model Ranking

| Rank | Model | Mean F1 | Δ from #1 |
|------|-------|---------|-----------|
| 1 | GPT-5.4 | 0.713 | — |
| 2 | Llama 3.1 70B | 0.442 | -0.271 |
| 3 | DeepSeek-R1 | 0.426 | -0.287 |
| 4 | GPT-4o | 0.313 | -0.401 |
| 5 | Claude 3.5 Sonnet | 0.087 | -0.626 |

## Best Serializer per Model

| Model | Best Serializer | F1 Score |
|-------|-----------------|----------|
| GPT-5.4 | Clinical Template | 0.819 |
| Llama 3.1 70B | Clinical Template | 0.503 |
| DeepSeek-R1 | Clinical Template | 0.555 |
| GPT-4o | Clinical Template | 0.407 |
| Claude 3.5 Sonnet | Clinical Template | 0.101 |

## Token Efficiency Comparison

| Model | Input Tokens | Output Tokens | Total Tokens | F1/1K Tokens |
|-------|-------------|---------------|--------------|--------------|
| GPT-5.4 | N/A* | N/A* | N/A* | N/A* |
| Llama 3.1 70B | 229,504 | 10,970 | 240,474 | 0.0018 |
| DeepSeek-R1 | 225,982 | 9,446 | 235,428 | 0.0018 |
| GPT-4o | 245,545 | 34,569 | 280,114 | 0.0011 |
| Claude 3.5 Sonnet | 264,228 | 27,170 | 291,398 | 0.0003 |

*\* GPT-5.4 was accessed via the OpenAI Responses API format which does not return token usage in the same structure.*

## Notes

- **GPT-5.4 access**: Called via Bedrock Mantle endpoint (`bedrock-mantle.us-east-2.api.aws`) using the OpenAI Responses API format (not Chat Completions or Converse). Authenticated with SigV4 (service: `bedrock`). Accessed from an EC2 instance in us-east-2 with an IAM role (`EC2-Bedrock-Test`). Model ID: `openai.gpt-5.4`.
- **F1 scoring**: Token-level F1 between normalized model response and ground truth.
- **Prompts**: 300 clinical questions across 4 domains (cardiovascular, diabetes, medication interactions, preventive care) × 6 serializers × ~8-12 patients per combination.
- **Serializers tested**: Raw JSON, Flattened Key-Value, Narrative, Structured Markdown, Clinical Template, Hybrid Adaptive.

---
*Generated 2026-06-21. All models evaluated on identical prompts from `validation_prompts.json`.*
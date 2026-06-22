# Re-Run Complex Cases: Context Budget Mitigation Results

**Run date:** 2026-06-22 17:40
**Strategy:** Relevance-filtered serialization with 4000 token budget
**Cases re-run:** 2520 (COMPLEX + HIGHLY_COMPLEX)

## Before vs After

| Metric | Before (Original) | After (Context Budget) |
|--------|-------------------|------------------------|
| Total calls | 2520 | 2520 |
| Successful responses | 0 (0%) | 1791 (71%) |
| Empty responses | 2520 (100%) | 729 |
| Avg F1 Score | 0.0 | 0.4761 |

## Truncation Statistics

- Records truncated: 0/2520 (0%)
- Records within budget: 2520/2520
- Original token range: 58 - 3729
- Mean original tokens: 616

### Truncation by Serializer
| Serializer | Avg Original Tokens | % Truncated |
|------------|--------------------:|:-----------:|
| raw_json | 2771 | 0% |
| narrative | 187 | 0% |
| key_value | 155 | 0% |
| markdown_table | 268 | 0% |
| fhir_path | 226 | 0% |
| condensed | 92 | 0% |

## F1 Scores by Serializer (Re-run)
| Serializer | Avg F1 | Avg Coverage | N Success |
|------------|--------|--------------|-----------|
| raw_json | 0.3999 | 0.8379 | 216 |
| narrative | 0.4890 | 0.8028 | 315 |
| key_value | 0.4955 | 0.8138 | 315 |
| markdown_table | 0.4782 | 0.8048 | 315 |
| fhir_path | 0.4841 | 0.8410 | 315 |
| condensed | 0.4862 | 0.8009 | 315 |

## F1 Scores by Model (Re-run)
| Model | Avg F1 | N Success |
|-------|--------|-----------|
| qwen.qwen3-32b-v1:0 | 0.4942 | 630 |
| us.anthropic.claude-sonnet-4-5-20250929-v1:0 | 0.0000 | 0 |
| meta.llama3-70b-instruct-v1:0 | 0.4902 | 531 |
| deepseek.v3.2 | 0.4463 | 630 |

## F1 by Complexity Level
| Complexity | Avg F1 | N Success | N Total |
|------------|--------|-----------|---------|
| COMPLEX | 0.4634 | 1281 | 1800 |
| HIGHLY_COMPLEX | 0.5082 | 510 | 720 |

## Model × Serializer (Avg F1)
| Model | raw_json | narrative | key_value | markdown_table | fhir_path | condensed |
|-------|-------|-------|-------|-------|-------|-------|
| qwen | 0.439 | 0.505 | 0.514 | 0.500 | 0.489 | 0.520 |
| us | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| meta | 0.432 | 0.495 | 0.499 | 0.474 | 0.503 | 0.484 |
| deepseek | 0.359 | 0.468 | 0.474 | 0.461 | 0.461 | 0.455 |

# Generation Run Log — Batch 1 (2026-07-22)

## Configuration
- Model: DeepSeek V3.2 (`deepseek.v3.2` on Bedrock, us-east-2)
- Workers: 5 concurrent (reduced from initial 10 due to timeouts)
- max_tokens: 8192 (initial setting)
- Read timeout: 300 seconds (boto3 config)
- Run from: Local Mac (HK) — DeepSeek not geo-blocked

## Results

| Metric | Value |
|--------|-------|
| Target | 1,000 patients |
| Processed | ~500 |
| ✅ Successfully saved | 248 |
| ❌ Failed (all 3 retries exhausted) | 247 |
| Failure rate | ~50% overall, ~98% for complex/highly_complex |

### Success by Complexity

| Complexity | Generated | Expected | Success Rate |
|------------|-----------|----------|:---:|
| Simple | 82 | 250 | ~80% |
| Moderate | 161 | 400 | ~75% |
| Complex | 5 | 250 | ~2% |
| Highly Complex | 0 | 100 | 0% |

### Success by Domain

| Domain | Generated |
|--------|-----------|
| Preventive Care | 76 |
| Diabetes | 75 |
| Cardiovascular | 62 |
| Medication Interactions | 35 |

## Root Cause Analysis

### Primary Failure: Output Token Truncation

All 247 failures were `JSONDecodeError` — the model produces valid FHIR JSON but gets **truncated mid-stream** when hitting the `max_tokens=8192` ceiling. Truncation points cluster around character 32,000–35,000 (≈8K tokens), confirming the limit is the cause.

Error patterns:
- `Unterminated string starting at: line 1356 column 15`
- `Expecting ',' delimiter: line 1245 column 21`
- `Expecting property name enclosed in double quotes: line 1302 column 32`

All errors occur at high line numbers (1100–1400), indicating the JSON was being generated correctly until output was cut off.

### Comparison with Paper 1 Llama 3.1 70B Failure

| Dimension | Paper 1 (Llama 3.1 70B) | Paper 2 (DeepSeek V3.2) |
|-----------|---|---|
| Failure mode | 100% inference timeout | ~50% output truncation |
| Affected complexity | All (but worse on complex) | Complex/Highly Complex only |
| Root cause | Insufficient context handling | max_tokens too low |
| Fixable? | No (fundamental model limitation) | **Yes** — increase max_tokens |

Key insight: DeepSeek's failure is an **artificial ceiling** (parameter misconfiguration), not a fundamental model limitation. The model generates valid FHIR JSON — it just runs out of allowed output space.

### DeepSeek V3.2 Actual Token Limits (Bedrock)

Per AWS documentation and pricing calculators:
- Context window: 163,840 tokens
- Maximum output tokens: 82,000–163,840 tokens (sources vary)
- The "quality degrades above 8,192" warning applies to **DeepSeek-R1** (reasoning model), NOT V3.2 (generation model)

### Secondary Issue: Invalid NHS Numbers

~20% of saved bundles have NHS Numbers that fail Modulus 11 check digit validation. The bundles are kept (valid FHIR structure otherwise) — NHS Numbers will be corrected in post-processing via a deterministic algorithm that recalculates the check digit.

## Fix Applied

`max_tokens` increased from 8192 → **32768** (32K) for all patients uniformly. This provides:
- ~4× the previous limit
- Well within DeepSeek V3.2's actual output capability
- Sufficient for highly_complex patients (70–120+ resources, ~16K tokens estimated)
- No quality degradation (the 8K quality warning is R1-specific, not V3.2)

## Next Steps (Batch 2)

1. Re-run full 1,000 patients with `max_tokens=32768`
2. Script skips existing valid files (248 already generated)
3. Expected: ~752 new patients needed
4. Post-processing: fix NHS Number check digits
5. Validation pass against UK Core StructureDefinitions

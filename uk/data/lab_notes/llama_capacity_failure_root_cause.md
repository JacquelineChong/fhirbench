# Lab Note: Root Cause Analysis — Llama 3.1 70B "Capacity Failure" (Paper 1)

## Date: 2026-07-26

## Context

Paper 1 (FHIRBench, medRxiv) reported that Llama 3.1 70B exhibited a "complete capacity failure" — 100% inference timeout on complex FHIR data (630/630 prompts failed). This was framed as Finding #4: a patient safety gap where certain models fail entirely on complex clinical records.

Paper 2 (FHIRBench-UK) tested Llama 3.3 70B, which achieved **100% success rate** (1,800/1,800 prompts, including all complex and highly complex patients). This prompted a retrospective investigation into the Paper 1 failure.

---

## Investigation Findings

### Evidence from Paper 1 Code and Data

| File | Contents |
|------|----------|
| `run_layer1_3models.py` | Benchmark script — `read_timeout=60`, `maxTokens=2048` |
| `layer1_llama_630.json` | Only **2 entries**, both `ReadTimeoutError` |
| `bedrock_llama_300.json` | **300 entries, ALL SUCCESSFUL** (F1=0.44 avg) |

### Key Discovery: Llama 3.1 DID Work

The file `bedrock_llama_300.json` contains 300 successful Llama 3.1 70B responses with valid F1 scores (range: 0.14–0.56, mean: 0.44). This proves Llama 3.1 was **never fundamentally incapable** of processing FHIR data. It successfully handled 50 patients × 6 serialisers across all clinical tasks.

---

## Root Cause Analysis (6 Factors)

### Factor 1: Read Timeout — PRIMARY CAUSE

| | Paper 1 | Paper 2 |
|--|---------|---------|
| `read_timeout` | **60 seconds** | **600 seconds** |
| Result | 100% timeout on complex | 100% success |

Complex FHIR bundles (up to 55K chars in Paper 1, 122K in Paper 2) require 2–5 minutes for inference. A 60-second timeout guarantees failure on any prompt requiring >60s of processing time. This is a **configuration error**, not a model limitation.

### Factor 2: Only 2 Prompts Attempted

The `layer1_llama_630.json` file contains only 2 entries. The script saves results after each prompt, confirming only 2 of 630 prompts were attempted before the run was terminated. With 60s timeout × 3 retries = 180s per failed prompt, 2 failures took ~6 minutes before the run was likely killed manually.

**We did not give the model a fair trial.** 2/630 = 0.3% of the intended evaluation.

### Factor 3: Model Version (Llama 3.1 → 3.3)

Cannot be isolated from Factor 1 without a controlled experiment (running Llama 3.1 with 600s timeout). Llama 3.3 may have faster inference or better long-context handling, but we have no evidence this was necessary — the timeout fix alone is sufficient to explain the difference.

### Factor 4: Cross-Region Inference Latency

| | Paper 1 | Paper 2 |
|--|---------|---------|
| Model ID | `us.meta.llama3-1-70b-instruct-v1:0` | `meta.llama3-3-70b-instruct-v1:0` |
| Prefix | `us.` (cross-region) | None (direct) |

Cross-region inference adds network latency, potentially pushing borderline requests past the 60s timeout. Not the primary cause, but may have contributed.

### Factor 5: max_tokens Constraint

| | Paper 1 | Paper 2 |
|--|---------|---------|
| `maxTokens` | 2048 | 4096 |

Minor factor. The timeout error occurs during inference (before generation completes), so output token limits are not the bottleneck. However, 2048 tokens is restrictive for comprehensive clinical responses.

### Factor 6: API Format

Both Paper 1 and Paper 2 used the Bedrock **Converse API** (confirmed in code). This is NOT a contributing factor — the API format was the same.

---

## Impact Assessment

### What Paper 1 Reported (Finding #4):

> "Llama 3.1 70B exhibited complete capacity failure — 100% inference timeout on complex FHIR data. This represents a patient safety gap where model selection directly impacts whether clinical data can be processed at all."

### What Actually Happened:

1. A **60-second read timeout** (insufficient for large-context inference) caused 100% failure on 2 tested prompts
2. The run was abandoned after 2 failures — 628 prompts were never attempted
3. An earlier pilot run proved Llama 3.1 **can process FHIR data successfully** (300/300, F1=0.44)
4. The "capacity failure" was a timeout configuration issue, not a fundamental model limitation

### Severity of Overstatement:

**Moderate.** The finding that complex FHIR bundles stress model inference time IS valid — but attributing it to "model capacity" rather than "infrastructure configuration" mischaracterises the root cause. The patient safety implication (some models can't process data) remains directionally valid if timeout budgets are constrained in production systems, but the absolute claim of "Llama cannot do this" is unsupported.

---

## Corrective Actions for Paper 2

1. **Do NOT claim** Llama 3.3 "fixed a capacity failure" — the fix was our timeout setting
2. **Report honestly** in §5 Discussion that the Paper 1 Llama finding was confounded by insufficient timeout configuration
3. **Reframe the finding as:** "Adequate inference timeout (≥600s for complex FHIR bundles) is a prerequisite for fair model evaluation. Under-provisioned timeout budgets can produce spurious model capacity conclusions."
4. **New framing for Paper 2:** "All five models — including Llama 3.3 70B — successfully processed all complexity levels when given adequate inference time (600s timeout). This contrasts with the Paper 1 observation where Llama 3.1 timed out under a 60s ceiling, suggesting the earlier finding reflected infrastructure constraints rather than fundamental model limitations."
5. **Acknowledge** that we cannot definitively separate the timeout fix from the model version upgrade without running Llama 3.1 under Paper 2's configuration — which is outside scope for this study but noted as future work.

---

## Lessons Learned

1. **Always set read_timeout ≥ 10× the expected inference time** for benchmark evaluation. For FHIR bundles: ≥600s.
2. **Never draw conclusions from <5% of intended samples.** 2/630 prompts is not a valid basis for claiming "100% failure."
3. **Check for prior successful runs** before characterising a model as incapable. The bedrock_llama_300.json file was available but not consulted when writing the Paper 1 finding.
4. **Separate infrastructure failures from model failures** in research reporting. A timeout is an infrastructure constraint; a wrong/incoherent response is a model limitation.
5. **Configuration parameters are experimental variables.** They must be reported and justified in methodology, not assumed as defaults.

---

## References

- Paper 1 benchmark script: `~/Desktop/Kiro/FHIR/code/run_layer1_3models.py`
- Llama 3.1 complex results (2 entries): `~/Desktop/Kiro/FHIR/code/results/layer1_llama_630.json`
- Llama 3.1 pilot results (300 successes): `~/Desktop/Kiro/FHIR/code/results/bedrock_llama_300.json`
- Paper 2 Llama 3.3 results (1,800 successes): `~/Desktop/Kiro/FHIR-UK/results/layer1_llama_1800.json`

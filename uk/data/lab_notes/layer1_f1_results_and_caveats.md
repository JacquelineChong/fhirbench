# Lab Note: Layer 1 F1 Results — Methodological Caveats & Cross-Study Comparability

## Date: 2026-07-27

## Context

Layer 1 (token-level F1) scoring completed for all 5 models × 1,800 prompts = 9,000 evaluations. This note documents the results, methodological caveats, and why absolute F1 scores are NOT directly comparable between Paper 1 (US Core) and Paper 2 (UK Core).

---

## Layer 1 Results Summary

### Model Rankings (Mean F1, 95% CI)

| Rank | Model | Mean F1 | 95% CI |
|:---:|-------|---------|--------|
| 1 | Llama 3.3 70B | 0.4540 | [0.4447, 0.4633] |
| 2 | Qwen3 32B | 0.4482 | [0.4396, 0.4567] |
| 3 | Claude Sonnet 4.5 | 0.4279 | [0.4186, 0.4372] |
| 4 | GPT-5.4 | 0.4168 | [0.4067, 0.4269] |
| 5 | DeepSeek V3.2 | 0.4159 | [0.4066, 0.4252] |

### By Serialiser (all models)
- **raw_json** consistently scores highest (0.43-0.48)
- **flattened_kv** scores lowest (0.39-0.43)
- narrative, clinical_template, structured_markdown, hybrid_adaptive cluster in middle

### By Task
- **clinical_qa** dominates (~0.64-0.68 F1) — factual extraction is easiest
- **clinical_summarization** is moderate (~0.41-0.51)
- **clinical_reasoning** is hardest (~0.16-0.22) — reasoning tokens don't overlap well with ground truth facts

### By Complexity
- F1 increases with complexity (more resources = more token overlap opportunity)
- Simple: ~0.37-0.41 | Moderate: ~0.42-0.46 | Complex: ~0.45-0.49 | Highly Complex: ~0.45-0.48

---

## CRITICAL CAVEAT: Cross-Study F1 Comparison Is Invalid

### Paper 1 (US Core) vs Paper 2 (UK Core) F1 scores are NOT comparable

Paper 1 avg F1: ~0.32 | Paper 2 avg F1: ~0.42

This difference does NOT mean "models improved" or "UK prompts are easier." The difference is an artifact of **methodological differences** between the two studies:

### Difference 1: Ground Truth Extraction Method

| | Paper 1 | Paper 2 |
|--|---------|---------|
| Method | Manually curated per prompt | Automatically extracted from FHIR bundles |
| Granularity | Specific expected answers | All extractable clinical tokens |
| Effect | Stricter matching (fewer GT tokens) | More lenient matching (more GT tokens) |

If Paper 2's automated extraction pulls more tokens as "ground truth" than Paper 1's manual curation, recall becomes easier to achieve, inflating F1.

### Difference 2: Prompt Structure

| | Paper 1 | Paper 2 |
|--|---------|---------|
| Format | system_prompt + user_prompt (two fields) | Single combined prompt |
| Effect | Models may split attention | Models get one focused instruction |

This could affect response focus and token overlap patterns.

### Difference 3: Patient Data Source

| | Paper 1 | Paper 2 |
|--|---------|---------|
| Source | Modified Synthea (realistic clinical trajectories) | DeepSeek-generated (LLM-synthesised) |
| Characteristics | Messy, realistic, varied naming | Potentially more "textbook," predictable |
| Effect on F1 | Harder to extract from realistic data | Easier to extract from structured/predictable data |

LLM-generated FHIR bundles may use more standardised terminology that other LLMs can more easily match, artificially inflating F1.

### Difference 4: Tokenisation in F1 Calculation

The F1 scoring scripts may differ in:
- Word splitting rules
- Stopword lists
- Case normalisation
- Punctuation handling

Small differences compound across 9,000 evaluations.

---

## Correct Interpretation for Paper 2

### What we CAN report:
- **Within-study relative rankings** (which model outperforms which on UK Core data)
- **Within-study effects** (serialiser impact, complexity impact, task difficulty)
- **Serialiser × model interactions** (is there a universal best format?)
- **Llama 3.3 participation** (100% success vs Paper 1's Llama 3.1 timeout)

### What we CANNOT report:
- "F1 scores improved from Paper 1 to Paper 2" (methodological artifact)
- "UK Core data is easier than US Core" (confounded by extraction method)
- "Claude improved from 0.22 to 0.43" (different ground truth, different scoring)

### Recommended Paper 2 Framing:

> "We report within-study F1 scores for the UK Core evaluation. Cross-national comparison of absolute F1 values is not meaningful due to differences in ground truth extraction methodology between the two studies. However, relative model rankings and serialiser effects can be compared qualitatively."

---

## Observations for Layer 2 Hypothesis

Based on Paper 1's "ranking reversal" (Claude last on F1, first on Judge), we predict:
- If the same pattern holds: Claude and GPT-5.4 may rank higher on Layer 2 (LLM-as-Judge) despite being 3rd and 4th on F1
- Llama's high F1 may be because it produces concise responses (fewer tokens = higher precision) rather than because it's more accurate
- Verbose models (GPT-5.4: 5,880 avg chars) may score lower on token F1 but higher on completeness/quality judge scores

This will be tested in Layer 2.

---

## Raw Data Locations

- F1 scored results: `~/Desktop/Kiro/FHIR-UK/results/layer1_{model}_1800_scored.json`
- F1 summary: `~/Desktop/Kiro/FHIR-UK/results/layer1_f1_summary.json`
- All to be published to Zenodo at end of project

---

## Next Steps

1. Layer 2 LLM-as-Judge scoring (4-dimension rubric: accuracy, completeness, safety, relevance)
2. Cross-judging protocol (Claude judges others, Qwen judges Claude)
3. Statistical analysis (Kruskal-Wallis, Wilcoxon, effect sizes — patient-level aggregation from day 1)
4. Compare relative rankings between L1 and L2 (ranking reversal replication?)

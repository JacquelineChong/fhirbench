# 3. Experimental Protocol

## 3.1 Models Under Evaluation

Five large language models were evaluated, representing the major architecture families available through AWS Bedrock as of July 2026:

| Model | Parameters | API | Cost/prompt | Context Window |
|-------|:----------:|-----|:-----------:|:--------------:|
| Claude Sonnet 4.5 | Undisclosed | Bedrock Converse | $0.032 | 200K tokens |
| GPT-5.4 | Undisclosed | Bedrock Mantle (OpenAI) | $0.028 | 128K tokens |
| DeepSeek V3.2 | 671B MoE | Bedrock Converse | $0.005 | 128K tokens |
| Qwen3 32B | 32B | Bedrock Converse | $0.002 | 32K tokens |
| Llama 3.3 70B | 70B | Bedrock Converse | $0.003 | 128K tokens |

All models were accessed via AWS Bedrock with the following shared configuration:
- `temperature`: 0.0 (deterministic generation for reproducibility)
- `max_tokens`: 4096 (output)
- `read_timeout`: 600 seconds (extended from 60s default to prevent Llama timeouts—see §4.7 of Paper 1)
- `region`: us-east-1 (primary), us-east-2 (GPT-5.4 Mantle endpoint)
- Concurrency: 5 workers per model

GPT-5.4 was accessed via AWS Bedrock's Mantle integration (OpenAI Responses API). All other models used the standard Bedrock Converse API. No system prompts were used; all instructions were provided in the user message.

## 3.2 Prompt Generation

The full evaluation matrix is:

```
100 patients × 6 serialisers × 3 tasks = 1,800 prompts per model
1,800 prompts × 5 models = 9,000 total Layer 1 evaluations
9,000 responses × 1 judge each = 9,000 Layer 2 judgments
```

Each prompt is constructed by:
1. Loading the patient FHIR Bundle JSON
2. Applying the specified serialiser to produce a text representation
3. Inserting the serialised text into the task-specific prompt template
4. Recording metadata (patient_id, serialiser, task, timestamp)

Prompts are generated deterministically from the evaluation cohort using `generate_prompts.py`. The prompt set is fixed across all models—each model receives identical prompts for fair comparison.

Prompt identifiers follow the pattern: `{patient_id}__{serialiser}__{task}` (e.g., `patient_diabetes_complex_0059__narrative__clinical_reasoning`).

## 3.3 Layer 1 Execution

Each model processes all 1,800 prompts sequentially within a concurrent worker pool (5 workers). For each prompt, the following are recorded:

- `response`: Full model response text
- `input_tokens`: Number of input tokens (from API response metadata)
- `output_tokens`: Number of output tokens
- `latency_ms`: End-to-end API call latency in milliseconds
- `success`: Boolean indicating successful completion (no timeout, no error)
- `error`: Error message if failed (null otherwise)

Failed prompts (timeout, throttling, malformed response) are retried once with exponential backoff (base 30 seconds). Prompts that fail twice are recorded with `success: false` and `response: null`.

Results are saved as `layer1_{model}_1800.json` containing all 1,800 prompt-response records.

### Success Rates

All five models achieved ≥99.8% success rate across both cohorts:
- Claude: 1800/1800 (100%)
- GPT-5.4: 1800/1800 (100%)
- DeepSeek: 1800/1800 (100%)
- Qwen: 1797/1800 (99.8%)
- Llama: 1800/1800 (100%)

The three Qwen failures were `ThrottlingException` errors that persisted through retry.

## 3.4 Layer 1 Scoring

Token-level F1 scoring is performed by `score_layer1_f1.py`:

1. For each scored prompt, the patient's FHIR Bundle is loaded from the evaluation cohort directory.
2. Ground truth text is extracted based on task type:
   - **clinical_qa**: NHS Number, condition codes/displays, medication codes/displays, latest HbA1c value, GP practice name.
   - **clinical_reasoning**: All medication names/codes, all observation values/dates, all condition names.
   - **clinical_summarization**: All of the above plus patient name, demographics, and GP practice.
3. Both response and ground truth are tokenised: lowercased, split on `[^a-z0-9]`, filtered to remove stopwords (110 common English words plus clinical stop phrases) and tokens shorter than 2 characters.
4. Precision = |response ∩ truth| / |response|
5. Recall = |response ∩ truth| / |truth|
6. F1 = 2 × precision × recall / (precision + recall)

Scored results are saved as `layer1_{model}_1800_scored.json` with per-prompt `f1_score`, `precision`, `recall`, and `ground_truth_tokens` count appended to each record.

## 3.5 Layer 2 Execution

The cross-judging protocol (§2.4.2) is executed by `run_layer2_judge.py`:

1. Load all Layer 1 scored results for the target model.
2. For each prompt-response pair, construct a judge prompt containing:
   - The original clinical question (task prompt without serialised data)
   - The model's complete response
   - The 4-dimension scoring rubric with anchor descriptions
3. Send the judge prompt to the assigned judge model.
4. Parse the judge's JSON response to extract integer scores (0–5) for each dimension.
5. Record all metadata: prompt_id, patient_id, serialiser, task, target_model, judge_model, four dimension scores, judge token usage, judge latency.

Judge responses that cannot be parsed as valid JSON (scores outside 0–5 range, missing dimensions) are retried once. Persistent parse failures are recorded with `success: false`.

## 3.6 Perturbation Protocol

The perturbation experiment applies clinically realistic data noise to the evaluation cohort, simulating the quality issues characteristic of production NHS records. The perturbed cohort is generated by `perturb_cohort.py` with fixed random seed (42) for reproducibility.

### Perturbation Types

Eight perturbation types were implemented, drawn from documented NHS data quality issues:

1. **Duplicate MedicationRequests** (applied to 34/100 patients): Simulates GP system renewal duplicates where the same medication appears as multiple active requests with slightly different `authoredOn` dates.

2. **Legacy Read codes** (21/100): Adds Read v2 code codings alongside existing SNOMED CT codings in Condition resources, simulating records migrated from legacy GP systems (EMIS, Vision) that retain historical coding.

3. **Missing observation units** (47/100): Removes `valueQuantity.unit` and `valueQuantity.system` from selected Observation resources, simulating incomplete data entry where numeric values are recorded without explicit units.

4. **Free-text abbreviated clinical notes** (33/100): Adds abbreviated clinical note extensions (e.g., "Pt c/o SOB on exertion, ?COPD, Rx salbutamol inh PRN") using standard NHS clinical abbreviations.

5. **Mixed date formats** (25/100): Alters date representations in narrative text to use mixed formats (DD/MM/YYYY, D-Mon-YY, "15th March 2024") whilst preserving ISO 8601 in structured fields.

6. **Incomplete medication histories** (39/100): Sets `status: "entered-in-error"` on selected historical MedicationRequest resources and removes `dosageInstruction`, simulating the common NHS pattern of medications marked as errors during reconciliation.

7. **Contradictory entries** (39/100): Adds `abatementDateTime` to Conditions that retain `clinicalStatus: active`, creating logically contradictory records that real NHS systems frequently contain.

8. **Variable terminology** (38/100): Replaces standard SNOMED display terms with common clinical variations (e.g., "T2DM" for "Type 2 diabetes mellitus", "AF" for "Atrial fibrillation"), simulating inconsistent display text in practice records.

### Perturbation Intensity

The number of perturbations applied per patient scales with complexity:
- Simple: 1–2 perturbations
- Moderate: 2–3 perturbations
- Complex: 3–4 perturbations
- Highly complex: 4–5 perturbations

Perturbation types are selected randomly (uniform without replacement per patient). The perturbed cohort thus contains the same clinical information as the clean cohort but with realistic noise patterns overlaid.

### Perturbed Evaluation

The perturbed cohort undergoes the identical evaluation pipeline:
1. Prompt generation using the same 6 serialisers × 3 tasks matrix (1,800 prompts per model)
2. Layer 1 execution across all 5 models (9,000 responses)
3. Layer 1 F1 scoring against the **perturbed** bundles (ground truth extracted from perturbed data)
4. Layer 2 judging using the same cross-judge protocol (9,000 judgments)

Scoring the perturbed cohort against perturbed ground truth ensures that F1 measures the model's ability to extract information from noisy data, not its ability to "correct" perturbations.

## 3.7 Reproducibility

All code, data, and configuration are available in the project repository:

- `code/generate_uk_patients.py`: Patient bundle generation
- `code/validate_uk_core.py`: UK Core conformance validation
- `code/stratify_cohort.py`: Stratified sampling
- `code/generate_prompts.py`: Prompt matrix generation
- `code/serializers/`: Six serialiser implementations
- `code/run_benchmark_layer1.py`: Layer 1 model evaluation
- `code/score_layer1_f1.py`: Token-level F1 scoring
- `code/run_layer2_judge.py`: Layer 2 judge evaluation
- `code/perturb_cohort.py`: Perturbation generation
- `data/evaluation_cohort/`: 100 clean patient bundles
- `data/evaluation_cohort_perturbed/`: 100 perturbed patient bundles
- `data/perturbation_manifest.json`: Full perturbation audit trail
- `results/`: All scored output files

Random seeds are fixed at 42 for all stochastic operations (stratification, perturbation selection). Model temperature is 0.0 throughout. The only source of non-determinism is API-level variation in model responses at temperature 0 (which cloud providers document as occasionally producing minor token-level differences across calls).

## 3.8 Ethical Considerations

All patient data is fully synthetic. No real patient records were used at any stage. Generated bundles use fictitious names, addresses, and NHS Numbers that do not correspond to real individuals. NHS Numbers were generated to pass Modulus 11 validation but are drawn from number ranges not allocated to real patients. The study did not require ethics committee approval as it involves no human participants or real patient data.

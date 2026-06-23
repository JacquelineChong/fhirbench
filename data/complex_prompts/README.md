# FHIRBench Complex Patient Prompts

630 self-contained prompts for evaluating LLM clinical reasoning on FHIR data.

## Structure

- `part_01.json` through `part_10.json`: Split prompt files (63 prompts each)
- Each prompt contains the full serialized FHIR data + task question + ground truth

## Dimensions

| Dimension | Values |
|-----------|--------|
| Patients | 35 (COMPLEX + HIGHLY_COMPLEX) |
| Serializers | raw_json, key_value, narrative, markdown_table, condensed, fhir_path |
| Tasks | clinical_qa, clinical_reasoning, clinical_summarization |
| Domains | diabetes (8), cardiovascular (10), medication_interactions (5), preventive_care (12) |

## Usage

```bash
# Concatenate parts
python3 -c "
import json, glob
parts = sorted(glob.glob('data/complex_prompts/part_*.json'))
prompts = []
for p in parts:
    prompts.extend(json.load(open(p)))
json.dump(prompts, open('complex_prompts_630.json', 'w'))
print(f'Combined {len(prompts)} prompts')
"

# Run evaluation
python3 code/run_bedrock_standalone.py
```

## Prompt Schema

```json
{
  "patient_id": "PAT-XXXX",
  "domain": "diabetes|cardiovascular|medication_interactions|preventive_care",
  "complexity": "COMPLEX|HIGHLY_COMPLEX",
  "task": "clinical_qa|clinical_reasoning|clinical_summarization",
  "task_subtype": "...",
  "serializer": "raw_json|key_value|narrative|markdown_table|condensed|fhir_path",
  "ground_truth": "expected answer",
  "system_prompt": "...",
  "user_prompt": "full prompt with serialized FHIR data + question"
}
```

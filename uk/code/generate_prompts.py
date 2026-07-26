#!/usr/bin/env python3
"""
generate_prompts.py

Generates evaluation prompts by combining:
- 100 patient files × 6 serialisers × 3 clinical tasks = 1,800 prompts

Each prompt pairs a serialised patient representation with a clinical task question.
"""

import argparse
import json
import os
import sys
import traceback
from datetime import datetime

# Add parent directory to path for serializer imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from serializers.raw_json import RawJsonSerializer
from serializers.flattened_kv import FlattenedKVSerializer
from serializers.narrative import NarrativeSerializer
from serializers.clinical_template import ClinicalTemplateSerializer
from serializers.structured_markdown import StructuredMarkdownSerializer
from serializers.hybrid_adaptive import HybridAdaptiveSerializer


# ============================================================================
# Clinical Task Prompt Templates (UK Context)
# ============================================================================

CLINICAL_QA_TEMPLATE = """Based on the following patient record, answer these clinical questions:
1. What is the patient's NHS Number?
2. What are the patient's active conditions (with SNOMED CT UK codes)?
3. What medications are currently prescribed (with dm+d codes)?
4. What is the most recent HbA1c result (in mmol/mol)?
5. Who is the patient's registered GP practice?

Patient Record:
{serialised_data}"""

CLINICAL_REASONING_TEMPLATE = """Based on the following patient record, provide clinical reasoning:
1. Identify any potential drug interactions or contraindications.
2. Based on the latest observations, are there any concerning trends?
3. What clinical actions would you recommend as next steps?
4. Are there any gaps in the patient's care plan?

Patient Record:
{serialised_data}"""

CLINICAL_SUMMARIZATION_TEMPLATE = """Based on the following patient record, produce a comprehensive clinical summary suitable for a GP referral letter. Include:
1. Patient demographics and NHS Number
2. Presenting conditions with SNOMED CT codes
3. Current medication list with dm+d codes and dosages
4. Recent investigation results (labs, observations) with trends
5. Relevant social and family history
6. Current care plan and outstanding actions
7. Reason for referral and clinical urgency

Use standard NHS clinical letter format.

Patient Record:
{serialised_data}"""

TASK_TEMPLATES = {
    "clinical_qa": CLINICAL_QA_TEMPLATE,
    "clinical_reasoning": CLINICAL_REASONING_TEMPLATE,
    "clinical_summarization": CLINICAL_SUMMARIZATION_TEMPLATE,
}


# ============================================================================
# Serialiser Configuration
# ============================================================================

def get_serializers():
    """Instantiate all 6 serialisers."""
    return {
        "raw_json": RawJsonSerializer(),
        "flattened_kv": FlattenedKVSerializer(),
        "narrative": NarrativeSerializer(),
        "clinical_template": ClinicalTemplateSerializer(template="soap"),
        "structured_markdown": StructuredMarkdownSerializer(),
        "hybrid_adaptive": HybridAdaptiveSerializer(),
    }


def serialize_bundle(serializer, bundle: dict, serializer_name: str, task_type: str) -> str:
    """
    Serialize a bundle using the given serializer.
    Handles hybrid_adaptive's task_type parameter specially.
    """
    if serializer_name == "hybrid_adaptive":
        return serializer.serialize_bundle(bundle, task_type=task_type)
    else:
        return serializer.serialize_bundle(bundle)


def main():
    parser = argparse.ArgumentParser(
        description="Generate evaluation prompts from FHIR bundles × serialisers × clinical tasks."
    )
    parser.add_argument(
        "--input-dir",
        default="../data/evaluation_cohort/",
        help="Directory containing the 100 evaluation cohort JSON files"
    )
    parser.add_argument(
        "--output-dir",
        default="../data/prompts/",
        help="Directory to save generated prompts"
    )
    args = parser.parse_args()

    input_dir = os.path.expanduser(args.input_dir)
    output_dir = os.path.expanduser(args.output_dir)

    if not os.path.isdir(input_dir):
        print(f"ERROR: Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    # Collect patient files (exclude manifest.json)
    patient_files = sorted([
        f for f in os.listdir(input_dir)
        if f.lower().endswith('.json') and f != 'manifest.json'
    ])

    print(f"Found {len(patient_files)} patient files in {input_dir}")

    # Initialize serialisers
    serializers = get_serializers()
    serializer_names = list(serializers.keys())
    task_names = list(TASK_TEMPLATES.keys())

    expected_total = len(patient_files) * len(serializer_names) * len(task_names)
    print(f"Generating {len(patient_files)} × {len(serializer_names)} serialisers × {len(task_names)} tasks = {expected_total} prompts")
    print()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Generate prompts
    all_prompts = []
    errors = []
    generated = 0

    for file_idx, filename in enumerate(patient_files):
        filepath = os.path.join(input_dir, filename)

        # Load bundle
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                bundle = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            errors.append({"file": filename, "error": f"File read error: {e}"})
            continue

        # Extract patient ID from filename (without .json)
        patient_id = filename.replace('.json', '')

        for ser_name in serializer_names:
            serializer = serializers[ser_name]

            for task_name in task_names:
                try:
                    # Serialize the bundle
                    serialised_data = serialize_bundle(
                        serializer, bundle, ser_name, task_name
                    )

                    # Generate prompt from template
                    prompt_text = TASK_TEMPLATES[task_name].format(
                        serialised_data=serialised_data
                    )

                    # Create prompt record
                    prompt_record = {
                        "prompt_id": f"{patient_id}__{ser_name}__{task_name}",
                        "patient_file": filename,
                        "patient_id": patient_id,
                        "serializer": ser_name,
                        "task": task_name,
                        "prompt": prompt_text,
                        "serialised_length": len(serialised_data),
                        "prompt_length": len(prompt_text),
                    }

                    all_prompts.append(prompt_record)
                    generated += 1

                except Exception as e:
                    error_detail = {
                        "file": filename,
                        "serializer": ser_name,
                        "task": task_name,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                    errors.append(error_detail)

        # Progress
        if (file_idx + 1) % 10 == 0:
            print(f"  Processed {file_idx + 1}/{len(patient_files)} patients ({generated} prompts generated)...")

    # Save all prompts as a single JSON file
    prompts_output_path = os.path.join(output_dir, "all_prompts.json")
    with open(prompts_output_path, 'w', encoding='utf-8') as f:
        json.dump(all_prompts, f, indent=2, ensure_ascii=False)
        f.write('\n')

    # Save prompts grouped by task (for easier evaluation)
    for task_name in task_names:
        task_prompts = [p for p in all_prompts if p["task"] == task_name]
        task_path = os.path.join(output_dir, f"prompts_{task_name}.json")
        with open(task_path, 'w', encoding='utf-8') as f:
            json.dump(task_prompts, f, indent=2, ensure_ascii=False)
            f.write('\n')

    # Save prompts grouped by serializer (for format comparison)
    for ser_name in serializer_names:
        ser_prompts = [p for p in all_prompts if p["serializer"] == ser_name]
        ser_path = os.path.join(output_dir, f"prompts_{ser_name}.json")
        with open(ser_path, 'w', encoding='utf-8') as f:
            json.dump(ser_prompts, f, indent=2, ensure_ascii=False)
            f.write('\n')

    # Save errors if any
    if errors:
        errors_path = os.path.join(output_dir, "generation_errors.json")
        with open(errors_path, 'w', encoding='utf-8') as f:
            json.dump(errors, f, indent=2, ensure_ascii=False)
            f.write('\n')

    # Save manifest/metadata
    # Compute stats
    length_stats = {}
    for ser_name in serializer_names:
        ser_prompts = [p for p in all_prompts if p["serializer"] == ser_name]
        if ser_prompts:
            lengths = [p["serialised_length"] for p in ser_prompts]
            length_stats[ser_name] = {
                "count": len(ser_prompts),
                "avg_serialised_chars": int(sum(lengths) / len(lengths)),
                "min_serialised_chars": min(lengths),
                "max_serialised_chars": max(lengths),
            }

    manifest = {
        "timestamp": datetime.now().isoformat(),
        "input_dir": input_dir,
        "output_dir": output_dir,
        "total_patients": len(patient_files),
        "total_serializers": len(serializer_names),
        "total_tasks": len(task_names),
        "total_prompts_generated": generated,
        "total_prompts_expected": expected_total,
        "total_errors": len(errors),
        "serializers": serializer_names,
        "tasks": task_names,
        "serializer_stats": length_stats,
    }

    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')

    # Print summary
    print()
    print("=" * 70)
    print("PROMPT GENERATION SUMMARY")
    print("=" * 70)
    print(f"\n  Patients processed:    {len(patient_files)}")
    print(f"  Serialisers used:      {len(serializer_names)}")
    print(f"  Clinical tasks:        {len(task_names)}")
    print(f"  Total prompts:         {generated}/{expected_total}")
    print(f"  Errors:                {len(errors)}")

    print(f"\n--- Serialiser Output Stats ---")
    print(f"{'Serialiser':<25} {'Count':>6} {'Avg Chars':>10} {'Min':>8} {'Max':>8}")
    print("-" * 60)
    for ser_name in serializer_names:
        stats = length_stats.get(ser_name, {})
        print(f"{ser_name:<25} {stats.get('count', 0):>6} "
              f"{stats.get('avg_serialised_chars', 0):>10} "
              f"{stats.get('min_serialised_chars', 0):>8} "
              f"{stats.get('max_serialised_chars', 0):>8}")

    print(f"\n--- Output Files ---")
    print(f"  All prompts:           {prompts_output_path}")
    for task_name in task_names:
        print(f"  {task_name}:  {os.path.join(output_dir, f'prompts_{task_name}.json')}")
    for ser_name in serializer_names:
        print(f"  {ser_name}:  {os.path.join(output_dir, f'prompts_{ser_name}.json')}")
    print(f"  Manifest:              {manifest_path}")
    if errors:
        print(f"  Errors:                {os.path.join(output_dir, 'generation_errors.json')}")

    print("=" * 70)

    if errors:
        print(f"\nWARNING: {len(errors)} errors occurred during generation.")
        for e in errors[:5]:
            print(f"  - {e.get('file', 'unknown')}/{e.get('serializer', '?')}/{e.get('task', '?')}: {e.get('error', '')[:80]}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more (see generation_errors.json)")


if __name__ == "__main__":
    main()

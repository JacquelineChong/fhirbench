#!/usr/bin/env python3
"""
FHIRBench Layer 1 Re-run: Claude Sonnet 4.5 + GPT-5.4 on COMPLEX/HIGHLY_COMPLEX cases.
Run this on EC2 instance i-00e7baa3921a62a7c (us-east-2).

Prerequisites:
- FHIR code repo at ~/fhirbench/ (or wherever it's cloned)
- AWS credentials configured with Bedrock access
- Python packages: boto3, pyyaml

Usage:
    cd ~/fhirbench/code  # or wherever the repo is
    python run_rerun_claude_gpt.py
"""

import json, time, sys, os, csv, logging
from pathlib import Path
from collections import defaultdict

import boto3

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ─── Configuration ───────────────────────────────────────────────────────────
MODELS = {
    "claude": {
        "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "region": "us-east-1",
    },
    "gpt54": {
        "model_id": "openai.gpt-5.4",
        "region": "us-east-2",
    },
}

# Only run COMPLEX + HIGHLY_COMPLEX
TARGET_COMPLEXITIES = {"COMPLEX", "HIGHLY_COMPLEX"}

# Serializer name mapping (code names → benchmark result names)
SERIALIZER_MAP = {
    "raw_json": "raw_json",
    "flattened_kv": "key_value",
    "narrative": "narrative",
    "structured_markdown": "markdown_table",
    "clinical_template": "condensed",
    "hybrid_adaptive": "fhir_path",
}

DATA_DIR = Path("data/fhir_bundles")
RESULTS_DIR = Path("results")
MANIFEST = Path("data/manifest_1000.csv")
OUTPUT_FILE = RESULTS_DIR / "layer1_complex_claude_gpt54.json"

MAX_TOKENS = 2048
TEMPERATURE = 0.0
RATE_LIMIT_SLEEP = 0.5  # seconds between calls


# ─── Bedrock Client ──────────────────────────────────────────────────────────
class BedrockCaller:
    def __init__(self, model_id, region):
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=region)

    def invoke(self, system_prompt, user_prompt):
        """Call model via Converse API. Returns response text or error string."""
        try:
            resp = self.client.converse(
                modelId=self.model_id,
                messages=[{"role": "user", "content": [{"text": user_prompt}]}],
                system=[{"text": system_prompt}],
                inferenceConfig={"maxTokens": MAX_TOKENS, "temperature": TEMPERATURE},
            )
            return resp["output"]["message"]["content"][0]["text"]
        except Exception as e:
            return f"ERROR: {e}"


# ─── Serializers ─────────────────────────────────────────────────────────────
sys.path.insert(0, ".")
from serializers import (
    RawJsonSerializer,
    FlattenedKVSerializer,
    NarrativeSerializer,
    StructuredMarkdownSerializer,
    ClinicalTemplateSerializer,
    HybridAdaptiveSerializer,
)

SERIALIZERS = {
    "raw_json": RawJsonSerializer(),
    "flattened_kv": FlattenedKVSerializer(),
    "narrative": NarrativeSerializer(),
    "structured_markdown": StructuredMarkdownSerializer(),
    "clinical_template": ClinicalTemplateSerializer(template="soap"),
    "hybrid_adaptive": HybridAdaptiveSerializer(),
}


# ─── Tasks ───────────────────────────────────────────────────────────────────
from tasks import ClinicalQATask, ClinicalReasoningTask, ClinicalSummarizationTask

TASKS = {
    "clinical_qa": ClinicalQATask(),
    "clinical_reasoning": ClinicalReasoningTask(),
    "clinical_summarization": ClinicalSummarizationTask(),
}

SYSTEM_PROMPT = (
    "You are a clinical data assistant. Answer questions about patient data "
    "precisely and concisely based only on the provided FHIR data."
)


# ─── Main Pipeline ───────────────────────────────────────────────────────────
def get_complex_patients():
    """Read manifest and return list of COMPLEX/HIGHLY_COMPLEX patient IDs with metadata."""
    patients = []
    with open(MANIFEST) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["complexity_level"] in TARGET_COMPLEXITIES:
                patients.append(row)
    return patients


def serialize_bundle(bundle, serializer_name, task_name):
    """Serialize a FHIR bundle using the named serializer."""
    serializer = SERIALIZERS[serializer_name]
    if hasattr(serializer, "serialize_bundle"):
        if serializer_name == "hybrid_adaptive":
            return serializer.serialize_bundle(bundle, task_type=task_name)
        return serializer.serialize_bundle(bundle)
    return serializer.serialize(bundle)


def generate_prompts_for_bundle(bundle, patient_meta):
    """Generate all (serializer × task) prompts for one bundle."""
    prompts = []
    for ser_name in SERIALIZERS:
        for task_name, task in TASKS.items():
            try:
                serialized = serialize_bundle(bundle, ser_name, task_name)
            except Exception as e:
                logger.warning(f"Serialization failed ({ser_name}): {e}")
                continue

            if task_name == "clinical_qa":
                qa_pairs = task.generate_questions(bundle)
                for qa in qa_pairs[:1]:  # 1 question per serializer per patient
                    prompt = (
                        f"Based on the following patient data, answer the question "
                        f"accurately and concisely.\n\n## Patient Data:\n{serialized}"
                        f"\n\nQuestion: {qa['question']}"
                    )
                    prompts.append({
                        "patient_id": patient_meta["patient_id"],
                        "domain": patient_meta.get("domain", "unknown"),
                        "complexity": patient_meta["complexity_level"],
                        "task": task_name,
                        "task_subtype": qa.get("category", "general"),
                        "serializer": SERIALIZER_MAP.get(ser_name, ser_name),
                        "ground_truth": qa["answer"],
                        "system_prompt": SYSTEM_PROMPT,
                        "user_prompt": prompt,
                    })

            elif task_name == "clinical_reasoning":
                reasoning_tasks = task.generate_tasks(bundle)
                for rt in reasoning_tasks[:1]:
                    prompt = (
                        f"Based on the following patient data:\n\n## Patient Data:\n"
                        f"{serialized}\n\n{rt['prompt']}"
                    )
                    prompts.append({
                        "patient_id": patient_meta["patient_id"],
                        "domain": patient_meta.get("domain", "unknown"),
                        "complexity": patient_meta["complexity_level"],
                        "task": task_name,
                        "task_subtype": rt.get("type", "reasoning"),
                        "serializer": SERIALIZER_MAP.get(ser_name, ser_name),
                        "ground_truth": rt.get("expected_answer", ""),
                        "system_prompt": SYSTEM_PROMPT,
                        "user_prompt": prompt,
                    })

            elif task_name == "clinical_summarization":
                sum_tasks = task.generate_tasks(bundle)
                for st in sum_tasks[:1]:
                    prompt = (
                        f"Based on the following patient data:\n\n## Patient Data:\n"
                        f"{serialized}\n\n{st['prompt']}"
                    )
                    prompts.append({
                        "patient_id": patient_meta["patient_id"],
                        "domain": patient_meta.get("domain", "unknown"),
                        "complexity": patient_meta["complexity_level"],
                        "task": task_name,
                        "task_subtype": "summarization",
                        "serializer": SERIALIZER_MAP.get(ser_name, ser_name),
                        "ground_truth": st.get("reference_summary", ""),
                        "system_prompt": SYSTEM_PROMPT,
                        "user_prompt": prompt,
                    })
    return prompts


def main():
    logger.info("=" * 60)
    logger.info("FHIRBench Layer 1 Re-run: Claude + GPT-5.4 (COMPLEX)")
    logger.info("=" * 60)

    # 1. Get COMPLEX/HIGHLY_COMPLEX patients
    patients = get_complex_patients()
    logger.info(f"Found {len(patients)} COMPLEX/HIGHLY_COMPLEX patients")

    # 2. Generate all prompts
    all_prompts = []
    skipped = 0
    for pat in patients:
        bundle_path = DATA_DIR / f"{pat['patient_id']}.json"
        if not bundle_path.exists():
            logger.warning(f"Bundle not found: {bundle_path}")
            skipped += 1
            continue
        with open(bundle_path) as f:
            bundle = json.load(f)
        prompts = generate_prompts_for_bundle(bundle, pat)
        all_prompts.extend(prompts)

    logger.info(f"Generated {len(all_prompts)} prompts ({skipped} patients skipped)")
    logger.info(f"Expected: ~{len(patients) * 18} (patients × 6 serializers × 3 tasks)")

    # 3. Run each model
    results = []
    for model_name, model_cfg in MODELS.items():
        logger.info(f"\n{'='*40}")
        logger.info(f"Running {model_name} ({model_cfg['model_id']})")
        logger.info(f"Region: {model_cfg['region']}")
        logger.info(f"{'='*40}")

        caller = BedrockCaller(model_cfg["model_id"], model_cfg["region"])
        successes = 0
        errors = 0
        start_time = time.time()

        for i, prompt_data in enumerate(all_prompts):
            response = caller.invoke(prompt_data["system_prompt"], prompt_data["user_prompt"])

            is_error = response.startswith("ERROR:")
            results.append({
                "patient_id": prompt_data["patient_id"],
                "domain": prompt_data["domain"],
                "complexity": prompt_data["complexity"],
                "task": prompt_data["task"],
                "task_subtype": prompt_data["task_subtype"],
                "serializer": prompt_data["serializer"],
                "model": model_cfg["model_id"],
                "ground_truth": prompt_data["ground_truth"],
                "response": None if is_error else response,
                "status": response if is_error else "success",
            })

            if is_error:
                errors += 1
                if errors <= 5:
                    logger.error(f"  Error [{i}]: {response[:100]}")
            else:
                successes += 1

            if (i + 1) % 50 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                eta = (len(all_prompts) - i - 1) / rate / 60
                logger.info(
                    f"  [{model_name}] {i+1}/{len(all_prompts)} "
                    f"({successes} ok, {errors} err) "
                    f"{rate:.1f} req/s, ETA {eta:.0f}min"
                )

            # Checkpoint every 200 entries
            if (i + 1) % 200 == 0:
                checkpoint_file = RESULTS_DIR / f"checkpoint_{model_name}.json"
                with open(checkpoint_file, "w") as f:
                    json.dump(results, f)
                logger.info(f"  Checkpoint saved: {checkpoint_file}")

            time.sleep(RATE_LIMIT_SLEEP)

        elapsed = time.time() - start_time
        logger.info(
            f"  {model_name} complete: {successes}/{len(all_prompts)} success "
            f"in {elapsed/60:.1f}min"
        )

    # 4. Save final results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"\n{'='*60}")
    logger.info(f"DONE! Results saved to {OUTPUT_FILE}")
    logger.info(f"Total entries: {len(results)}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()

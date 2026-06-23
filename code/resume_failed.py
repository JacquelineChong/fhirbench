#!/usr/bin/env python3
"""
Resume script: retries only FAILED prompts from layer1_complex_claude_gpt54.json.
Reads existing results, identifies failures, re-runs them, and merges back.

Usage:
    python3 code/resume_failed.py
"""
import json, time, boto3, logging
from botocore.config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MODELS = {
    "claude": {"model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0", "region": "us-east-2"},
    "gpt54": {"model_id": "openai.gpt-5.4", "region": "us-east-2"},
}

PROMPTS_FILE = "complex_prompts_630.json"
OUTPUT_FILE = "layer1_complex_claude_gpt54.json"
MAX_TOKENS = 2048
TEMPERATURE = 0.0
RATE_LIMIT_SLEEP = 0.5
CLIENT_CONFIG = Config(read_timeout=60, connect_timeout=10, retries={"max_attempts": 3})


def call_bedrock(client, model_id, system_prompt, user_prompt):
    try:
        resp = client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": user_prompt}]}],
            system=[{"text": system_prompt}],
            inferenceConfig={"maxTokens": MAX_TOKENS, "temperature": TEMPERATURE},
        )
        return resp["output"]["message"]["content"][0]["text"], None
    except Exception as e:
        return None, str(e)


def main():
    # Load existing results
    with open(OUTPUT_FILE) as f:
        results = json.load(f)
    logger.info(f"Loaded {len(results)} existing results")

    # Load prompts
    with open(PROMPTS_FILE) as f:
        prompts = json.load(f)
    logger.info(f"Loaded {len(prompts)} prompts")

    # Identify failed entries and their indices
    failed_indices = []
    for i, r in enumerate(results):
        if r["status"] != "success":
            failed_indices.append(i)
    logger.info(f"Found {len(failed_indices)} failed entries to retry")

    # Also identify prompts not yet attempted (GPT-5.4 only ran 140/630)
    claude_count = sum(1 for r in results if r["model"] == MODELS["claude"]["model_id"])
    gpt54_count = sum(1 for r in results if r["model"] == MODELS["gpt54"]["model_id"])
    logger.info(f"Claude: {claude_count}/630, GPT-5.4: {gpt54_count}/630")

    # Retry failed entries
    if failed_indices:
        logger.info(f"\n=== Retrying {len(failed_indices)} failed entries ===")
        clients = {}
        for model_name, cfg in MODELS.items():
            clients[cfg["model_id"]] = boto3.client(
                "bedrock-runtime", region_name=cfg["region"], config=CLIENT_CONFIG
            )

        retried_ok = 0
        retried_fail = 0
        for idx in failed_indices:
            r = results[idx]
            model_id = r["model"]
            client = clients[model_id]

            # Find matching prompt
            matching = [p for p in prompts if p["patient_id"] == r["patient_id"]
                       and p["serializer"] == r["serializer"]
                       and p["task"] == r["task"]
                       and p["task_subtype"] == r["task_subtype"]]
            if not matching:
                logger.warning(f"  Could not find prompt for index {idx}, skipping")
                continue

            p = matching[0]
            model_short = "claude" if "anthropic" in model_id else "gpt54"
            logger.info(f"  [{model_short}] Retrying index {idx}...")

            response, error = call_bedrock(client, model_id, p["system_prompt"], p["user_prompt"])
            if response:
                results[idx]["response"] = response
                results[idx]["status"] = "success"
                retried_ok += 1
                logger.info(f"  [{model_short}] Index {idx} OK")
            else:
                results[idx]["status"] = f"ERROR: {error}"
                retried_fail += 1
                logger.info(f"  [{model_short}] Index {idx} FAILED: {error}")

            time.sleep(RATE_LIMIT_SLEEP)

            # Save incrementally
            with open(OUTPUT_FILE, "w") as f:
                json.dump(results, f, indent=2)

        logger.info(f"  Retry results: {retried_ok} ok, {retried_fail} failed")

    # Run remaining GPT-5.4 prompts (if less than 630 attempted)
    if gpt54_count < 630:
        remaining_start = gpt54_count
        logger.info(f"\n=== Running remaining GPT-5.4 prompts ({remaining_start+1} to 630) ===")
        cfg = MODELS["gpt54"]
        client = boto3.client("bedrock-runtime", region_name=cfg["region"], config=CLIENT_CONFIG)
        ok, err = 0, 0
        t0 = time.time()

        for i in range(remaining_start, 630):
            p = prompts[i]
            logger.info(f"  [gpt54] Calling prompt {i+1}/630...")
            response, error = call_bedrock(client, cfg["model_id"], p["system_prompt"], p["user_prompt"])
            results.append({
                "patient_id": p["patient_id"],
                "domain": p["domain"],
                "complexity": p["complexity"],
                "task": p["task"],
                "task_subtype": p["task_subtype"],
                "serializer": p["serializer"],
                "model": cfg["model_id"],
                "ground_truth": p["ground_truth"],
                "response": response,
                "status": "success" if response else f"ERROR: {error}",
            })
            if response:
                ok += 1
            else:
                err += 1
            logger.info(f"  [gpt54] Prompt {i+1} {'OK' if response else 'FAILED'}")

            # Save incrementally
            with open(OUTPUT_FILE, "w") as f:
                json.dump(results, f, indent=2)

            if (i + 1) % 50 == 0:
                elapsed = time.time() - t0
                done = i - remaining_start + 1
                logger.info(f"  [gpt54] {i+1}/630 ({ok} ok, {err} err) ETA {(630-i-1)*(elapsed/done)/60:.0f}min")

            time.sleep(RATE_LIMIT_SLEEP)

        logger.info(f"  GPT-5.4 remaining: {ok}/{630-remaining_start} success in {(time.time()-t0)/60:.1f}min")

    # Final save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    total_ok = sum(1 for r in results if r["status"] == "success")
    logger.info(f"\nDONE! {len(results)} total, {total_ok} success, {len(results)-total_ok} failed")
    logger.info(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

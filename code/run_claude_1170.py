#!/usr/bin/env python3
"""
Run Claude Sonnet 4.5 on 1,170 SIMPLE+MODERATE prompts via Bedrock Converse API.
Run on EC2 (us-east-2) to bypass geo-block.

Usage on EC2:
    aws s3 cp s3://fhirbench-temp-chongaws/simple_moderate_prompts_1170.json /tmp/simple_moderate_prompts_1170.json --region us-east-2
    python3 run_claude_1170.py
"""
import json, time, boto3, logging
from botocore.config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
REGION = "us-east-2"
PROMPTS_FILE = "/tmp/simple_moderate_prompts_1170.json"
OUTPUT_FILE = "/tmp/layer1_claude_1170.json"
MAX_TOKENS = 2048
TEMPERATURE = 0.0
RATE_LIMIT_SLEEP = 0.5
CLIENT_CONFIG = Config(read_timeout=60, connect_timeout=10, retries={"max_attempts": 3})


def main():
    with open(PROMPTS_FILE) as f:
        prompts = json.load(f)
    logger.info(f"Loaded {len(prompts)} prompts")

    client = boto3.client("bedrock-runtime", region_name=REGION, config=CLIENT_CONFIG)
    results = []
    ok, err = 0, 0
    t0 = time.time()

    for i, p in enumerate(prompts):
        logger.info(f"  [claude] Calling prompt {i+1}/{len(prompts)}...")
        try:
            resp = client.converse(
                modelId=MODEL_ID,
                messages=[{"role": "user", "content": [{"text": p["user_prompt"]}]}],
                system=[{"text": p["system_prompt"]}],
                inferenceConfig={"maxTokens": MAX_TOKENS, "temperature": TEMPERATURE},
            )
            response = resp["output"]["message"]["content"][0]["text"]
            results.append({
                "patient_id": p["patient_id"], "domain": p["domain"],
                "complexity": p["complexity"], "task": p["task"],
                "task_subtype": p["task_subtype"], "serializer": p["serializer"],
                "model": MODEL_ID, "ground_truth": p["ground_truth"],
                "response": response, "status": "success",
            })
            ok += 1
            logger.info(f"  [claude] Prompt {i+1} OK")
        except Exception as e:
            results.append({
                "patient_id": p["patient_id"], "domain": p["domain"],
                "complexity": p["complexity"], "task": p["task"],
                "task_subtype": p["task_subtype"], "serializer": p["serializer"],
                "model": MODEL_ID, "ground_truth": p["ground_truth"],
                "response": None, "status": f"error: {e}",
            })
            err += 1
            logger.info(f"  [claude] Prompt {i+1} FAILED: {e}")

        with open(OUTPUT_FILE, "w") as f:
            json.dump(results, f, indent=2)

        if (i + 1) % 50 == 0:
            elapsed = time.time() - t0
            eta = (len(prompts) - i - 1) * (elapsed / (i + 1)) / 60
            logger.info(f"  [claude] {i+1}/{len(prompts)} ({ok} ok, {err} err) ETA {eta:.0f}min")

        time.sleep(RATE_LIMIT_SLEEP)

    logger.info(f"Done: {ok}/{len(prompts)} success in {(time.time()-t0)/60:.1f}min")
    logger.info(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

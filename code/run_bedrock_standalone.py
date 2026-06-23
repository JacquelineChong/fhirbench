#!/usr/bin/env python3
"""
Self-contained Bedrock runner. Downloads prompts.json and calls Claude + GPT-5.4.
No local dependencies needed beyond boto3.

IMPORTANT: Run this on EC2 in us-east-2. Both models use us-east-2.

Usage:
    python3 run_bedrock_standalone.py
"""
import json, time, boto3, logging, os
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

CLIENT_CONFIG = Config(read_timeout=60, connect_timeout=10)

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
    with open(PROMPTS_FILE) as f:
        prompts = json.load(f)
    logger.info(f"Loaded {len(prompts)} prompts")

    results = []
    for model_name, cfg in MODELS.items():
        logger.info(f"Running {model_name} ({cfg['model_id']}) in {cfg['region']}")
        client = boto3.client("bedrock-runtime", region_name=cfg["region"], config=CLIENT_CONFIG)
        ok, err = 0, 0
        t0 = time.time()

        for i, p in enumerate(prompts):
            logger.info(f"  [{model_name}] Calling prompt {i+1}/{len(prompts)}...")
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
            if response: ok += 1
            else: err += 1
            logger.info(f"  [{model_name}] Prompt {i+1} {'OK' if response else 'FAILED'}")

            # Incremental write after every prompt
            with open(OUTPUT_FILE, "w") as f:
                json.dump(results, f, indent=2)

            if (i+1) % 50 == 0:
                elapsed = time.time() - t0
                logger.info(f"  [{model_name}] {i+1}/{len(prompts)} ({ok} ok, {err} err) ETA {(len(prompts)-i-1)*(elapsed/(i+1))/60:.0f}min")

            time.sleep(RATE_LIMIT_SLEEP)

        logger.info(f"  {model_name}: {ok}/{len(prompts)} success in {(time.time()-t0)/60:.1f}min")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"DONE! {len(results)} results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

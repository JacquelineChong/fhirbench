#!/usr/bin/env python3
"""
Run GPT-5.4 on 1,170 SIMPLE+MODERATE prompts via Bedrock Mantle endpoint.
Run on EC2 (us-east-2) to bypass geo-block.

Usage on EC2:
    aws s3 cp s3://fhirbench-temp-chongaws/simple_moderate_prompts_1170.json /tmp/simple_moderate_prompts_1170.json --region us-east-2
    python3 run_gpt54_mantle_1170.py
"""
import json, time, logging, urllib.request, urllib.error
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MANTLE_ENDPOINT = "https://bedrock-mantle.us-east-2.api.aws/openai/v1/responses"
MODEL_ID = "openai.gpt-5.4"
REGION = "us-east-2"
SERVICE = "bedrock"
PROMPTS_FILE = "/tmp/simple_moderate_prompts_1170.json"
OUTPUT_FILE = "/tmp/layer1_gpt54_1170.json"
MAX_TOKENS = 2048
TEMPERATURE = 0.0
RATE_LIMIT_SLEEP = 0.5


def get_sigv4_headers(url, body, region, service):
    session = boto3.Session()
    credentials = session.get_credentials()
    creds = credentials.get_frozen_credentials()
    request = AWSRequest(method="POST", url=url, data=body, headers={"Content-Type": "application/json"})
    SigV4Auth(creds, service, region).add_auth(request)
    return dict(request.headers)


def call_gpt54(system_prompt, user_prompt):
    body = json.dumps({
        "model": MODEL_ID,
        "input": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": TEMPERATURE,
        "max_output_tokens": MAX_TOKENS,
    })
    headers = get_sigv4_headers(MANTLE_ENDPOINT, body, REGION, SERVICE)
    req = urllib.request.Request(MANTLE_ENDPOINT, data=body.encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            output = result.get("output", [])
            for item in output:
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            return content["text"], None
            choices = result.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", ""), None
            return None, f"Unexpected response: {json.dumps(result)[:200]}"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        return None, f"HTTP {e.code}: {error_body[:200]}"
    except Exception as e:
        return None, str(e)


def main():
    with open(PROMPTS_FILE) as f:
        prompts = json.load(f)
    logger.info(f"Loaded {len(prompts)} prompts")

    # Test access first
    logger.info("Testing GPT-5.4 via Mantle...")
    test_resp, test_err = call_gpt54("You are helpful.", "Say hello.")
    if test_resp:
        logger.info(f"Test SUCCESS: {test_resp[:30]}")
    else:
        logger.error(f"Test FAILED: {test_err}")
        return

    results = []
    ok, err = 0, 0
    t0 = time.time()

    for i, p in enumerate(prompts):
        logger.info(f"  [gpt54] Calling prompt {i+1}/{len(prompts)}...")
        response, error = call_gpt54(p["system_prompt"], p["user_prompt"])
        results.append({
            "patient_id": p["patient_id"], "domain": p["domain"],
            "complexity": p["complexity"], "task": p["task"],
            "task_subtype": p["task_subtype"], "serializer": p["serializer"],
            "model": MODEL_ID, "ground_truth": p["ground_truth"],
            "response": response, "status": "success" if response else f"error: {error}",
        })
        if response:
            ok += 1
            logger.info(f"  [gpt54] Prompt {i+1} OK")
        else:
            err += 1
            logger.info(f"  [gpt54] Prompt {i+1} FAILED: {error[:80]}")

        with open(OUTPUT_FILE, "w") as f:
            json.dump(results, f, indent=2)

        if (i + 1) % 50 == 0:
            elapsed = time.time() - t0
            eta = (len(prompts) - i - 1) * (elapsed / (i + 1)) / 60
            logger.info(f"  [gpt54] {i+1}/{len(prompts)} ({ok} ok, {err} err) ETA {eta:.0f}min")

        time.sleep(RATE_LIMIT_SLEEP)

    logger.info(f"Done: {ok}/{len(prompts)} success in {(time.time()-t0)/60:.1f}min")
    logger.info(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

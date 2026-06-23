#!/usr/bin/env python3
"""
GPT-5.4 runner using Bedrock Mantle endpoint (OpenAI Responses API format).
The Converse API does NOT support openai.gpt-5.4 — must use Mantle.

Endpoint: https://bedrock-mantle.us-east-2.api.aws/openai/v1/responses
Auth: SigV4 (service: bedrock)
Region: us-east-2

Usage:
    python3 code/run_gpt54_mantle.py
"""
import json, time, logging, os
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.config import Config
import urllib.request
import urllib.error

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MANTLE_ENDPOINT = "https://bedrock-mantle.us-east-2.api.aws/openai/v1/responses"
MODEL_ID = "openai.gpt-5.4"
REGION = "us-east-2"
SERVICE = "bedrock"

PROMPTS_FILE = "complex_prompts_630.json"
OUTPUT_FILE = "layer1_complex_claude_gpt54.json"
MAX_TOKENS = 2048
TEMPERATURE = 0.0
RATE_LIMIT_SLEEP = 0.5


def get_sigv4_headers(url, body, region, service):
    """Sign a request with SigV4 for Bedrock Mantle."""
    session = boto3.Session()
    credentials = session.get_credentials()
    creds = credentials.get_frozen_credentials()

    request = AWSRequest(
        method="POST",
        url=url,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    SigV4Auth(creds, service, region).add_auth(request)
    return dict(request.headers)


def call_gpt54(system_prompt, user_prompt):
    """Call GPT-5.4 via Mantle endpoint using OpenAI Responses API format."""
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

    req = urllib.request.Request(
        MANTLE_ENDPOINT,
        data=body.encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            # Extract text from OpenAI Responses format
            output = result.get("output", [])
            for item in output:
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            return content["text"], None
            # Fallback: try choices format
            choices = result.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", ""), None
            return None, f"Unexpected response format: {json.dumps(result)[:200]}"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        return None, f"HTTP {e.code}: {error_body[:200]}"
    except Exception as e:
        return None, str(e)


def main():
    # Load prompts
    with open(PROMPTS_FILE) as f:
        prompts = json.load(f)
    logger.info(f"Loaded {len(prompts)} prompts")

    # Load existing results (Claude should already be done)
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            results = json.load(f)
        logger.info(f"Loaded {len(results)} existing results from {OUTPUT_FILE}")
    else:
        results = []

    # Remove any failed GPT-5.4 entries (we'll re-run them all)
    results = [r for r in results if r["model"] != MODEL_ID]
    logger.info(f"After removing old GPT-5.4 entries: {len(results)} results")

    # Test single call first
    logger.info("Testing GPT-5.4 access via Mantle endpoint...")
    test_resp, test_err = call_gpt54("You are helpful.", "Say hello in one word.")
    if test_resp:
        logger.info(f"Test SUCCESS: {test_resp[:50]}")
    else:
        logger.error(f"Test FAILED: {test_err}")
        logger.error("Fix credentials or endpoint issue before running full benchmark.")
        return

    # Run all 630 prompts
    logger.info(f"\n=== Running GPT-5.4 via Mantle ({len(prompts)} prompts) ===")
    ok, err = 0, 0
    t0 = time.time()

    for i, p in enumerate(prompts):
        logger.info(f"  [gpt54] Calling prompt {i+1}/{len(prompts)}...")
        response, error = call_gpt54(p["system_prompt"], p["user_prompt"])
        results.append({
            "patient_id": p["patient_id"],
            "domain": p["domain"],
            "complexity": p["complexity"],
            "task": p["task"],
            "task_subtype": p["task_subtype"],
            "serializer": p["serializer"],
            "model": MODEL_ID,
            "ground_truth": p["ground_truth"],
            "response": response,
            "status": "success" if response else f"ERROR: {error}",
        })
        if response:
            ok += 1
        else:
            err += 1
        logger.info(f"  [gpt54] Prompt {i+1} {'OK' if response else 'FAILED: ' + str(error)[:80]}")

        # Incremental save
        with open(OUTPUT_FILE, "w") as f:
            json.dump(results, f, indent=2)

        if (i + 1) % 50 == 0:
            elapsed = time.time() - t0
            eta = (len(prompts) - i - 1) * (elapsed / (i + 1)) / 60
            logger.info(f"  [gpt54] {i+1}/{len(prompts)} ({ok} ok, {err} err) ETA {eta:.0f}min")

        time.sleep(RATE_LIMIT_SLEEP)

    elapsed_total = (time.time() - t0) / 60
    logger.info(f"\n  GPT-5.4: {ok}/{len(prompts)} success in {elapsed_total:.1f}min")
    logger.info(f"  Total results in {OUTPUT_FILE}: {len(results)}")
    logger.info("DONE!")


if __name__ == "__main__":
    main()

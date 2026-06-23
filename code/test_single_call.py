#!/usr/bin/env python3
"""Single converse call to Claude with 30s timeout. Tests API reachability."""
import boto3, time
from botocore.config import Config

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
REGION = "us-east-2"

config = Config(read_timeout=30, connect_timeout=10)
client = boto3.client("bedrock-runtime", region_name=REGION, config=config)

print(f"Calling {MODEL_ID} in {REGION} with 30s timeout...")
t0 = time.time()
try:
    resp = client.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": "Say hello"}]}],
        inferenceConfig={"maxTokens": 50, "temperature": 0.0},
    )
    text = resp["output"]["message"]["content"][0]["text"]
    print(f"SUCCESS ({time.time()-t0:.1f}s): {text}")
except Exception as e:
    print(f"FAILED ({time.time()-t0:.1f}s): {e}")

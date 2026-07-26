#!/usr/bin/env python3
"""
run_benchmark_layer1.py

Layer 1 Benchmark Runner: Sends 1,800 prompts to a specified model,
collects responses, and records token usage and latency for F1 scoring.

Supports 5 models via AWS Bedrock (Converse API and invoke_model).
"""

import argparse
import json
import os
import sys
import time
import hashlib
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Lock

import boto3
from botocore.config import Config
from botocore.auth import SigV4Auth
from botocore.credentials import Credentials
import requests


# ============================================================================
# Model Configuration
# ============================================================================

MODEL_CONFIG = {
    "claude": {
        "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "api_type": "converse",
        "display_name": "Claude Sonnet 4.5",
    },
    "gpt54": {
        "model_id": "openai.gpt-5.4",
        "api_type": "mantle",
        "endpoint": "https://bedrock-mantle.us-east-2.api.aws/openai/v1/responses",
        "display_name": "GPT-5.4",
    },
    "llama": {
        "model_id": "meta.llama3-3-70b-instruct-v1:0",
        "api_type": "converse",
        "display_name": "Llama 3.3 70B",
    },
    "qwen": {
        "model_id": "qwen.qwen3-32b-v1:0",
        "api_type": "converse",
        "display_name": "Qwen3 32B",
    },
    "deepseek": {
        "model_id": "deepseek.v3.2",
        "api_type": "converse",
        "display_name": "DeepSeek V3.2",
    },
}


# ============================================================================
# API Callers
# ============================================================================

class BedrockConverseCaller:
    """Calls models using Bedrock Converse API."""

    def __init__(self, model_id: str, region: str, config: Config):
        self.model_id = model_id
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=config,
        )

    def call(self, prompt: str) -> dict:
        """
        Send prompt via Converse API.

        Returns:
            dict with keys: response, input_tokens, output_tokens
        """
        messages = [
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ]

        response = self.client.converse(
            modelId=self.model_id,
            messages=messages,
            inferenceConfig={
                "maxTokens": 4096,
                "temperature": 0.0,
            },
        )

        # Extract response text
        output_message = response.get("output", {}).get("message", {})
        content_blocks = output_message.get("content", [])
        response_text = ""
        for block in content_blocks:
            if "text" in block:
                response_text += block["text"]

        # Extract token usage
        usage = response.get("usage", {})
        input_tokens = usage.get("inputTokens", 0)
        output_tokens = usage.get("outputTokens", 0)

        return {
            "response": response_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }


class MantleCaller:
    """Calls GPT models via Bedrock Mantle endpoint with SigV4 auth."""

    def __init__(self, model_id: str, endpoint: str, region: str):
        self.model_id = model_id
        self.endpoint = endpoint
        self.region = region
        self.session = boto3.Session()

    def call(self, prompt: str) -> dict:
        """
        Send prompt via Mantle OpenAI-compatible endpoint with SigV4.

        Returns:
            dict with keys: response, input_tokens, output_tokens
        """
        from botocore.awsrequest import AWSRequest

        payload = {
            "model": self.model_id,
            "input": prompt,
            "instructions": "You are a clinical AI assistant specialising in UK NHS healthcare. Answer accurately and comprehensively.",
        }

        body = json.dumps(payload)

        # Create and sign request
        credentials = self.session.get_credentials().get_frozen_credentials()
        request = AWSRequest(
            method="POST",
            url=self.endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        SigV4Auth(credentials, "bedrock", self.region).add_auth(request)

        # Send request
        resp = requests.post(
            self.endpoint,
            data=body,
            headers=dict(request.headers),
            timeout=600,
        )
        resp.raise_for_status()

        result = resp.json()

        # Parse OpenAI-style response
        response_text = ""
        output = result.get("output", [])
        if isinstance(output, list):
            for item in output:
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            response_text += content.get("text", "")
        elif isinstance(output, str):
            response_text = output

        # Fallback: check for choices format
        if not response_text:
            choices = result.get("choices", [])
            if choices:
                response_text = choices[0].get("message", {}).get("content", "")

        # Token usage
        usage = result.get("usage", {})
        input_tokens = usage.get("input_tokens", usage.get("prompt_tokens", 0))
        output_tokens = usage.get("output_tokens", usage.get("completion_tokens", 0))

        return {
            "response": response_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }


# ============================================================================
# Benchmark Runner
# ============================================================================

class BenchmarkRunner:
    """Orchestrates benchmark execution with concurrency and retries."""

    def __init__(self, model_name: str, region: str, workers: int, max_retries: int = 3):
        self.model_name = model_name
        self.model_config = MODEL_CONFIG[model_name]
        self.region = region
        self.workers = workers
        self.max_retries = max_retries
        self.results = []
        self.results_lock = Lock()

        # Progress tracking
        self.completed = 0
        self.total = 0
        self.progress_lock = Lock()

        # Initialize caller
        config = Config(
            read_timeout=600,
            connect_timeout=10,
            retries={"max_attempts": 0},  # We handle retries ourselves
        )

        api_type = self.model_config["api_type"]
        if api_type == "converse":
            self.caller = BedrockConverseCaller(
                model_id=self.model_config["model_id"],
                region=region,
                config=config,
            )
        elif api_type == "mantle":
            self.caller = MantleCaller(
                model_id=self.model_config["model_id"],
                endpoint=self.model_config["endpoint"],
                region=region,
            )
        else:
            raise ValueError(f"Unknown API type: {api_type}")

    def process_prompt(self, prompt_record: dict) -> dict:
        """Process a single prompt with retries."""
        prompt_id = prompt_record["prompt_id"]
        prompt_text = prompt_record["prompt"]

        result = {
            "prompt_id": prompt_id,
            "patient_id": prompt_record["patient_id"],
            "serializer": prompt_record["serializer"],
            "task": prompt_record["task"],
            "model": self.model_name,
            "response": None,
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": 0,
            "success": False,
            "error": None,
        }

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()
                api_result = self.caller.call(prompt_text)
                elapsed_ms = int((time.time() - start_time) * 1000)

                result["response"] = api_result["response"]
                result["input_tokens"] = api_result["input_tokens"]
                result["output_tokens"] = api_result["output_tokens"]
                result["latency_ms"] = elapsed_ms
                result["success"] = True
                result["error"] = None
                break

            except Exception as e:
                last_error = str(e)
                if attempt < self.max_retries:
                    backoff = 2 ** attempt
                    time.sleep(backoff)
                else:
                    result["error"] = f"Failed after {self.max_retries} attempts: {last_error}"

        # Update progress
        with self.progress_lock:
            self.completed += 1
            if self.completed % 50 == 0 or self.completed == self.total:
                success_count = sum(1 for r in self.results if r.get("success"))
                print(f"  Progress: {self.completed}/{self.total} "
                      f"({self.completed/self.total*100:.1f}%) | "
                      f"Success so far: {success_count + (1 if result['success'] else 0)}")

        with self.results_lock:
            self.results.append(result)

        return result

    def run(self, prompts: list) -> list:
        """Run benchmark on all prompts with concurrent execution."""
        self.total = len(prompts)
        self.completed = 0
        self.results = []

        print(f"\nRunning benchmark: {self.model_config['display_name']}")
        print(f"  Model ID: {self.model_config['model_id']}")
        print(f"  API type: {self.model_config['api_type']}")
        print(f"  Prompts: {self.total}")
        print(f"  Workers: {self.workers}")
        print(f"  Max retries: {self.max_retries}")
        print()

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {
                executor.submit(self.process_prompt, prompt): prompt
                for prompt in prompts
            }

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"  ERROR: Unexpected exception in worker: {e}", file=sys.stderr)

        elapsed = time.time() - start_time

        # Sort results to match input order
        prompt_id_order = {p["prompt_id"]: i for i, p in enumerate(prompts)}
        self.results.sort(key=lambda r: prompt_id_order.get(r["prompt_id"], 0))

        # Summary
        successes = sum(1 for r in self.results if r["success"])
        failures = len(self.results) - successes
        total_input_tokens = sum(r["input_tokens"] for r in self.results)
        total_output_tokens = sum(r["output_tokens"] for r in self.results)
        avg_latency = (
            sum(r["latency_ms"] for r in self.results if r["success"])
            / max(successes, 1)
        )

        print()
        print(f"  Completed in {elapsed:.1f}s")
        print(f"  Success: {successes}/{self.total} ({successes/self.total*100:.1f}%)")
        print(f"  Failures: {failures}")
        print(f"  Total input tokens: {total_input_tokens:,}")
        print(f"  Total output tokens: {total_output_tokens:,}")
        print(f"  Avg latency: {avg_latency:.0f}ms")

        return self.results


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Layer 1 Benchmark Runner: Send prompts to models and collect responses."
    )
    parser.add_argument(
        "--model",
        required=True,
        choices=list(MODEL_CONFIG.keys()),
        help="Model to benchmark (run one at a time)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of concurrent workers (default: 5)"
    )
    parser.add_argument(
        "--input-file",
        default="../data/prompts/all_prompts.json",
        help="Path to prompts JSON file"
    )
    parser.add_argument(
        "--output-dir",
        default="../results/",
        help="Directory to save results"
    )
    parser.add_argument(
        "--region",
        default="us-east-2",
        help="AWS region (default: us-east-2)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process first N prompts (for testing)"
    )
    args = parser.parse_args()

    input_file = os.path.expanduser(args.input_file)
    output_dir = os.path.expanduser(args.output_dir)

    # Load prompts
    if not os.path.isfile(input_file):
        print(f"ERROR: Input file not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading prompts from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        prompts = json.load(f)

    print(f"Loaded {len(prompts)} prompts")

    if args.limit:
        prompts = prompts[:args.limit]
        print(f"Limited to first {args.limit} prompts (for testing)")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Run benchmark
    runner = BenchmarkRunner(
        model_name=args.model,
        region=args.region,
        workers=args.workers,
    )

    results = runner.run(prompts)

    # Save results
    output_filename = f"layer1_{args.model}_{len(prompts)}.json"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"\nResults saved to: {output_path}")

    # Save run metadata
    meta = {
        "timestamp": datetime.now().isoformat(),
        "model": args.model,
        "model_config": MODEL_CONFIG[args.model],
        "region": args.region,
        "workers": args.workers,
        "total_prompts": len(prompts),
        "total_success": sum(1 for r in results if r["success"]),
        "total_failures": sum(1 for r in results if not r["success"]),
        "total_input_tokens": sum(r["input_tokens"] for r in results),
        "total_output_tokens": sum(r["output_tokens"] for r in results),
        "avg_latency_ms": int(
            sum(r["latency_ms"] for r in results if r["success"])
            / max(sum(1 for r in results if r["success"]), 1)
        ),
        "output_file": output_filename,
    }

    meta_path = os.path.join(output_dir, f"layer1_{args.model}_meta.json")
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"Metadata saved to: {meta_path}")

    # Print final summary
    print()
    print("=" * 70)
    print(f"LAYER 1 BENCHMARK COMPLETE: {MODEL_CONFIG[args.model]['display_name']}")
    print("=" * 70)
    print(f"  Prompts processed: {len(results)}")
    print(f"  Success rate: {meta['total_success']}/{len(results)} "
          f"({meta['total_success']/len(results)*100:.1f}%)")
    print(f"  Output: {output_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()

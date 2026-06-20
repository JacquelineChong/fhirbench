"""Unified Bedrock client using the Converse API for all 5 benchmark models."""

import logging
import time
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Supported models with their Bedrock model IDs
MODEL_REGISTRY: Dict[str, str] = {
    "claude-sonnet-4.5": "anthropic.claude-sonnet-4-5-20260301-v1:0",
    "gpt-5.4": "openai.gpt-5-4",
    "llama-3-70b": "meta.llama3-70b-instruct-v1:0",
    "deepseek-v3.2": "deepseek.deepseek-v3-2",
    "qwen3-32b": "qwen.qwen3-32b",
}


class BedrockClient:
    """Unified Amazon Bedrock client using the Converse API.

    Handles all 5 benchmark models through a single interface with
    exponential backoff retry logic for throttling/transient errors.
    """

    def __init__(
        self,
        region_name: str = "us-east-1",
        max_retries: int = 5,
        base_delay: float = 1.0,
    ):
        """Initialize the Bedrock client.

        Args:
            region_name: AWS region for Bedrock API calls.
            max_retries: Maximum number of retry attempts.
            base_delay: Base delay in seconds for exponential backoff.
        """
        self.client = boto3.client("bedrock-runtime", region_name=region_name)
        self.max_retries = max_retries
        self.base_delay = base_delay

    def invoke(
        self,
        model_id: str,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.0,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Invoke a model using the Bedrock Converse API.

        Args:
            model_id: Bedrock model ID (or short name from MODEL_REGISTRY).
            prompt: User message/prompt text.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature (0.0 = deterministic).
            system_prompt: Optional system prompt.

        Returns:
            Model response text.

        Raises:
            RuntimeError: If all retries are exhausted.
        """
        # Resolve short name to full model ID
        resolved_id = MODEL_REGISTRY.get(model_id, model_id)

        # Build Converse API request
        messages: List[Dict] = [
            {"role": "user", "content": [{"text": prompt}]}
        ]

        inference_config = {
            "maxTokens": max_tokens,
            "temperature": temperature,
        }

        kwargs = {
            "modelId": resolved_id,
            "messages": messages,
            "inferenceConfig": inference_config,
        }

        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]

        # Invoke with retry
        return self._invoke_with_retry(kwargs)

    def invoke_multi_turn(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 2048,
        temperature: float = 0.0,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Invoke a model with multi-turn conversation history.

        Args:
            model_id: Bedrock model ID.
            messages: List of {"role": "user"|"assistant", "content": "..."} dicts.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.
            system_prompt: Optional system prompt.

        Returns:
            Model response text.
        """
        resolved_id = MODEL_REGISTRY.get(model_id, model_id)

        converse_messages = [
            {"role": m["role"], "content": [{"text": m["content"]}]}
            for m in messages
        ]

        kwargs = {
            "modelId": resolved_id,
            "messages": converse_messages,
            "inferenceConfig": {"maxTokens": max_tokens, "temperature": temperature},
        }

        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]

        return self._invoke_with_retry(kwargs)

    def _invoke_with_retry(self, kwargs: Dict) -> str:
        """Execute Converse API call with exponential backoff retry.

        Args:
            kwargs: Arguments for the bedrock-runtime converse call.

        Returns:
            Response text from the model.

        Raises:
            RuntimeError: If all retries are exhausted.
        """
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.converse(**kwargs)
                # Extract text from response
                output = response.get("output", {})
                message = output.get("message", {})
                content_blocks = message.get("content", [])
                text_parts = [
                    block["text"] for block in content_blocks if "text" in block
                ]
                return "\n".join(text_parts)

            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                last_error = e

                # Retry on throttling and transient errors
                if error_code in (
                    "ThrottlingException",
                    "ServiceUnavailableException",
                    "ModelTimeoutException",
                    "InternalServerException",
                ):
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(
                        f"Retry {attempt + 1}/{self.max_retries} for {kwargs['modelId']} "
                        f"(error: {error_code}), waiting {delay:.1f}s"
                    )
                    time.sleep(delay)
                else:
                    # Non-retryable error
                    logger.error(f"Non-retryable error for {kwargs['modelId']}: {e}")
                    raise RuntimeError(f"Bedrock API error: {e}") from e

            except Exception as e:
                last_error = e
                delay = self.base_delay * (2 ** attempt)
                logger.warning(
                    f"Retry {attempt + 1}/{self.max_retries} for {kwargs['modelId']} "
                    f"(error: {e}), waiting {delay:.1f}s"
                )
                time.sleep(delay)

        raise RuntimeError(
            f"All {self.max_retries} retries exhausted for {kwargs['modelId']}: {last_error}"
        )

    def list_available_models(self) -> List[str]:
        """List all supported model IDs.

        Returns:
            List of short model name strings.
        """
        return list(MODEL_REGISTRY.keys())

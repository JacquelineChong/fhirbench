"""Main benchmark runner - orchestrates serialization x model x task evaluation."""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from evaluation.metrics import compute_accuracy, compute_rouge, compute_clinical_correctness, compute_f1
from evaluation.scoring import ScoringRubric
from serializers import (
    RawJsonSerializer,
    FlattenedKVSerializer,
    NarrativeSerializer,
    StructuredMarkdownSerializer,
    ClinicalTemplateSerializer,
    HybridAdaptiveSerializer,
)
from tasks import ClinicalQATask, ClinicalReasoningTask, ClinicalSummarizationTask

logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """Orchestrates the FHIRBench evaluation pipeline.

    Runs all combinations of:
    - 6 serialization strategies
    - 5 LLMs via Bedrock Converse API
    - 3 clinical task types (QA, Reasoning, Summarization)
    """

    def __init__(
        self,
        config_path: str = "config/experiment.yaml",
        data_dir: str = "data/fhir_bundles",
        output_dir: str = "results",
    ):
        """Initialize benchmark runner.

        Args:
            config_path: Path to experiment configuration YAML.
            data_dir: Directory containing FHIR bundle JSON files.
            output_dir: Directory for saving results.
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load config
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._default_config()

        self.rubric = ScoringRubric()
        self._init_serializers()
        self._init_tasks()
        self._model_client = None

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "experiment": {"name": "fhirbench-v1", "seed": 42},
            "models": [
                {"id": "claude-sonnet-4.5", "model_id": "anthropic.claude-sonnet-4-5-20260301-v1:0"},
                {"id": "gpt-5.4", "model_id": "openai.gpt-5-4"},
                {"id": "llama-3-70b", "model_id": "meta.llama3-70b-instruct-v1:0"},
                {"id": "deepseek-v3.2", "model_id": "deepseek.deepseek-v3-2"},
                {"id": "qwen3-32b", "model_id": "qwen.qwen3-32b"},
            ],
            "evaluation": {"temperature": 0.0, "max_tokens": 2048},
        }

    def _init_serializers(self) -> None:
        """Initialize all serialization strategies."""
        self.serializers = {
            "raw_json": RawJsonSerializer(),
            "flattened_kv": FlattenedKVSerializer(),
            "narrative": NarrativeSerializer(),
            "structured_markdown": StructuredMarkdownSerializer(),
            "clinical_template": ClinicalTemplateSerializer(template="soap"),
            "hybrid_adaptive": HybridAdaptiveSerializer(),
        }

    def _init_tasks(self) -> None:
        """Initialize task generators."""
        self.tasks = {
            "clinical_qa": ClinicalQATask(),
            "clinical_reasoning": ClinicalReasoningTask(),
            "clinical_summarization": ClinicalSummarizationTask(),
        }

    @property
    def model_client(self):
        """Lazy-load the Bedrock client."""
        if self._model_client is None:
            from models.bedrock_client import BedrockClient
            region = self.config.get("aws", {}).get("region", "us-east-1")
            self._model_client = BedrockClient(region_name=region)
        return self._model_client

    def load_bundles(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load FHIR bundles from the data directory.

        Args:
            limit: Maximum number of bundles to load.

        Returns:
            List of FHIR Bundle dictionaries.
        """
        bundles = []
        json_files = sorted(self.data_dir.glob("*.json"))
        if limit:
            json_files = json_files[:limit]

        for path in json_files:
            with open(path) as f:
                bundle = json.load(f)
            bundles.append(bundle)

        logger.info(f"Loaded {len(bundles)} FHIR bundles from {self.data_dir}")
        return bundles

    def run(
        self,
        serializer_names: Optional[List[str]] = None,
        model_ids: Optional[List[str]] = None,
        task_names: Optional[List[str]] = None,
        bundle_limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Run the full benchmark evaluation.

        Args:
            serializer_names: Subset of serializers to run (None = all).
            model_ids: Subset of model IDs to run (None = all from config).
            task_names: Subset of tasks to run (None = all).
            bundle_limit: Max bundles to evaluate.

        Returns:
            Nested results dict: results[serializer][model][task] = scores.
        """
        bundles = self.load_bundles(limit=bundle_limit)
        if not bundles:
            logger.warning("No FHIR bundles found. Run data generation first.")
            return {}

        serializers_to_run = {
            k: v for k, v in self.serializers.items()
            if serializer_names is None or k in serializer_names
        }

        models_to_run = model_ids or [m["id"] for m in self.config.get("models", [])]
        tasks_to_run = {
            k: v for k, v in self.tasks.items()
            if task_names is None or k in task_names
        }

        results: Dict[str, Any] = {}
        total_conditions = len(serializers_to_run) * len(models_to_run) * len(tasks_to_run)
        logger.info(f"Running {total_conditions} conditions across {len(bundles)} bundles")

        for ser_name, serializer in serializers_to_run.items():
            results[ser_name] = {}
            for model_id in models_to_run:
                results[ser_name][model_id] = {}
                for task_name, task in tasks_to_run.items():
                    logger.info(f"Evaluating: {ser_name} x {model_id} x {task_name}")
                    scores = self._evaluate_condition(
                        serializer, ser_name, model_id, task_name, task, bundles
                    )
                    results[ser_name][model_id][task_name] = scores

        # Save results
        self.save_results(results)
        return results

    def _evaluate_condition(
        self,
        serializer,
        ser_name: str,
        model_id: str,
        task_name: str,
        task,
        bundles: List[Dict],
    ) -> Dict[str, float]:
        """Evaluate one serializer x model x task condition.

        Returns:
            Dict of aggregated metric scores.
        """
        predictions: List[str] = []
        ground_truths: List[Any] = []

        # Resolve Bedrock model ID from config
        bedrock_model_id = model_id
        for m in self.config.get("models", []):
            if m["id"] == model_id:
                bedrock_model_id = m.get("model_id", model_id)
                break

        for bundle in bundles:
            # Serialize the bundle
            if hasattr(serializer, "serialize_bundle"):
                if ser_name == "hybrid_adaptive":
                    serialized = serializer.serialize_bundle(bundle, task_type=task_name)
                else:
                    serialized = serializer.serialize_bundle(bundle)
            else:
                serialized = serializer.serialize(bundle)

            # Generate task prompts
            if task_name == "clinical_qa":
                qa_pairs = task.generate_questions(bundle)
                for qa in qa_pairs:
                    prompt = f"Context:\n{serialized}\n\nQuestion: {qa['question']}\nAnswer concisely."
                    response = self._invoke_model(bedrock_model_id, prompt)
                    predictions.append(response)
                    ground_truths.append(qa["answer"])

            elif task_name == "clinical_reasoning":
                reasoning_tasks = task.generate_tasks(bundle)
                for rt in reasoning_tasks:
                    prompt = f"Context:\n{serialized}\n\n{rt['prompt']}"
                    response = self._invoke_model(bedrock_model_id, prompt)
                    predictions.append(response)
                    ground_truths.append(rt)

            elif task_name == "clinical_summarization":
                sum_tasks = task.generate_tasks(bundle)
                for st in sum_tasks:
                    prompt = f"Context:\n{serialized}\n\n{st['prompt']}"
                    response = self._invoke_model(bedrock_model_id, prompt)
                    predictions.append(response)
                    ground_truths.append(st["reference_summary"])

        # Compute metrics based on task type
        scores: Dict[str, float] = {}
        if not predictions:
            return scores

        if task_name == "clinical_qa":
            scores["accuracy"] = compute_accuracy(predictions, ground_truths)
            scores["f1"] = sum(
                compute_f1(p, g) for p, g in zip(predictions, ground_truths)
            ) / len(predictions)

        elif task_name == "clinical_reasoning":
            scores["clinical_correctness"] = compute_clinical_correctness(
                predictions, ground_truths
            )
            rubric_scores = self.rubric.score_batch(predictions, ground_truths)
            scores.update(rubric_scores)

        elif task_name == "clinical_summarization":
            rouge_scores = compute_rouge(predictions, ground_truths)
            scores.update(rouge_scores)

        scores["n_samples"] = len(predictions)
        return scores

    def _invoke_model(self, model_id: str, prompt: str) -> str:
        """Invoke a model via Bedrock Converse API.

        Args:
            model_id: Bedrock model ID.
            prompt: Full prompt string.

        Returns:
            Model response text.
        """
        try:
            max_tokens = self.config.get("evaluation", {}).get("max_tokens", 2048)
            temperature = self.config.get("evaluation", {}).get("temperature", 0.0)
            return self.model_client.invoke(
                model_id=model_id,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception as e:
            logger.error(f"Model invocation failed for {model_id}: {e}")
            return ""

    def run_single(
        self, serializer, model_id: str, task, fhir_bundle: Dict
    ) -> Dict[str, float]:
        """Run a single evaluation: one serializer x one model x one task x one bundle.

        Args:
            serializer: Serializer instance.
            model_id: Bedrock model ID string.
            task: Task generator instance.
            fhir_bundle: A FHIR Bundle dict.

        Returns:
            Dict of metric scores.
        """
        return self._evaluate_condition(
            serializer,
            getattr(serializer, "name", "unknown"),
            model_id,
            getattr(task, "name", "unknown"),
            task,
            [fhir_bundle],
        )

    def save_results(
        self, results: Dict[str, Any], filename: str = "benchmark_results.json"
    ) -> None:
        """Save benchmark results to JSON.

        Args:
            results: Results dictionary to save.
            filename: Output filename.
        """
        output_path = self.output_dir / filename
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_path}")


def main():
    """CLI entry point for running the benchmark."""
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Run FHIRBench evaluation")
    parser.add_argument("--config", default="config/experiment.yaml", help="Config YAML path")
    parser.add_argument("--data-dir", default="data/fhir_bundles", help="FHIR bundle directory")
    parser.add_argument("--output-dir", default="results", help="Results output directory")
    parser.add_argument("--models", nargs="*", help="Subset of model IDs to run")
    parser.add_argument("--serializers", nargs="*", help="Subset of serializers to run")
    parser.add_argument("--tasks", nargs="*", help="Subset of tasks to run")
    parser.add_argument("--limit", type=int, help="Max bundles to evaluate")
    args = parser.parse_args()

    runner = BenchmarkRunner(
        config_path=args.config,
        data_dir=args.data_dir,
        output_dir=args.output_dir,
    )
    results = runner.run(
        serializer_names=args.serializers,
        model_ids=args.models,
        task_names=args.tasks,
        bundle_limit=args.limit,
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

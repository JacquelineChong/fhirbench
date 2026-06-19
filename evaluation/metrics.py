"""Metrics computation - accuracy, ROUGE, clinical correctness scoring."""

from typing import Dict, List


def compute_accuracy(predictions: List[str], ground_truths: List[str]) -> float:
    """Compute exact-match accuracy for clinical QA tasks.

    Args:
        predictions: List of predicted answer strings.
        ground_truths: List of ground truth answer strings.

    Returns:
        Fraction of exact matches (case-insensitive, stripped).
    """
    if not predictions:
        return 0.0
    correct = sum(
        1 for p, g in zip(predictions, ground_truths)
        if p.strip().lower() == g.strip().lower()
    )
    return correct / len(predictions)


def compute_rouge(predictions: List[str], references: List[str]) -> Dict[str, float]:
    """Compute ROUGE scores for summarization tasks.

    Args:
        predictions: List of generated summaries.
        references: List of reference summaries.

    Returns:
        Dict with rouge_1, rouge_2, rouge_l F-measure averages.
    """
    from rouge_score import rouge_scorer

    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

    totals = {"rouge_1": 0.0, "rouge_2": 0.0, "rouge_l": 0.0}
    n = len(predictions)
    if n == 0:
        return totals

    for pred, ref in zip(predictions, references):
        scores = scorer.score(ref, pred)
        totals["rouge_1"] += scores["rouge1"].fmeasure
        totals["rouge_2"] += scores["rouge2"].fmeasure
        totals["rouge_l"] += scores["rougeL"].fmeasure

    return {k: v / n for k, v in totals.items()}


def compute_clinical_correctness(predictions: List[str], ground_truths: List[Dict]) -> float:
    """Compute clinical correctness score for reasoning tasks.

    Uses a rubric-based approach: checks whether expected clinical findings
    are mentioned in the model's response.

    Args:
        predictions: List of model response strings.
        ground_truths: List of dicts with 'expected_findings' keys.

    Returns:
        Average correctness score between 0 and 1.
    """
    if not predictions:
        return 0.0

    total_score = 0.0
    for pred, truth in zip(predictions, ground_truths):
        expected = truth.get("expected_findings", [])
        if not expected:
            total_score += 1.0
            continue

        pred_lower = pred.lower()
        found = sum(1 for finding in expected if finding.lower() in pred_lower)
        total_score += found / len(expected)

    return total_score / len(predictions)


def compute_f1(prediction: str, ground_truth: str) -> float:
    """Compute token-level F1 score between prediction and ground truth.

    Args:
        prediction: Predicted answer string.
        ground_truth: Ground truth answer string.

    Returns:
        F1 score between 0 and 1.
    """
    pred_tokens = set(prediction.lower().split())
    truth_tokens = set(ground_truth.lower().split())

    if not pred_tokens and not truth_tokens:
        return 1.0
    if not pred_tokens or not truth_tokens:
        return 0.0

    common = pred_tokens & truth_tokens
    if not common:
        return 0.0

    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(truth_tokens)
    return 2 * precision * recall / (precision + recall)


def compute_token_efficiency(serialized_texts: List[str]) -> Dict[str, float]:
    """Compute token efficiency metrics as cost proxy.

    Uses whitespace tokenization as approximation. Actual token counts
    vary by model tokenizer.

    Args:
        serialized_texts: List of serialized text strings.

    Returns:
        Dict with avg_tokens and total_tokens.
    """
    if not serialized_texts:
        return {"avg_tokens": 0.0, "total_tokens": 0.0}

    # Approximate token count (words ≈ 0.75 tokens for English)
    token_counts = [len(text.split()) * 1.33 for text in serialized_texts]
    total = sum(token_counts)
    return {"avg_tokens": total / len(token_counts), "total_tokens": total}

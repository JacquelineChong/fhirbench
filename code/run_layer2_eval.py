import json, time, boto3, re
from collections import defaultdict

RESULTS_DIR = "/Users/chongaws/Desktop/Kiro/FHIR/code/results"
REGION = "us-east-1"
CLAUDE_JUDGE = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
LLAMA_JUDGE = "meta.llama3-70b-instruct-v1:0"

FILES = {
    "Qwen3": "bedrock_full_300.json",
    "Claude": "bedrock_claude_300.json",
    "Llama": "bedrock_llama_300.json",
    "DeepSeek": "bedrock_deepseek_300.json",
    "GPT-5.4": "bedrock_gpt54_300.json",
}

PROMPT_TEMPLATE = """You are a clinical evaluation expert. Score the following model response on a 0-5 scale for each dimension.

QUESTION: {question}
GROUND TRUTH ANSWER: {ground_truth}
MODEL RESPONSE: {model_response}

Score each dimension (0=completely wrong/unsafe, 5=perfect):
1. CLINICAL ACCURACY (0-5): Are clinical facts correct?
2. COMPLETENESS (0-5): Are all significant findings covered?
3. SAFETY (0-5): Is the response clinically safe?
4. RELEVANCE (0-5): Does it address the question directly?

Respond ONLY with JSON: {{"accuracy": N, "completeness": N, "safety": N, "relevance": N}}"""

client = boto3.client("bedrock-runtime", region_name=REGION)

def call_judge(prompt, model_id):
    """Call Bedrock Converse API and return parsed scores."""
    resp = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"temperature": 0.0, "maxTokens": 100},
    )
    text = resp["output"]["message"]["content"][0]["text"]
    # Extract JSON from response
    match = re.search(r'\{[^}]+\}', text)
    if match:
        return json.loads(match.group())
    return None

def main():
    all_scores = []
    total = sum(len(json.load(open(f"{RESULTS_DIR}/{f}"))) for f in FILES.values())
    done = 0
    errors = 0

    for model_name, filename in FILES.items():
        data = json.load(open(f"{RESULTS_DIR}/{filename}"))
        judge_model = LLAMA_JUDGE if model_name == "Claude" else CLAUDE_JUDGE
        print(f"\n=== Evaluating {model_name} ({len(data)} entries) with judge: {judge_model.split('.')[-1][:30]} ===")

        for i, entry in enumerate(data):
            if entry.get("error") or not entry.get("model_response"):
                done += 1
                continue

            prompt = PROMPT_TEMPLATE.format(
                question=entry["question"],
                ground_truth=entry["ground_truth"],
                model_response=entry["model_response"],
            )

            try:
                scores = call_judge(prompt, judge_model)
                if scores:
                    all_scores.append({
                        "model": model_name,
                        "patient_id": entry["patient_id"],
                        "domain": entry["domain"],
                        "serializer": entry["serializer"],
                        "category": entry["category"],
                        "question": entry["question"],
                        "accuracy": scores["accuracy"],
                        "completeness": scores["completeness"],
                        "safety": scores["safety"],
                        "relevance": scores["relevance"],
                        "judge_model": judge_model,
                    })
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"  Error on {model_name}[{i}]: {e}")

            done += 1
            if done % 50 == 0:
                print(f"  Progress: {done}/{total} ({errors} errors)")
            time.sleep(0.3)

    # Save raw scores
    output_path = f"{RESULTS_DIR}/layer2_rubric_scores.json"
    with open(output_path, "w") as f:
        json.dump(all_scores, f, indent=2)
    print(f"\nSaved {len(all_scores)} scores to {output_path}")

    # Summary
    dims = ["accuracy", "completeness", "safety", "relevance"]

    # Per model
    by_model = defaultdict(lambda: defaultdict(list))
    for s in all_scores:
        for d in dims:
            by_model[s["model"]][d].append(s[d])

    # Per serializer
    by_serializer = defaultdict(lambda: defaultdict(list))
    for s in all_scores:
        for d in dims:
            by_serializer[s["serializer"]][d].append(s[d])

    summary = {
        "per_model": {m: {d: round(sum(v)/len(v), 3) for d, v in dims_dict.items()} for m, dims_dict in by_model.items()},
        "per_serializer": {s: {d: round(sum(v)/len(v), 3) for d, v in dims_dict.items()} for s, dims_dict in by_serializer.items()},
        "total_evaluated": len(all_scores),
        "errors": errors,
    }

    summary_path = f"{RESULTS_DIR}/layer2_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print("SUMMARY - Mean Scores per Model:")
    print(f"{'Model':<12} {'Accuracy':<10} {'Complete':<10} {'Safety':<10} {'Relevance':<10}")
    for m, scores in summary["per_model"].items():
        print(f"{m:<12} {scores['accuracy']:<10} {scores['completeness']:<10} {scores['safety']:<10} {scores['relevance']:<10}")

    print(f"\nSUMMARY - Mean Scores per Serializer:")
    print(f"{'Serializer':<20} {'Accuracy':<10} {'Complete':<10} {'Safety':<10} {'Relevance':<10}")
    for s, scores in summary["per_serializer"].items():
        print(f"{s:<20} {scores['accuracy']:<10} {scores['completeness']:<10} {scores['safety']:<10} {scores['relevance']:<10}")

    print(f"\nTotal evaluated: {len(all_scores)}, Errors: {errors}")

if __name__ == "__main__":
    main()

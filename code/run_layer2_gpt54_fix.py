import json, time, boto3, re

RESULTS_DIR = "/Users/chongaws/Desktop/Kiro/FHIR/code/results"
REGION = "us-east-1"
CLAUDE_JUDGE = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

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
    resp = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"temperature": 0.0, "maxTokens": 100},
    )
    text = resp["output"]["message"]["content"][0]["text"]
    match = re.search(r'\{[^}]+\}', text)
    if match:
        return json.loads(match.group())
    return None

data = json.load(open(f"{RESULTS_DIR}/bedrock_gpt54_300.json"))
print(f"Evaluating GPT-5.4: {len(data)} entries")

gpt_scores = []
errors = 0
for i, entry in enumerate(data):
    if entry.get("status") == "error" or not entry.get("model_response"):
        continue
    prompt = PROMPT_TEMPLATE.format(
        question=entry["question"],
        ground_truth=entry["ground_truth"],
        model_response=entry["model_response"],
    )
    try:
        scores = call_judge(prompt, CLAUDE_JUDGE)
        if scores:
            gpt_scores.append({
                "model": "GPT-5.4",
                "patient_id": entry["patient_id"],
                "domain": entry["domain"],
                "serializer": entry.get("serializer", "unknown"),
                "category": entry["category"],
                "question": entry["question"],
                "accuracy": scores["accuracy"],
                "completeness": scores["completeness"],
                "safety": scores["safety"],
                "relevance": scores["relevance"],
                "judge_model": CLAUDE_JUDGE,
            })
        else:
            errors += 1
    except Exception as e:
        errors += 1
        if errors <= 3:
            print(f"  Error [{i}]: {e}")
    if (i+1) % 50 == 0:
        print(f"  Progress: {i+1}/300 ({errors} errors)")
    time.sleep(0.3)

print(f"GPT-5.4 done: {len(gpt_scores)} scores, {errors} errors")

# Merge with existing scores
existing = json.load(open(f"{RESULTS_DIR}/layer2_rubric_scores.json"))
all_scores = existing + gpt_scores

with open(f"{RESULTS_DIR}/layer2_rubric_scores.json", "w") as f:
    json.dump(all_scores, f, indent=2)
print(f"Total scores saved: {len(all_scores)}")

# Rebuild summary
from collections import defaultdict
dims = ["accuracy", "completeness", "safety", "relevance"]

by_model = defaultdict(lambda: defaultdict(list))
for s in all_scores:
    for d in dims:
        by_model[s["model"]][d].append(s[d])

by_serializer = defaultdict(lambda: defaultdict(list))
for s in all_scores:
    if s["serializer"] != "unknown":
        for d in dims:
            by_serializer[s["serializer"]][d].append(s[d])

summary = {
    "per_model": {m: {d: round(sum(v)/len(v), 3) for d, v in dd.items()} for m, dd in by_model.items()},
    "per_serializer": {s: {d: round(sum(v)/len(v), 3) for d, v in dd.items()} for s, dd in by_serializer.items()},
    "total_evaluated": len(all_scores),
    "errors": errors,
}

with open(f"{RESULTS_DIR}/layer2_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"\n{'='*60}")
print("FINAL SUMMARY - Mean Scores per Model:")
print(f"{'Model':<12} {'Accuracy':<10} {'Complete':<10} {'Safety':<10} {'Relevance':<10}")
for m, scores in summary["per_model"].items():
    print(f"{m:<12} {scores['accuracy']:<10} {scores['completeness']:<10} {scores['safety']:<10} {scores['relevance']:<10}")

print(f"\nFINAL SUMMARY - Mean Scores per Serializer:")
print(f"{'Serializer':<20} {'Accuracy':<10} {'Complete':<10} {'Safety':<10} {'Relevance':<10}")
for s, scores in summary["per_serializer"].items():
    print(f"{s:<20} {scores['accuracy']:<10} {scores['completeness']:<10} {scores['safety']:<10} {scores['relevance']:<10}")

print(f"\nTotal evaluated: {len(all_scores)}")

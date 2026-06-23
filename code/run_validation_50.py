"""FHIRBench Full Validation: 50 patients × 6 serializers × Clinical QA
Generates all prompts and token statistics (no Bedrock call - credentials unavailable)
"""
import json, sys, os, glob, statistics
from datetime import datetime

sys.path.insert(0, ".")

from serializers import (
    RawJsonSerializer, FlattenedKVSerializer, NarrativeSerializer,
    StructuredMarkdownSerializer, ClinicalTemplateSerializer, HybridAdaptiveSerializer,
)
from tasks.clinical_qa import ClinicalQATask

# Setup
SERIALIZERS = [
    ("raw_json", RawJsonSerializer()),
    ("flattened_kv", FlattenedKVSerializer()),
    ("narrative", NarrativeSerializer()),
    ("structured_markdown", StructuredMarkdownSerializer()),
    ("clinical_template", ClinicalTemplateSerializer(template="soap")),
    ("hybrid_adaptive", HybridAdaptiveSerializer()),
]
task = ClinicalQATask()
SYSTEM_PROMPT = "You are a clinical data assistant. Answer questions about patient data precisely and concisely based only on the provided FHIR data."

# Discover all patient files
patient_files = sorted(glob.glob("data/fhir_bundles/**/patient_*.json", recursive=True))
print(f"Found {len(patient_files)} patient files")

# Results storage
all_prompts = []  # For validation_prompts.json
token_stats = {name: [] for name, _ in SERIALIZERS}
qa_by_domain = {}
qa_by_category = {}
errors = []
patient_results = []

for pf in patient_files:
    domain = os.path.basename(os.path.dirname(pf))
    patient_id = os.path.basename(pf).replace(".json", "")
    
    # Load bundle
    with open(pf) as f:
        bundle = json.load(f)
    
    # Generate QA pairs
    qa_pairs = task.generate_questions(bundle)
    qa_by_domain[domain] = qa_by_domain.get(domain, 0) + len(qa_pairs)
    for qa in qa_pairs:
        qa_by_category[qa["category"]] = qa_by_category.get(qa["category"], 0) + 1
    
    if not qa_pairs:
        errors.append({"patient": patient_id, "domain": domain, "error": "No QA pairs generated"})
        continue
    
    test_qa = qa_pairs[0]  # Use first QA pair for benchmarking
    
    for ser_name, ser in SERIALIZERS:
        try:
            if ser_name == "hybrid_adaptive":
                serialized = ser.serialize_bundle(bundle, task_type="clinical_qa")
            else:
                serialized = ser.serialize_bundle(bundle)
            
            token_count = len(serialized.split()) * 1.33
            token_stats[ser_name].append(token_count)
            
            # Build prompt
            prompt = f"""You are a clinical assistant. Based on the following patient data, answer the question accurately and concisely.

## Patient Data:
{serialized}

## Question:
{test_qa['question']}

## Answer:"""
            
            all_prompts.append({
                "patient_id": patient_id,
                "domain": domain,
                "serializer": ser_name,
                "question": test_qa["question"],
                "ground_truth": test_qa["answer"],
                "category": test_qa["category"],
                "prompt_length_chars": len(prompt),
                "token_count_approx": round(token_count),
                "prompt": prompt,
                "system_prompt": SYSTEM_PROMPT,
                "model": "qwen.qwen3-32b",
            })
        except Exception as e:
            errors.append({"patient": patient_id, "domain": domain, "serializer": ser_name, "error": str(e)})
            token_stats[ser_name].append(0)

    # Progress
    idx = patient_files.index(pf) + 1
    if idx % 10 == 0:
        print(f"  Processed {idx}/{len(patient_files)} patients...")

print(f"\nProcessed all {len(patient_files)} patients. Generated {len(all_prompts)} prompts.")

# Save prompts
os.makedirs("results", exist_ok=True)
with open("results/validation_prompts.json", "w") as f:
    json.dump(all_prompts, f, indent=2)
print(f"Saved {len(all_prompts)} prompts to results/validation_prompts.json")

# Compute statistics
raw_json_mean = statistics.mean(token_stats["raw_json"]) if token_stats["raw_json"] else 1

summary_stats = {}
for name, tokens in token_stats.items():
    if not tokens:
        continue
    mean_t = statistics.mean(tokens)
    summary_stats[name] = {
        "mean": round(mean_t, 1),
        "min": round(min(tokens), 1),
        "max": round(max(tokens), 1),
        "std": round(statistics.stdev(tokens), 1) if len(tokens) > 1 else 0,
        "compression_vs_raw": round(mean_t / raw_json_mean, 3),
        "count": len(tokens),
    }

# Save structured results
results_json = {
    "metadata": {
        "timestamp": datetime.now().isoformat(),
        "total_patients": len(patient_files),
        "total_prompts": len(all_prompts),
        "serializers": [n for n, _ in SERIALIZERS],
        "task": "clinical_qa",
        "model": "qwen.qwen3-32b",
        "bedrock_status": "UNAVAILABLE - no credentials",
    },
    "token_statistics": summary_stats,
    "qa_by_domain": qa_by_domain,
    "qa_by_category": qa_by_category,
    "errors": errors,
}
with open("results/validation_50_results.json", "w") as f:
    json.dump(results_json, f, indent=2)
print("Saved results/validation_50_results.json")

# Print summary
print("\n" + "=" * 70)
print("TOKEN STATISTICS BY SERIALIZER")
print("=" * 70)
print(f"{'Serializer':<25} {'Mean':>8} {'Min':>8} {'Max':>8} {'Std':>8} {'Ratio':>8}")
print("-" * 70)
for name, stats in summary_stats.items():
    print(f"{name:<25} {stats['mean']:>8.1f} {stats['min']:>8.1f} {stats['max']:>8.1f} {stats['std']:>8.1f} {stats['compression_vs_raw']:>8.3f}")

print(f"\n{'QA Pairs by Domain:'}")
for domain, count in sorted(qa_by_domain.items()):
    print(f"  {domain}: {count}")

print(f"\n{'QA Pairs by Category:'}")
for cat, count in sorted(qa_by_category.items()):
    print(f"  {cat}: {count}")

if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors[:5]:
        print(f"  {e}")
else:
    print("\nNo errors.")

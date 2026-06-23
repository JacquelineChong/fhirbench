"""Run all 300 staged prompts against Bedrock qwen.qwen3-32b-v1:0"""
import boto3, json, time, sys
sys.path.insert(0, ".")
from evaluation.metrics import compute_f1

client = boto3.client('bedrock-runtime', region_name='us-east-1')
MODEL_ID = 'qwen.qwen3-32b-v1:0'

with open('results/validation_prompts.json') as f:
    prompts = json.load(f)

print(f"Running {len(prompts)} prompts against {MODEL_ID}...")

results = []
errors = 0
start_time = time.time()

for i, p in enumerate(prompts):
    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=[{'role': 'user', 'content': [{'text': p['prompt']}]}],
            system=[{'text': p['system_prompt']}],
            inferenceConfig={'maxTokens': 512, 'temperature': 0}
        )
        answer = response['output']['message']['content'][0]['text']
        usage = response['usage']
        f1 = compute_f1(answer, p['ground_truth'])
        results.append({
            'patient_id': p['patient_id'],
            'domain': p['domain'],
            'serializer': p['serializer'],
            'category': p['category'],
            'question': p['question'],
            'ground_truth': p['ground_truth'],
            'model_response': answer,
            'f1_score': round(f1, 4),
            'input_tokens': usage['inputTokens'],
            'output_tokens': usage['outputTokens'],
            'error': None,
        })
    except Exception as e:
        errors += 1
        results.append({
            'patient_id': p['patient_id'],
            'domain': p['domain'],
            'serializer': p['serializer'],
            'category': p['category'],
            'question': p['question'],
            'ground_truth': p['ground_truth'],
            'model_response': None,
            'f1_score': None,
            'input_tokens': None,
            'output_tokens': None,
            'error': str(e),
        })
    
    if (i + 1) % 10 == 0:
        elapsed = time.time() - start_time
        rate = (i + 1) / elapsed
        print(f"  [{i+1}/{len(prompts)}] {rate:.1f} req/s | errors: {errors}")
    
    time.sleep(0.3)  # Rate limiting

elapsed = time.time() - start_time
print(f"\nDone! {len(prompts)} prompts in {elapsed:.1f}s ({len(prompts)/elapsed:.1f} req/s)")
print(f"Errors: {errors}/{len(prompts)}")

with open('results/bedrock_full_300.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Saved results/bedrock_full_300.json")

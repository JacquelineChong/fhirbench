# FHIRBench-UK — Session Notes (19 Jul 2026)

## Project Status

### Completed This Session
- Git branch `uk-core` created on JacquelineChong/fhirbench
- Zotero collection created: "Paper #2 — FHIRBench-UK (NPJ)" (key: DMQFFBM8)
- Local folder: /Users/chongaws/Desktop/Kiro/FHIR-UK/
- Literature review complete (30 citations, 5,500 words)
- Paper 2 outline written (NPJ format, ~4,500 words target)
- UK experiment config created (experiment_uk.yaml)
- All 6 serialisers adapted for UK Core FHIR
- Official UK Core FHIR data downloaded (NHSDigital repo, 101 StructureDefinitions, 209 examples)
- All 6 serialisers VALIDATED against real UK Core Patient (Richard Smith example)
- Introduction draft written (~800 words, UK English)

### Model Routing Plan
| Model | Geo-restricted? | Run from |
|---|---|---|
| Claude Sonnet 4.5 | YES | EC2 (us-east-2) |
| GPT-5.4 | YES (Mantle endpoint) | EC2 (us-east-2) |
| Qwen3 32B | NO | Local Mac |
| DeepSeek V3.2 | NO | Local Mac |
| Llama 3.3 70B (NEW) | Likely YES | EC2 (us-east-2) |

### Next Session Tasks
1. Refresh AWS credentials and verify Llama 3.3 70B on Bedrock
2. Push remaining large serialiser files (narrative, clinical_template, structured_markdown, flattened_kv)
3. Import 30 citations into Zotero collection DMQFFBM8
4. Generate 100 UK synthetic patients
5. Run benchmark on EC2
6. Statistical analysis and paper writing
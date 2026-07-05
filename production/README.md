# Context-Adaptive FHIR Serialization Engine

## Production Path — From Benchmark to Deployable Middleware

This folder contains design specifications and prototype architecture for a context-adaptive serialization engine informed by the FHIRBench benchmark findings.

## Concept

A middleware layer that sits between FHIR data sources (e.g., AWS HealthLake) and LLM inference endpoints (e.g., Amazon Bedrock), dynamically selecting the optimal serialization strategy based on:

1. **Target model** — each model has a different optimal serializer (Finding 3: Model × Serializer interaction, p=0.0009)
2. **Patient complexity** — complex patients require compact formats for open-weight models (Finding 4: Llama 100% failure on Raw JSON)
3. **Clinical task type** — QA vs reasoning vs summarization show different format sensitivities
4. **Deployment constraints** — cost budget, latency SLA, quality threshold (Pareto frontier, §4.7)

## Architecture

```
┌─────────────────┐     ┌──────────────────────────────┐     ┌─────────────┐
│  FHIR R4 Bundle │────▶│  Serialization Engine         │────▶│  LLM (Bedrock)│
│  (HealthLake)   │     │                              │     │             │
└─────────────────┘     │  1. Assess complexity        │     └─────────────┘
                        │  2. Select format (Pareto)   │
                        │  3. Apply serializer         │
                        │  4. Enforce token budget     │
                        │  5. Fallback on timeout      │
                        └──────────────────────────────┘
                                     ↑
                        ┌──────────────────────────────┐
                        │  Calibration Tables          │
                        │  (from FHIRBench results)    │
                        │  - Model × Serializer scores │
                        │  - Token counts per format   │
                        │  - Pareto frontier points    │
                        └──────────────────────────────┘
```

## Decision Logic (Pseudocode)

```
function select_serializer(bundle, model, task, constraints):
    complexity = assess_complexity(bundle)  # Simple/Moderate/Complex/HC
    
    # Get model-specific Pareto frontier
    frontier = get_pareto_frontier(model, task)
    
    # Filter by constraints
    viable = [s for s in frontier if s.cost <= constraints.budget 
              and s.latency <= constraints.sla]
    
    # Select highest quality among viable
    selected = max(viable, key=lambda s: s.quality)
    
    # Capacity check for open-weight models
    if model.is_open_weight and complexity in (COMPLEX, HIGHLY_COMPLEX):
        selected = min(viable, key=lambda s: s.tokens)  # Force compact
    
    return selected.serialize(bundle)
```

## Calibration Data (from FHIRBench)

### Model-Specific Optimal Serializers

| Model | Best Format | L2 Accuracy | Tokens |
|-------|------------|:-----------:|:------:|
| Claude Sonnet 4.5 | Narrative/Condensed | 4.01–4.02 | 337/266 |
| GPT-5.4 | Raw JSON | 4.03 | 1,991 |
| Qwen3 32B | Raw JSON* | 3.46 | 1,991 |
| DeepSeek V3.2 | Raw JSON/Narrative | 3.92–3.93 | 1,991/337 |

*Qwen benefits more from compression (p < 10⁻³⁸) despite Raw JSON scoring highest in absolute terms.

### Pareto-Optimal Formats

| Format | Tokens | Quality | Use When |
|--------|:------:|:-------:|----------|
| Raw JSON | 1,991 | 3.83 | Quality-maximizing, cost secondary |
| Narrative | 337 | 3.64 | Balanced (95% quality, 83% savings) |
| FHIRPath | 329 | 3.49 | Compact + structured |
| Condensed | 266 | 3.33 | Cost-minimizing / model-constrained |

## IP / Patent Considerations

| Element | Novelty Claim |
|---------|--------------|
| Model-aware serialization selection | No prior art for dynamic model-specific FHIR serialization |
| Complexity-adaptive format switching | Novel — current systems use fixed pipelines regardless of input |
| Pareto-optimal strategy selection at inference time | Novel — uses benchmark calibration data for runtime decisions |
| Fallback cascade on timeout detection | Practical implementation with clinical safety rationale |

## Implementation Roadmap

- [ ] Phase 1: Static lookup table (model → serializer mapping)
- [ ] Phase 2: Complexity assessment + dynamic selection
- [ ] Phase 3: Token budget enforcement + timeout fallback
- [ ] Phase 4: Online learning (adapt calibration from production metrics)

## Dependencies

- FHIRBench calibration data (`results/layer1_f1_summary.json`, `results/layer2_scores_7200.json`)
- FHIR R4 parser
- Serializer implementations (`serializers/`)
- Amazon Bedrock integration

---

*This design is informed by the research findings in the FHIRBench paper (§4–§5). See `paper/sections/05-discussion.md` §5.4.1 for the academic framing.*

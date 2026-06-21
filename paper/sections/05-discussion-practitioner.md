## 5.3 Practitioner Application Scenarios

The value of FHIRBench extends beyond academic contribution — it provides directly actionable guidance for clinical AI teams. This section describes how practitioners across different roles are expected to use the benchmark findings.

### 5.3.1 Target Audience and Use Cases

| Practitioner Role | Problem Statement | How FHIRBench Helps |
|---|---|---|
| **Health AI Engineer** | "Which serialization format should I use for my FHIR-to-LLM pipeline?" | Consult Decision Matrix (Table X): task type + model + priority → recommended strategy |
| **Clinical Informatics Lead** | "Is our default JSON serialization costing us accuracy?" | Compare baseline (Raw JSON) performance against alternatives — our results show up to 2× F1 improvement with Clinical Template |
| **Digital Health Startup CTO** | "How do I minimize inference costs without losing clinical quality?" | Use Pareto frontier to find cost-optimal strategy for their chosen model |
| **EHR Vendor Product Manager** | "Should we add serialization middleware to our FHIR API?" | Use token efficiency data (5.4× compression) to build ROI case — fewer tokens = proportionally lower Bedrock/API costs |
| **Clinical Safety Officer** | "Which format produces the safest LLM outputs?" | Consult Safety dimension scores per serializer × model combination |

### 5.3.2 Three-Step Adoption Workflow

We envision a three-step workflow for practitioners adopting FHIRBench findings:

**Step 1: Consult the Decision Matrix.**
The practitioner identifies their clinical task type (QA, reasoning, or summarization), their deployed model (or candidate models), and their priority constraint (accuracy-first, cost-first, or balanced). The Decision Matrix maps this triple to a recommended serialization strategy. No computation is required — the practitioner reads a lookup table.

**Step 2: Implement the recommended serializer.**
The FHIRBench repository (https://github.com/JacquelineChong/fhirbench) provides production-ready Python implementations of all six serialization strategies under `serializers/`. The practitioner integrates the recommended module into their existing FHIR data pipeline. Estimated integration effort: 30 minutes for a standard Python-based pipeline, versus 3+ weeks of empirical testing without FHIRBench guidance.

**Step 3: Validate on local data (optional but recommended).**
While FHIRBench findings are expected to generalize across US Core FHIR implementations, practitioners may wish to confirm on their own patient population. We recommend running 50–100 of their own FHIR bundles through the pipeline using the 4-dimension evaluation rubric (§3.5.3) as a quality gate. The `evaluation/` module and scoring rubric are provided for this purpose.

### 5.3.3 Expected Impact

| Metric | Without FHIRBench | With FHIRBench |
|---|---|---|
| Time to select serialization strategy | 3–6 weeks (empirical trial-and-error) | 30 minutes (consult Decision Matrix) |
| Confidence in strategy selection | Low (single-task, single-model testing) | High (90-condition systematic evaluation) |
| Token cost awareness | Unknown (default to Raw JSON) | Quantified (Pareto frontier) |
| Reproducibility of pipeline decisions | Ad hoc, undocumented | Evidence-based, citable |

### 5.3.4 Limitations of Practitioner Guidance

The Decision Matrix is derived from synthetic US Core FHIR data (§3.2). Practitioners should note:

1. **Domain specificity** — Strategy rankings may differ for clinical domains not covered by our four evaluation domains (diabetes, cardiovascular, medication interactions, preventive care)
2. **Model versioning** — Rankings may shift as model providers release updates; we recommend periodic re-validation
3. **Real-world data complexity** — Institutional FHIR implementations may include extensions, custom profiles, or data quality issues not represented in our synthetic benchmark
4. **Task granularity** — Our three task categories are broad; highly specific subtasks (e.g., allergy cross-checking) may benefit from different strategies

These limitations motivate future work on domain-specific validation and institutional benchmark extensions (§6).

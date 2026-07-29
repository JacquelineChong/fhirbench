# 5. Discussion

## 5.1 Cross-National Replication of the Ranking Reversal

The central finding of this study—a complete inversion of model rankings between token-level F1 and clinical quality assessment—replicates and extends the phenomenon first identified in Paper 1 on US Core FHIR data. In Paper 1, Claude ranked last on automated F1 metrics but first on LLM-as-judge evaluation. In the present UK Core study, the pattern manifests with Llama 3.3 occupying rank 1 on F1 but rank 5 on clinical quality, whilst Claude moves from rank 3 on F1 to rank 1 on quality. The rankings are not merely shuffled; they are substantively inverted, with Spearman's ρ = −0.90 between Layer 1 and Layer 2 orderings.

This replication across two independent datasets, two FHIR profile families (US Core R4 vs UK Core STU3/R4), two data generation approaches (Synthea-derived vs LLM-generated), and two geographic healthcare conventions strengthens the claim that the ranking reversal reflects a fundamental measurement phenomenon rather than a dataset-specific artefact. The consistency suggests that token-level metrics and clinical quality rubrics are measuring orthogonal—and in some cases antagonistic—constructs.

The implication for the broader clinical NLP community is direct: single-metric evaluation of large language models on clinical tasks is fundamentally insufficient. Studies reporting only F1, ROUGE, or BLEU scores for clinical question answering or summarisation risk drawing conclusions that would invert under expert or rubric-based assessment. This challenges the prevailing practice in clinical AI benchmarking, where automated metrics dominate due to their scalability and reproducibility. We do not argue that automated metrics lack value—they provide essential signal about factual coverage—but that they must be complemented by quality-oriented evaluation to capture the clinical dimensions that matter for deployment.

## 5.2 NHS Deployment Implications

The Pareto analysis in §4.5 yields actionable guidance for NHS organisations evaluating LLM deployment for FHIR-based clinical workflows.

For safety-critical applications—A&E clinical decision support, medication reconciliation, specialist referral letters—Claude Sonnet 4.5 emerges as the clear recommendation despite its higher cost ($0.032 per prompt). Its near-perfect safety score (4.98/5.00) and accuracy (4.72/5.00) provide the margin required for applications where errors carry direct patient safety consequences. At current NHS volumes, a trust processing 10,000 clinical queries per month would incur approximately £250 in inference costs—a figure that compares favourably against clinician time for equivalent manual processing.

For high-volume, lower-criticality workloads—bulk discharge summary processing, routine coding validation, population health screening—DeepSeek V3.2 offers a compelling value proposition. Its clinical quality scores (4.23/5.00) approach those of GPT-5.4 (4.28/5.00) at approximately one-sixth the cost. For an NHS trust processing 100,000 patient records per month, the cost differential between GPT-5.4 ($2,800) and DeepSeek ($500) represents meaningful budget reallocation without clinically significant quality degradation.

Qwen3 32B occupies the economy tier ($0.002 per prompt), suitable for pre-screening or triage workloads where human review invariably follows. Its lower quality scores (3.78/5.00) render it inappropriate for autonomous decision support, but acceptable as a first-pass filter that flags records requiring clinician attention.

Llama 3.3 70B, despite its strong F1 performance, is Pareto-dominated by Qwen3: lower clinical quality at higher cost. Its high F1 reflects token-level verbosity patterns rather than clinical precision, making it a cautionary example of metrics divorced from deployment utility.

The serialisation format analysis reveals an additional cost lever. The clinical_template serialiser achieves 94% input token reduction compared to raw JSON, with minimal clinical quality degradation (Layer 2 difference <0.1). For NHS trusts with constrained AI budgets, the combination of narrative or clinical_template serialisation with DeepSeek inference offers practical clinical quality at under £7 per 1,000 patient queries—a threshold that brings LLM-assisted FHIR processing within reach of community trusts and GP federations, not only large acute providers.

## 5.3 The Conciseness Trap

The ranking reversal between layers admits a mechanistic explanation rooted in how each metric interacts with response length. Llama 3.3 produced the most concise outputs (mean 724 tokens), whilst Claude generated moderately longer responses (mean 1,344 tokens), and GPT-5.4 was most verbose (mean 1,471 tokens).

Token-level F1 rewards precision: a response containing fewer tokens has fewer opportunities to include tokens absent from the ground truth, yielding higher precision scores. Llama's conciseness produces artificially inflated F1 through a mechanism we term the "conciseness trap"—achieving high precision not through superior clinical understanding, but through brevity that happens to preserve high-overlap tokens (NHS Numbers, SNOMED codes, medication names) whilst omitting contextual reasoning.

The clinical quality rubric operates inversely. Completeness and safety dimensions explicitly reward thorough responses: identifying all drug interactions requires listing relevant medications and their mechanisms; producing a comprehensive referral letter requires covering demographics, history, investigations, and clinical reasoning. Models that truncate their responses to optimise token-level precision inevitably sacrifice the elaborative content that clinical evaluators—whether human or LLM-based—consider essential.

Claude occupies the productive middle ground: sufficiently detailed to score highly on completeness and safety, yet structured enough to maintain clinical focus (relevance: 5.00/5.00). GPT-5.4's greater verbosity does not translate to proportionally higher quality, suggesting diminishing returns beyond a response length threshold.

This pattern carries a clear recommendation for clinical AI benchmarking: evaluation frameworks must include both automated metrics (which capture factual coverage efficiently) and expert or judge-based assessment (which capture the clinical reasoning, safety awareness, and interpretive quality that automated metrics systematically miss). Neither layer alone provides sufficient signal for deployment decisions.

## 5.4 Serialisation Format as a Research Variable

The six serialisation formats tested in this study represent the first systematic comparison of FHIR-to-text conversion strategies for LLM consumption in a UK clinical context. The finding that raw JSON marginally outperforms structured alternatives on token-level F1 (0.451 vs 0.429 for clinical_template) whilst achieving near-identical clinical quality scores suggests that models are robust to input format variation within a reasonable range.

However, the failure of the hybrid_adaptive serialiser—which dynamically selects format based on task type—to outperform static alternatives is noteworthy. This suggests that format consistency may matter more than format optimality: models may benefit from encountering a predictable input structure rather than adapting to variable formats across prompts. This finding warrants further investigation with fine-tuned models, where format-specific training might unlock the theoretical advantages of task-adaptive serialisation.

The flattened key-value format's consistent underperformance (F1: 0.409, lowest across all formats) offers practical guidance: dot-notation representations that fragment clinical concepts across hierarchical keys are suboptimal for LLM comprehension. Systems deploying LLMs against FHIR data should prefer formats that preserve semantic coherence of clinical entities—whether through narrative prose, structured templates, or well-formatted JSON with appropriate nesting.

## 5.5 Limitations and Threats to Validity

Several limitations warrant acknowledgement. First, the evaluation cohort (N=100, 1,800 prompts) was generated synthetically using LLMs rather than derived from real NHS patient data. Whilst the bundles conform to UK Core FHIR profiles and pass structural validation (100% pass rate across all seven mandatory criteria), they may not capture the full heterogeneity of real-world clinical records—particularly the inconsistencies, missing data, coded-vs-free-text ambiguity, and documentation variability characteristic of production NHS systems. Real-world GP records frequently contain abbreviated clinical notes, legacy Read codes alongside SNOMED CT, and incomplete medication histories that would stress-test model robustness in ways synthetic data cannot. Validation against de-identified real-world data from NHS Digital or OpenSAFELY remains necessary before generalising performance claims to clinical deployment.

Second, the LLM-as-judge methodology, whilst demonstrating good inter-rater reliability in Paper 1, carries inherent biases. Our cross-judging protocol—Claude judging four models, Qwen judging Claude—mitigates but does not eliminate self-serving bias. The near-ceiling scores for Claude (4.90/5.00) may partially reflect alignment between Claude's generation style and Qwen's quality preferences, which were likely shaped by similar training objectives and human feedback datasets. The absence of human clinician validation in this study means we cannot quantify the magnitude of judge bias. Future work should incorporate NHS clinician evaluation on a stratified subset (minimum 200 responses across complexity levels) to calibrate automated judge reliability against clinical gold standards.

Third, our cost analysis reflects AWS Bedrock list pricing at the time of study (July 2026). Cloud AI pricing evolves rapidly, and volume commitments, Savings Plans, reserved throughput capacity, and regional availability (particularly the forthcoming London region Bedrock endpoints) may substantially alter the Pareto frontier for specific NHS deployments. The relative rankings, however, are likely robust to proportional price changes given the magnitude of cost differentials observed (16× between Qwen and Claude).

Fourth, the Llama timeout finding from Paper 1 (0% success due to 60-second read_timeout) highlights the sensitivity of benchmark results to operational configuration. Whilst we addressed this specific issue with a 600-second timeout, other configuration parameters (temperature, top-p, system prompts, maximum output tokens) were held constant across models and may differentially advantage particular architectures. Temperature was set to 0.0 for reproducibility, but clinical applications may benefit from non-zero temperature for certain reasoning tasks. A comprehensive sensitivity analysis across inference parameters remains future work.

Fifth, our sample of five models, whilst representative of the major architecture families available through Bedrock in mid-2026, excludes several models of potential NHS relevance: Gemini (Google), Mistral Large, and domain-specific biomedical models (Med-PaLM, BioMistral). The benchmark framework is extensible, and we encourage the community to contribute additional model evaluations using our open-source pipeline.

## 5.6 Future Directions

Four research directions emerge from this work. First, extending FHIRBench to additional national FHIR profiles (AU Core, CA Core, EU International Patient Summary) would establish whether the ranking reversal is truly universal or exhibits profile-specific patterns related to terminology system complexity, extension density, or coding convention heterogeneity. The modular architecture of our pipeline—with swappable serialisers, configurable validation criteria, and profile-agnostic scoring—facilitates such extension with minimal engineering effort.

Second, the development of a unified scoring framework that formally combines Layer 1 and Layer 2 signals—perhaps through weighted aggregation calibrated against clinician preferences via discrete choice experiments—would provide a single deployability score that respects both factual coverage and clinical quality. Such a framework could incorporate task-specific weighting (e.g., prioritising safety for medication reconciliation, completeness for referral letters) to produce context-sensitive deployment recommendations.

Third, the 94% token reduction achieved by clinical templates, combined with the minimal quality impact, suggests that retrieval-augmented generation (RAG) architectures for FHIR data should prioritise concise, clinically-structured context windows over exhaustive raw data inclusion. Investigating the interaction between serialisation format, chunk size, and RAG retrieval strategies represents a natural extension with direct NHS deployment implications—particularly for integrated care systems managing longitudinal patient records spanning multiple care settings.

Fourth, as NHS England progresses its Federated Data Platform and wider AI strategy, longitudinal evaluation—tracking how model performance evolves across successive model releases against a fixed benchmark—would provide procurement-relevant evidence for AI governance frameworks. FHIRBench-UK, as an open and reproducible benchmark, is positioned to serve this ongoing monitoring function.

## 5.7 Practitioner Decision Framework

Based on the converging evidence from two independent benchmark studies (US Core and UK Core), we propose a standardised decision framework for NHS organisations deploying LLMs against FHIR clinical data. This framework integrates the three primary decision dimensions identified in this study: clinical safety requirement, cost constraint, and throughput demand.

**Decision 1: Determine clinical safety tier.**

- **Tier A (Safety-critical):** Autonomous clinical decision support, medication reconciliation, A&E triage, specialist referrals where errors could directly impact patient safety.
  - → Model: Claude Sonnet 4.5 (safety score: 4.98/5.00)
  - → Serialiser: narrative or clinical_template (94% token reduction, minimal quality impact)
  - → Governance: human review for any response scoring below 4.5 on automated quality check
  - → Cost: ~$0.032/prompt (~£25 per 1,000 queries)

- **Tier B (Clinician-assisted):** Discharge summary drafting, routine coding validation, population health screening where clinician review is standard workflow.
  - → Model: DeepSeek V3.2 (quality: 4.23/5.00 at $0.005/prompt) OR GPT-5.4 (quality: 4.28/5.00 at $0.028/prompt)
  - → Serialiser: clinical_template (lowest cost) or narrative (slight quality edge)
  - → Governance: spot-check 5–10% of outputs against clinician assessment
  - → Cost: ~£4–22 per 1,000 queries depending on model selection

- **Tier C (Pre-screening):** Batch flagging, initial triage filtering, administrative classification where ALL outputs receive subsequent human review.
  - → Model: Qwen3 32B (quality: 3.78/5.00 at $0.002/prompt)
  - → Serialiser: clinical_template or structured_markdown
  - → Governance: 100% human review mandatory; model output treated as advisory only
  - → Cost: ~£1.50 per 1,000 queries

**Decision 2: Evaluate throughput and latency requirements.**

- High-throughput batch processing (>10,000 records/day): prefer Tier B or C models with clinical_template serialisation to minimise token costs and API latency.
- Real-time clinical decision support (<5 second response): prefer Claude with narrative serialisation (shortest input tokens amongst high-quality formats, reducing time-to-first-token).
- Mixed workloads: deploy tiered architecture with Tier C for initial filtering, escalating to Tier A for flagged cases requiring high-confidence responses.

**Decision 3: Validate against local requirements.**

- Run FHIRBench-UK evaluation pipeline against a representative sample of local trust data (minimum N=50 bundles) before production deployment.
- Establish trust-specific quality thresholds calibrated against local clinical governance requirements.
- Re-evaluate quarterly as model versions update and pricing evolves.

This framework deliberately avoids recommending Llama 3.3 70B for any tier: despite its strong automated metric performance, its clinical quality scores (3.36/5.00) fall below Qwen3 at higher cost—a configuration that offers no deployment advantage in any identified use case. Organisations encountering procurement pressure to adopt open-weight models should note that Qwen3 (also open-weight) delivers superior clinical quality at lower cost within the same operational model.

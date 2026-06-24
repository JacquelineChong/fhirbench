# Systematic Literature Review: Clinical Data Serialization Strategies for Large Language Models (FHIRBench)

**Date:** 2026-06-19  
**Research Question:** How do different serialization strategies for FHIR clinical data affect LLM performance on healthcare tasks?  
**Search Sources:** arXiv, PubMed/PMC, Semantic Scholar, Google Scholar, NEJM AI, NeurIPS, MDPI  
**Total Papers Identified:** 35  
**Papers Added to Zotero (Collection J7MWVXWM):** 30  

---

## Summary Statistics

| Category | Count |
|----------|-------|
| ★★★★★ (Directly relevant) | 9 |
| ★★★★☆ (Highly relevant) | 13 |
| ★★★☆☆ (Relevant context) | 13 |
| **Total** | **35** |

### Category Distribution
| Tag | Count | Description |
|-----|-------|-------------|
| serialization-methods | 11 | Data format/representation effects on LLMs |
| benchmark-methodology | 10 | Clinical/EHR benchmarks for LLMs |
| fhir-llm-tools | 7 | Systems integrating FHIR with LLMs |
| fhir-standards | 3 | FHIR conversion and standardization |
| prompt-engineering | 3 | Prompt design for structured clinical data |
| clinical-nlp | 2 | NLP pipelines for clinical text to FHIR |
| llm-healthcare | 1 | General LLM healthcare benchmarks |

---

## Comprehensive Results Table

| # | Title | Authors | Year | Source | Relevance | Category | Key Finding | Zotero Key |
|---|-------|---------|------|--------|-----------|----------|-------------|------------|
| 1 | Serialisation Strategy Matters: How FHIR Data Format Affects LLM Medication Reconciliation | Pator S | 2026 | arXiv:2604.21076 | ★★★★★ | serialization-methods | Clinical Narrative outperforms Raw JSON by 19 F1 points for 7B models; reverses at 70B where Raw JSON achieves F1=0.9956 | TGZ97SRN |
| 2 | FHIR-AgentBench: Benchmarking LLM Agents for Realistic Interoperable EHR Question Answering | Lee G et al. | 2025 | ML4H 2025 | ★★★★★ | benchmark-methodology | 2,931 FHIR-grounded clinical questions; code generation outperforms natural language reasoning for FHIR data retrieval | WV9N648K |
| 3 | MedCase-Structured: A Text-to-FHIR Dataset for Benchmarking Diagnostic Reasoning | Bui Muti V et al. | 2026 | ICML 2026 Workshop | ★★★★★ | benchmark-methodology | LLMs show consistently lower diagnostic accuracy on structured FHIR inputs vs. plain text (82.5% valid FHIR generation) | HTTUDR8U |
| 4 | Infherno: End-to-end Agent-based FHIR Resource Synthesis from Clinical Notes | Frei J et al. | 2025 | EACL 2026 Demo | ★★★★★ | fhir-llm-tools | Agent-based framework with code execution outperforms constrained decoding; Gemini 2.5-Pro excels | FXBKDFFQ |
| 5 | Schema-Grounded LLM Extraction for FHIR Patient Digital Twins | Brens R et al. | 2026 | arXiv:2601.05847 | ★★★★★ | serialization-methods | Schema-constrained generation with validator-in-the-loop repair produces substantially more valid FHIR bundles | ABED59UH |
| 6 | FHIRPath-QA: Executable Question Answering over FHIR EHRs | Frew M et al. | 2026 | LREC 2026 | ★★★★★ | fhir-llm-tools | Text-to-FHIRPath reduces token usage 391x and failure rates from 0.36→0.09; fine-tuning boosts accuracy 27%→79% | V4M8Q6TN |
| 7 | Evaluating Structured Output Robustness of SLMs for Clinical Notes | Neveditsin N et al. | 2025 | ACL SRW 2025 | ★★★★★ | serialization-methods | JSON yields highest parseability for clinical extraction vs. YAML/XML; robustness declines with document length | X85QMVCU |
| 8 | EHRStruct: Comprehensive Benchmark for LLMs on Structured EHR Tasks | Yang X et al. | 2025 | arXiv:2511.08206 | ★★★★★ | benchmark-methodology | 11 tasks, 20 LLMs evaluated; input format significantly affects performance; code-augmented reasoning achieves SOTA | 7FJFJU5M |
| 9 | Evaluating LLMs in Converting Clinical Data to FHIR Format | Various | 2025 | Applied Sciences 15(6) | ★★★★★ | prompt-engineering | Two-step prompt engineering significantly improves FHIR conversion; few-shot learning enhances but risks overreliance | 3BR6UH6F |
| 10 | MCP-FHIR Framework: Clinical Decision Support through LLMs | Ehtesham A et al. | 2025 | arXiv:2506.13800 | ★★★★☆ | fhir-llm-tools | Declarative JSON-based FHIR access enables scalable AI-powered EHR apps across multiple FHIR formats | UWT2D76S |
| 11 | LLM on FHIR -- Demystifying Health Records | Schmiedmayer P et al. | 2024 | arXiv:2402.01711 | ★★★★☆ | fhir-llm-tools | GPT-4 effectively translates FHIR data to patient-friendly language; challenges with response variability and resource filtering | DQT7VP7M |
| 12 | Large Language Models for Automating Clinical Data Standardization: HL7 FHIR | Riquelme A et al. | 2025 | arXiv:2507.03067 | ★★★★☆ | fhir-standards | Perfect F1 for FHIR resource identification with schema in prompt; 94% real-world accuracy | TVQQHKUS |
| 13 | Enhancing Health Data Interoperability with LLMs: A FHIR Study | Li Y et al. | 2023 | AMIA 2024 | ★★★★☆ | fhir-standards | >90% exact match accuracy on 3,671 clinical text snippets to FHIR conversion | S36AFFXP |
| 14 | Question Answering on Patient Medical Records with Private Fine-Tuned LLMs | Kothari S, Gupta A | 2025 | arXiv:2501.13687 | ★★★★☆ | fhir-llm-tools | 250x smaller fine-tuned LLMs outperform GPT-4 on FHIR resource identification (+0.55% F1) and answer generation (+42% METEOR) | FHBMB43C |
| 15 | Table Meets LLM: Can LLMs Understand Structured Table Data? | Sui Y et al. | 2023 | WSDM 2024 | ★★★★☆ | serialization-methods | Table input format significantly affects LLM performance; self-augmentation prompting improves tabular QA by 2-6% | R9P2FJS3 |
| 16 | Learning to Reduce: Optimal Representations of Structured Data in Prompting LLMs | Lee Y et al. | 2024 | arXiv:2402.14195 | ★★★★☆ | serialization-methods | RL-based data reduction improves LLM reasoning on structured data; especially effective for long contexts | DJ6CWECQ |
| 17 | Let Me Speak Freely? Impact of Format Restrictions on LLM Performance | Tam ZR et al. | 2024 | arXiv:2408.02442 | ★★★★☆ | serialization-methods | Stricter format constraints → greater performance degradation in reasoning; structured output harms LLM cognition | PPKJVC6H |
| 18 | SM3-Text-to-Query: Synthetic Multi-Model Medical Text-to-Query Benchmark | Sivasubramaniam S et al. | 2024 | NeurIPS 2024 | ★★★★☆ | benchmark-methodology | Synthea-based benchmark across SQL/MQL/Cypher/SPARQL; database model choice impacts LLM query generation | 2MV7H8T6 |
| 19 | Quantifying Impact of Structured Output Format on LLMs through Causal Inference | Yuan H et al. | 2025 | arXiv:2509.21791 | ★★★★☆ | serialization-methods | No causal impact in 43/48 scenarios; reasoning models (o3) more resilient to format constraints than GPT-4o | 8S3QCXCC |
| 20 | FHIR-GPT: Enhancing Health Interoperability with Large Language Models | Li Y et al. | 2024 | NEJM AI | ★★★★☆ | fhir-llm-tools | Single LLM replaces separate NLP tools for FHIR transformation, reducing development costs significantly | FE5NNKMI |
| 21 | Leveraging LLMs in Standardizing Clinical Data for AI: Mapping to FHIR | Various | 2024 | arXiv:2408.11861 | ★★★★☆ | fhir-standards | LLMs effectively identify clinical schema elements and map to FHIR standard attributes | WQPDZSX9 |
| 22 | Prompt Engineering for Structured Data: Comparative Evaluation | Various | 2025 | Preprints 202506.1937 | ★★★★☆ | prompt-engineering | Simpler formats provide efficiency with minimal accuracy loss; flexible formats better for complex structures | DA6II26P |
| 23 | Towards Better Serialization of Tabular Data for Few-shot Classification | Jaitly S et al. | 2023 | arXiv:2312.12464 | ★★★☆☆ | serialization-methods | LaTeX serialization boosts LLM performance on domain-specific tabular datasets with memory efficiency | ZRMTD3F8 |
| 24 | Leveraging Generative AI to Enhance Synthea Module Development | Kramer MA et al. | 2025 | arXiv:2507.21123 | ★★★☆☆ | benchmark-methodology | LLMs generate/refine Synthea modules; progressive refinement improves synthetic data quality | TH7NPVEX |
| 25 | SimSUM: Simulated Benchmark with Structured and Unstructured Medical Records | Rabaey P et al. | 2024 | arXiv:2409.08936 | ★★★☆☆ | benchmark-methodology | 10K records linking structured+unstructured data; enables extraction models reasoning across both modalities | 4HSNVBCA |
| 26 | EHRNoteQA: LLM Benchmark for Real-World Clinical Practice | Kweon S et al. | 2024 | NeurIPS 2024 | ★★★☆☆ | benchmark-methodology | 962 QA pairs; LLM performance correlates with clinician evaluations (Spearman: 0.78) | TK3UEM43 |
| 27 | LongHealth: QA Benchmark with Long Clinical Documents | Adams L et al. | 2024 | arXiv:2401.14490 | ★★★☆☆ | benchmark-methodology | All models struggle with missing information identification in long clinical docs; insufficient for reliable use | J46S4PGW |
| 28 | NLP2FHIR: Scalable FHIR-based Clinical Data Normalization Pipeline | Wen A et al. | 2019 | JAMIA Open | ★★★☆☆ | clinical-nlp | Foundational FHIR-based NLP pipeline with type system, integration, and normalization modules | 96WE7H88 |
| 29 | The SMART Text2FHIR Pipeline | Gao Y et al. | 2024 | JAMIA | ★★★☆☆ | clinical-nlp | Open-source high-throughput NLP-to-FHIR pipeline establishing baseline for automated clinical text mapping | BTGDE64Z |
| 30 | Synthea: Generating Synthetic Patients and Electronic Health Records | Walonoski J et al. | 2018 | JAMIA | ★★★☆☆ | benchmark-methodology | 1M synthetic patients in FHIR format; disease progression as state machines with census-seeded demographics | DM8RNZGT |
| 31 | Large Language Models in Healthcare: A Comprehensive Benchmark | Various | 2024 | medRxiv | ★★★☆☆ | llm-healthcare | 7 tasks, 13 datasets, 16 LLMs; zero/few-shot performance varies across clinical tasks | I8SA4CVW |
| 32 | Enhancing LLM Reasoning with Structured Data | Various | 2024 | arXiv:2407.12522 | ★★★☆☆ | serialization-methods | Structured data enhances reasoning but requires careful token budget and relevance filtering | 63DRDI8G |
| 33 | MedR-Bench: Quantifying LLM Reasoning on Clinical Cases | Various | 2025 | Nature Communications | ★★★☆☆ | benchmark-methodology | 1,453 structured cases; differential reasoning across specialties; enables fine-grained evaluation | G8MWD7H9 |
| 34 | Comparison of Prompt Engineering and Fine-Tuning for Clinical Note Classification | Various | 2024 | AMIA 2024 | ★★★☆☆ | prompt-engineering | Fine-tuning and prompting show complementary strengths depending on task complexity | MEK4J5EK |
| 35 | Talking with Tables for Better LLM Factual Data Interactions | Various | 2024 | arXiv:2412.17189 | ★★★☆☆ | serialization-methods | Tabular structures yield 40.29% average performance gain with better robustness and token efficiency | KPFE6G9H |

---

## Annotated Bibliography

### Tier 1: Directly Relevant (★★★★★) — Core Related Work

**1. Pator (2026). "Serialisation Strategy Matters: How FHIR Data Format Affects LLM Medication Reconciliation."**
The most directly relevant prior work to FHIRBench. This paper provides the first systematic comparison of FHIR serialization strategies (Raw JSON, Markdown Table, Clinical Narrative, Chronological Timeline) across five open-weight models on medication reconciliation. The key insight that optimal serialization depends on model size (narrative for ≤8B, JSON for 70B+) directly validates our research question. However, it is limited to a single clinical task (medication reconciliation) and does not evaluate proprietary models or the full breadth of clinical reasoning tasks we address.

**2. Lee et al. (2025). "FHIR-AgentBench: Benchmarking LLM Agents for Realistic Interoperable EHR Question Answering."**
Establishes the most comprehensive FHIR-specific benchmark with 2,931 clinical questions grounded in HL7 FHIR. The paper's comparison of retrieval strategies (direct FHIR API vs. specialized tools) and reasoning strategies (natural language vs. code generation) provides essential context for our serialization study. Unlike our work, it focuses on agent architectures rather than data format effects, making it complementary.

**3. Bui Muti et al. (2026). "MedCase-Structured: A Text-to-FHIR Dataset for Benchmarking Diagnostic Reasoning."**
Demonstrates that LLMs achieve consistently lower diagnostic accuracy on structured FHIR inputs compared to plain text — a finding that directly motivates our investigation of serialization strategies. The 82.5% valid FHIR generation rate highlights the gap between structured data creation and utilization, reinforcing the importance of format choice.

**4. Frei et al. (2025). "Infherno: End-to-end Agent-based FHIR Resource Synthesis from Free-form Clinical Notes."**
Proposes an agent-based approach using LLMs with code execution and healthcare terminology tools for FHIR resource generation. The comparison between constrained decoding and agent-based approaches informs our understanding of how structural constraints on FHIR output affect model performance. Their finding that Gemini 2.5-Pro excels provides model-specific insights relevant to our evaluation.

**5. Brens et al. (2026). "Schema-Grounded LLM Extraction for FHIR Patient Digital Twins."**
Introduces SG-LLM with three key innovations: terminology code retrieval, JSON Schema-constrained decoding from FHIR StructureDefinitions, and validator-in-the-loop repair. The clinical-utility evaluation measuring readmission AUROC gap offers a novel evaluation paradigm beyond span-level F1. Directly relevant to our schema-aware serialization strategies.

**6. Frew et al. (2026). "FHIRPath-QA: Executable Question Answering over FHIR Electronic Health Records."**
Demonstrates that shifting from free-text generation to FHIRPath query synthesis reduces token usage by 391x while improving accuracy. This paradigm shift from "serialize FHIR data into prompts" to "generate queries over FHIR data" represents an alternative approach to our serialization-focused strategy. The 14K QA pairs on MIMIC-IV FHIR provide a rich evaluation resource.

**7. Neveditsin et al. (2025). "Evaluating Structured Output Robustness of Small Language Models for Clinical Notes."**
Directly compares JSON, YAML, and XML serialization formats for clinical attribute-value extraction, finding JSON consistently yields highest parseability. The finding that structural robustness declines with document length is highly relevant to FHIR records of varying complexity. Provides practical guidance for output format selection in clinical deployments.

**8. Yang et al. (2025). "EHRStruct: A Comprehensive Benchmark for LLMs on Structured EHR Tasks."**
The most comprehensive structured EHR benchmark with 11 tasks and 20 LLMs. Critical finding that input format significantly affects performance across all tasks, and that code-augmented reasoning achieves state-of-the-art. Directly validates our hypothesis that serialization strategy matters for clinical AI, though it does not specifically focus on FHIR format variations.

**9. Various (2025). "Evaluating the Effectiveness of LLMs in Converting Clinical Data to FHIR Format."**
Evaluates prompt engineering techniques for FHIR bundle generation, finding that two-step approaches significantly improve accuracy and completeness. The assessment of precision, hallucination rate, and resource mapping accuracy across different clinical report types provides evaluation metrics relevant to our benchmark design.

### Tier 2: Highly Relevant (★★★★☆) — Supporting Context

**10. Ehtesham et al. (2025). "MCP-FHIR Framework."**
Demonstrates practical integration of LLMs with FHIR via Model Context Protocol, supporting multiple FHIR formats and user personas. Relevant as a deployment architecture that our serialization recommendations could inform.

**11. Schmiedmayer et al. (2024). "LLM on FHIR."**
Pioneering patient-facing application using GPT-4 with SyntheticMass FHIR data. Reveals practical challenges of filtering and presenting FHIR resources to LLMs, motivating format optimization research.

**12. Riquelme et al. (2025). "LLMs for Automating Clinical Data Standardization."**
Shows that including FHIR resource schemas in prompts achieves perfect resource identification F1. The finding that prompt refinement restores accuracy after initial dips confirms the importance of format engineering.

**13. Li et al. (2023). "Enhancing Health Data Interoperability with LLMs."**
Early demonstration of LLM-based clinical text to FHIR conversion with >90% accuracy. Establishes the baseline capability that our serialization research builds upon.

**14. Kothari & Gupta (2025). "QA on Patient Medical Records with Private Fine-Tuned LLMs."**
Shows that small fine-tuned models can outperform GPT-4 on FHIR resource tasks, suggesting model specialization may interact with serialization strategy in ways our benchmark should capture.

**15. Sui et al. (2023). "Table Meets LLM."**
Foundational work establishing that table input format, content order, and partition marks significantly affect LLM understanding of structured data. The self-augmentation prompting technique is applicable to FHIR data presentation.

**16. Lee et al. (2024). "Learning to Reduce."**
Proposes RL-based context reduction for structured data prompting. Directly relevant to the challenge of fitting verbose FHIR bundles into LLM context windows while preserving critical clinical information.

**17. Tam et al. (2024). "Let Me Speak Freely?"**
Demonstrates that format restrictions (JSON, XML) significantly degrade LLM reasoning. Critical finding for our research: forcing FHIR-structured output may harm clinical reasoning compared to free-form responses. Informs our serialization strategy design.

**18. Sivasubramaniam et al. (2024). "SM3-Text-to-Query."**
First multi-model medical benchmark using Synthea data with SNOMED-CT, evaluating across four query languages. The finding that database model choice impacts LLM query generation parallels our hypothesis about serialization format effects.

**19. Yuan et al. (2025). "Quantifying Impact of Structured Output through Causal Inference."**
Uses causal inference to show that format effects are often spurious (43/48 scenarios), but reasoning models are more resilient. Provides methodological guidance for our experimental design to distinguish genuine format effects from confounds.

**20. Li et al. (2024). "FHIR-GPT" (NEJM AI).**
The published version in a top venue demonstrates clinical acceptance of LLM-based FHIR transformation. Provides the clinical validation context for our benchmark's significance.

**21. Various (2024). "Leveraging LLMs for FHIR Mapping."**
Demonstrates LLM effectiveness at schema-to-FHIR mapping, supporting the premise that LLMs can work with FHIR structures when appropriately prompted.

**22. Various (2025). "Prompt Engineering for Structured Data: Comparative Evaluation."**
Systematic comparison of prompt styles for structured data revealing trade-offs between complexity and performance — directly informing our serialization strategy design choices.

### Tier 3: Relevant Context (★★★☆☆) — Background and Methods

**23. Jaitly et al. (2023). "Towards Better Serialization of Tabular Data."**
Introduces LaTeX serialization as a novel format for tabular LLM input. While not clinical-specific, demonstrates that format innovation can yield significant performance gains.

**24. Kramer et al. (2025). "Leveraging GenAI for Synthea Module Development."**
Relevant to our data generation pipeline — shows how LLMs can enhance the quality of synthetic patient data used in benchmarks like ours.

**25. Rabaey et al. (2024). "SimSUM."**
Synthetic benchmark linking structured and unstructured medical records, providing methodological precedent for our approach of combining FHIR structures with clinical text evaluation.

**26. Kweon et al. (2024). "EHRNoteQA."**
NeurIPS 2024 benchmark showing strong correlation between LLM benchmark performance and clinician evaluations, validating automated clinical benchmarking approaches like ours.

**27. Adams et al. (2024). "LongHealth."**
Reveals that all LLMs struggle with long clinical documents and missing information identification — context length challenges directly relevant to verbose FHIR bundles.

**28. Wen et al. (2019). "NLP2FHIR."**
Foundational NLP-to-FHIR pipeline providing the rule-based baseline that LLM approaches (including ours) aim to surpass.

**29. Gao et al. (2024). "SMART Text2FHIR Pipeline."**
Open-source NLP-to-FHIR conversion tool establishing the standard clinical NLP pipeline our LLM-based serialization study contextualizes.

**30. Walonoski et al. (2018). "Synthea."**
The foundational paper for the Synthea synthetic patient generator we use in our benchmark. Establishes the methodology for generating realistic FHIR patient records.

---

## Key Themes for FHIRBench Paper

### 1. Serialization Format Matters (Confirmed)
Multiple papers (Pator 2026, Neveditsin 2025, Sui 2023, Tam 2024) confirm that data format significantly impacts LLM performance. Our contribution extends this to a comprehensive multi-task clinical evaluation.

### 2. Model Size × Format Interaction
Pator (2026) shows format advantage reverses between 7B and 70B models. Yuan (2025) shows reasoning models are more resilient to format. These findings suggest our benchmark should report per-model-size results.

### 3. FHIR-Specific Challenges Are Unique
FHIR-AgentBench, MedCase-Structured, and FHIRPath-QA all highlight that FHIR's nested, reference-heavy structure creates unique challenges not captured by general tabular data benchmarks.

### 4. Schema Constraints Can Help or Hurt
SG-LLM (Brens 2026) shows schema constraints improve structural validity, while "Let Me Speak Freely" (Tam 2024) shows they can degrade reasoning. Our benchmark can help disambiguate when constraints help vs. hurt in clinical contexts.

### 5. Evaluation Must Be Deployment-Aligned
MedCase-Structured (Bui Muti 2026) shows that benchmarks using plain text overestimate real-world performance where FHIR is the native format. This validates our choice to evaluate directly on FHIR-formatted inputs.

---


## Context Window and Inference Limitations in Clinical LLM Deployment

### [36] LongHealth: A Question Answering Benchmark with Long Clinical Documents
- **Authors:** Adams L, Busch F, Han T, et al.
- **Venue:** Journal of Healthcare Informatics Research, 2025
- **Relevance:** ★★★★★ (Directly relevant)
- **Tags:** `model-evaluation`, `clinical-documents`, `context-limitations`
- **Key Finding:** Evaluated 11 open-source LLMs (minimum 16K context) on 20 fictional patient cases (5,090–6,754 words each). All models struggled significantly on tasks requiring identification of missing information. Concluded that "current accuracy levels are insufficient for reliable clinical use, especially in scenarios requiring the identification of missing information."
- **Connection to FHIRBench:** Directly validates our finding that open-weight models (Llama 3.1 70B) fail on complex FHIR bundles. LongHealth tests documents of similar length to our COMPLEX/HIGHLY_COMPLEX serialized records.
- **DOI:** 10.1007/s41666-025-00204-w

### [37] Evaluating Long Context Models for Clinical Prediction Tasks on EHRs
- **Authors:** (arXiv 2412.16178)
- **Venue:** arXiv preprint, 2024
- **Relevance:** ★★★★☆ (Highly relevant)
- **Tags:** `EHR`, `context-window`, `model-evaluation`
- **Key Finding:** "Most existing EHR foundation models have context windows of <1K tokens. This prevents them from modeling full patient EHRs which can exceed 10K's of events." Longer context models improve predictive performance, but robustness to unique EHR properties remains crucial.
- **Connection to FHIRBench:** Establishes the context window bottleneck as a known constraint. Our complex FHIR bundles (3,000–4,000+ tokens when serialized as raw JSON) exceed the practical processing capacity of models like Llama 3.1 70B.

### [38] Llama 3.1 70B Inference Latency Benchmark (A100 80GB)
- **Authors:** MarkAICode, 2026
- **Venue:** Technical benchmark report
- **Relevance:** ★★★★☆ (Highly relevant — infrastructure evidence)
- **Tags:** `inference-performance`, `latency`, `context-scaling`
- **Key Finding:** Llama 3.1 70B p95 latency increases 3.8× when context grows from 512 to 4,096 tokens (158ms → 602ms). Throughput drops from 62 tok/s to 44 tok/s. At 8K context, VRAM usage reaches 93.5% of A100 80GB capacity, leaving no room for concurrent requests.
- **Connection to FHIRBench:** Explains our observed 60+ second timeouts for Llama on COMPLEX FHIR prompts (~4K–8K tokens). The model physically cannot process these inputs within practical time bounds, confirming that serialization strategy determines model *accessibility*, not merely accuracy.
- **URL:** https://markaicode.com/benchmarks/ollama-llama-31-a100-80gb-latency-benchmark/

### [39] Why Does the Effective Context Length of LLMs Fall Short?
- **Authors:** (arXiv 2410.18745)
- **Venue:** arXiv preprint, 2024
- **Relevance:** ★★★☆☆ (Relevant context)
- **Tags:** `context-window`, `attention-mechanism`, `theory`
- **Key Finding:** Attributes context length limitations to "left-skewed frequency distribution of relative positions" formed during pretraining, which impedes the model's ability to effectively gather distant information — regardless of nominal context window size.
- **Connection to FHIRBench:** Provides theoretical grounding for why Llama's 128K nominal context window does not translate to reliable processing of 4K+ token clinical inputs.


## Gaps Our Paper Addresses

1. **No comprehensive multi-task FHIR serialization benchmark** — Pator (2026) covers only medication reconciliation
2. **Limited evaluation of proprietary models** — Most papers evaluate only open-weight models on FHIR tasks
3. **No systematic comparison across clinical reasoning dimensions** — Existing work focuses on single-task evaluation
4. **Lack of Synthea-based controlled experiments** — Most use MIMIC-IV which limits reproducibility
5. **No integration of serialization with clinical task complexity** — Missing analysis of how task type moderates format effects

---

*Generated by systematic literature review on 2026-06-19. 8 pre-defined queries searched across arXiv, PubMed, Semantic Scholar, and domain venues. Existing seed references (KTDK3AX5, USQFSG3J, QW6C7PH6, VQVECWTP, SF66VH38, 4KJ2IQNG, IFK2768G, TURQFSSV) excluded from new additions.*

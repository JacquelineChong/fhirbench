# FHIRBench — User Stories

## Epic 1: Data Generation

### Story 1.1: Generate Synthetic FHIR Bundles
**As a** researcher  
**I want to** generate 1,000 synthetic patient FHIR R4 bundles with Synthea  
**So that** I have reproducible test data covering my target clinical domains

**Acceptance Criteria:**
- [ ] Synthea generates 1,000 patients with realistic clinical histories
- [ ] Patients cover: diabetes (250), cardiovascular (250), medication interactions (250), preventive care (250)
- [ ] Output is valid FHIR R4 JSON bundles
- [ ] A manifest CSV lists patient IDs, conditions, resource counts
- [ ] Generation is reproducible with a fixed seed

### Story 1.2: Load and Validate FHIR Data
**As a** researcher  
**I want to** load FHIR bundles and validate them against the R4 spec  
**So that** I know my test data is well-formed before serialization

**Acceptance Criteria:**
- [ ] `fhir_loader.py` reads bundles from `data/fhir_bundles/`
- [ ] Validates against FHIR R4 resource schemas using `fhir.resources`
- [ ] Reports validation errors with resource type and patient ID
- [ ] Returns typed Python objects for downstream processing

---

## Epic 2: Serialization Pipeline

### Story 2.1: Implement Raw JSON Serializer (Baseline)
**As a** researcher  
**I want to** pass unmodified FHIR JSON as the baseline serialization  
**So that** I can measure how much other strategies improve over raw data

**Acceptance Criteria:**
- [ ] Returns `json.dumps(bundle, indent=2)` of the FHIR bundle
- [ ] Optionally filters to relevant resource types for the task
- [ ] Reports token count for the serialized output
- [ ] Handles bundles exceeding context window with truncation

### Story 2.2: Implement Flattened Key-Value Serializer
**As a** researcher  
**I want to** flatten FHIR JSON into dot-notation key-value pairs  
**So that** I can test whether structural simplification helps LLM comprehension

**Acceptance Criteria:**
- [ ] Converts nested FHIR JSON to `resource.path.key = value` format
- [ ] Handles arrays with index notation: `patient.name[0].given = "John"`
- [ ] Resolves terminology codes to display text (configurable)
- [ ] Produces compact output (~40-60% fewer tokens than raw JSON)

### Story 2.3: Implement Natural Language Narrative Serializer
**As a** researcher  
**I want to** convert FHIR data into natural language prose  
**So that** I can test whether LLMs perform better with "human-readable" input

**Acceptance Criteria:**
- [ ] Converts Patient → "John Smith is a 45-year-old male..."
- [ ] Converts Conditions → "The patient has been diagnosed with Type 2 Diabetes..."
- [ ] Converts Medications → "Currently taking Metformin 500mg twice daily..."
- [ ] Maintains clinical accuracy — no hallucinated details
- [ ] Uses Bedrock (Claude) for high-quality narrative generation

### Story 2.4: Implement Structured Markdown Serializer
**As a** researcher  
**I want to** convert FHIR data into hierarchical markdown  
**So that** I can test whether structured formatting aids LLM reasoning

**Acceptance Criteria:**
- [ ] Uses headers (##) for resource types, tables for observations
- [ ] Groups related resources (all medications together, all conditions together)
- [ ] Includes timeline information where relevant
- [ ] Token-efficient compared to narrative (~30% fewer tokens)

### Story 2.5: Implement Clinical Summary Template Serializer
**As a** researcher  
**I want to** convert FHIR data into standard clinical formats (SOAP note, problem list)  
**So that** I can test whether domain-specific templates improve accuracy

**Acceptance Criteria:**
- [ ] Supports SOAP note format
- [ ] Supports Problem List format
- [ ] Supports Medication Reconciliation format
- [ ] Template selection configurable per task type
- [ ] Fills templates from FHIR resources programmatically

### Story 2.6: Implement Hybrid Adaptive Serializer
**As a** researcher  
**I want to** dynamically select the best serialization per task type  
**So that** I can test whether task-aware preprocessing is worth the complexity

**Acceptance Criteria:**
- [ ] Routes Clinical QA → Flattened KV (fast lookup)
- [ ] Routes Clinical Reasoning → Structured Markdown (reasoning chains)
- [ ] Routes Summarization → Clinical Template (domain format)
- [ ] Decision logic is configurable via rules or learned routing
- [ ] Reports which strategy was selected for each prompt

---

## Epic 3: Evaluation Tasks

### Story 3.1: Build Clinical QA Task Set
**As a** researcher  
**I want to** generate factual questions with ground truth answers from FHIR data  
**So that** I can measure accuracy across serialization strategies

**Acceptance Criteria:**
- [ ] 50 questions per clinical domain (200 total)
- [ ] Questions cover: medication lists, diagnoses, lab values, demographics, procedures
- [ ] Ground truth extracted programmatically from FHIR bundles
- [ ] Scoring: exact match + semantic similarity (for paraphrased answers)

### Story 3.2: Build Clinical Reasoning Task Set
**As a** researcher  
**I want to** create inference tasks requiring multi-step clinical reasoning  
**So that** I can measure whether serialization affects reasoning quality

**Acceptance Criteria:**
- [ ] Tasks: drug interaction detection, risk stratification, care gap identification
- [ ] Ground truth validated against clinical guidelines
- [ ] Scoring rubric: 0-5 scale for clinical correctness
- [ ] Rubric dimensions: accuracy, completeness, clinical relevance, safety

### Story 3.3: Build Clinical Summarization Task Set
**As a** researcher  
**I want to** evaluate patient summary generation quality  
**So that** I can measure serialization impact on generative tasks

**Acceptance Criteria:**
- [ ] Tasks: discharge summary, care plan, handoff note, patient-facing summary
- [ ] Reference summaries written by clinical guidelines (not human-written)
- [ ] Scoring: ROUGE-L + structured preference (completeness, accuracy, readability)
- [ ] Reports hallucination rate (claims not in source data)

---

## Epic 4: Benchmark Runner

### Story 4.1: Orchestrate Full Experimental Matrix
**As a** researcher  
**I want to** run all 72 conditions (6 × 4 × 3) with progress tracking  
**So that** I can complete the benchmark with experiment tracking

**Acceptance Criteria:**
- [ ] Runs all serializer × model × task combinations
- [ ] Checkpoints results after each condition (resume on failure)
- [ ] Tracks: prompts sent, responses received, scores, token counts, latency
- [ ] Exports results to JSON + CSV for analysis
- [ ] Configurable parallelism for Bedrock calls (respects rate limits)

### Story 4.2: Model Client Integration
**As a** researcher  
**I want to** call all 4 models through a unified interface  
**So that** model-specific logic doesn't contaminate my evaluation code

**Acceptance Criteria:**
- [ ] `bedrock_client.py` handles Claude + Llama 3 via `boto3`
- [ ] `openai_client.py` handles GPT-5.4 via `openai` SDK
- [ ] `google_client.py` handles Qwen3 via `google-generativeai` SDK
- [ ] All clients implement `generate(prompt, config) -> ModelResponse`
- [ ] Retry logic with exponential backoff for rate limits

---

## Epic 5: Analysis & Reporting

### Story 5.1: Statistical Analysis
**As a** researcher  
**I want to** perform rigorous statistical comparison across conditions  
**So that** I can make valid claims about serialization strategy impact

**Acceptance Criteria:**
- [ ] Two-way ANOVA (serializer × model) per task type
- [ ] Post-hoc pairwise comparisons (Tukey HSD)
- [ ] Effect sizes (Cohen's d) for key comparisons
- [ ] Confidence intervals for all reported metrics
- [ ] Results formatted for LaTeX tables

### Story 5.2: Pareto Frontier Visualization
**As a** researcher  
**I want to** plot accuracy vs. token cost tradeoffs  
**So that** I can identify the optimal strategies for practitioners

**Acceptance Criteria:**
- [ ] Scatter plot: x=token cost, y=accuracy for each strategy
- [ ] Pareto frontier line highlighted
- [ ] Per-model and per-task variants
- [ ] Publication-quality figures (300 DPI, clean labels)
- [ ] Saved as PDF + PNG for paper inclusion

### Story 5.3: Decision Framework Generation
**As a** researcher  
**I want to** generate a practitioner decision matrix  
**So that** teams can select the right serialization for their use case

**Acceptance Criteria:**
- [ ] Matrix: task type × constraint (latency/cost/accuracy) → recommended strategy
- [ ] Includes confidence levels for each recommendation
- [ ] Formatted as a visual table for the paper
- [ ] Exportable as standalone reference card (PDF)

## 5.4 Implications for Health Data Interoperability Architecture

Our findings raise a broader question that extends beyond serialization optimization: whether the current health data interoperability paradigm — structured exchange formats consumed by increasingly capable AI systems — represents an architectural mismatch that will intensify as LLMs become primary data consumers in clinical workflows.

### The Interoperability Paradox

FHIR was designed to solve machine-to-machine interoperability — enabling deterministic parsing, schema validation, and cross-resource reference resolution between heterogeneous clinical software systems [CITE:IFK2768G]. The ONC Cures Act and TEFCA mandate FHIR APIs specifically to enable programmatic data exchange [CITE:TURQFSSV]. However, our Pareto analysis reveals that 56–63% of tokens in raw FHIR JSON encode structural overhead — profile URLs, extension metadata, narrative divs, conformance elements — with no contribution to clinical reasoning accuracy. This overhead represents a direct cost when LLMs are the downstream consumer: every structural token displaces a clinically relevant token within finite context windows.

This creates a paradox: regulators mandate structured data (FHIR) for exchange, yet the AI systems increasingly consuming that data perform optimally when it is de-structured into narrative or semi-structured formats. Healthcare is simultaneously investing in structuring clinical data *for machines* while deploying AI that comprehends data *like humans*.

### Three Evolutionary Paths

Our empirical findings inform three possible futures for health data interoperability:

**Path A: Persistent Serialization Middleware (Near-Term).** FHIR remains the exchange standard; serialization constitutes a permanent optimization layer between storage and AI consumption. FHIRBench directly serves this path by providing evidence-based strategy selection. The finding that optimal format varies by model scale [CITE:TGZ97SRN] and task type implies this middleware must be adaptive rather than static.

**Path B: Write-Only Structured Data (Medium-Term).** Clinicians capture information via natural language (voice, chat); AI generates structured FHIR representations for storage, billing, and public health reporting, but the primary clinical workflow bypasses structured formats entirely. In this model, serialization reverses direction — the problem becomes FHIR *generation* from text rather than FHIR *consumption* by text models. Recent work on clinical note-to-FHIR synthesis [CITE:FXBKDFFQ] [CITE:ABED59UH] suggests this path is technically feasible.

**Path C: LLM-Native Interchange Formats (Long-Term).** New exchange formats emerge that achieve both machine parseability (for validation, billing, research) and model comprehensibility (for AI reasoning) in a single representation. Our empirical finding that Structured Markdown achieves near-optimal accuracy at minimal token cost (0.3–0.5× baseline) may represent an early indicator of what such a format could look like — a structured yet readable representation that serves both human clinicians and AI systems simultaneously.

### A Call for Architectural Debate

The healthcare informatics community has invested two decades in building the FHIR ecosystem. We do not suggest abandoning this investment — FHIR's value for deterministic exchange, audit trails, regulatory compliance, and population health analytics is well established and unlikely to diminish. Rather, we argue that the emergence of LLMs as primary clinical data consumers necessitates a complementary architectural layer — one that our evaluation framework helps optimize today, and that future interoperability standards may need to address natively.

FHIRBench provides the first empirical evidence base for this debate: quantifying the cost of the current structured-then-serialize paradigm and identifying which presentation formats best bridge the gap between machine-readable exchange and AI-comprehensible input.

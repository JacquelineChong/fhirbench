# FHIRBench-UK: Validating Clinical Data Serialization Strategies for LLMs in NHS FHIR Environments

**Target:** NPJ Digital Medicine
**Format:** ~4,500 words main text, 150-word abstract, up to 10 display items
**Authors:** Jacqueline Chong (The Hong Kong Polytechnic University)

---

## Structure

### Abstract (150 words, unstructured)
- Problem: NHS mandates FHIR APIs but no guidance on LLM serialization
- Method: FHIRBench adapted to UK Core FHIR profile
- Key finding: [TBD after experiments]
- Implication: Practical guidance for NHS Trusts deploying clinical AI

### 1. Introduction (~800 words)
- NHS FHIR mandate (NHS England Interoperability Framework)
- Growing LLM deployment in NHS (AI Lab, NHSX)
- Gap: No serialization guidance for UK-specific FHIR profiles
- Prior work: FHIRBench (US Core) showed significant serialization effects
- This paper: Validates and extends to UK Core, with NHS-specific implications

### 2. Methods (~1,200 words)
- 2.1 UK Core FHIR Profile Adaptation
- 2.2 Patient Generation (UK demographics)
- 2.3 Serialization Strategies (NHS SOAP format)
- 2.4 Evaluation (same two-layer framework)

### 3. Results (~1,000 words)
- 3.1 Overall Performance
- 3.2 UK-Specific Elements (NHS Number, dm+d, SNOMED CT UK)
- 3.3 Cross-National Comparison (US vs UK)
- 3.4 Complexity Analysis

### 4. Discussion (~1,200 words)
- NHS implications
- Why UK Core may differ from US Core
- Limitations
- Recommendations for NHS Trusts

### 5. Conclusion (~300 words)

---

## Key Differentiators from Paper 1:
1. UK Core FHIR profile (not US Core)
2. NHS terminology (dm+d, SNOMED CT UK, NHS Data Dictionary)
3. Validation study framing (does the finding generalize?)
4. Shorter, focused (NPJ format ~4,500 words)
5. Explicit NHS deployment guidance
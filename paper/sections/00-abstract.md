# Abstract

The integration of Large Language Models (LLMs) into clinical decision support systems necessitates transforming structured health data — primarily encoded in HL7 FHIR — into representations that maximize model comprehension and reasoning accuracy. Despite growing adoption, no systematic benchmark exists examining how serialization strategies for clinical data affect downstream LLM performance across diverse model architectures.

This paper presents FHIRBench, an open-source benchmark framework evaluating six serialization strategies (raw JSON, flattened key-value, natural language narrative, structured markdown, clinical summary templates, and hybrid adaptive) across five foundation models (Claude 3.5 Sonnet, GPT-5.4, Llama 3 70B, DeepSeek V3.2, and Qwen3) on three clinical task types: factual question answering, clinical reasoning, and patient summarization. Using 1,000 synthetic FHIR R4 patient bundles generated via Synthea across four clinical domains, we evaluate 90 experimental conditions with standardized metrics including accuracy, clinical correctness scoring, ROUGE-L, and token efficiency.

Our findings demonstrate that serialization strategy significantly impacts model accuracy (up to 23% variance on clinical QA tasks), with optimal approaches varying by task type, model architecture, and clinical domain. We identify a Pareto frontier of format complexity versus performance and propose a practitioner decision framework for serialization strategy selection. All code, data generation configurations, and evaluation harnesses are publicly available, enabling direct reproducibility and adoption as production clinical AI middleware.

<!-- 
Word count: ~220
Structure: Background (2 sentences) → Objective/Methods (3 sentences) → Results (2 sentences) → Conclusion/Implications (1 sentence)
Citation style: None in abstract (per convention)
-->

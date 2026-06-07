# Skill: Literature Review Search

> **Purpose:** Systematic literature search and synthesis for the FHIR serialization research paper (Paper #1).

## Trigger

Activate when the user asks to:
- Find papers on FHIR, LLM, clinical data serialization, health AI preprocessing
- Search for related work on a specific sub-topic
- Build or extend the literature review section
- Add references to the bibliography

## Configuration

| Key | Value |
|-----|-------|
| Zotero Collection | `J7MWVXWM` (Paper #1 — FHIR Serialization for LLMs) |
| Default Tags | `fhir-serialization`, `paper-1` |
| Max Results Per Source | 20 |

## Search Sources

| Source | Method |
|--------|--------|
| PubMed | `site:pubmed.ncbi.nlm.nih.gov {query}` |
| arXiv | `site:arxiv.org {query}` |
| Semantic Scholar | API + web search |
| Google Scholar | `site:scholar.google.com {query}` |
| ACM Digital Library | `site:dl.acm.org {query}` |
| IEEE Xplore | `site:ieeexplore.ieee.org {query}` |

## Workflow

1. Parse research question → multiple search queries
2. Execute multi-source search
3. Extract metadata (title, authors, year, DOI, abstract, key findings)
4. Deduplicate (DOI match + fuzzy title match >90%)
5. Rank by relevance (topic match 40%, recency 20%, citations 15%, venue 15%, methodology 10%)
6. Add to Zotero collection J7MWVXWM with taxonomy tags
7. Output: markdown table + annotated bibliography

## Taxonomy Tags

| Category | Tag | Covers |
|----------|-----|--------|
| Core | `serialization-methods` | Direct serialization/format comparison |
| Core | `fhir-llm-tools` | Tools/frameworks for FHIR + LLM |
| Context | `llm-healthcare` | LLMs in clinical applications |
| Context | `fhir-standards` | FHIR R4/R5 specification |
| Context | `clinical-nlp` | Clinical NLP, EHR text processing |
| Methods | `benchmark-methodology` | LLM evaluation methodology |
| Methods | `prompt-engineering` | Prompt design for structured data |

## Pre-defined Searches for Paper #1

1. `"FHIR" AND "large language model" OR "LLM"`
2. `"clinical data serialization" OR "health data representation"`
3. `"EHR" AND "GPT-4" OR "Claude" OR "LLM" AND "structured data"`
4. `"FHIR" AND "prompt engineering" OR "preprocessing"`
5. `"clinical decision support" AND "language model" AND "evaluation"`
6. `"medical benchmark" AND "LLM" AND "structured data"`
7. `"HL7" AND "natural language processing" 2023..2026`
8. `"Synthea" AND "evaluation" OR "benchmark"`

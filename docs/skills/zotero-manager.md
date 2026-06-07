# Skill: Zotero Manager

> **Purpose:** Full Zotero library management for the FHIRBench research project.

## Configuration

| Key | Value |
|-----|-------|
| User ID | `13796165` |
| Username | `JacquelineChong` |
| Base URL | `https://api.zotero.org/users/13796165` |
| Primary Collection | `J7MWVXWM` (Paper #1 — FHIR Serialization for LLMs) |
| Default Citation Style | APA 7th Edition |

## Capabilities

| # | Capability | Endpoint |
|---|-----------|----------|
| 1 | Search library | `GET /items?q={term}` |
| 2 | Add items | `POST /items` (max 50/batch) |
| 3 | Add to collection | Include `collections` in item data |
| 4 | Tag items | Include `tags` array |
| 5 | Get citations | `GET /items/{key}?format=bib&style=apa` |
| 6 | List collections | `GET /collections` |
| 7 | Create collection | `POST /collections` |
| 8 | Export BibTeX | `GET /collections/{key}/items?format=bibtex` |

## Item Types Supported

- journalArticle, conferencePaper, preprint, computerProgram, webpage

## Existing References (Collection J7MWVXWM)

| # | Title | Key | Type |
|---|-------|-----|------|
| 1 | Serialisation Strategy Matters (2025) | `KTDK3AX5` | Journal Article |
| 2 | LLMonFHIR (StanfordBDHG) | `USQFSG3J` | Software |
| 3 | llm-fhir-eval (Flexpa) | `QW6C7PH6` | Software |
| 4 | FHIR-Former | `VQVECWTP` | Conference Paper |
| 5 | Med-PaLM 2 | `SF66VH38` | Journal Article |
| 6 | Synthea | `4KJ2IQNG` | Software |
| 7 | FHIR R4 Specification | `IFK2768G` | Document |
| 8 | ONC Cures Act / TEFCA | `TURQFSSV` | Document |

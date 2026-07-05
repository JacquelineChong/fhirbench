# Paper: Clinical Data Serialization Strategies for LLMs — FHIRBench

## Status: Results Complete, Finalizing Discussion

**Last updated:** 2026-07-05

## Writing Workflow

1. **Drafting** → Markdown in `paper/sections/` (Quick Desktop writes, auto-commits via GitHub API)
2. **Citations** → `[CITE:ZOTERO_KEY]` markers → resolved to IEEE `[1]` format
3. **Review** → Peer Review Agent validates statistical claims + internal consistency
4. **Submission** → `arxiv-formatter` skill → LaTeX + BibTeX → arXiv

## Sections

| # | File | Status | Notes |
|---|------|--------|-------|
| 0 | `00-abstract.md` | 🟡 Needs update | Update with final numbers |
| 1 | `01-introduction.md` | ✅ Written | 14.9 KB |
| 2 | `02-background.md` | ✅ Written | 20.8 KB (lit review integrated) |
| 3.1 | `03-research-design.md` | ✅ Updated | 100 patients, 9,000 evals, sampling design |
| 3.2 | `03-data-methodology.md` | ✅ Updated | Cohort sampling subsection added |
| 3.3 | `03-serialization-taxonomy.md` | ✅ Written | 6 strategies detailed (24.9 KB) |
| 3.4 | `03-pipeline-validation-results.md` | ✅ Written | 50-patient validation |
| 3.5 | `03-evaluation-framework.md` | ✅ Updated | 9,000 evals, multi-layer design |
| 4 | `04-results.md` | ✅ **Rewritten** | Full 100-patient, 4-model analysis with Pareto frontier |
| 5 | `05-discussion.md` | ✅ **Rewritten** | 4 expanded findings + production path |
| 6 | `06-conclusion.md` | 🟡 Needs update | Fill [TBD] placeholders |
| A | `appendix-a-technical-design.md` | ✅ Written | Architecture specs |
| B | `appendix-b-development-stories.md` | ✅ Written | User stories |

**Deprecated files (superseded):**
- `04-preliminary-results.md` → replaced by `04-results.md`
- `05-discussion-main.md` → replaced by `05-discussion.md`
- `05-discussion-practitioner.md` → merged into `05-discussion.md`
- `05-discussion-interoperability.md` → merged into `05-discussion.md`

## Key Results (100 patients × 4 models × 6 serializers × 3 tasks)

### Layer 1 (F1) Rankings
| Rank | Model | F1 |
|------|-------|----|
| 1 | GPT-5.4 | 0.367 |
| 2 | DeepSeek V3.2 | 0.354 |
| 3 | Qwen3 32B | 0.323 |
| 4 | Claude Sonnet 4.5 | 0.222 |

### Layer 2 (Judge) Rankings — REVERSED
| Rank | Model | Avg Score (0-5) |
|------|-------|:---:|
| 1 | Claude Sonnet 4.5 | 4.00 |
| 2 | DeepSeek V3.2 | 3.88 |
| 3 | GPT-5.4 | 3.59 |
| 4 | Qwen3 32B | 3.29 |

### Key Findings
1. Serialization strategy significantly impacts quality (Wilcoxon p < 10⁻³⁷)
2. Complete ranking reversal between F1 and judge evaluation (p < 10⁻³⁵)
3. Model × Serializer interaction precludes universal recommendations (Friedman p = 0.0009)
4. Open-weight model (Llama 3.1 70B) fails 100% on complex FHIR bundles
5. Narrative achieves 95% of Raw JSON quality at 83% fewer tokens

## Statistical Analysis
- `results/statistical_tests_report.md` — full report
- `results/statistical_tests_summary.json` — machine-readable
- `results/layer1_f1_summary.json` — F1 breakdown

## Citation Format

- In-text: IEEE numeric `[1]`, `[2, 3]`, `[4–7]`
- Marker during drafting: `[CITE:KTDK3AX5]` (Zotero item key)
- Final: resolved via Zotero BibTeX export → `\cite{key}` in LaTeX
- Zotero Collection: J7MWVXWM (52 references)

## Production Path
See `production/README.md` — Context-Adaptive FHIR Serialization Engine design spec.

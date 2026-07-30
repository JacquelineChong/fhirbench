# Supplementary Methodology Note: Data Quality Perturbation Layer

## Date: 2026-07-30

## Context

A significant discrepancy was identified between Paper 1 and Paper 2 regarding the impact of serialisation strategy on model performance. Paper 1 found serialisation to be a major quality lever (Condensed beats Raw JSON, p < 10^-37). Paper 2 found minimal quality impact across serialisers (Layer 2 delta < 0.1), with model selection dominating.

Three hypotheses explain this discrepancy:
- H1: LLM-generated data too clean (data source artefact)
- H2: Ground truth extraction biases F1 toward raw_json (measurement artefact)
- H3: UK Core profile rigidity reduces format-dependent information loss (real structural difference)

---

## H1: Synthetic Data Cleanliness

Paper 1 used Synthea (messy, variable) vs Paper 2 used DeepSeek (clean, uniform). Our 4 complexity levels vary VOLUME not MESSINESS. Real NHS complexity = both quantity AND noise.

## H2: Ground Truth Extraction Methodology

Paper 2 extracts ground truth from the same JSON that raw_json serialises verbatim -> trivially higher F1 for raw_json. Layer 2 (judge) is NOT affected. Layer 1 serialiser F1 comparisons are confounded.

## H3: UK Core Profile Rigidity

UK Core mandates strict coding (NHS Number, dm+d, SNOMED CT UK). Key clinical tokens are preserved regardless of serialisation format because they are mandatory fixed strings. Implication: more standardised FHIR = less serialiser impact (real finding, not artefact).

---

## Planned Remediation: Data Quality Perturbation Layer

### Perturbation Types (Based on Real NHS Data)

1. Duplicate MedicationRequests (GP renewals)
2. Legacy Read codes alongside SNOMED (pre-2020 records)
3. Missing observation units (incomplete lab imports)
4. Free-text abbreviated clinical notes ("T2DM, poor ctrl")
5. Mixed date formats (DD/MM/YY, YYYY-MM-DD, text)
6. Incomplete medication histories (entered-in-error)
7. Contradictory entries (resolved condition still active)
8. Variable terminology (brand vs generic, abbreviations)

### Design

- Apply 2-5 perturbations per patient (scaled by complexity)
- Re-run 6 serialisers on perturbed data -> 1,800 new prompts
- Benchmark with same 5 models
- Compare: if serialiser effect INCREASES with noise -> validates Paper 1

### Expected Outcome

Perturbation will increase serialiser effect. Narrative/clinical_template will outperform raw_json on messy data (they normalise noise). Raw_json loses F1 advantage (noisy JSON = more irrelevant tokens).

### Finding (if confirmed)

"Serialisation strategy is critical for real-world NHS data. The minimal serialiser impact on clean synthetic data does not generalise to production clinical records."

---

## Timeline

- Perturbation script: ~2 hours
- Prompts: ~30 minutes
- Benchmark re-run: ~24 hours
- Analysis: ~2 hours
- Total: ~2 days

## Recommendation

Include perturbation analysis in Paper 2 before submission. Resolves the Paper 1 contradiction that reviewers will notice. 2 days of additional work significantly strengthens the contribution.

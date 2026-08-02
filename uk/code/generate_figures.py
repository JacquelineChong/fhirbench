#!/usr/bin/env python3
"""
generate_figures.py

Generates publication-quality figures for FHIRBench-UK paper.
Figure 2: Clinical quality vs. token reduction by model and serialisation format.
"""

import json
import os
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# ============================================================================
# Configuration
# ============================================================================

RESULTS_DIR = os.path.expanduser("~/Desktop/Kiro/FHIR-UK/results/")
OUTPUT_DIR = os.path.expanduser("~/Desktop/Kiro/FHIR-UK/figures/")

MODELS = ["claude", "gpt54", "deepseek", "qwen", "llama"]
MODEL_LABELS = {
    "claude": "Claude Sonnet 4.5",
    "gpt54": "GPT-5.4",
    "deepseek": "DeepSeek V3.2",
    "qwen": "Qwen3 32B",
    "llama": "Llama 3.3 70B",
}

SERIALIZERS = [
    "raw_json", "flattened_kv", "structured_markdown",
    "narrative", "hybrid_adaptive", "clinical_template"
]

SERIALIZER_ABBREVS = {
    "raw_json": "JSON",
    "flattened_kv": "KV",
    "structured_markdown": "MD",
    "narrative": "Narr",
    "hybrid_adaptive": "Hybrid",
    "clinical_template": "Template",
}

# Token reduction percentages (computed from actual data)
TOKEN_REDUCTION = {
    "raw_json": 0.0,
    "flattened_kv": 38.6,
    "structured_markdown": 87.6,
    "narrative": 88.1,
    "hybrid_adaptive": 88.7,
    "clinical_template": 90.5,
}

# Colourblind-safe palette (Wong, 2011 — Nature Methods)
COLOURS = {
    "claude": "#0072B2",      # Blue
    "gpt54": "#D55E00",       # Vermillion
    "deepseek": "#009E73",    # Bluish green
    "qwen": "#CC79A7",        # Reddish purple
    "llama": "#E69F00",       # Orange
}

MARKERS = {
    "claude": "o",
    "gpt54": "s",
    "deepseek": "^",
    "qwen": "D",
    "llama": "v",
}


# ============================================================================
# Data Loading
# ============================================================================

def load_layer2_judgments() -> list:
    """Load all Layer 2 judgment files from the clean cohort."""
    all_judgments = []

    # Claude judged by Qwen
    path = os.path.join(RESULTS_DIR, "layer2_qwen_judges_claude.json")
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            all_judgments.extend(json.load(f))

    # Other models judged by Claude
    for model in ["gpt54", "llama", "qwen", "deepseek"]:
        path = os.path.join(RESULTS_DIR, f"layer2_claude_judges_{model}.json")
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                all_judgments.extend(json.load(f))

    return all_judgments


def compute_model_serializer_scores(judgments: list) -> dict:
    """Compute mean composite score per model x serialiser."""
    scores = defaultdict(lambda: defaultdict(list))

    for j in judgments:
        if not j.get("success"):
            continue
        model = j.get("target_model", "")
        ser = j.get("serializer", "")
        acc = j.get("accuracy", 0)
        comp = j.get("completeness", 0)
        safety = j.get("safety", 0)
        rel = j.get("relevance", 0)
        if acc and comp and safety and rel:
            composite = (acc + comp + safety + rel) / 4.0
            scores[model][ser].append(composite)

    # Compute means
    means = {}
    for model in MODELS:
        means[model] = {}
        for ser in SERIALIZERS:
            vals = scores[model][ser]
            means[model][ser] = float(np.mean(vals)) if vals else 0.0
    return means


# ============================================================================
# Figure Generation
# ============================================================================

def generate_figure(means: dict):
    """Generate Figure 2: Quality vs Token Reduction."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Set up clean academic style
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 10,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 8.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })

    fig, ax = plt.subplots(figsize=(10, 6))

    # Use evenly-spaced x positions (0–5) for categorical layout
    sorted_sers = sorted(SERIALIZERS, key=lambda s: TOKEN_REDUCTION[s])
    x_positions = list(range(len(sorted_sers)))  # [0, 1, 2, 3, 4, 5]

    # Vertical dashed line between position 1 (flattened_kv) and 2 (struct_md)
    # to highlight the gap between KV and the high-reduction cluster
    ax.axvline(x=1.5, color="#888888", linewidth=0.9, linestyle="--", zorder=1, alpha=0.5)

    # Shaded region for the high-reduction formats (positions 2–5)
    ax.axvspan(1.5, 5.5, alpha=0.04, color="#2ca02c", zorder=0)

    # Plot each model
    for model in MODELS:
        y_vals = [means[model][s] for s in sorted_sers]
        overall_mean = np.mean(y_vals)

        label = f"{MODEL_LABELS[model]} ({overall_mean:.2f})"
        ax.plot(
            x_positions, y_vals,
            marker=MARKERS[model],
            color=COLOURS[model],
            linewidth=1.8,
            markersize=8,
            markeredgecolor="white",
            markeredgewidth=0.6,
            label=label,
            zorder=3,
        )

    # --- Annotations ---
    ax.text(
        3.0, 5.02,
        "Claude: robust (range = 0.10)",
        fontsize=8.5, color=COLOURS["claude"], ha="center", va="bottom",
        style="italic",
    )

    ax.text(
        3.0, 3.45,
        "Llama: format-sensitive (range = 0.39)",
        fontsize=8.5, color=COLOURS["llama"], ha="center", va="top",
        style="italic",
    )

    # Light horizontal reference lines
    for y in [3.5, 4.0, 4.5, 5.0]:
        ax.axhline(y, color="#eeeeee", linewidth=0.4, zorder=0)

    # --- X-axis labels: full serialiser name + reduction % ---
    x_tick_labels = [
        "raw_json\n(0% reduction)",
        "flattened_kv\n(39% reduction)",
        "structured_markdown\n(88% reduction)",
        "narrative\n(88% reduction)",
        "hybrid_adaptive\n(89% reduction)",
        "clinical_template\n(91% reduction)",
    ]
    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_tick_labels, rotation=30, ha="right", fontsize=8.5)

    # Axis labels
    ax.set_xlabel("")  # Tick labels are self-explanatory
    ax.set_ylabel("Layer 2 Clinical Quality Score (0-5)", fontsize=10, labelpad=8)
    ax.set_xlim(-0.4, 5.4)
    ax.set_ylim(3.2, 5.1)
    ax.set_yticks([3.5, 4.0, 4.5, 5.0])

    # Legend — below the plot, outside axes
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.20),
        ncol=3,
        frameon=True,
        framealpha=0.95,
        edgecolor="#cccccc",
        borderpad=0.6,
        handlelength=2.0,
        columnspacing=1.2,
    )

    # Title
    ax.set_title(
        "Figure 2: Clinical quality vs. token reduction by model and serialisation format",
        fontsize=11, pad=14, weight="medium",
    )

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.28)

    # Save
    png_path = os.path.join(OUTPUT_DIR, "fig2_quality_vs_tokens.png")
    pdf_path = os.path.join(OUTPUT_DIR, "fig2_quality_vs_tokens.pdf")

    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")

    print(f"Saved: {png_path}")
    print(f"Saved: {pdf_path}")
    plt.close(fig)


# ============================================================================
# Main
# ============================================================================

def main():
    print("Loading Layer 2 judgments...")
    judgments = load_layer2_judgments()
    print(f"  Loaded {len(judgments)} judgments")

    print("Computing model x serialiser scores...")
    means = compute_model_serializer_scores(judgments)

    # Print summary
    print("\nMean L2 composite score by model x serialiser:")
    header = f"{'Model':<12}" + "".join(
        f"{SERIALIZER_ABBREVS[s]:>10}"
        for s in sorted(SERIALIZERS, key=lambda s: TOKEN_REDUCTION[s])
    )
    print(f"  {header}")
    for model in MODELS:
        row = f"  {model:<12}"
        for ser in sorted(SERIALIZERS, key=lambda s: TOKEN_REDUCTION[s]):
            row += f"{means[model][ser]:>10.3f}"
        print(row)

    print("\nGenerating Figure 2...")
    generate_figure(means)
    print("\nDone.")


if __name__ == "__main__":
    main()

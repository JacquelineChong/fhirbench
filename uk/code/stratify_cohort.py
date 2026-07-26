#!/usr/bin/env python3
"""
stratify_cohort.py

Stratified sampling of FHIR bundles for evaluation cohort.
Selects 100 files balanced by complexity and domain.
"""

import argparse
import json
import os
import random
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime


# Filename pattern: patient_{domain}_{complexity}_{NNN}.json
# Domains: cardiovascular, diabetes, medication_interactions, preventive_care
# Complexities: simple, moderate, complex, highly_complex
FILENAME_PATTERN = re.compile(
    r'^patient_(.+?)_(simple|moderate|complex|highly_complex)_(\d+)\.json$'
)

# Sampling targets per complexity
COMPLEXITY_TARGETS = {
    "simple": 25,
    "moderate": 40,
    "complex": 25,
    "highly_complex": 10,
}

# Domain balance targets (for checking)
DOMAIN_TARGETS = {
    "diabetes": 0.28,
    "cardiovascular": 0.27,
    "preventive_care": 0.26,
    "medication_interactions": 0.19,
}

# Balance thresholds
MIN_DOMAIN_RATIO = 0.15
MAX_DOMAIN_RATIO = 0.35


def parse_filename(filename: str) -> tuple:
    """
    Parse filename to extract domain and complexity.

    Returns:
        (domain, complexity) or (None, None) if not parseable.
    """
    match = FILENAME_PATTERN.match(filename)
    if match:
        domain = match.group(1)
        complexity = match.group(2)
        return domain, complexity
    return None, None


def check_domain_balance(selected_files: list) -> bool:
    """Check if domain distribution is within acceptable bounds."""
    total = len(selected_files)
    if total == 0:
        return False

    domain_counts = defaultdict(int)
    for f in selected_files:
        domain, _ = parse_filename(f)
        if domain:
            domain_counts[domain] += 1

    for domain in DOMAIN_TARGETS:
        ratio = domain_counts.get(domain, 0) / total
        if ratio < MIN_DOMAIN_RATIO or ratio > MAX_DOMAIN_RATIO:
            return False

    return True


def stratified_sample(files_by_complexity: dict, seed: int) -> list:
    """
    Perform stratified sampling by complexity.

    Args:
        files_by_complexity: Dict mapping complexity -> list of filenames.
        seed: Random seed for reproducibility.

    Returns:
        List of selected filenames.
    """
    rng = random.Random(seed)
    selected = []

    for complexity, target in COMPLEXITY_TARGETS.items():
        pool = files_by_complexity.get(complexity, [])
        if len(pool) <= target:
            selected.extend(pool)
        else:
            selected.extend(rng.sample(pool, target))

    return selected


def main():
    parser = argparse.ArgumentParser(
        description="Stratified sampling of FHIR bundles for evaluation cohort."
    )
    parser.add_argument(
        "--input-dir",
        default="../data/fhir_bundles/",
        help="Source directory with FHIR JSON bundles"
    )
    parser.add_argument(
        "--output-dir",
        default="../data/evaluation_cohort/",
        help="Destination directory for selected cohort"
    )
    args = parser.parse_args()

    input_dir = os.path.expanduser(args.input_dir)
    output_dir = os.path.expanduser(args.output_dir)

    if not os.path.isdir(input_dir):
        print(f"ERROR: Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    # Collect and group files
    all_files = sorted(f for f in os.listdir(input_dir) if f.lower().endswith('.json'))
    print(f"Total files found: {len(all_files)}")

    files_by_complexity = defaultdict(list)
    files_by_domain = defaultdict(list)

    for f in all_files:
        domain, complexity = parse_filename(f)
        if domain and complexity:
            files_by_complexity[complexity].append(f)
            files_by_domain[domain].append(f)
        else:
            print(f"  WARNING: Could not parse filename: {f}")

    print("\nPool sizes:")
    for c in ["simple", "moderate", "complex", "highly_complex"]:
        print(f"  {c}: {len(files_by_complexity[c])}")
    print()
    for d in sorted(files_by_domain):
        print(f"  {d}: {len(files_by_domain[d])}")

    # Perform stratified sampling with balance checking
    seed = 42
    max_attempts = 100
    selected = None

    for attempt in range(max_attempts):
        candidate = stratified_sample(files_by_complexity, seed + attempt)
        if check_domain_balance(candidate):
            selected = candidate
            final_seed = seed + attempt
            print(f"\nBalanced sample achieved with seed={final_seed} (attempt {attempt + 1})")
            break
    else:
        # Use the first attempt if we can't find a balanced one
        selected = stratified_sample(files_by_complexity, seed)
        final_seed = seed
        print(f"\nWARNING: Could not achieve perfect balance after {max_attempts} attempts.")
        print(f"Using seed={final_seed}")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Copy selected files
    print(f"\nCopying {len(selected)} files to {output_dir}...")
    for f in sorted(selected):
        src = os.path.join(input_dir, f)
        dst = os.path.join(output_dir, f)
        shutil.copy2(src, dst)

    # Compute distributions
    complexity_dist = defaultdict(int)
    domain_dist = defaultdict(int)
    domain_complexity = defaultdict(lambda: defaultdict(int))

    for f in selected:
        domain, complexity = parse_filename(f)
        complexity_dist[complexity] += 1
        domain_dist[domain] += 1
        domain_complexity[domain][complexity] += 1

    # Print summary
    print("\n" + "=" * 70)
    print("STRATIFIED COHORT SELECTION SUMMARY")
    print("=" * 70)

    print(f"\nTotal selected: {len(selected)}")
    print(f"Seed used: {final_seed}")

    print("\n--- Complexity Distribution ---")
    print(f"{'Complexity':<20} {'Count':>6} {'Percent':>8}")
    print("-" * 36)
    for c in ["simple", "moderate", "complex", "highly_complex"]:
        count = complexity_dist[c]
        pct = count / len(selected) * 100
        print(f"{c:<20} {count:>6} {pct:>7.1f}%")

    print("\n--- Domain Distribution ---")
    print(f"{'Domain':<30} {'Count':>6} {'Percent':>8}")
    print("-" * 46)
    for d in sorted(domain_dist):
        count = domain_dist[d]
        pct = count / len(selected) * 100
        print(f"{d:<30} {count:>6} {pct:>7.1f}%")

    print("\n--- Domain × Complexity Cross-tabulation ---")
    complexities = ["simple", "moderate", "complex", "highly_complex"]
    header = f"{'Domain':<25}" + "".join(f"{c:>15}" for c in complexities) + f"{'Total':>8}"
    print(header)
    print("-" * len(header))
    for d in sorted(domain_complexity):
        row = f"{d:<25}"
        total = 0
        for c in complexities:
            count = domain_complexity[d][c]
            row += f"{count:>15}"
            total += count
        row += f"{total:>8}"
        print(row)

    print("\n--- Selected Files ---")
    for i, f in enumerate(sorted(selected), 1):
        print(f"  {i:>3}. {f}")

    # Save manifest
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "seed_used": final_seed,
        "total_selected": len(selected),
        "source_dir": input_dir,
        "filenames": sorted(selected),
        "complexity_distribution": dict(complexity_dist),
        "domain_distribution": dict(domain_dist),
        "domain_complexity_matrix": {d: dict(v) for d, v in domain_complexity.items()},
    }

    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"\nManifest saved to: {manifest_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
validate_uk_core.py

Validates UK Core FHIR Bundle JSON files against NHS/UK-specific criteria.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime


def calculate_check_digit(first_nine: str) -> int:
    """Calculate NHS Number check digit using Modulus 11."""
    weights = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(int(d) * w for d, w in zip(first_nine, weights))
    remainder = total % 11
    result = 11 - remainder
    if result == 11:
        return 0
    elif result == 10:
        return -1
    return result


def validate_nhs_number(nhs_number: str) -> bool:
    """Validate NHS Number using Modulus 11 check digit."""
    if not nhs_number or len(nhs_number) != 10 or not nhs_number.isdigit():
        return False
    expected = calculate_check_digit(nhs_number[:9])
    if expected == -1:
        return False
    return int(nhs_number[9]) == expected


def is_nhs_system(system: str) -> bool:
    """Check if identifier system is NHS Number."""
    if not system:
        return False
    s = system.lower()
    return "nhs-number" in s or "nhs.uk" in s


def get_resources_by_type(bundle: dict) -> dict:
    """Extract resources grouped by resourceType from a bundle."""
    resources = defaultdict(list)
    entries = bundle.get("entry", [])
    for entry in entries:
        resource = entry.get("resource", {})
        rt = resource.get("resourceType", "Unknown")
        resources[rt].append(resource)
    return resources


def check_bundle_structure(bundle: dict) -> tuple:
    """Criterion 1: Valid FHIR Bundle structure."""
    if bundle.get("resourceType") != "Bundle":
        return False, "resourceType is not 'Bundle'"
    entries = bundle.get("entry")
    if not isinstance(entries, list) or len(entries) == 0:
        return False, "No 'entry' array or it is empty"
    # Check entries have resources
    has_resource = any("resource" in e for e in entries)
    if not has_resource:
        return False, "No entries contain a 'resource' field"
    return True, f"{len(entries)} entries"


def check_nhs_number_present(resources: dict) -> tuple:
    """Criterion 2: NHS Number present in Patient."""
    patients = resources.get("Patient", [])
    if not patients:
        return False, "No Patient resource found"

    for patient in patients:
        identifiers = patient.get("identifier", [])
        for ident in identifiers:
            system = ident.get("system", "")
            value = ident.get("value", "")
            if is_nhs_system(system):
                cleaned = value.replace(" ", "").replace("-", "")
                if cleaned.isdigit() and len(cleaned) == 10:
                    return True, f"NHS Number: {cleaned}"
    return False, "No valid 10-digit NHS Number found"


def check_nhs_number_valid(resources: dict) -> tuple:
    """Criterion 3: NHS Number passes Modulus 11."""
    patients = resources.get("Patient", [])
    for patient in patients:
        identifiers = patient.get("identifier", [])
        for ident in identifiers:
            system = ident.get("system", "")
            value = ident.get("value", "")
            if is_nhs_system(system):
                cleaned = value.replace(" ", "").replace("-", "")
                if cleaned.isdigit() and len(cleaned) == 10:
                    if validate_nhs_number(cleaned):
                        return True, f"Valid check digit for {cleaned}"
                    else:
                        return False, f"Invalid check digit for {cleaned}"
    return False, "No NHS Number to validate"


def check_dmd_codes(resources: dict) -> tuple:
    """Criterion 4: MedicationRequest uses dm+d codes."""
    med_requests = resources.get("MedicationRequest", [])
    if not med_requests:
        return True, "No MedicationRequest resources (N/A, pass)"

    total = 0
    valid = 0
    for mr in med_requests:
        # Check medicationCodeableConcept
        med_cc = mr.get("medicationCodeableConcept", {})
        codings = med_cc.get("coding", [])
        if not codings:
            # Also check medicationReference (still valid structure)
            if mr.get("medicationReference"):
                total += 1
                valid += 1  # Reference-based is acceptable
                continue
            total += 1
            continue

        total += 1
        for coding in codings:
            system = coding.get("system", "").lower()
            if "dmd" in system:
                valid += 1
                break

    if total == 0:
        return True, "No medication codings to check"
    if valid == total:
        return True, f"All {total} MedicationRequests use dm+d"
    return False, f"{valid}/{total} MedicationRequests use dm+d"


def check_snomed_codes(resources: dict) -> tuple:
    """Criterion 5: Condition resources use SNOMED CT."""
    conditions = resources.get("Condition", [])
    if not conditions:
        return True, "No Condition resources (N/A, pass)"

    total = 0
    valid = 0
    for cond in conditions:
        code = cond.get("code", {})
        codings = code.get("coding", [])
        if not codings:
            total += 1
            continue
        total += 1
        for coding in codings:
            system = coding.get("system", "").lower()
            if "snomed" in system:
                valid += 1
                break

    if total == 0:
        return True, "No condition codings to check"
    if valid == total:
        return True, f"All {total} Conditions use SNOMED CT"
    return False, f"{valid}/{total} Conditions use SNOMED CT"


def check_uk_core_extensions(resources: dict) -> tuple:
    """Criterion 6: Patient has UK Core extensions."""
    patients = resources.get("Patient", [])
    if not patients:
        return False, "No Patient resource found"

    for patient in patients:
        extensions = patient.get("extension", [])
        for ext in extensions:
            url = ext.get("url", "").lower()
            if "ethniccategory" in url or "nhsnumberverification" in url:
                return True, f"Found UK Core extension: {ext.get('url', '')[:60]}"

    return False, "No ethniccategory or nhsnumberverification extensions"


def check_gp_practice(resources: dict) -> tuple:
    """Criterion 7: Patient has GP Practice reference."""
    patients = resources.get("Patient", [])
    if not patients:
        return False, "No Patient resource found"

    for patient in patients:
        # Check generalPractitioner
        gp = patient.get("generalPractitioner")
        if gp:
            return True, "Has generalPractitioner reference"

        # Check extensions for GP practice
        extensions = patient.get("extension", [])
        for ext in extensions:
            url = ext.get("url", "").lower()
            if "gppractice" in url or "preferredbranchsurgery" in url:
                return True, f"Has GP extension: {ext.get('url', '')[:60]}"

    # Also check if there's a PractitionerRole or Organization that implies GP
    # Some bundles reference GP via contained or referenced resources
    if resources.get("Organization"):
        for org in resources["Organization"]:
            org_type = org.get("type", [])
            for t in org_type:
                codings = t.get("coding", [])
                for c in codings:
                    if "gp" in c.get("code", "").lower() or "practice" in c.get("display", "").lower():
                        return True, "GP Organization found in bundle"

    return False, "No GP Practice reference found"


def check_metric_units(resources: dict) -> tuple:
    """Criterion 8 (warning): Observations use metric units."""
    observations = resources.get("Observation", [])
    if not observations:
        return True, "No Observation resources (N/A)"

    non_metric_flags = []
    non_metric_units = {"lbs", "lb", "[lb_av]", "fahrenheit", "°f", "[degf]",
                        "mg/dl", "mg/dL", "in", "[in_i]", "ft", "[ft_i]"}

    for obs in observations:
        vq = obs.get("valueQuantity", {})
        unit = vq.get("unit", "")
        code = vq.get("code", "")

        unit_lower = unit.lower().strip()
        code_lower = code.lower().strip()

        if unit_lower in non_metric_units or code_lower in non_metric_units:
            display = obs.get("code", {}).get("coding", [{}])[0].get("display", "unknown")
            non_metric_flags.append(f"{display}: {unit or code}")

        # Also check components (e.g., blood pressure)
        for component in obs.get("component", []):
            cvq = component.get("valueQuantity", {})
            cunit = cvq.get("unit", "").lower().strip()
            ccode = cvq.get("code", "").lower().strip()
            if cunit in non_metric_units or ccode in non_metric_units:
                non_metric_flags.append(f"component: {cunit or ccode}")

    if non_metric_flags:
        return False, f"{len(non_metric_flags)} non-metric units: {', '.join(non_metric_flags[:3])}"
    return True, "All observations use metric units"


def check_resource_count(bundle: dict, filename: str) -> tuple:
    """Criterion 9 (warning): Resource count matches complexity."""
    entries = bundle.get("entry", [])
    count = len(entries)

    # Determine complexity from filename
    fname_lower = filename.lower()
    ranges = {
        "highly_complex": (50, 200),
        "complex": (30, 100),
        "moderate": (15, 60),
        "simple": (10, 30),
    }

    complexity = None
    for key in ["highly_complex", "complex", "moderate", "simple"]:
        if key in fname_lower:
            complexity = key
            break

    if complexity is None:
        return True, f"{count} resources (complexity not in filename, skipped)"

    low, high = ranges[complexity]
    if low <= count <= high:
        return True, f"{count} resources ({complexity}: {low}-{high})"
    else:
        return False, f"{count} resources (expected {low}-{high} for {complexity})"


def validate_file(filepath: str) -> dict:
    """Validate a single FHIR bundle file."""
    filename = os.path.basename(filepath)
    result = {
        "file": filename,
        "criteria": {},
        "pass_mandatory": True,
        "warnings": [],
    }

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        result["criteria"] = {f"c{i}": {"pass": False, "detail": f"File read error: {e}"} for i in range(1, 10)}
        result["pass_mandatory"] = False
        return result

    # Criterion 1: Bundle structure
    c1_pass, c1_detail = check_bundle_structure(data)
    result["criteria"]["c1_bundle_structure"] = {"pass": c1_pass, "detail": c1_detail}

    if not c1_pass:
        # Can't check further if not a valid bundle
        for c in ["c2_nhs_present", "c3_nhs_valid", "c4_dmd_codes",
                  "c5_snomed", "c6_uk_extensions", "c7_gp_practice",
                  "c8_metric_units", "c9_resource_count"]:
            result["criteria"][c] = {"pass": False, "detail": "Skipped (invalid bundle)"}
        result["pass_mandatory"] = False
        return result

    resources = get_resources_by_type(data)

    # Criterion 2: NHS Number present
    c2_pass, c2_detail = check_nhs_number_present(resources)
    result["criteria"]["c2_nhs_present"] = {"pass": c2_pass, "detail": c2_detail}

    # Criterion 3: NHS Number valid (Modulus 11)
    c3_pass, c3_detail = check_nhs_number_valid(resources)
    result["criteria"]["c3_nhs_valid"] = {"pass": c3_pass, "detail": c3_detail}

    # Criterion 4: dm+d codes
    c4_pass, c4_detail = check_dmd_codes(resources)
    result["criteria"]["c4_dmd_codes"] = {"pass": c4_pass, "detail": c4_detail}

    # Criterion 5: SNOMED CT codes
    c5_pass, c5_detail = check_snomed_codes(resources)
    result["criteria"]["c5_snomed"] = {"pass": c5_pass, "detail": c5_detail}

    # Criterion 6: UK Core extensions
    c6_pass, c6_detail = check_uk_core_extensions(resources)
    result["criteria"]["c6_uk_extensions"] = {"pass": c6_pass, "detail": c6_detail}

    # Criterion 7: GP Practice reference
    c7_pass, c7_detail = check_gp_practice(resources)
    result["criteria"]["c7_gp_practice"] = {"pass": c7_pass, "detail": c7_detail}

    # Criterion 8: Metric units (warning only)
    c8_pass, c8_detail = check_metric_units(resources)
    result["criteria"]["c8_metric_units"] = {"pass": c8_pass, "detail": c8_detail}
    if not c8_pass:
        result["warnings"].append(c8_detail)

    # Criterion 9: Resource count (warning only)
    c9_pass, c9_detail = check_resource_count(data, filename)
    result["criteria"]["c9_resource_count"] = {"pass": c9_pass, "detail": c9_detail}
    if not c9_pass:
        result["warnings"].append(c9_detail)

    # Mandatory pass: criteria 1-7 must all pass
    mandatory = [c1_pass, c2_pass, c3_pass, c4_pass, c5_pass, c6_pass, c7_pass]
    result["pass_mandatory"] = all(mandatory)

    return result


def print_summary(results: list) -> None:
    """Print summary table and overall verdict."""
    total_files = len(results)

    criteria_names = [
        ("c1_bundle_structure", "1. Bundle Structure"),
        ("c2_nhs_present", "2. NHS Number Present"),
        ("c3_nhs_valid", "3. NHS Number Valid (Mod 11)"),
        ("c4_dmd_codes", "4. dm+d Medication Codes"),
        ("c5_snomed", "5. SNOMED CT Codes"),
        ("c6_uk_extensions", "6. UK Core Extensions"),
        ("c7_gp_practice", "7. GP Practice Reference"),
        ("c8_metric_units", "8. Metric Units (warning)"),
        ("c9_resource_count", "9. Resource Count (warning)"),
    ]

    print()
    print("=" * 70)
    print("UK CORE FHIR VALIDATION RESULTS")
    print("=" * 70)
    print(f"\nTotal files processed: {total_files}")
    print()

    # Summary table
    print(f"{'Criterion':<35} {'Pass':>6} {'Fail':>6} {'Rate':>8}")
    print("-" * 58)

    for key, name in criteria_names:
        passes = sum(1 for r in results if r["criteria"].get(key, {}).get("pass", False))
        fails = total_files - passes
        rate = (passes / total_files * 100) if total_files > 0 else 0
        marker = " ⚠" if key.startswith("c8") or key.startswith("c9") else ""
        print(f"{name:<35} {passes:>6} {fails:>6} {rate:>7.1f}%{marker}")

    print("-" * 58)

    # Overall verdict
    mandatory_pass = sum(1 for r in results if r["pass_mandatory"])
    mandatory_rate = (mandatory_pass / total_files * 100) if total_files > 0 else 0

    print()
    print(f"Files passing ALL mandatory checks (1-7): {mandatory_pass}/{total_files} ({mandatory_rate:.1f}%)")
    print()

    # Show some failures if any
    failures = [r for r in results if not r["pass_mandatory"]]
    if failures:
        print(f"Files with mandatory failures: {len(failures)}")
        # Show first few
        for r in failures[:10]:
            failed_criteria = [k for k, v in r["criteria"].items()
                             if not v.get("pass", False) and not k.startswith("c8") and not k.startswith("c9")]
            print(f"  {r['file']}: failed {', '.join(failed_criteria)}")
        if len(failures) > 10:
            print(f"  ... and {len(failures) - 10} more")
    else:
        print("✓ All files pass mandatory validation!")

    # Warning summary
    warning_files = sum(1 for r in results if r["warnings"])
    if warning_files:
        print(f"\nFiles with warnings: {warning_files}")

    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Validate UK Core FHIR Bundle JSON files."
    )
    parser.add_argument(
        "--input-dir",
        default="../data/fhir_bundles/",
        help="Directory containing FHIR JSON bundles (default: ../data/fhir_bundles/)"
    )
    parser.add_argument(
        "--output",
        default="../data/validation_results.json",
        help="Path to save detailed results JSON (default: ../data/validation_results.json)"
    )
    args = parser.parse_args()

    input_dir = os.path.expanduser(args.input_dir)
    output_path = os.path.expanduser(args.output)

    if not os.path.isdir(input_dir):
        print(f"ERROR: Directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    # Collect all JSON files
    json_files = []
    for root, _dirs, files in os.walk(input_dir):
        for f in sorted(files):
            if f.lower().endswith('.json'):
                json_files.append(os.path.join(root, f))

    print(f"Found {len(json_files)} JSON files in {input_dir}")
    print("Validating...")

    results = []
    for i, filepath in enumerate(json_files):
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(json_files)} files...")
        result = validate_file(filepath)
        results.append(result)

    # Print summary
    print_summary(results)

    # Save detailed results
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "input_dir": input_dir,
        "total_files": len(results),
        "mandatory_pass": sum(1 for r in results if r["pass_mandatory"]),
        "results": results,
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"\nDetailed results saved to: {output_path}")


if __name__ == "__main__":
    main()

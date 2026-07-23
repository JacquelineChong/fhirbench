"""Fix invalid NHS Numbers in generated FHIR bundles using Modulus 11 check digit algorithm."""

import json
import os
import argparse
import random


def calc_check_digit(nine_digits):
    """Calculate NHS Number check digit using Modulus 11 algorithm.
    
    Algorithm:
    1. Take first 9 digits, multiply by weights [10, 9, 8, 7, 6, 5, 4, 3, 2]
    2. Sum the products
    3. Take remainder when divided by 11
    4. Subtract remainder from 11
    5. If result is 11, check digit is 0
    6. If result is 10, number is invalid (no valid check digit for these 9 digits)
    7. Otherwise, result is the check digit
    """
    weights = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    total = sum(int(d) * w for d, w in zip(nine_digits, weights))
    remainder = total % 11
    check = 11 - remainder
    if check == 11:
        return '0'
    if check == 10:
        return None  # Invalid — no valid check digit possible
    return str(check)


def generate_valid_nhs():
    """Generate a random but valid NHS Number (10 digits, valid Modulus 11)."""
    while True:
        nine = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        cd = calc_check_digit(nine)
        if cd is not None:
            return nine + cd


def validate_nhs(number):
    """Validate an NHS Number using Modulus 11 check digit."""
    if len(number) != 10 or not number.isdigit():
        return False
    return calc_check_digit(number[:9]) == number[9]


def fix_identifiers(resource, path=""):
    """Recursively find and fix NHS Number identifiers in a FHIR resource/bundle.
    
    Returns count of fixed numbers.
    """
    fixed = 0
    if not isinstance(resource, dict):
        return 0

    # Handle Bundle — recurse into entries
    if resource.get("resourceType") == "Bundle":
        for entry in resource.get("entry", []):
            fixed += fix_identifiers(entry.get("resource", {}), path)
        return fixed

    # Check identifiers on this resource
    for ident in resource.get("identifier", []):
        system = ident.get("system", "")
        if "nhs-number" in system.lower() or "nhs.uk" in system.lower():
            value = ident.get("value", "").replace(" ", "")
            if len(value) == 10 and value.isdigit():
                if not validate_nhs(value):
                    cd = calc_check_digit(value[:9])
                    if cd is not None:
                        ident["value"] = value[:9] + cd
                    else:
                        ident["value"] = generate_valid_nhs()
                    fixed += 1

    # Also check nested resources (e.g., contained)
    for contained in resource.get("contained", []):
        fixed += fix_identifiers(contained, path)

    return fixed


def main():
    parser = argparse.ArgumentParser(description="Fix NHS Numbers in FHIR bundles")
    parser.add_argument("--input-dir", default="./data/fhir_bundles/",
                        help="Directory containing FHIR bundle JSON files")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: {args.input_dir} is not a directory")
        return

    total_files = 0
    total_fixed = 0
    total_already_valid = 0
    files_modified = 0

    for fname in sorted(os.listdir(args.input_dir)):
        if not fname.endswith(".json"):
            continue
        total_files += 1
        fpath = os.path.join(args.input_dir, fname)

        with open(fpath, 'r') as f:
            data = json.load(f)

        fixed = fix_identifiers(data, fpath)

        if fixed > 0:
            total_fixed += fixed
            files_modified += 1
            with open(fpath, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            total_already_valid += 1

    print(f"\nNHS Number Fix Summary")
    print(f"{'=' * 40}")
    print(f"Files processed:    {total_files}")
    print(f"Files modified:     {files_modified}")
    print(f"Files unchanged:    {total_already_valid}")
    print(f"NHS Numbers fixed:  {total_fixed}")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    main()

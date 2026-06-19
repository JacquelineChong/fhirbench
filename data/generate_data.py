"""Generate synthetic FHIR R4 patient data using Synthea.

Downloads Synthea if not present, generates 1,000 patients across 4 clinical
condition categories (250 each), validates output as FHIR R4, and creates a manifest.
"""

import csv
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Configuration
SYNTHEA_VERSION = "3.3.0"
SYNTHEA_JAR_URL = (
    f"https://github.com/synthetichealth/synthea/releases/download/"
    f"v{SYNTHEA_VERSION}/synthea-with-dependencies.jar"
)
OUTPUT_DIR = Path("data/fhir_bundles")
SYNTHEA_DIR = Path("data/synthea")
MANIFEST_PATH = Path("data/manifest.csv")

# Condition modules and patients per condition
CONDITIONS: Dict[str, Dict] = {
    "diabetes": {
        "module": "diabetes",
        "count": 250,
        "keepModule": "metabolic_syndrome",
    },
    "cardiovascular": {
        "module": "cardiovascular_disease",
        "count": 250,
        "keepModule": "heart/coronary_heart_disease",
    },
    "medication_interactions": {
        "module": "medications/otc_pain_reliever",
        "count": 250,
        "keepModule": None,
    },
    "preventive_care": {
        "module": "wellness_encounters",
        "count": 250,
        "keepModule": None,
    },
}


def download_synthea(synthea_dir: Path) -> Path:
    """Download Synthea JAR if not already present.

    Args:
        synthea_dir: Directory to store the JAR file.

    Returns:
        Path to the Synthea JAR file.
    """
    synthea_dir.mkdir(parents=True, exist_ok=True)
    jar_path = synthea_dir / "synthea-with-dependencies.jar"

    if jar_path.exists():
        logger.info(f"Synthea JAR already exists at {jar_path}")
        return jar_path

    logger.info(f"Downloading Synthea v{SYNTHEA_VERSION}...")
    try:
        subprocess.run(
            ["curl", "-L", "-o", str(jar_path), SYNTHEA_JAR_URL],
            check=True,
            capture_output=True,
        )
        logger.info(f"Downloaded Synthea to {jar_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download Synthea: {e.stderr.decode()}")
        sys.exit(1)

    return jar_path


def run_synthea(
    jar_path: Path,
    output_dir: Path,
    population: int,
    condition: str,
    module: str,
    seed: int = 42,
) -> List[Path]:
    """Run Synthea to generate patient FHIR bundles.

    Args:
        jar_path: Path to Synthea JAR.
        output_dir: Output directory for FHIR JSON files.
        population: Number of patients to generate.
        condition: Condition category name.
        module: Synthea module to use.
        seed: Random seed for reproducibility.

    Returns:
        List of generated FHIR JSON file paths.
    """
    condition_dir = output_dir / condition
    condition_dir.mkdir(parents=True, exist_ok=True)

    # Clean previous output
    fhir_output = Path("output/fhir")
    if fhir_output.exists():
        shutil.rmtree(fhir_output)

    cmd = [
        "java", "-jar", str(jar_path),
        "-p", str(population),
        "-s", str(seed),
        "--exporter.fhir.export", "true",
        "--exporter.fhir.transaction_bundle", "true",
        "--exporter.ccda.export", "false",
        "--exporter.csv.export", "false",
        "--exporter.hospital.fhir.export", "false",
        "--exporter.practitioner.fhir.export", "false",
        "-m", module,
        "Massachusetts",
    ]

    logger.info(f"Generating {population} patients for condition: {condition}")
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=600)
    except subprocess.CalledProcessError as e:
        logger.error(f"Synthea generation failed: {e.stderr.decode()[:500]}")
        return []
    except subprocess.TimeoutExpired:
        logger.error("Synthea generation timed out (10 min)")
        return []

    # Move generated files to condition directory
    generated_files: List[Path] = []
    if fhir_output.exists():
        for f in fhir_output.glob("*.json"):
            dest = condition_dir / f.name
            shutil.move(str(f), str(dest))
            generated_files.append(dest)

    logger.info(f"Generated {len(generated_files)} files for {condition}")
    return generated_files


def validate_fhir_bundle(filepath: Path) -> bool:
    """Validate that a JSON file is a valid FHIR R4 Bundle.

    Args:
        filepath: Path to JSON file.

    Returns:
        True if valid FHIR R4 Bundle.
    """
    try:
        with open(filepath) as f:
            data = json.load(f)

        # Basic FHIR R4 Bundle validation
        if data.get("resourceType") != "Bundle":
            return False
        if "entry" not in data:
            return False
        if not isinstance(data["entry"], list):
            return False

        # Check at least one entry has a valid resource
        for entry in data["entry"][:5]:
            resource = entry.get("resource", {})
            if "resourceType" not in resource:
                return False

        return True
    except (json.JSONDecodeError, KeyError, TypeError):
        return False


def create_manifest(all_files: Dict[str, List[Path]], manifest_path: Path) -> None:
    """Create a manifest CSV cataloging all generated files.

    Args:
        all_files: Dict mapping condition name to list of file paths.
        manifest_path: Output path for the CSV manifest.
    """
    with open(manifest_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "condition", "path", "valid_fhir", "resource_count"])

        for condition, files in all_files.items():
            for filepath in files:
                valid = validate_fhir_bundle(filepath)
                resource_count = 0
                if valid:
                    with open(filepath) as jf:
                        data = json.load(jf)
                    resource_count = len(data.get("entry", []))

                writer.writerow([
                    filepath.name,
                    condition,
                    str(filepath),
                    valid,
                    resource_count,
                ])

    logger.info(f"Manifest written to {manifest_path}")


def main():
    """Main entry point for data generation."""
    logger.info("FHIRBench Data Generation")
    logger.info("=" * 50)

    # Download Synthea
    jar_path = download_synthea(SYNTHEA_DIR)

    # Check Java is available
    try:
        result = subprocess.run(["java", "-version"], capture_output=True)
        if result.returncode != 0:
            logger.error("Java is not installed. Please install JDK 11+.")
            sys.exit(1)
    except FileNotFoundError:
        logger.error("Java is not installed. Please install JDK 11+.")
        sys.exit(1)

    # Generate patients for each condition
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_files: Dict[str, List[Path]] = {}
    seed = 42

    for condition_name, config in CONDITIONS.items():
        files = run_synthea(
            jar_path=jar_path,
            output_dir=OUTPUT_DIR,
            population=config["count"],
            condition=condition_name,
            module=config["module"],
            seed=seed,
        )
        all_files[condition_name] = files
        seed += 100  # Different seed per condition for variety

        # Validate generated files
        valid_count = sum(1 for f in files if validate_fhir_bundle(f))
        logger.info(f"  {condition_name}: {valid_count}/{len(files)} valid FHIR bundles")

    # Create manifest
    create_manifest(all_files, MANIFEST_PATH)

    # Summary
    total_files = sum(len(f) for f in all_files.values())
    total_valid = sum(
        sum(1 for f in files if validate_fhir_bundle(f))
        for files in all_files.values()
    )
    logger.info("=" * 50)
    logger.info(f"Generation complete: {total_files} files, {total_valid} valid FHIR bundles")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info(f"Manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()

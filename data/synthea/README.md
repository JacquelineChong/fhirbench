# Synthea Configuration

This folder contains Synthea generation configs for 1,000 synthetic patients.

## Target Conditions
- Diabetes management
- Cardiovascular risk
- Medication interactions
- Preventive care gaps

## Usage
```bash
./run_synthea -p 1000 -c synthea.properties
```

## Data Output
Generated FHIR R4 bundles will be placed in `../fhir_bundles/`.

## Requirements
- Java 11+
- Synthea v3.0+

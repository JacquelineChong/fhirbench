"""Clinical QA task - factual questions about patient data."""

from typing import Any, Dict, List


class ClinicalQATask:
    """Factual question-answering task about patient clinical data."""
    
    name = "clinical_qa"
    description = "Factual questions about patient data"
    
    QUESTION_TEMPLATES = [
        "What medications is this patient currently taking?",
        "What are the patient's active conditions?",
        "What is the patient's most recent blood pressure reading?",
        "When was the patient's last HbA1c test and what was the result?",
        "List all allergies documented for this patient.",
    ]
    
    def generate_questions(self, fhir_bundle: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate QA pairs from a FHIR bundle."""
        # TODO: Implement question generation from FHIR data
        return []
    
    def evaluate(self, predicted: str, ground_truth: str) -> float:
        """Evaluate accuracy of a QA response."""
        # TODO: Implement exact match / F1 scoring
        return 0.0

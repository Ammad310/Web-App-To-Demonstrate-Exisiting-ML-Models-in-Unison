from dataclasses import dataclass, field
from typing import List, Dict, Any
import json

# Load disease recommendations from JSON file
with open("static/recommendations.json", "r") as file:
    DISEASE_RECOMMENDATIONS = json.load(file)

# Load disease name mappings from JSON file
with open("static/disease_name_mapping.json", "r") as file:
    DISEASE_MAPPINGS = json.load(file)

@dataclass
class Recommendations:
    """
    A class to manage recommendations related to diseases based on patient data.
    
    Attributes:
        names (List[str]): A list to store the names of diseases for which recommendations are provided.
        procedures (Dict[str, Any]): A dictionary storing procedures for each disease.
        surgeries (Dict[str, Any]): A dictionary storing surgeries for each disease.
        labs (Dict[str, Any]): A dictionary storing lab tests for each disease.
        lifestyle_changes (Dict[str, Any]): A dictionary storing lifestyle changes for each disease.
    
    Methods:
        set_values(names: List[str], data: Dict[str, Any]) -> None:
            Populates the recommendations based on disease names and the provided data.
            
        filter_recommendations(chronic_pred, medlab_pred) -> List[str]:
            Filters and returns disease names based on probabilities from predictions.
    """
    
    names: List[str] = field(default_factory=list)
    procedures: Dict[str, Any] = field(default_factory=dict)
    surgeries: Dict[str, Any] = field(default_factory=dict)
    labs: Dict[str, Any] = field(default_factory=dict)
    lifestyle_changes: Dict[str, Any] = field(default_factory=dict)

    def set_values(self, names: List[str]) -> None:
        """
        Sets the recommendations for the given disease names using the recommendation data.

        Args:
            names (List[str]): A list of disease names.
            data (Dict[str, Any]): A dictionary containing patient-specific data.
        """
        for name in names:
            if name not in self.names:
                self.names.append(name)
                
                # Retrieve the corresponding recommendations for each disease
                self.procedures[name] = DISEASE_RECOMMENDATIONS.get(name, {}).get("Procedures", [])
                self.surgeries[name] = DISEASE_RECOMMENDATIONS.get(name, {}).get("Surgeries", [])
                self.labs[name] = DISEASE_RECOMMENDATIONS.get(name, {}).get("Labs", [])
                self.lifestyle_changes[name] = DISEASE_RECOMMENDATIONS.get(name, {}).get("Lifestyle changes", [])

    def filter_recommendations(self, chronic_pred, medlab_pred) -> List[str]:
        """
        Filters the diseases based on probabilities from chronic and medlab predictions.

        Args:
            chronic_pred: A prediction object containing chronic disease probabilities.
            medlab_pred: A prediction object containing medlab test results.

        Returns:
            List[str]: A filtered list of disease names based on probabilities.
        """
        names = []

        # Filter diseases from chronic predictions with probabilities >= 0.5
        for name in chronic_pred.names:
            if chronic_pred.prob.get(name, 0) >= 0.5:
                names.append(DISEASE_MAPPINGS.get(name, name))  # Use name mapping if available

        # Add 'Normal' if 'normal' is found in medlab predictions
        if "normal" in medlab_pred.names:
            names.append("Normal")
        else:
            # Filter diseases from medlab predictions with probabilities >= 60
            for name in medlab_pred.names:
                if medlab_pred.prob.get(name, 0) >= 60:
                    names.append(DISEASE_MAPPINGS.get(name, name))  # Use name mapping if available
            for name in medlab_pred.confirmed_names:
                names.append(DISEASE_MAPPINGS.get(name, name))

        return names

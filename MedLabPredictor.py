from dataclasses import dataclass, field
from typing import List, Dict, Any
from DiseasePredictor import DiseasePredictor

@dataclass
class MedLabPredictor(DiseasePredictor):
    """
    A subclass of DiseasePredictor specifically for handling MedLab predictions.
    
    Attributes:
        confirmed_diag (Dict[str, Any]): A dictionary containing confirmed diagnoses, mapping verbose disease names to their details.
    """
    confirmed_diag: Dict[str, Any] = field(default_factory=dict)
    confirmed_names: list[str] = field(default_factory=list)

    def select_top_four(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Selects the top four most likely diagnoses from the provided data.
        
        Args:
            data (Dict[str, Any]): A dictionary containing potential diagnoses and their probabilities.
                                   Expects a key 'likely_diag' which is a list of dictionaries.
        
        Returns:
            List[Dict[str, Any]]: A list of the top four most likely diagnoses, sorted in descending order by probability.
        """
        # Sort the likely diagnoses by probability in descending order
        sorted_responses = sorted(data.get("likely_diag", []), key=lambda x: x.get('probability', 0), reverse=True)
        
        # Return the top four diagnoses
        return sorted_responses[:4]

    def set_values(self, data: Dict[str, Any]) -> None:
        """
        Sets the values for the names, probabilities, important features, and confirmed diagnoses.
        
        Args:
            data (Dict[str, Any]): A dictionary containing the diagnosis data. It includes:
                                   - 'likely_diag': A list of likely diagnoses with their probabilities and feature importances.
                                   - 'confirmed_diag': A list of confirmed diagnoses.
        """
        # Select the top four diagnoses based on their probabilities
        diagnosis = self.select_top_four(data)
        
        # Iterate through the top four likely diagnoses and set values for names, probabilities, and important features
        for disease in diagnosis:
            name = disease["disease_name"]
            
            # If the disease name is not already in the names list, add it
            if name not in self.names:
                self.names.append(name)
                
                # Set the disease probability
                self.prob[name] = disease["probability"]
                
                # Set the important features for the disease, sorted by their importance
                self.imp_features[name] = dict(sorted(disease["feature_importances"].items(), key=lambda item: item[1], reverse=True))

                
        
        # Add the confirmed diagnoses to the confirmed_diag attribute
        for disease in data["confirmed_diag"]:
            self.confirmed_diag[disease["verbose_name"]] = disease
            self.confirmed_names.append(disease["verbose_name"])
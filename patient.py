from ChronicPredictor import ChronicPredictor
from MedLabPredictor import MedLabPredictor
from Recommendations import Recommendations
import json
from datetime import datetime

# Load disease name mappings from JSON file
with open("static/disease_name_mapping.json", "r") as file:
    DISEASE_MAPPINGS = json.load(file)

class Patient:
    """
    A class to represent a Patient and handle their medical data, predictions, and recommendations.

    Attributes:
        patient_ID (int): The patient's unique ID.
        patient_practice (str): The practice or clinic associated with the patient.
        data (dict): The patient's medical data including diagnoses.
        chronic_pred (ChronicPredictor): Predictions related to chronic diseases.
        medlab_pred (MedLabPredictor): Predictions related to medical labs.
        recommendations (Recommendations): Recommendations based on predictions.
        
    Methods:
        reset_patient(): Resets patient attributes to default values.
        clean_data(keys): Removes specified keys from the patient's data.
        sort_diagnosis(): Sorts the patient's diagnoses by date in descending order.
        collect_patient_data(data): Collects and processes patient data into predictions and recommendations.
        get_chronic_pred(): Returns information related to chronic disease predictions.
        get_medlab_pred(): Returns information related to medical lab predictions.
        get_recommendations(): Returns recommendations related to the patient's data.
    """

    def __init__(self, patient_ID=0, patient_practice="", data=None, chronic_pred=None, medlab_pred=None, recommendations=None):
        """ 
        Initializes a Patient object with default or provided values. 
        """
        self._patient_ID = patient_ID
        self._patient_practice = patient_practice
        self._data = data
        self.chronic_pred = chronic_pred
        self.medlab_pred = medlab_pred
        self.recommendations = recommendations

    # Getter, Setter, and Deleter for patient_ID
    @property
    def patient_ID(self):
        return self._patient_ID

    @patient_ID.setter
    def patient_ID(self, ID):
        self._patient_ID = ID

    @patient_ID.deleter
    def patient_ID(self):
        del self._patient_ID

    # Getter, Setter, and Deleter for patient_practice
    @property
    def patient_practice(self):
        return self._patient_practice

    @patient_practice.setter
    def patient_practice(self, practice):
        self._patient_practice = practice

    @patient_practice.deleter
    def patient_practice(self):
        del self._patient_practice

    # Getter, Setter, and Deleter for data
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, val):
        self._data = val

    @data.deleter
    def data(self):
        del self._data

    def reset_patient(self):
        """
        Resets the patient's attributes to default values.
        """
        self.patient_ID = 0
        self.patient_practice = ""
        self.chronic_pred = None
        self.medlab_pred = None
        self.recommendations = None
        self.data = None

    def clean_data(self, keys):
        """
        Removes specified keys from the patient's data.

        Args:
            keys (List[str]): List of keys to remove from data.

        Returns:
            dict: The cleaned patient data.
        """
        for key in keys:
            self._data.pop(key, None)
        return self._data

    def sort_diagnosis(self):
        """
        Sorts the patient's diagnoses by date in descending order.
        """
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                return datetime.min

        # Sort diagnoses by date, with the most recent first
        sorted_diagnoses = sorted(self.data["Diagnoses"], key=lambda x: parse_date(x.get('Date', '')), reverse=True)
        self.data["Diagnoses"] = sorted_diagnoses

    def collect_patient_data(self, data):
        """
        Collects patient data and uses it to make predictions and set recommendations.

        Args:
            data (dict): A dictionary containing patient data including chronic diseases and medlabs responses.
        """
        # Set chronic disease predictions
        self.chronic_pred = ChronicPredictor()
        self.chronic_pred.set_values(data["chronic_diseases_response"])
        
        # Set medical lab predictions
        self.medlab_pred = MedLabPredictor()
        self.medlab_pred.set_values(data["medlabs_response"])
        
        # Set recommendations based on filtered predictions
        self.recommendations = Recommendations()
        filtered_names = self.recommendations.filter_recommendations(self.chronic_pred, self.medlab_pred)
        self.recommendations.set_values(filtered_names)

    def get_chronic_pred(self):
        """
        Returns information related to chronic disease predictions.

        Returns:
            Tuple: (names, prob, feature_vector, imp_features, risky_features, top_pred_rules)
        """
        return (self.chronic_pred.names, 
                self.chronic_pred.prob, 
                self.chronic_pred.feature_vector, 
                self.chronic_pred.imp_features, 
                self.chronic_pred.risky_features, 
                self.chronic_pred.top_pred_rules)

    def get_medlab_pred(self):
        """
        Returns information related to medical lab predictions.

        Returns:
            Tuple: (names, prob, imp_features, confirmed_diag)
        """
        return (self.medlab_pred.names, 
                self.medlab_pred.prob, 
                self.medlab_pred.imp_features, 
                self.medlab_pred.confirmed_diag)

    def get_recommendations(self):
        """
        Returns recommendations based on the patient's chronic and medlab predictions.

        Returns:
            Tuple: (names, procedures, surgeries, labs, lifestyle_changes)
        """
        return (self.recommendations.names, 
                self.recommendations.procedures, 
                self.recommendations.surgeries, 
                self.recommendations.labs, 
                self.recommendations.lifestyle_changes)

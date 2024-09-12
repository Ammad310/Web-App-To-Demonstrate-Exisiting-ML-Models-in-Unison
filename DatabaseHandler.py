from pymongo import MongoClient
import json

class DatabaseHandler:
    """
    A class to handle interaction with the MongoDB database containing patient data.

    Attributes:
        client (MongoClient): A client for connecting to the MongoDB instance.
        db (Database): The database containing patient data.
        collection (Collection): The collection within the database containing patient data.

    Methods:
        get_patients_from_mongo(patientid: str, practice: str) -> str:
            Fetches patient data from the MongoDB collection based on the patient ID and practice.
            Returns the data in a formatted JSON string for easier readability.
    """
    
    def __init__(self):
        """
        Initializes the DatabaseHandler by connecting to the MongoDB instance and selecting the
        appropriate database and collection.
        """
        # Connect to the MongoDB instance (replace with the actual server address and port if needed)
        self.client = MongoClient('mongodb://172.16.103.206:27017/')
        
        # Select the database ('Patients_for_API') to interact with
        self.db = self.client['Patients_for_API']
        
        # Select the collection ('PatientData200') within the database
        self.collection = self.db['PatientData200']

    def get_patients_from_mongo(self, patientid, practice):
        """
        Fetches patient data from the MongoDB collection based on the provided patient ID and practice.
        
        Args:
            patientid (str): The ID of the patient to fetch data for.
            practice (str): The practice associated with the patient.

        Returns:
            str: A formatted JSON string containing the patient data or None if no document is found.
        """
        # Fetch a single document from the MongoDB collection based on patient ID and practice
        document = self.collection.find_one({"patientid": patientid, "practice": practice})

        # Convert the MongoDB document to a pretty-formatted JSON string, defaulting to str for non-serializable types
        pretty_json = json.dumps(document, indent=4, sort_keys=False, default=str)
        
        # Return the formatted JSON string containing the patient data
        return pretty_json

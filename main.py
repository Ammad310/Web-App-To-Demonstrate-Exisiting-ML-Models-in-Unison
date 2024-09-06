from flask import Flask, render_template, request, session, flash, redirect, jsonify, url_for
from flask_session import Session
import json
import requests
from patient import Patient
from starter import DatabaseHandler
import os

with open("static\disease_name_mapping.json", "r") as file:
    DISEASE_MAPPINGS = json.load(file)

API_URL = "http://172.16.101.167:5000/integrate"



class FlaskApp:
    def __init__(self):
        self.app = Flask("__main__")
        self.app.config["SESSION_TYPE"] = "filesystem"
        self.app.config["SECRET_KEY"] = "your_secret_key_here"
        Session(self.app)
        
        self.patient1 = Patient()
        
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/', methods=["GET", "POST"])
        def home():
            return self.handle_home()

        @self.app.route('/diagnose')
        def diagnose():
            return self.handle_diagnose()

        @self.app.route("/chronic")
        def chronic_diagnosis():
            return self.handle_chronic_diagnosis()

        @self.app.route("/medlabs")
        def medlabs_response():
            return self.handle_medlabs_response()

        @self.app.route("/pattern")
        def pattern_recognition():
            return self.handle_pattern_recognition()

        @self.app.route("/recommendation")
        def recommendations_response():
            return self.handle_recommendations_response()

    def handle_home(self):
        # self.patient1.reset_patient()
        if request.method == "POST":
            session['PID'] = request.form.get("PID", None)
            session['PP'] = request.form.get("PP", None)
            
            mongo_fetcher = DatabaseHandler()
            self.patient1.patient_ID = session.get("PID", '')
            self.patient1.patient_practice = session.get("PP", '')
            pat = mongo_fetcher.get_patients_from_mongo(self.patient1.patient_ID, self.patient1.patient_practice)
            self.patient1.data = json.loads(pat)
            if not self.patient1.data:
                response = {
                    'status': 'error',
                    'message': 'Patient ID or Practice is Incorrect!'
                }
                return jsonify(response), 400  # Return a 400 Bad Request status
            else:
                keys = ["_id", "patientid", "practice"]
                self.patient1.clean_data(keys)
                response = {
                    'status': 'success'
                }
                return jsonify(response)
        
        # Read practices from the JSON file
        json_file_path = os.path.join(self.app.static_folder, 'PatientsWithAllResponses.json')
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        # Extract unique practices from the data
        practices = list({item['practice']: item for item in data}.values())
        
        return render_template("index.html", practices=practices)

    # def handle_diagnose(self):
    #     response = requests.post(API_URL, json=self.patient1.data)
    #     self.patient1.collect_patient_data(response.json())
    #     self.patient1.sort_diagnosis()
    #     return render_template('diagnose.html', data=self.patient1.data)

    def handle_diagnose(self):
        response = requests.post(API_URL, json=self.patient1.data)
        
        # Check if the response contains the key "chronic_disease_response"
        if "chronic_diseases_response" not in response.json():
            flash("The server failed to respond, please try again later!", "danger")
            return redirect(url_for("home"))
        
        # Continue with the normal flow if the key exists
        # print(response.json())
        self.patient1.collect_patient_data(response.json())
        self.patient1.sort_diagnosis()
        return render_template('diagnose.html', data=self.patient1.data)


    def handle_chronic_diagnosis(self):
        names, prob, vector, imp_features, risky, rules = self.patient1.get_chronic_pred()
        sorted_names = sorted(names, key=lambda x: prob[x], reverse=True)
        return render_template("chronic_disease.html", names=sorted_names, prob=prob, imp=imp_features, vector=vector, risk=risky, data=self.patient1.data, rules=rules)

    def handle_medlabs_response(self):
        names, probs, feature_imp, confirmed= self.patient1.get_medlab_pred()
        print(confirmed)
        return render_template("medlabs_response.html", names=names, probs=probs, feature_imp=feature_imp, confirmed=confirmed, data=self.patient1.data)

    def handle_pattern_recognition(self):
        fig = self.patient1.chronic_pred.generate_sankey_plot()
        plot_html = fig.to_html(full_html=False) if fig else None
        return render_template("pattern_recognition.html", html=plot_html, data=self.patient1.data)


    def handle_recommendations_response(self):
        names, procedures, surgeries, labs, lifestyle_changes = self.patient1.get_recommendations()
        
        # Aggregating data
        def aggregate_data(recommendations):
            aggregated = {}
            for name in names:
                if name != "Normal":
                    for item in recommendations[name]:
                        if item not in aggregated:
                            aggregated[item] = []
                        aggregated[item].append(name)
            return aggregated

        aggregated_procedures = aggregate_data(procedures)
        aggregated_surgeries = aggregate_data(surgeries)
        aggregated_lifestyle_changes = aggregate_data(lifestyle_changes)
        aggregated_labs = aggregate_data(labs)
        
        return render_template(
            "Recommendation.html",
            names=names,
            procedures=aggregated_procedures,
            surgeries=aggregated_surgeries,
            lifestyle_changes=aggregated_lifestyle_changes,
            labs=aggregated_labs,
            data=self.patient1.data
        )


if __name__ == '__main__':
    app_instance = FlaskApp()
    app_instance.app.run(host="172.16.105.134", debug=True, port=5000)

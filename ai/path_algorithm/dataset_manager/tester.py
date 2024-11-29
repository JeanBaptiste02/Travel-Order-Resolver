from flask import Flask, request, jsonify
from flask_cors import CORS  
import pandas as pd

app = Flask(__name__)

CORS(app)  

timetables = pd.read_csv("C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/path_algorithm/dataset/timetables.csv", delimiter="\t")
train_stations = pd.read_csv("C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/path_algorithm/dataset/liste-des-gares.csv", delimiter=";")
voyageurs_stations = pd.read_csv("C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/path_algorithm/dataset/gares-de-voyageurs.csv", delimiter=";")

def normalize_name(name):
    return name.strip().lower()

train_stations["LIBELLE"] = train_stations["LIBELLE"].apply(normalize_name)
voyageurs_stations["Nom"] = voyageurs_stations["Nom"].apply(normalize_name)


@app.route('/find_path', methods=['POST'])
def find_path():
    data = request.get_json()
    depart = normalize_name(data.get("depart", ""))
    arrivee = normalize_name(data.get("arrivée", ""))

    gares_depart = train_stations[train_stations["LIBELLE"].str.contains(depart)]
    gares_arrivee = train_stations[train_stations["LIBELLE"].str.contains(arrivee)]

    if gares_depart.empty or gares_arrivee.empty:
        return jsonify({"error": "Gare(s) introuvable(s)"}), 404

    trajets = timetables[timetables["trajet"].str.contains(depart, case=False) &
                         timetables["trajet"].str.contains(arrivee, case=False)]

    if trajets.empty:
        return jsonify({"error": "Aucun trajet trouvé"}), 404

    result = []
    for _, row in trajets.iterrows():
        result.append({
            "trip_id": row["trip_id"],
            "trajet": row["trajet"],
            "durée (minutes)": row["duree"]
        })

    return jsonify({"trajets": result})


if __name__ == '__main__':
    app.run(debug=True)

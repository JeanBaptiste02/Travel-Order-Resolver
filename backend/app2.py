from flask import Flask, request, jsonify
import joblib
import spacy
import warnings
import pandas as pd
import networkx as nx

warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

# Load models and resources
lang_model_path = r"C:\\Users\\vikne\\Documents\\Master 2\\Semestre 9\\Intelligence artificielle\\Travel-Order-Resolver\\ai\\nlp\\models\\text_classification\\lang_detector\\naive_bayes_lang_detection.pkl"
lang_pipeline = joblib.load(lang_model_path)

intention_model_path = r'C:\\Users\\vikne\\Documents\\Master 2\\Semestre 9\\Intelligence artificielle\\Travel-Order-Resolver\\ai\\nlp\\models\\text_classification\\intention_detector\\bow_bigram_naive_bayes.joblib'
intention_pipeline = joblib.load(intention_model_path)

spacy_model_path = r"C:\\Users\\vikne\\Documents\\Master 2\\Semestre 9\\Intelligence artificielle\\Travel-Order-Resolver\\ai\\nlp\\models\\tokens_classification\\spacy_sm"
nlp = spacy.load(spacy_model_path)

id2label = {
    0: 'is_correct',
    1: 'is_not_trip',
    2: 'is_unknown'
}

# Flask app initialization
app = Flask(__name__)

# Helper functions
def load_graph_from_parquet(parquet_path: str) -> nx.Graph:
    graph_df = pd.read_parquet(parquet_path)
    G = nx.Graph()

    for _, row in graph_df.iterrows():
        city_from = row['city_from']
        city_to = row['city_to']
        distance = row['distance']

        G.add_edge(city_from, city_to, weight=distance)

    return G

def find_shortest_path(graph: nx.Graph, start: str, end: str) -> dict:
    try:
        length, path = nx.single_source_dijkstra(graph, source=start, target=end)
        return {
            'path': path,
            'total_duration': length
        }
    except nx.NetworkXNoPath:
        return {
            'path': ["No path found"],
            'total_duration': None
        }

# Load graph
parquet_path = r"C:\\Users\\vikne\\Documents\\Master 2\\Semestre 9\\Intelligence artificielle\\Travel-Order-Resolver\\ai\\path_algorithm\\dataset\\graph.parquet"
graph = load_graph_from_parquet(parquet_path)

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# Endpoints
@app.route('/process_message', methods=['POST'])
def process_message():
    data = request.json
    sentence = data.get('sentence', '')

    # Detect Language
    lang_prediction = lang_pipeline.predict([sentence])
    language = "French" if lang_prediction == 0 else "Not French"

    if language != "French":
        return jsonify({"message": "La langue détectée n'est pas le français", "language": language})

    # Detect Entities
    doc = nlp(sentence)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    # If at least two entities are detected, find the shortest path
    if len(entities) >= 2:
        depart = entities[0]['text']
        arrivee = entities[1]['text']

        # Find the path between the two entities
        result = find_shortest_path(graph, depart, arrivee)

        if result['path'][0] == "No path found":
            return jsonify({
                "message": f"Aucun trajet trouvé entre {depart} et {arrivee}.",
                "path": result['path'],
                "total_duration": result['total_duration']
            })

        return jsonify({
            "message": "",
            "path": result['path'],
            "total_duration": result['total_duration'],
            "entities": entities
        })

    else:
        return jsonify({
            "message": "Pas assez d'entités détectées pour trouver un trajet.",
            "entities": entities
        })

if __name__ == '__main__':
    app.run(debug=True)

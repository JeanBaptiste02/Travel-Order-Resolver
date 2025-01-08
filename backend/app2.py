from flask import Flask, request, jsonify
import joblib
import spacy
import warnings
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

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

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# Handle OPTIONS requests
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = jsonify({})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

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

# Endpoints
@app.route('/detect_language', methods=['POST'])
def detect_language():
    data = request.json
    sentence = data.get('sentence', '')
    prediction = lang_pipeline.predict([sentence])
    language = "French" if prediction == 0 else "Not French"
    return jsonify({"language": language})

@app.route('/detect_intention', methods=['POST'])
def detect_intention():
    data = request.json
    sentence = data.get('sentence', '')
    predicted_labels = intention_pipeline.predict([sentence])
    predicted_proba = intention_pipeline.predict_proba([sentence])

    intention_scores = {
        id2label[i]: round(predicted_proba[0][i] * 100, 1)
        for i in range(len(id2label))
    }
    max_prob_idx = predicted_proba.argmax()
    return jsonify({
        "intention": id2label[max_prob_idx],
        "probability": intention_scores
    })

@app.route('/predict_entities', methods=['POST'])
def predict_entities():
    data = request.json
    sentence = data.get('sentence', '')
    doc = nlp(sentence)
    entities = [{
        "text": ent.text,
        "label": ent.label_,
        "start_char": ent.start_char,
        "end_char": ent.end_char
    } for ent in doc.ents]
    return jsonify({"entities": entities})

@app.route('/shortest_path', methods=['POST'])
def shortest_path():
    data = request.json
    start_city = data.get('start_city', '')
    end_city = data.get('end_city', '')

    result = find_shortest_path(graph, start_city, end_city)

    if result['path'][0] == "No path found":
        return jsonify({"message": "No path found", "path": result['path'], "total_duration": result['total_duration']})

    return jsonify({
        "path": result['path'],
        "total_duration": result['total_duration'],
    })

if __name__ == '__main__':
    app.run(debug=True)

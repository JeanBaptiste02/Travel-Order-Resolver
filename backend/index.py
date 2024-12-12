from flask import Flask, request, jsonify, Response
import joblib
import spacy
from travelPathFinder import TravelPathFinder
import os
import warnings
from time import sleep

# Ignorer les avertissements de versions inconsistantes
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.base")

# Initialize Flask app
app = Flask(__name__)

# Load models with error handling
try:
    # Paths for the models
    lang_model_path = "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/models/text_classification/lang_detector/naive_bayes_lang_detection.pkl"
    intent_model_path = "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/models/text_classification/intention_detector/tfidf_unigram_naive_bayes.joblib"
    ner_model_path = "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/models/tokens_classification/spacy"

    # Checking if models exist
    if not os.path.exists(lang_model_path):
        raise FileNotFoundError(f"Language model not found at {lang_model_path}")
    if not os.path.exists(intent_model_path):
        raise FileNotFoundError(f"Intent model not found at {intent_model_path}")
    if not os.path.exists(ner_model_path):
        raise FileNotFoundError(f"NER model not found at {ner_model_path}")

    # Load the models
    print("Loading models...")
    lang_model = joblib.load(lang_model_path)
    intent_model = joblib.load(intent_model_path)
    ner_model = spacy.load(ner_model_path)

    # Preload graph and verify data
    print("Verifying travel data...")
    TravelPathFinder.verify_data_exists()

    print("Models loaded successfully.")
except Exception as e:
    print(f"Error during initialization: {e}")
    raise

# Helper functions
def is_french(sentence):
    """Check if the sentence is in French."""
    try:
        print("Detecting language...")
        is_french_result = lang_model.predict([sentence])[0] == 0
        print(f"Language detected: {'French' if is_french_result else 'Not French'}")
        return is_french_result
    except Exception as e:
        print(f"Error in language detection: {e}")
        return False

def is_travel_order(sentence):
    """Check if the sentence is a travel order."""
    try:
        print("Detecting intent...")
        prediction = intent_model.predict([sentence])  # Prediction is an array
        print(f"Intent detected: {'Travel order' if prediction[0] == 1 else 'Not a travel order'}")
        return prediction[0] == 1  # Access the first element of the prediction array
    except Exception as e:
        print(f"Error in intent detection: {e}")
        return False

def extract_entities(sentence):
    """Extract departure and destination entities from the sentence."""
    try:
        print("Extracting entities (departure, destination)...")
        doc = ner_model(sentence)
        departure = None
        destination = None

        for ent in doc.ents:
            if ent.label_ == "DEP":
                departure = ent.text
            elif ent.label_ == "ARR":
                destination = ent.text

        print(f"Entities extracted: Departure = {departure}, Destination = {destination}")
        return departure, destination
    except Exception as e:
        print(f"Error in entity extraction: {e}")
        return None, None

def generate_progress():
    """Yield the progress in streaming form."""
    yield "Step 1: Detecting language...\n"
    sleep(2)  # Simulate processing time
    yield "Step 2: Detecting intent...\n"
    sleep(2)  # Simulate processing time
    yield "Step 3: Extracting entities...\n"
    sleep(2)  # Simulate processing time
    yield "Step 4: Loading graph...\n"
    sleep(2)  # Simulate processing time
    yield "Step 5: Calculating path...\n"
    sleep(2)  # Simulate processing time
    yield "Process Complete.\n"

# Routes for each individual task
@app.route("/detect_language", methods=["POST"])
@cache.cached(timeout=60, query_string=True)  
def detect_language():
    """Detect the language of the provided sentence."""
    if not request.json or "sentence" not in request.json:
        return jsonify({"error": "Invalid input, 'sentence' field is required."}), 400

    sentence = request.json.get("sentence", "")
    print(f"Received sentence: {sentence}")

    is_french_result = is_french(sentence)
    return jsonify({"language": "French" if is_french_result else "Not French"}), 200

@app.route("/detect_intent", methods=["POST"])
def detect_intent():
    """Detect if the sentence is a travel order."""
    if not request.json or "sentence" not in request.json:
        return jsonify({"error": "Invalid input, 'sentence' field is required."}), 400

    sentence = request.json.get("sentence", "")
    print(f"Received sentence: {sentence}")

    is_travel_order_result = is_travel_order(sentence)
    return jsonify({"intent": "Travel order" if is_travel_order_result else "Not a travel order"}), 200

@app.route("/extract_entities", methods=["POST"])
def extract_entities_route():
    """Extract departure and destination entities from the sentence."""
    if not request.json or "sentence" not in request.json:
        return jsonify({"error": "Invalid input, 'sentence' field is required."}), 400

    sentence = request.json.get("sentence", "")
    print(f"Received sentence: {sentence}")

    departure, destination = extract_entities(sentence)
    if not departure or not destination:
        return jsonify({"error": "Unable to extract departure and destination."}), 400

    return jsonify({"departure": departure, "destination": destination}), 200

@app.route("/process", methods=["POST"])
def process_request():
    """Process the incoming travel request."""
    if not request.json or "sentence" not in request.json:
        print("Error: Invalid input, 'sentence' field is required.")
        return jsonify({"error": "Invalid input, 'sentence' field is required."}), 400

    sentence = request.json.get("sentence", "")
    print(f"Received sentence: {sentence}")

    # Step 1: Detect language
    if not is_french(sentence):
        print("Error: The sentence is not in French.")
        return jsonify({"error": "The sentence is not in French."}), 400

    # Step 2: Detect intention
    if not is_travel_order(sentence):
        print("Error: The sentence is not a valid travel order.")
        return jsonify({"error": "The sentence is not a valid travel order."}), 400

    # Step 3: Extract entities
    departure, destination = extract_entities(sentence)

    if not departure or not destination:
        print("Error: Unable to extract departure and destination.")
        return jsonify({"error": "Unable to extract departure and destination."}), 400

    # Step 4: Find shortest path
    try:
        print("Loading graph for shortest path calculation...")
        graph = TravelPathFinder.load_graph()
        print(f"Graph loaded, calculating shortest path from {departure.upper()} to {destination.upper()}...")

        # Using tqdm for visual feedback if the pathfinding is complex
        path_data = TravelPathFinder.calculate_shortest_path(graph, departure.upper(), destination.upper())

        if "UNKNOWN" in path_data["path"]:
            print("Error: Unable to find a valid path.")
            return jsonify({"error": "Unable to find a valid path."}), 400

        # Step 5: Format response
        response = {
            "sentence": sentence,
            "departure": path_data["departure"],
            "destination": path_data["arrival"],
            "path": path_data["path"],
            "durations": path_data["duration_between_stations"],
            "total_duration": TravelPathFinder.convert_minutes_to_hours(path_data["total_duration"]),
        }

        print(f"Path found: {response}")
        return jsonify(response), 200

    except Exception as e:
        print(f"Error in path finding: {e}")
        return jsonify({"error": "An internal error occurred while finding the path."}), 500

# Endpoint to test streaming progress
@app.route("/progress", methods=["GET"])
def progress():
    """Returns the progress of the processing."""
    return Response(generate_progress(), content_type='text/plain;charset=utf-8')

if __name__ == "__main__":
    # Run Flask app
    print("Starting Flask app...")
    app.run(debug=True, threaded=True)  # Enable threading for parallel requests

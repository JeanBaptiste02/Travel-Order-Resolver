from flask import Flask, request, jsonify, abort
import joblib
import spacy
import warnings
import pandas as pd
import networkx as nx
import random

warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

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

app = Flask(__name__)

special_cities = {
    "saint-germain-en-laye", "saint-denis", "saint-etienne", "saint-nazaire", "saint-quentin", 
    "saint-brieuc", "saint-raphael", "saint-lo", "saint-paul", "saint-malo", "saint-tropez", 
    "saint-louis", "saint-pierre", "saint-joseph", "saint-saulve", "saint-helier", "saint-brevin-les-pins", 
    "saint-gilles", "saint-martin", "saint-leu", "saint-barthelemy", "saint-augustin", "saint-claude", 
    "saint-jean-de-la-ruisse", "saint-pierre-des-corps", "saint-ines", "saint-michel", "saint-emilion", 
    "saint-cyr-sur-loire", "saint-remy-de-provence", "saint-raphael-de-la-rose", "saint-aubin", 
    "saint-augustin-de-desmaures", "saint-andre", "saint-ambroise", "saint-julien-en-genevois", 
    "saint-doulchard", "saint-laurent-du-var", "saint-martin-de-seignanx", "saint-thierry", "saint-roch", 
    "saint-leger-de-la-montagne", "saint-herblain", "saint-francois", "saint-paul-de-vence", 
    "saint-sauveur", "saint-jean-de-luz", "saint-tropez-le-rouge", "saint-michel-de-latour", 
    "saint-remy-de-provence", "saint-arnoult-en-yvelines", "saint-leger-les-domart", "saint-pierre-et-miquelon",
    "saint-georges", "saint-dizier"
}

def load_cities_from_txt(txt_path: str) -> set:
    with open(txt_path, 'r', encoding='utf-8') as file:
        cities = {line.strip().upper() for line in file.readlines()}
    return cities

cities_set = load_cities_from_txt(r'C:\\Users\\vikne\\Documents\\Master 2\\Semestre 9\\Intelligence artificielle\\Travel-Order-Resolver\\ai\\nlp\\utils\\supporting_datas\\urban_geodata_masterlist_v1.0.txt')

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

parquet_path = r"C:\\Users\\vikne\\Documents\\Master 2\\Semestre 9\\Intelligence artificielle\\Travel-Order-Resolver\\ai\\path_algorithm\\dataset\\graph.parquet"
graph = load_graph_from_parquet(parquet_path)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

def convert_cities_to_uppercase(sentence: str, cities: set) -> str:
    words = sentence.split()
    converted_sentence = []

    for word in words:
        if word.lower() in special_cities:
            converted_sentence.append(word.upper())
        elif word.upper() in cities:
            converted_sentence.append(word.upper())
        else:
            converted_sentence.append(word)

    return ' '.join(converted_sentence)

error_responses = [
    "Je n'ai pas tout compris, pourrais-tu reformuler ta demande ?",
    "Désolé, je n'arrive pas à saisir ce que tu veux dire. Peux-tu expliquer autrement ?",
    "Hmm, il semble y avoir un malentendu. Pourrais-tu préciser ?",
    "Oups, je n'ai pas bien saisi. Peux-tu reformuler ta phrase ?",
    "Je crois que je ne comprends pas tout. Pourrais-tu clarifier ?",
    "Désolé, je ne suis pas sûr de ce que tu demandes. Peux-tu être plus précis ?",
    "Je n'ai pas bien saisi. Peux-tu reformuler ta question, s'il te plaît ?",
    "Je suis un peu perdu. Pourrais-tu être plus clair ?",
    "Je ne suis pas sûr de comprendre. Est-ce que tu peux expliquer différemment ?",
    "Désolé, je n'ai pas compris. Tu pourrais reformuler ta demande ?",
]

non_french_responses = [
    "Je ne comprends que le français, pourrais-tu reformuler dans cette langue ?",
    "Désolé, mon intelligence est limitée au français. Peux-tu m'écrire en français ?",
    "Je ne parle que français. Essaie de me poser la question en français.",
    "Malheureusement, je ne peux répondre qu'en français. Reformule dans cette langue, s'il te plaît.",
    "Je suis désolé, mais je ne comprends que le français. Peux-tu essayer à nouveau en français ?"
]

success_responses = [
    "Super, j'ai trouvé un itinéraire pour toi : {path}. Ça prendra environ {duration} minutes.",
    "Voilà ce que j'ai trouvé comme itinéraire : {path}. Tu seras à destination en environ {duration} minutes.",
    "Je t'ai déniché un trajet : {path}. Compte environ {duration} minutes pour le parcours.",
    "Check ça ! Voici un trajet : {path}. Il te faudra environ {duration} minutes.",
    "C'est tout bon, voici le chemin : {path}. Cela prendra environ {duration} minutes.",
    "Voici ce que j'ai trouvé pour toi : {path}. Prépare-toi à environ {duration} minutes de trajet.",
    "Tu peux suivre ce parcours : {path}. La durée totale sera d'environ {duration} minutes.",
    "J'ai trouvé un itinéraire : {path}. Attends-toi à environ {duration} minutes pour le trajet.",
    "Voici l'itinéraire que j'ai trouvé : {path}. Le trajet devrait durer environ {duration} minutes.",
    "J'ai une suggestion pour toi : {path}. Cela prendra environ {duration} minutes.",
]

@app.route('/process_message', methods=['POST'])
def process_message():
    data = request.json
    sentence = data.get('sentence', '')

    sentence = convert_cities_to_uppercase(sentence, cities_set)

    lang_prediction = lang_pipeline.predict([sentence])
    language = "French" if lang_prediction == 0 else "Not French"

    if language != "French":
        return jsonify({
            "message": random.choice(non_french_responses),
            "language": language
        })

    doc = nlp(sentence)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    if len(entities) >= 2:
        depart = entities[0]['text']
        arrivee = entities[1]['text']

        result = find_shortest_path(graph, depart, arrivee)

        if result['path'][0] == "No path found":
            return jsonify({
                "message": f"Aucun trajet trouvé entre {depart} et {arrivee}.",
                "path": result['path'],
                "total_duration": result['total_duration']
            })

        path = " -> ".join(result['path'])
        total_duration = result['total_duration']
        return jsonify({
            "message": random.choice(success_responses).format(path=path, duration=total_duration),
            "path": result['path'],
            "total_duration": result['total_duration'],
            "entities": entities
        })

    else:
        return jsonify({"message": random.choice(error_responses)})

if __name__ == '__main__':
    app.run(debug=True)

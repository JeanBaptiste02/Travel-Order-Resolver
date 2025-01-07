import joblib
import spacy
import warnings
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import pyarrow.parquet as pq
import random
import ipywidgets as widgets
from IPython.display import display

warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

lang_model_path = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\models\text_classification\lang_detector\naive_bayes_lang_detection.pkl"
lang_pipeline = joblib.load(lang_model_path)

intention_model_path = r'C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\models\text_classification\intention_detector\bow_bigram_naive_bayes.joblib'
intention_pipeline = joblib.load(intention_model_path)

spacy_model_path = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\models\tokens_classification\spacy_sm"
nlp = spacy.load(spacy_model_path)

id2label = {
    0: 'is_correct',
    1: 'is_not_trip',
    2: 'is_unknown'
}

def detect_language(sentence):
    print("\n[INFO] Détection de la langue...")
    prediction = lang_pipeline.predict([sentence])
    if prediction == 0:
        print("[INFO] La langue de la phrase est : Français")
        return "French"
    else:
        print("[INFO] La langue de la phrase n'est pas le Français.")
        return "Not French"

def detect_intention(sentence):
    print("\n[INFO] Détection de l'intention...")
    predicted_labels = intention_pipeline.predict([sentence])
    predicted_proba = intention_pipeline.predict_proba([sentence])

    print(f"Phrase : {sentence}")
    for i, label in id2label.items():
        print(f"Intention '{label}' : {round(predicted_proba[0][i] * 100, 1)}%")
    
    max_prob_idx = predicted_proba.argmax()
    return id2label[max_prob_idx], predicted_proba[0][max_prob_idx]

def predict_entities(sentence):
    print("\n[INFO] Détection des entités avec SpaCy...")
    doc = nlp(sentence)
    
    print(f"\nPhrase : {sentence}")
    print("Entités reconnues :")
    entities = []
    for ent in doc.ents:
        print(f" - Texte : {ent.text}, Label : {ent.label_}, Position : ({ent.start_char}, {ent.end_char})")
        entities.append(ent.text)
    
    return entities

def load_graph_from_parquet(parquet_path: str) -> nx.Graph:
    """Load the graph from the Parquet file."""
    graph_df = pd.read_parquet(parquet_path)
    G = nx.Graph()
    
    for _, row in graph_df.iterrows():
        city_from = row['city_from']
        city_to = row['city_to']
        distance = row['distance']
        
        G.add_edge(city_from, city_to, weight=distance)
    
    return G

def find_shortest_path(graph: nx.Graph, start: str, end: str) -> dict:
    """Find the shortest path using Dijkstra's algorithm."""
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

def main():
    parquet_path = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\path_algorithm\dataset\graph.parquet"
    print("Loading graph from Parquet...")
    graph = load_graph_from_parquet(parquet_path)
    print("Graph loaded.")
    
    while True:
        sentence = input("\nEntrez une phrase (ou tapez 'exit' pour quitter) : ")

        if sentence.lower() == 'exit':
            print("[INFO] Fermeture du programme.")
            break

        language = detect_language(sentence)
        if language != "French":
            print("[INFO] Arrêt du programme : la phrase n'est pas en français.")
            break

        intention, prob = detect_intention(sentence)

        if intention != 'is_correct' and not (40 <= prob <= 60):
            print("[INFO] Arrêt du programme : ce n'est pas un Travel Order.")
            break

        print("[INFO] Travel Order détecté, classification par tokens en cours...")
        
        entities = predict_entities(sentence)

        if len(entities) >= 2:
            start_city = entities[0]
            end_city = entities[1]

            result = find_shortest_path(graph, start_city, end_city)
            
            if result['path'][0] == "No path found":
                print(f"No path found between {start_city} and {end_city}.")
            else:
                print(f"Shortest path from {start_city} to {end_city}: {result['path']}")
                print(f"Total duration: {result['total_duration']} minutes")
                
                path_subgraph = graph.subgraph(result['path']).copy()
                plt.figure(figsize=(6, 6))
                pos = nx.spring_layout(path_subgraph, seed=42)
                plt.title(f"Shortest Path: {start_city} to {end_city}")
                nx.draw(path_subgraph, pos, with_labels=True, node_size=3000, node_color='lightgreen', font_size=10, font_weight='bold', edge_color='gray')
                edge_labels = nx.get_edge_attributes(path_subgraph, 'weight')
                nx.draw_networkx_edge_labels(path_subgraph, pos, edge_labels=edge_labels)
                plt.show()

        else:
            print("[INFO] Pas assez d'entités détectées pour calculer un chemin.")

if __name__ == "__main__":
    main()
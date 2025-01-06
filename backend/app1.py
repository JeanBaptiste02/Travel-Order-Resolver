import joblib
import spacy
import warnings

# Désactiver les avertissements InconsistentVersionWarning de scikit-learn
warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

# Charger le modèle de détection de la langue (Naive Bayes pour la détection du français)
lang_model_path = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\models\text_classification\lang_detector\naive_bayes_lang_detection.pkl"
lang_pipeline = joblib.load(lang_model_path)

# Charger le modèle pour la détection de l'intention
intention_model_path = r'C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\models\text_classification\intention_detector\tfidf_bigram_naive_bayes.joblib'
intention_pipeline = joblib.load(intention_model_path)

# Charger le modèle SpaCy pour la classification par tokens
spacy_model_path = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\models\tokens_classification\spacy_sm"
nlp = spacy.load(spacy_model_path)

# Mappings pour l'intention
id2label = {
    0: 'is_correct',
    1: 'is_not_trip',
    2: 'is_unknown'
}

# Fonction pour détecter la langue (Français ou pas)
def detect_language(sentence):
    print("\n[INFO] Détection de la langue...")
    prediction = lang_pipeline.predict([sentence])
    if prediction == 0:
        print("[INFO] La langue de la phrase est : Français")
        return "French"
    else:
        print("[INFO] La langue de la phrase n'est pas le Français.")
        return "Not French"

# Fonction pour prédire l'intention de la phrase
def detect_intention(sentence):
    print("\n[INFO] Détection de l'intention...")
    predicted_labels = intention_pipeline.predict([sentence])
    predicted_proba = intention_pipeline.predict_proba([sentence])

    print(f"Phrase : {sentence}")
    for i, label in id2label.items():
        print(f"Intention '{label}' : {round(predicted_proba[0][i] * 100, 1)}%")
    
    # Retourner l'intention principale
    max_prob_idx = predicted_proba.argmax()
    return id2label[max_prob_idx], predicted_proba[0][max_prob_idx]

# Fonction pour prédire les entités avec le modèle SpaCy
def predict_entities(sentence):
    print("\n[INFO] Détection des entités avec SpaCy...")
    doc = nlp(sentence)
    
    print(f"\nPhrase : {sentence}")
    print("Entités reconnues :")
    for ent in doc.ents:
        print(f" - Texte : {ent.text}, Label : {ent.label_}, Position : ({ent.start_char}, {ent.end_char})")

# Fonction principale pour enchaîner les étapes
def main():
    while True:
        # Entrée utilisateur
        sentence = input("\nEntrez une phrase (ou tapez 'exit' pour quitter) : ")

        if sentence.lower() == 'exit':
            print("[INFO] Fermeture du programme.")
            break

        # Étape 1: Détecter la langue
        language = detect_language(sentence)
        if language != "French":
            print("[INFO] Arrêt du programme : la phrase n'est pas en français.")
            break

        # Étape 2: Détecter l'intention
        intention, prob = detect_intention(sentence)

        # Si l'intention est 'is_correct' avec une probabilité entre 40% et 60%, on passe à l'étape suivante
        if intention != 'is_correct' and not (40 <= prob <= 60):
            print("[INFO] Arrêt du programme : ce n'est pas un Travel Order.")
            break

        print("[INFO] Travel Order détecté, classification par tokens en cours...")
        
        # Étape 3: Si c'est un Travel Order, classer les entités
        predict_entities(sentence)

if __name__ == "__main__":
    main()

import joblib  # Pour charger un modèle pickle
from typing import Any

class LangDetector:
    def __init__(self, model_path: str = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\models\text_classification\lang_detector\naive_bayes_lang_detection.pkl"):
        self.model = joblib.load(model_path)

    def detect_language(self, text: str) -> str:
        """Detect the language of a given text using the Naive Bayes model."""
        # Utiliser le modèle pour prédire la langue du texte
        prediction = self.model.predict([text])  # Le modèle retourne une liste avec la prédiction
        return prediction[0]  # Retourner le code de la langue

from keras.models import load_model

class IntentClassifier:
    def __init__(self, model_path=r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\models\text_classification\intention_detector\gru_nn.h5"):
        self.model = load_model(model_path)

    def classify_intent(self, text: str) -> str:
        """Classify the intent of the text."""
        prediction = self.model.predict([text])
        return prediction  # returning predicted intent

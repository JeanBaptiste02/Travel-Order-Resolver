import spacy

class NERExtractor:
    def __init__(self, model_path=r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\models\tokens_classification\spacy"):
        self.nlp = spacy.load(model_path)

    def extract_entities(self, text: str) -> dict:
        """Extract departure and destination entities."""
        doc = self.nlp(text)
        entities = {"departure": None, "destination": None}

        for ent in doc.ents:
            if ent.label_ == "GPE":  # Label for location entities
                if not entities["departure"]:
                    entities["departure"] = ent.text
                elif entities["departure"] and not entities["destination"]:
                    entities["destination"] = ent.text
        return entities

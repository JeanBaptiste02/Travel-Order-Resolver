from text_classifier_lang import LangDetector
from text_classifier_intent import IntentClassifier
from token_classifier_ner import NERExtractor
from travel_path_finder import TravelPathFinder


class TripResolver:
    def __init__(self):
        # Initialize the models
        self.lang_detector = LangDetector("ai/nlp/models/lang_detector/fasttext_model.bin")
        self.intent_classifier = IntentClassifier("ai/nlp/models/intent_classifier/gru_nn.h5")
        self.ner_extractor = NERExtractor("ai/nlp/models/ner_extractor/spacy_model")
        
    def resolve_trip(self, sentence: str):
        """Resolve the trip by detecting language, intent, and extracting entities."""
        # 1. Lang detection
        lang = self.lang_detector.detect_language(sentence)
        print(f"Detected Language: {lang}")

        # 2. Intent classification
        intent = self.intent_classifier.classify_intent(sentence)
        print(f"Detected Intent: {intent}")

        # 3. NER extraction (departure and destination)
        entities = self.ner_extractor.extract_entities(sentence)
        departure = entities.get("departure")
        destination = entities.get("destination")
        print(f"Departure: {departure}, Destination: {destination}")

        if intent == "TravelOrder" and departure and destination:
            # Get shortest path using the Dijkstra algorithm if it's a valid travel order
            path = TravelPathFinder.get_shortest_route([departure, destination])
            return path
        else:
            return "Invalid travel order or missing entities."

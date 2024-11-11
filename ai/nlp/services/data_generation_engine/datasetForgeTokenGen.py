import pandas as pd
import random
import spacy
from typing import List
import os

class TokenClassificationGenerator:
    def __init__(self, files: dict):
        self.files = files
        self.ner_labels = ["O", "B-DEP", "I-DEP", "B-ARR", "I-ARR"]
        self.nlp = spacy.load("fr_core_news_sm")

        self.sentences_data = pd.read_csv(files["sentences_samples_csv"], delimiter=";")
        self.random_sentences = pd.read_csv(files["stochastic_sentence_collection_csv"], delimiter=";")
        self.correct_sentences = self._load_sentences(files["validated_text_sequences_txt"])
        self.wrong_sentences_departure = self._load_sentences(files["departure_statements_without_arrivals_txt"])
        self.wrong_sentences_arrival = self._load_sentences(files["arrival_statements_without_departures_txt"])
        self.french_cities = self._load_cities(files["french_cities_txt"])
        self.names = pd.read_csv(files["french_national_names_csv"], header=None).iloc[:, 0].tolist()

    def _load_sentences(self, filename: str) -> List[str]:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]

    def _load_cities(self, filename: str) -> List[str]:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]

    def split_sentence(self, sentence: str) -> List[str]:
        doc = self.nlp(sentence)
        return [token.text for token in doc]

    def generate(self, steps: dict) -> None:
        sentences = self.prepare_sentences()
        df = self.generate_ner_tags_from_sentences(steps, sentences)

        path = "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/dataset/raw/generated_dataset/"
        os.makedirs(path, exist_ok=True) 

        df.to_csv(f"{path}token.csv", index=False, sep=";")
        print("Dataset generated and saved to:", f"{path}token.csv")

    def prepare_sentences(self) -> List[str]:
        final_sentences = []
        for sentence in self.correct_sentences:
            final_sentences.append(sentence.format(departure="{departure}", arrival="{arrival}"))
        return final_sentences

    def generate_ner_tags_from_sentences(self, steps: dict, sentences: List[str]) -> pd.DataFrame:
        data = []
        for x, sentence in enumerate(sentences):
            departure_city = random.choice(self.french_cities) 
            arrival_city = random.choice(self.french_cities)
            alt_sentence = sentence.format(departure=departure_city, arrival=arrival_city)

            formatted_sentence = self.split_sentence(alt_sentence)

            tags_sentence = [self.ner_labels.index("O")] * len(formatted_sentence)

            for i, word in enumerate(formatted_sentence):
                if word == departure_city:
                    tags_sentence[i] = self.ner_labels.index("B-DEP")
                if word == arrival_city:
                    tags_sentence[i] = self.ner_labels.index("B-ARR")

            # Génération des tags NER
            data.append({
                "text": sentence.format(departure=departure_city, arrival=arrival_city),
                "tokens": formatted_sentence,
                "ner_tags": tags_sentence,
                "spacy_ner_tags": self.get_spacy_ner_tags(alt_sentence, departure_city, arrival_city),
            })

        return pd.DataFrame(data, columns=["text", "tokens", "ner_tags", "spacy_ner_tags"])

    def get_spacy_ner_tags(self, sentence: str, departure_city: str, arrival_city: str) -> List[dict]:
        spacy_tags = []
        
        if departure_city in sentence:
            dep_start = sentence.find(departure_city)
            dep_end = dep_start + len(departure_city)
            spacy_tags.append({"start": dep_start, "end": dep_end, "label": "DEP"})
        
        if arrival_city in sentence:
            arr_start = sentence.find(arrival_city)
            arr_end = arr_start + len(arrival_city)
            spacy_tags.append({"start": arr_start, "end": arr_end, "label": "ARR"})

        return spacy_tags

files = {
    "sentences_samples_csv": "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/sentences_samples_dataset.csv",
    "stochastic_sentence_collection_csv": "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/stochastic_sentence_collection.csv",
    "validated_text_sequences_txt": "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/validated_text_sequences/validated_text_sequences.txt",
    "departure_statements_without_arrivals_txt": "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences/missing_tags/departure_statements_without_arrivals.txt",
    "arrival_statements_without_departures_txt": "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences/missing_tags/arrival_statements_without_departures.txt",
    "french_cities_txt": "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/urban_geodata_basic_v1.0.txt",
    "french_national_names_csv": "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/fr_personal_identifiers_dataset_v1.0.csv",
}

generator = TokenClassificationGenerator(files)

steps = {
    "departure": "Paris",
    "arrival": "Lyon",
}

generator.generate(steps)
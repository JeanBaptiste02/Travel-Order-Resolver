import pandas as pd
import random
import spacy
import numpy as np
import os
from typing import List, Dict
from itertools import product
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

class TokenClassificationGenerator:
    def __init__(self, files: dict):
        self.files = files
        self.nlp = spacy.load("fr_core_news_sm")

        # Chargement des données
        self.correct_sentences = self._load_sentences(files["validated_text_sequences_txt"])
        self.correct_sentences_with_names = self._load_sentences(files["validated_sentences_with_identifiers_txt"])
        self.ordered_sentences = self._load_sentences(files["validated_ordered_text_sequences_txt"])
        self.french_cities = self._load_cities(files["french_cities_txt"])
        self.names = pd.read_csv(files["french_national_names_csv"], header=None).iloc[:, 0].tolist()

    def _load_sentences(self, filename: str) -> List[str]:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]

    def _load_cities(self, filename: str) -> List[str]:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]

    def split_sentence(self, sentence: str) -> List[str]:
        # Séparation des tokens avec gestion de la ponctuation finale
        doc = self.nlp(sentence)
        tokens = []
        for token in doc:
            if token.text[-1] in ".!?":
                tokens.append(token.text[:-1])  # Ajouter le mot sans la ponctuation
                tokens.append(token.text[-1])  # Ajouter la ponctuation comme un token séparé
            else:
                tokens.append(token.text)
        return tokens

    def generate_spacy_ner_tags(self, sentences: List[str], names: List[str], city_pairs: List[tuple]) -> pd.DataFrame:
        data = []

        total_sentences = len(sentences) * len(city_pairs)
        with tqdm(total=total_sentences, desc="Generating Spacy NER tags") as pbar:
            for sentence in sentences:
                for departure_city, arrival_city in city_pairs:
                    name = random.choice(names)

                    # Gestion de "de" et "d'"
                    departure_prefix = "d'" if departure_city[0].lower() in "aeiouy" else "de"
                    alt_sentence = sentence.format(
                        departure=f"{departure_prefix} {departure_city}",
                        arrival=arrival_city,
                        name=name
                    )

                    # Retirer ponctuation finale aléatoirement
                    if random.random() < 0.5:
                        alt_sentence = alt_sentence.rstrip(".!?")

                    tokens = self.split_sentence(alt_sentence)
                    ner_tags = [0] * len(tokens)  # Initialisation des tags NER

                    # Ajout des tags NER pour les villes
                    for idx, token in enumerate(tokens):
                        if token in departure_city.split():
                            ner_tags[idx] = 1  # DEP
                        elif token in arrival_city.split():
                            ner_tags[idx] = 2  # ARR

                    spacy_tags = []
                    for token in tokens:
                        if token in departure_city:
                            spacy_tags.append({"start": alt_sentence.find(departure_city),
                                               "end": alt_sentence.find(departure_city) + len(departure_city),
                                               "label": "DEP"})
                        if token in arrival_city:
                            spacy_tags.append({"start": alt_sentence.find(arrival_city),
                                               "end": alt_sentence.find(arrival_city) + len(arrival_city),
                                               "label": "ARR"})

                    data.append({
                        "text": alt_sentence,
                        "tokens": str(tokens),
                        "ner_tags": str(ner_tags),
                        "spacy_ner_tags": spacy_tags,
                    })
                    pbar.update(1)

        return pd.DataFrame(data, columns=["text", "tokens", "ner_tags", "spacy_ner_tags"])

    def save_datasets(self, spacy_data: pd.DataFrame, path: str, num_files: int = 1) -> None:
        os.makedirs(path, exist_ok=True)
        sentences_split = np.array_split(spacy_data, num_files)
        
        with tqdm(total=num_files, desc="Saving Datasets") as pbar:
            for idx, current_data in enumerate(sentences_split, start=1):
                current_data = current_data.drop_duplicates(subset=["text"]).sample(frac=1).reset_index(drop=True)
                current_data.to_csv(os.path.join(path, f"dataset_token_classification_spacy_{idx}.csv"), index=False, sep=";")
                pbar.update(1)

    def generate(self, steps: Dict[str, str], path: str, regenerate: bool = False) -> None:
        print("Generating token classification dataset with spaCy NER tags...")

        if os.path.exists(path) and not regenerate:
            print("Folder already exists, skipping generation.")
            return

        sentences = self.correct_sentences + self.correct_sentences_with_names + self.ordered_sentences
        names = np.random.choice(self.names, 1000).tolist()
        sample_cities = random.sample(self.french_cities, 50)
        city_pairs = [(d, a) for d, a in product(sample_cities, repeat=2) if d != a]

        with ProcessPoolExecutor() as executor:
            futures = []
            futures.append(executor.submit(self.generate_spacy_ner_tags, sentences, names, city_pairs))
            spacy_data = futures[0].result()

        self.save_datasets(spacy_data, path)
        print(f"Dataset generated and saved to {path}.")

# Exemple d'utilisation
if __name__ == '__main__':
    files = {
        "validated_text_sequences_txt": "validated_text_sequences.txt",
        "validated_sentences_with_identifiers_txt": "validated_sentences_with_identifiers.txt",
        "validated_ordered_text_sequences_txt": "validated_ordered_text_sequences.txt",
        "french_cities_txt": "urban_geodata_basic_v1.0.txt",
        "french_national_names_csv": "fr_personal_identifiers_dataset_v1.0.csv",
    }

    generator = TokenClassificationGenerator(files)
    generator.generate(steps={"spacy": "step1"}, path="generated_datasets", regenerate=True)

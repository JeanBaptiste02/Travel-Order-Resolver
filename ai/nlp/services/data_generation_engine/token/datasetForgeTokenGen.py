import pandas as pd
import random
import spacy
import numpy as np
import os
from typing import List, Dict
from itertools import product
from tqdm import tqdm  # Importer tqdm pour la barre de progression
from concurrent.futures import ProcessPoolExecutor

class TokenClassificationGenerator:
    def __init__(self, files: dict):
        self.files = files
        self.nlp = spacy.load("fr_core_news_sm")

        # Chargement des données
        self.correct_sentences = self._load_sentences(files["validated_text_sequences_txt"])
        self.correct_sentences_with_names = self._load_sentences(files["validated_sentences_with_identifiers_txt"])
        self.ordered_sentences = self._load_sentences(files["validated_ordered_text_sequences_txt"])  # Chargement du fichier validé pour ordonnancement
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

    def generate_spacy_ner_tags(self, sentences: List[str], names: List[str], city_pairs: List[tuple]) -> pd.DataFrame:
        data = []

        # Générer un dataset pour chaque ligne de chaque fichier
        total_sentences = len(sentences) * len(city_pairs)
        with tqdm(total=total_sentences, desc="Generating Spacy NER tags") as pbar:  # Progress bar pour la génération des tags spaCy
            for sentence in sentences:
                for departure_city, arrival_city in city_pairs:
                    name = random.choice(names)
                    alt_sentence = sentence.format(departure=departure_city, arrival=arrival_city, name=name)

                    spacy_tags = []
                    ner_tags = []  # Initialize the ner_tags list
                    tokens = self.split_sentence(alt_sentence)  # Tokenize the sentence

                    # Add NER labels for departure and arrival cities
                    for idx, token in enumerate(tokens):
                        # Default to 0 (non-entity)
                        ner_tags.append(0)

                        # Check if token matches departure or arrival city
                        if departure_city in alt_sentence and token in departure_city.split():
                            dep_start = alt_sentence.find(departure_city)
                            dep_end = dep_start + len(departure_city)
                            if dep_start <= sum(len(t) + 1 for t in tokens[:idx]) < dep_end:
                                ner_tags[idx] = 1  # Label for departure city (DEP)

                        if arrival_city in alt_sentence and token in arrival_city.split():
                            arr_start = alt_sentence.find(arrival_city)
                            arr_end = arr_start + len(arrival_city)
                            if arr_start <= sum(len(t) + 1 for t in tokens[:idx]) < arr_end:
                                ner_tags[idx] = 2  # Label for arrival city (ARR)

                    # Collect spaCy NER tags
                    for idx, token in enumerate(tokens):
                        if departure_city in alt_sentence and token in departure_city.split():
                            dep_start = alt_sentence.find(departure_city)
                            spacy_tags.append({"start": dep_start, "end": dep_start + len(departure_city), "label": "DEP"})

                        if arrival_city in alt_sentence and token in arrival_city.split():
                            arr_start = alt_sentence.find(arrival_city)
                            spacy_tags.append({"start": arr_start, "end": arr_start + len(arrival_city), "label": "ARR"})

                    # Store the data
                    data.append({
                        "text": alt_sentence,
                        "tokens": str(tokens),  # Convert tokens list to string
                        "ner_tags": str(ner_tags),  # Convert ner_tags list to string
                        "spacy_ner_tags": spacy_tags,
                    })
                    pbar.update(1)  # Mise à jour de la barre de progression après chaque ligne traitée

        return pd.DataFrame(data, columns=["text", "tokens", "ner_tags", "spacy_ner_tags"])

    def save_datasets(self, spacy_data: pd.DataFrame, path: str, num_files: int = 1) -> None:
        os.makedirs(path, exist_ok=True)

        # Diviser les données en 'num_files' sous-ensembles
        sentences_split = np.array_split(spacy_data, num_files)
        
        # Compteur pour la progression
        total_batches = num_files
        with tqdm(total=total_batches, desc="Saving Datasets") as pbar:  # Progress bar pour l'enregistrement des datasets
            for idx in range(1, total_batches + 1):
                # Extraire un sous-ensemble de phrases unique pour chaque fichier
                current_data = sentences_split[idx - 1]

                # Enregistrer les datasets sous forme de fichiers CSV
                current_data = current_data.drop_duplicates(subset=["text"]).sample(frac=1).reset_index(drop=True)
                current_data.to_csv(os.path.join(path, f"dataset_token_classification_spacy_{idx}.csv"), index=False, sep=";")
                pbar.update(1)  # Mise à jour de la barre de progression après chaque fichier enregistré

    def generate(self, steps: Dict[str, str], path: str, regenerate: bool = False) -> None:
        print("Generating token classification dataset with spaCy NER tags...")

        if os.path.exists(path) and not regenerate:
            print("Folder already exists, skipping generation.")
            return

        # Préparer les données
        sentences = self.correct_sentences + self.correct_sentences_with_names + self.ordered_sentences
        names = np.random.choice(self.names, 1000).tolist()
        
        # Limiter le nombre de villes pour éviter trop de combinaisons
        sample_cities = random.sample(self.french_cities, 50)  # Par exemple, choisir 50 villes au hasard
        city_pairs = [(d, a) for d, a in product(sample_cities, repeat=2) if d != a]

        # Paralléliser la génération des datasets
        with ProcessPoolExecutor() as executor:
            futures = []
            futures.append(executor.submit(self.generate_spacy_ner_tags, sentences, names, city_pairs))

            spacy_data = futures[0].result()

        # Sauvegarder les datasets générés avec une barre de progression
        self.save_datasets(spacy_data, path)
        print(f"Dataset generated with a massive number of sentences and saved to {path}.")

# Exemple d'utilisation
if __name__ == '__main__':
    files = {
        "validated_text_sequences_txt": "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/validated_text_sequences/validated_text_sequences.txt",
        "validated_sentences_with_identifiers_txt": "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/validated_text_sequences/validated_sentences_with_identifiers.txt",
        "validated_ordered_text_sequences_txt": "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/validated_text_sequences/validated_ordered_text_sequences.txt",
        "french_cities_txt": "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/urban_geodata_basic_v1.0.txt",
        "french_national_names_csv": "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/fr_personal_identifiers_dataset_v1.0.csv",
    }

    # Créer l'instance du générateur et générer les datasets
    generator = TokenClassificationGenerator(files)
    generator.generate(steps={"spacy": "step1"}, path="C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/dataset/raw/generated_dataset/tokens", regenerate=True)

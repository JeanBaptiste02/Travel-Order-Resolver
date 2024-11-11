import random
import pandas as pd
import numpy as np
import os
from langdetect import detect
from tqdm import tqdm 

class TextClassificationGenerator:
    
    def __init__(self):
        self.load_files()

    def load_files(self):
        self.departures = self.load_departures('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/sentences_samples_dataset.csv')
        self.arrivals = self.departures.copy()
        self.random_sentences = self.load_random_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/stochastic_sentence_collection.csv')
        self.correct_sentences = self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/validated_text_sequences/validated_text_sequences.txt')
        self.wrong_sentences = {
            "only_departure_fr": self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences/missing_tags/departure_statements_without_arrivals.txt'),
            "only_arrival_fr": self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences/missing_tags/arrival_statements_without_departures.txt'),
        }
        self.names = self.load_names('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/urban_geodata_basic_v1.0.txt')
        self.error_phrases = self.load_error_phrases('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences/anomalous_text_sequences.txt')
        

    def load_sentences(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]

    def load_departures(self, filepath):
        df = pd.read_csv(filepath, sep=';', header=None, dtype={0: str})
        return df[0].tolist()

    def load_random_sentences(self, filepath):
        df = pd.read_csv(filepath, sep=';', header=None, dtype={0: str})
        return df[0].tolist()

    def load_names(self, filepath):
        df = pd.read_csv(filepath)
        return df['name'].tolist()

    def load_error_phrases(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]

    def create_object_text_label(self, sentence, departure, arrival, prefix, name, correct, not_french, not_trip, unknown):
        if "{dup_departure}" in sentence:
            sentence = sentence.replace("{dup_departure}", "{arrival}")
            arrival = departure
        elif "{dup_arrival}" in sentence:
            sentence = sentence.replace("{dup_arrival}", "{departure}")
            departure = arrival

        option = self.get_random_option(departure, arrival, prefix)

        departure_prefix = f"{prefix}{departure}"
        arrival_prefix = f"{prefix}{arrival}"

        f_dict = {
            "departure": departure_prefix if option != 1 else departure,
            "arrival": arrival_prefix if option != 0 else arrival,
            "name": name
        }

        sentence = sentence.format(**f_dict)

        return {
            "text": sentence,
            "CORRECT": correct,
            "NOT_FRENCH": not_french,
            "NOT_TRIP": not_trip,
            "UNKNOWN": unknown
        }

    def get_random_option(self, departure, arrival, prefix):
        if not arrival:
            return 0
        elif not departure:
            return 1
        else:
            return np.random.randint(0, 3)

    def fill_sentences_templates(self, departure, arrival):
        correct_sentences = []
        wrong_sentences = []

        correct_sentences.extend([ 
            self.create_object_text_label(sentence, departure, arrival, "", "", 1, 0, 0, 0)
            for sentence in self.correct_sentences
        ])

        random_names = np.random.choice(self.names, len(self.correct_sentences))
        correct_sentences.extend([
            self.create_object_text_label(sentence, departure, arrival, "", random_names[i], 1, 0, 0, 0)
            for i, sentence in enumerate(self.correct_sentences)
        ])

        wrong_sentences.extend([ 
            self.create_object_text_label(sentence, departure, "", "", "", 0, 0, 1, 0)
            for sentence in self.wrong_sentences["only_departure_fr"]
        ])

        wrong_sentences.extend([ 
            self.create_object_text_label(sentence, "", arrival, "", "", 0, 0, 1, 0)
            for sentence in self.wrong_sentences["only_arrival_fr"]
        ])

        return correct_sentences + wrong_sentences

    def generate_unknown_sentences(self, number):
        sentences = []
        for _ in range(int(number / 2)):
            sentences.append(random.choice(self.error_phrases))

        return [{"text": sentence, "CORRECT": 0, "NOT_FRENCH": 0, "NOT_TRIP": 0, "UNKNOWN": 1} for sentence in sentences]

    def detect_language(self, sentence):
        try:
            language = detect(sentence)
            return language != 'fr'
        except:
            return True 

    def get_batch_sentences(self, departure, arrival):
        data = []
        for _ in range(1):
            data.extend(self.fill_sentences_templates(departure, arrival))
        return data

    def generate(self, regenerate=False):
        path = "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/dataset/raw/generated_dataset/"

        if os.path.exists(path) and not regenerate:
            print("Folder already exists, skipping generation.")
            return

        os.makedirs(path, exist_ok=True)

        dataset = []
        arrivals = self.arrivals.copy()

        for i, departure in enumerate(tqdm(self.departures, desc="Generating dataset")):
            arrival = np.random.choice(arrivals)
            arrivals.remove(arrival)
            dataset.extend(self.get_batch_sentences(departure, arrival))

        df = pd.DataFrame(dataset)
        print(f"Generated {len(df)} sentences.")
        df = df.drop_duplicates(subset=["text"])

        random_sentences = random.sample(self.random_sentences, len(df) // 2)
        unknown_sentences = self.generate_unknown_sentences(len(df))

        df['NOT_FRENCH'] = df['text'].apply(lambda x: 1 if self.detect_language(x) else 0)

        df = pd.concat([df, pd.DataFrame(random_sentences), pd.DataFrame(unknown_sentences)])
        df = df.drop_duplicates(subset=["text"])
        df = df.sample(frac=1).reset_index(drop=True)

        number_files = 4
        for id, df_i in enumerate(np.array_split(df, number_files)):
            df_i.to_csv(f"{path}text{id + 1}.csv", index=False, sep=";")
            print(f"File {id + 1} saved.")
        print(f"Dataset generated with {len(df)} sentences.")


if __name__ == "__main__":
    token_classification_generator = TextClassificationGenerator()
    token_classification_generator.generate(True)

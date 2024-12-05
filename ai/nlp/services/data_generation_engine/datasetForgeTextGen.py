import os
import random
import pandas as pd
from tqdm import tqdm


class TextClassificationGenerator:
    def __init__(self):
        print("Initializing...")
        self.departures = self.load_places('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/urban_geodata_basic_v1.0.txt')
        self.arrivals = self.departures.copy()

        self.correct_sentences_fr = self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/validated_text_sequences/validated_text_sequences.txt')
        self.correct_sentences_fr += self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/validated_text_sequences/validated_text_sequences_en.txt')

        self.wrong_sentences_fr = {
            "only_departure": self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences/missing_tags/departure_statements_without_arrivals.txt'),
            "only_arrival": self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences/missing_tags/arrival_statements_without_departures.txt')
        }

        self.correct_sentences_en = self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/validated_text_sequences/validated_text_sequences_en.txt')
        self.wrong_sentences_en = {
            "only_departure": self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences/missing_tags/departure_statements_without_arrivals_en.txt'),
            "only_arrival": self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences/missing_tags/arrival_statements_without_departures_en.txt')
        }

        print(f"Français - Phrases correctes chargées: {len(self.correct_sentences_fr)}")
        print(f"Anglais - Phrases correctes chargées: {len(self.correct_sentences_en)}")

        self.names = self.load_names('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/fr_personal_identifiers_dataset_v1.0.csv')

    @staticmethod
    def load_sentences(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                sentences = [line.strip() for line in file.readlines()]
                if not sentences:
                    print(f"Aucune phrase trouvée dans le fichier: {filepath}")
                return sentences
        except Exception as e:
            print(f"Error loading sentences from {filepath}: {e}")
            return []

    @staticmethod
    def load_places(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file.readlines()]
        except Exception as e:
            print(f"Error loading places from {filepath}: {e}")
            return []

    @staticmethod
    def load_names(filepath):
        try:
            df = pd.read_csv(filepath)
            return df['name'].dropna().tolist()
        except Exception as e:
            print(f"Error loading names from {filepath}: {e}")
            return []

    def create_object_text_label(self, sentence, departure, arrival, name, language, correct, not_french, not_trip, unknown):
        try:
            f_dict = {"departure": departure, "arrival": arrival, "name": name}
            formatted_sentence = sentence.format(**f_dict)
            return {
                "sentence": formatted_sentence,
                "is_correct": correct,
                "is_not_french": not_french,
                "is_not_trip": not_trip,
                "is_unknown": unknown
            }
        except KeyError as e:
            print(f"KeyError: Missing key '{e}' in sentence '{sentence}'")
            return None

    def shuffle_places(self):
        random.shuffle(self.departures)
        random.shuffle(self.arrivals)

    def generate_dataset(self, output_path, num_samples=1000):
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)

        dataset = []
        max_sentences_per_combination = 10
        chunk_size = 10000
        dfs = []

        for _ in tqdm(range(num_samples), desc="Generating dataset"):
            self.shuffle_places()

            for departure, arrival in zip(self.departures, self.arrivals):
                name = random.choice(self.names) if self.names else "Unknown"

                correct_fr_sentences = random.sample(self.correct_sentences_fr, min(len(self.correct_sentences_fr), max_sentences_per_combination))
                for sentence in correct_fr_sentences:
                    dataset.append(self.create_object_text_label(sentence, departure, arrival, name, "fr", 1, 0, 0, 0))

                for key, wrong_sentences in self.wrong_sentences_fr.items():
                    incorrect_sentences = random.sample(wrong_sentences, min(len(wrong_sentences), max_sentences_per_combination))
                    for sentence in incorrect_sentences:
                        dataset.append(self.create_object_text_label(sentence, departure, arrival, name, "fr", 0, 0, 1 if key == "only_departure" else 0, 0))

                correct_en_sentences = random.sample(self.correct_sentences_en, min(len(self.correct_sentences_en), max_sentences_per_combination))
                for sentence in correct_en_sentences:
                    dataset.append(self.create_object_text_label(sentence, departure, arrival, name, "eng", 1, 0, 0, 0))

                for key, wrong_sentences in self.wrong_sentences_en.items():
                    incorrect_sentences = random.sample(wrong_sentences, min(len(wrong_sentences), max_sentences_per_combination))
                    for sentence in incorrect_sentences:
                        dataset.append(self.create_object_text_label(sentence, departure, arrival, name, "eng", 0, 1, 0, 0))

            if len(dataset) >= chunk_size:
                chunk_df = pd.DataFrame(filter(None, dataset)).drop_duplicates(subset=["sentence"])
                dfs.append(chunk_df)
                dataset = [] 

        if dataset:
            chunk_df = pd.DataFrame(filter(None, dataset)).drop_duplicates(subset=["sentence"])
            dfs.append(chunk_df)

        # Fusionner tous les DataFrames
        final_df = pd.concat(dfs, ignore_index=True)
        output_file = os.path.join(output_path, "text.csv")
        final_df.to_csv(output_file, sep=';', index=False)
        print(f"Dataset generated and saved to {output_file}.")
        print(f"Total sentences: {len(final_df)}")


if __name__ == "__main__":
    generator = TextClassificationGenerator()
    output_path = "C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/dataset/text"
    generator.generate_dataset(output_path, num_samples=1000)
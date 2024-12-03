import os
import random
import pandas as pd
from tqdm import tqdm


class TextClassificationGenerator:
    def __init__(self):
        print("Initializing...")
        # Charger les données depuis les fichiers
        self.departures = self.load_places('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/urban_geodata_basic_v1.0.txt')
        self.arrivals = self.departures.copy()
        
        # Chargement des phrases correctes et incorrectes (Français)
        self.correct_sentences_fr = self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/validated_text_sequences/validated_text_sequences.txt')
        self.correct_sentences_fr += self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/validated_text_sequences/validated_text_sequences_en.txt')
        
        self.wrong_sentences_fr = {
            "only_departure": self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences/missing_tags/departure_statements_without_arrivals.txt'),
            "only_arrival": self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences/missing_tags/arrival_statements_without_departures.txt')
        }
        
        # Chargement des phrases correctes et incorrectes (Anglais)
        self.correct_sentences_en = self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/validated_text_sequences/validated_text_sequences_en.txt')
        self.wrong_sentences_en = {
            "only_departure": self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences_en/departure_statements_without_arrivals_en.txt'),
            "only_arrival": self.load_sentences('C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/utils/supporting_datas/sentences/erroneous_text_sequences_en/arrival_statements_without_departures_en.txt')
        }

        # Vérification des phrases chargées (Français et Anglais)
        print(f"Français - Phrases correctes chargées: {len(self.correct_sentences_fr)}")
        print(f"Anglais - Phrases correctes chargées: {len(self.correct_sentences_en)}")
        
        # Chargement des noms
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
            sentence = sentence.format(**f_dict)
            return {
                "text": sentence,
                "Language": language,
                "CORRECT": correct,
                "NOT_FRENCH": not_french,
                "NOT_TRIP": not_trip,
                "UNKNOWN": unknown
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
        for _ in tqdm(range(num_samples), desc="Generating dataset"):
            self.shuffle_places()  # Mélanger les villes aléatoirement

            for departure, arrival in zip(self.departures, self.arrivals):
                name = random.choice(self.names) if self.names else "Unknown"

                # Générer des phrases correctes et incorrectes en français
                for sentence in self.correct_sentences_fr:
                    dataset.append(self.create_object_text_label(sentence, departure, arrival, name, "fr", 1, 0, 0, 0))
                for key, wrong_sentences in self.wrong_sentences_fr.items():
                    for sentence in wrong_sentences:
                        dataset.append(self.create_object_text_label(sentence, departure, arrival, name, "fr", 0, 0, 1 if key == "only_departure" else 0, 0))

                # Générer des phrases correctes et incorrectes en anglais
                for sentence in self.correct_sentences_en:
                    dataset.append(self.create_object_text_label(sentence, departure, arrival, name, "eng", 1, 0, 0, 0))
                for key, wrong_sentences in self.wrong_sentences_en.items():
                    for sentence in wrong_sentences:
                        dataset.append(self.create_object_text_label(sentence, departure, arrival, name, "eng", 0, 0, 1 if key == "only_departure" else 0, 0))

        # Convertir en DataFrame et sauvegarder
        df = pd.DataFrame(filter(None, dataset)).drop_duplicates(subset=["text"])
        output_file = os.path.join(output_path, "generated_dataset.csv")
        df.to_csv(output_file, sep=';', index=False)
        print(f"Dataset generated and saved to {output_file}.")
        print(f"Total sentences: {len(df)} (French: {len(df[df['Language'] == 'fr'])}, English: {len(df[df['Language'] == 'eng'])})")


if __name__ == "__main__":
    generator = TextClassificationGenerator()
    generator.generate_dataset("output_texts", num_samples=1000)

import json
import pandas as pd # type: ignore
import random
from tqdm import tqdm # type: ignore

# on charge la liste des villes
print("Chargement de la liste des villes...")
with open('../utils/extra_datas/urban_geodata_basic_v1.0.txt', 'r', encoding='utf-8') as f:
    villes = [line.strip() for line in f.readlines() if line.strip()]
print(f"{len(villes)} villes chargées.\n")

# on charge les phrases
print("Chargement des phrases...")
with open('../utils/extra_datas/phrases.txt', 'r', encoding='utf-8') as f:
    phrases = [line.strip() for line in f.readlines() if line.strip()]
print(f"{len(phrases)} phrases chargées.\n")

# on verifie les phrases
print("Vérification des phrases...")
for idx, phrase in enumerate(phrases):
    try:
        phrase.format('ville1', 'ville2')
    except IndexError as e:
        print(f"Erreur dans la phrase {idx+1} : {phrase} -> {e}")
print("Vérification des phrases terminée.\n")

# liste pour stocker les annotations
annotations = []

print("Génération des combinaisons de phrases...\n")
total_combinations = (len(villes) * (len(villes) - 1))
progress_bar = tqdm(total=total_combinations, desc="Progression", ncols=100)

for i in range(len(villes)):
    for j in range(len(villes)):
        if i != j:  # on verifie si le depart et la destination ne sont pas les memes
            departure = villes[i]
            destination = villes[j]
            phrase = random.choice(phrases).format(departure, destination)

            # positions des entités
            entity_departure = {
                "start": phrase.find(departure),
                "end": phrase.find(departure) + len(departure),
                "label": "DEPARTURE"
            }

            entity_destination = {
                "start": phrase.find(destination),
                "end": phrase.find(destination) + len(destination),
                "label": "DESTINATION"
            }

            # ajout de l'annotation au format json
            annotations.append({
                "sentence": phrase,
                "entities": [entity_departure, entity_destination]
            })

            progress_bar.update(1)

progress_bar.close()

# structure finale au format json
dataset = {
    "classes": ["DEPARTURE", "DESTINATION"],
    "annotations": annotations
}

# on sauvegarde en fichier json
print("\nSauvegarde du dataset en format JSON...")
with open('../dataset/raw/initial_training_data.json', 'w', encoding='utf-8') as f:
    json.dump(dataset, f, ensure_ascii=False, indent=4)
print("Sauvegarde terminée.\n")

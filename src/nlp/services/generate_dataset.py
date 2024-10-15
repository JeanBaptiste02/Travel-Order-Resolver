import pandas as pd  # type: ignore
import random
from tqdm import tqdm # type: ignore

print("Chargement de la liste des villes...")
with open('../utils/extra_datas/urban_geodata_basic_v1.0.txt', 'r', encoding='utf-8') as f:
    villes = [line.strip() for line in f.readlines() if line.strip()]
print(f"{len(villes)} villes chargées.\n")

print("Chargement des phrases...")
with open('../utils/extra_datas/phrases.txt', 'r', encoding='utf-8') as f:
    phrases = [line.strip() for line in f.readlines() if line.strip()]
print(f"{len(phrases)} phrases chargées.\n")

print("Vérification des phrases...")
for idx, phrase in enumerate(phrases):
    try:
        phrase.format('ville1', 'ville2')
    except IndexError as e:
        print(f"Erreur dans la phrase {idx+1} : {phrase} -> {e}")
print("Vérification des phrases terminée.\n")

# Liste pour stocker les données
data = []

print("Génération des combinaisons de phrases...\n")
total_combinations = (len(villes) * (len(villes) - 1))
progress_bar = tqdm(total=total_combinations, desc="Progression", ncols=100)

for i in range(len(villes)):
    for j in range(len(villes)):
        if i != j:  # verifie si le départ et la destination ne sont pas les memes
            departure = villes[i]
            destination = villes[j]
            phrase = random.choice(phrases).format(departure, destination)

            # positions de départ et d'arrivée
            entity_start = phrase.find(departure)
            entity_end = entity_start + len(departure)
            data.append([phrase, entity_start, entity_end, "DEPARTURE"])

            entity_start = phrase.find(destination)
            entity_end = entity_start + len(destination)
            data.append([phrase, entity_start, entity_end, "DESTINATION"])

            progress_bar.update(1)

progress_bar.close()

print("\nCréation du DataFrame et sauvegarde en CSV...")
df = pd.DataFrame(data, columns=['sentence', 'entity_start', 'entity_end', 'entity_type'])
df.to_csv('../dataset/raw/initial_training_data.csv', index=False, encoding='utf-8')
print("Sauvegarde terminée.\n")
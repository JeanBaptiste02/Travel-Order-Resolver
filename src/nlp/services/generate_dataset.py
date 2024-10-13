import pandas as pd  # type: ignore
import random
from tqdm import tqdm # type: ignore

# Charger la liste des villes
print("Chargement de la liste des villes...")
with open('../utils/extra_datas/urban_geodata_masterlist_v1.0.txt', 'r', encoding='utf-8') as f:
    villes = [line.strip() for line in f.readlines() if line.strip()]
print(f"{len(villes)} villes chargées.\n")

# Charger la liste des phrases depuis un fichier externe
print("Chargement des phrases...")
with open('../utils/extra_datas/phrases.txt', 'r', encoding='utf-8') as f:
    phrases = [line.strip() for line in f.readlines() if line.strip()]
print(f"{len(phrases)} phrases chargées.\n")

# Vérification des phrases pour détecter d'éventuelles erreurs de formatage
print("Vérification des phrases...")
for idx, phrase in enumerate(phrases):
    try:
        phrase.format('ville1', 'ville2')
    except IndexError as e:
        print(f"Erreur dans la phrase {idx+1} : {phrase} -> {e}")
print("Vérification des phrases terminée.\n")

# Liste pour stocker les données
data = []

# Générer toutes les combinaisons de phrases pour chaque paire de villes
print("Génération des combinaisons de phrases...\n")
total_combinations = (len(villes) * (len(villes) - 1))
progress_bar = tqdm(total=total_combinations, desc="Progression", ncols=100)

for i in range(len(villes)):
    for j in range(len(villes)):
        if i != j:  # S'assurer que le départ et la destination ne sont pas identiques
            departure = villes[i]
            destination = villes[j]
            phrase = random.choice(phrases).format(departure, destination)

            # Déterminer les positions de départ et d'arrivée
            entity_start = phrase.find(departure)
            entity_end = entity_start + len(departure)
            data.append([phrase, entity_start, entity_end, "DEPARTURE"])

            entity_start = phrase.find(destination)
            entity_end = entity_start + len(destination)
            data.append([phrase, entity_start, entity_end, "DESTINATION"])

            # Mise à jour de la barre de progression
            progress_bar.update(1)

# Fermeture de la barre de progression
progress_bar.close()

# Créer un DataFrame et sauvegarder en CSV
print("\nCréation du DataFrame et sauvegarde en CSV...")
df = pd.DataFrame(data, columns=['sentence', 'entity_start', 'entity_end', 'entity_type'])
df.to_csv('../dataset/raw/initial_training_data.csv', index=False, encoding='utf-8')
print("Sauvegarde terminée.\n")

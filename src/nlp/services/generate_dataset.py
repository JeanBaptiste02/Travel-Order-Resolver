import pandas as pd # type: ignore
import random
import csv 
from tqdm import tqdm  # type: ignore 

# on charge la liste des villes
print("Chargement de la liste des villes...")
with open('../utils/extra_datas/urban_geodata_basic_v1.0.txt', 'r', encoding='utf-8') as f:
    villes = [line.strip().title() for line in f.readlines() if line.strip()]  # majuscule les noms des villes
print(f"{len(villes)} villes chargées\n")

# Charger les phrases
print("Chargement des phrases...")
with open('../utils/extra_datas/phrases.txt', 'r', encoding='utf-8') as f:
    phrases = [line.strip() for line in f.readlines() if line.strip()]
print(f"{len(phrases)} phrases chargées\n")

# Liste pour stocker les résultats
results = []

print("Génération des phrases...\n")

# on parcours chaque phrase avec tqdm pour la barre de progression
for phrase in tqdm(phrases, desc="En cours", ncols=100):
    # on check combien de fois {} apparait dans chaque phrase
    placeholders = phrase.count('{}')

    # si dans la phrase y'a {} et moins de 2 villes, on continue
    if placeholders == 0:
        results.append((phrase.capitalize(), "[]"))  # majuscule la phrase
        continue

    # on chousi des villes au hasard en fonction du nombre de {} dans la phrase
    selected_villes = random.sample(villes, min(placeholders, len(villes)))

    # on remplace les {} par les noms des villes
    formatted_phrase = phrase.format(*selected_villes)

    # on màj la 1ere lettre de la phrase formatee en majuscule
    formatted_phrase = formatted_phrase[0].upper() + formatted_phrase[1:]

    # on calcul les positions des entites
    entities = []
    
    # on determine le nb de villes pour les labels
    departure_found = False
    for ville in selected_villes:
        start = formatted_phrase.find(ville)
        end = start + len(ville)
        
        # on determine le label en fonction de la position
        if not departure_found:
            label = "DEPARTURE"
            departure_found = True
        else:
            # Si c'est la dernière ville, elle est la destination
            if ville == selected_villes[-1]:
                label = "DESTINATION"
            else:
                label = "ESCALE"  # sinon, c'est une escale
                
        entities.append(f"[{start}, {end}, '{label}']")

    # on cree l'entree pour le fichier CSV
    entities_str = f"[{', '.join(entities)}]"
    results.append((formatted_phrase, entities_str))

# on cree un DataFrame et l'enregistrer dans un fichier CSV
df = pd.DataFrame(results, columns=["Phrase", "Entities"])
df.to_csv('../dataset/raw/initial_training_data.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)

print("Fichier CSV généré avec succès\n")
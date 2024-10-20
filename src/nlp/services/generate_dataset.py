import pandas as pd  # type: ignore
import random
import csv
from tqdm import tqdm  # type: ignore
import re

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

# Mots-clés pour déterminer le départ et l'arrivée
departure_keywords = [
    'partir de', 'quitter', 'départ de', 'provenant de', 'en partant de',
    'venant de', 's’échapper de', 'sortir de', 'démarrer de', 'en provenance de',
    'départ à partir de', 'en route depuis', 'originaire de', 'en laissant',
    'avant de partir de', 'départ depuis', 'à partir de', 'de', 'en sortant de',
    'au départ de', 'sans retour de', 'en voyage depuis', 'au sortir de',
    'depuis', 'partir en', 'en fuite de', 'en revenant de', 'migrant de', 'fuyant'
]

destination_keywords = [
    'aller à', 'destination', 'arriver à', 'se rendre à', 'vers',
    'en direction de', 'en route vers', 'à destination de', 'en route pour',
    'atteindre', 'visiter', 'se déplacer vers', 'se diriger vers', 'à',
    'dans', 'destination vers', 'à l’adresse de', 'sur le chemin de',
    'en arrivant à', 'en allant à', 'à l’intention de', 'pour',
    'auprès de', 'à destination', 'en approche de', 'en visite à',
    'rendez-vous à', 'dans la direction de', 'en passant par', 'en direction de'
]

# on parcours chaque phrase avec tqdm pour la barre de progression
for phrase in tqdm(phrases, desc="En cours", ncols=100):
    # on check combien de fois {} apparait dans chaque phrase
    placeholders = phrase.count('{}')

    # si dans la phrase y'a {} et moins de 2 villes, on continue
    if placeholders == 0:
        results.append((phrase.capitalize(), "[]"))  # majuscule la phrase
        continue

    # on choisit des villes au hasard en fonction du nombre de {} dans la phrase
    selected_villes = random.sample(villes, min(placeholders, len(villes)))

    # on remplace les {} par les noms des villes
    formatted_phrase = phrase.format(*selected_villes)

    # on màj la 1ère lettre de la phrase formattée en majuscule
    formatted_phrase = formatted_phrase[0].upper() + formatted_phrase[1:]

    # on calcule les positions des entités
    entities = []

    # Analyse de la phrase pour trouver les départs et destinations
    departure_found = False
    destination_found = False
    for ville in selected_villes:
        start = formatted_phrase.find(ville)
        end = start + len(ville)

        # Déterminer le contexte de la ville pour étiqueter correctement
        if any(keyword in formatted_phrase[:start] for keyword in departure_keywords):
            label = "DEPARTURE"
            departure_found = True
        elif any(keyword in formatted_phrase[end:] for keyword in destination_keywords):
            label = "DESTINATION"
            destination_found = True
        else:
            label = "ESCALE"

        entities.append(f"[{start}, {end}, '{label}']")

    # Correction des étiquettes
    if departure_found and not destination_found:
        # Si on a trouvé un départ mais pas de destination, marquer la dernière ville comme destination
        entities[-1] = entities[-1].replace("ESCALE", "DESTINATION")

    # on crée l'entrée pour le fichier CSV
    entities_str = f"[{', '.join(entities)}]"
    results.append((formatted_phrase, entities_str))

# on crée un DataFrame et l'enregistre dans un fichier CSV
df = pd.DataFrame(results, columns=["Phrase", "Entities"])
df.to_csv('../dataset/raw/initial_training_data.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)

print("Fichier CSV généré avec succès\n")
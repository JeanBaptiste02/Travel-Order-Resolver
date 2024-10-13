import pandas as pd # type: ignore
import random

# Charger la liste des villes
with open('../utils/extra_datas/urban_geodata_masterlist_v1.0.txt', 'r', encoding='utf-8') as f:
    villes = [line.strip() for line in f.readlines() if line.strip()]

# Définir les modèles de phrases

phrases = [
    "Je voudrais aller de {} à {}.",
    "Comment me rendre à {} depuis {} ?",
    "Y a-t-il des trains de {} à {} ?",
    "Je souhaite me rendre à {} en partant de {}.",
    "Je quitte {} pour aller à {}.",
    "Peux-tu me dire le meilleur moyen d'aller de {} à {} ?",
    "Combien de temps faut-il pour aller de {} à {} ?",
    "Est-ce que je peux prendre un bus de {} à {} ?",
    "Quelles sont les options de transport entre {} et {} ?",
    "Quel est le prix d'un billet de {} à {} ?",
    "Avez-vous des recommandations pour voyager de {} à {} ?",
    "Je prévois un voyage de {} à {}. Avez-vous des conseils ?",
    "Est-ce que ça vaut le coup de visiter {} après être allé à {} ?",
    "À quelle heure part le dernier train de {} à {} ?",
    "Quels sites touristiques visiter en allant de {} à {} ?",
    "Y a-t-il des offres spéciales pour voyager entre {} et {} ?",
    "Je dois réserver un vol de {} à {}. Quel est le meilleur moment ?",
    "Comment faire pour rejoindre {} depuis {} ?",
    "Est-il facile de trouver un taxi de {} à {} ?",
    "Peut-on faire du covoiturage de {} à {} ?",
    "Quelles sont les distances entre {} et {} ?",
    "Je vais faire une escale à {} avant d'arriver à {}.",
    "Est-ce que tu sais si le train est direct de {} à {} ?",
    "Comment est la route de {} à {} ?",
    "J'aimerais planifier un itinéraire de {} à {}.",
    "As-tu déjà visité {} en partant de {} ?",
    "Y a-t-il des restrictions de voyage entre {} et {} ?",
    "Quel est le meilleur moment de l'année pour visiter {} depuis {} ?",
    "Peux-tu me donner des astuces pour voyager de {} à {} ?",
    "Quelles sont les meilleures compagnies pour aller de {} à {} ?",
    "Je cherche un hébergement à {} pour mon voyage depuis {}.",
    "Les vols de {} à {} sont-ils fréquents ?",
    "Quelle est la meilleure période pour aller de {} à {} ?",
    "Est-ce que le ferry est une option pour aller de {} à {} ?",
    "J'ai besoin d'informations sur les transports publics entre {} et {}.",
    "Est-ce que le train est en retard de {} à {} ?",
    "Peut-on louer une voiture à {} pour aller à {} ?",
    "Y a-t-il des visites guidées disponibles à {} ?",
    "Quel est le meilleur moyen de transport pour visiter {} ?",
    "Y a-t-il des réductions pour les étudiants sur les trajets de {} à {} ?",
    "Quels sont les moyens de transport les plus rapides entre {} et {} ?",
    "Est-il préférable de prendre un vol ou le train de {} à {} ?",
    "Peut-on se déplacer facilement à {} sans voiture ?",
    "Est-ce que je peux utiliser mon pass de transport à {} ?",
    "Y a-t-il des compagnies de bus recommandées pour aller de {} à {} ?",
    "Quel est le temps de trajet habituel en voiture de {} à {} ?",
    "Est-ce que des bus de nuit circulent entre {} et {} ?",
    "Quel est le meilleur moment pour éviter les foules entre {} et {} ?",
    "Y a-t-il des transports adaptés aux personnes à mobilité réduite entre {} et {} ?",
    "Peux-tu me recommander un trajet pittoresque de {} à {} ?",
    "Est-ce que les trains sont souvent en retard entre {} et {} ?",
    "Y a-t-il des cartes de transport à prix réduit pour les voyageurs fréquents entre {} et {} ?",
    "Quels sont les moyens de transport les plus écologiques pour aller de {} à {} ?",
    "Comment se rendre à l'aéroport de {} depuis {} ?",
    "Peut-on faire des excursions d'une journée à partir de {} vers {} ?",
    "Est-il possible de voyager de {} à {} sans passer par {} ?",
    "Peux-tu me donner des conseils pour éviter le trafic entre {} et {} ?",
    "Y a-t-il des applications utiles pour planifier mon voyage entre {} et {} ?"
]

# Liste pour stocker les données
data = []

# Générer toutes les combinaisons de phrases pour chaque paire de villes
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

# Créer un DataFrame et sauvegarder en CSV
df = pd.DataFrame(data, columns=['sentence', 'entity_start', 'entity_end', 'entity_type'])
df.to_csv('../dataset/raw/initial_training_data.csv', index=False, encoding='utf-8')

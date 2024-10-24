import spacy
import difflib
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------------------------------------
# Fonction pour extraire "DEPARTURE" et "DESTINATION" du texte avec les deux modèles
# -------------------------------------------------------------------------------
def extract_locations(text, lang_model, itinerary_model, verbose=False):
    # Analyse du texte avec les deux modèles
    doc_lang = lang_model(text)
    doc_itinerary = itinerary_model(text)

    if verbose:
        print("Entités détectées avec le modèle linguistique :")
        spacy.displacy.render(doc_lang, style='ent', jupyter=True)
        print("Entités détectées avec le modèle itinéraire :")
        spacy.displacy.render(doc_itinerary, style='ent', jupyter=True)

    departure, destination = None, None

    # Vérification si le texte est bien en français
    if doc_lang._.language['language'] != 'fr':
        return "NON_FRANÇAIS"

    # Parcourir les entités et chercher "DEPARTURE" et "DESTINATION"
    for ent in doc_itinerary.ents:
        if ent.label_ == "DEPARTURE":
            departure = ent.text
        elif ent.label_ == "DESTINATION":
            destination = ent.text

    # Si l'une des deux entités n'est pas trouvée
    if not departure or not destination:
        return "PAS_DE_TRAJET"
    return {"départ": departure, "destination": destination}

# -------------------------------------------------------------------------------
# Fonction pour traiter un fichier et extraire les informations de départ et destination
# -------------------------------------------------------------------------------
def process_file(filepath, lang_model, itinerary_model, verbose=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        lignes = f.readlines()

    resultat_trajets = []
    for ligne in lignes:
        # Séparer l'ID et le texte (si applicable)
        elements = ligne.strip().split(',', 1)
        identifiant = elements[0] if elements[0].isdigit() else 0
        texte = elements[1] if len(elements) > 1 else elements[0]

        # Extraction des trajets
        trajets = extract_locations(texte, lang_model, itinerary_model, verbose)
        if trajets == "NON_FRANÇAIS" or trajets == "PAS_DE_TRAJET":
            resultat_trajets.append(f"{identifiant},{trajets}")
        else:
            resultat_trajets.append(f"{identifiant},{trajets['départ']},{trajets['destination']}")

    if verbose:
        print("Trajets extraits :")
        print(resultat_trajets)

    return resultat_trajets

# -------------------------------------------------------------------------------
# Comparaison des résultats extraits avec les résultats attendus
# -------------------------------------------------------------------------------
def comparer_trajets(extraits, attendus):
    erreurs = 0
    for i in range(len(extraits)):
        if extraits[i] != attendus[i]:
            erreurs += 1
            print(f"Erreur ligne {i+1} :")
            print(f"Extrait : {extraits[i]}")
            print(f"Attendu : {attendus[i]}")

    # Calcul du taux de réussite
    taux_succès = round((len(extraits) - erreurs) / len(extraits) * 100, 2)
    print(f"\nTaux de réussite : {taux_succès}% ({erreurs} erreurs sur {len(extraits)} lignes).\n")

    # Affichage d'un graphique circulaire pour visualiser le taux d'erreur
    labels = 'Réussites', 'Erreurs'
    tailles = [len(extraits) - erreurs, erreurs]
    couleurs = ['green', 'red']
    plt.pie(tailles, labels=labels, colors=couleurs, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')
    plt.show()

    # Comparaison des résultats avec un DataFrame pour une visualisation facile
    df = pd.DataFrame({
        'ID': [item.split(',')[0] for item in extraits],
        'Départ Attendu': [item.split(',')[1] if len(item.split(',')) > 1 else '' for item in attendus],
        'Départ Prévu': [item.split(',')[1] if len(item.split(',')) > 1 else '' for item in extraits],
        'Destination Attendue': [item.split(',')[2] if len(item.split(',')) > 2 else '' for item in attendus],
        'Destination Prévue': [item.split(',')[2] if len(item.split(',')) > 2 else '' for item in extraits],
    })

    print("\nComparaison des résultats :\n", df)

# -------------------------------------------------------------------------------
# Fonction de correction des villes en utilisant la liste de villes
# -------------------------------------------------------------------------------
def corriger_villes(trajets, liste_villes, verbose=False):
    trajets_corrigés = []
    for trajet in trajets:
        parties = trajet.upper().replace('É', 'E').replace('-', ' ').split(',')
        ville_corrigée = ','.join([difflib.get_close_matches(item, liste_villes, n=1, cutoff=0.8)[0] if difflib.get_close_matches(item, liste_villes, n=1, cutoff=0.8) else item for item in parties])
        trajets_corrigés.append(ville_corrigée)

        if verbose:
            print(f"Avant : {trajet}")
            print(f"Après correction : {ville_corrigée}")

    return trajets_corrigés

import pandas as pd

# Chemin des fichiers d'entrée et de sortie
input_file = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\dataset\text\text_intention_detector.csv"
output_file = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\dataset\text\dataset_sans_doublons_intent.csv"

try:
    # Chargement du fichier CSV avec gestion des lignes incorrectes
    data = pd.read_csv(input_file, sep=';', on_bad_lines='skip', encoding='utf-8')
    print("Le fichier a été chargé avec succès.")
    
    # Afficher les colonnes pour s'assurer qu'elles sont correctes
    print("Colonnes du fichier CSV :")
    print(data.columns)

    # Nettoyer les noms de colonnes pour supprimer les espaces et caractères invisibles
    data.columns = data.columns.str.strip()

    # Vérification des colonnes essentielles
    required_columns = {'sentence', 'is_correct', 'is_not_trip', 'is_unknown'}
    if required_columns.issubset(data.columns):
        # Suppression des doublons basés sur la colonne 'sentence'
        data_sans_doublons = data.drop_duplicates(subset=['sentence'])
        print("Doublons supprimés avec succès.")
        
        # Sauvegarde du fichier nettoyé
        data_sans_doublons.to_csv(output_file, index=False, sep=';', encoding='utf-8')
        print(f"Fichier nettoyé sauvegardé sous le nom : {output_file}")
    else:
        print("Les colonnes essentielles ne sont pas présentes dans le fichier.")
        print("Colonnes disponibles :")
        print(data.columns)

except FileNotFoundError:
    print(f"Erreur : Le fichier spécifié '{input_file}' est introuvable.")
except pd.errors.EmptyDataError:
    print("Erreur : Le fichier est vide ou contient des données invalides.")
except Exception as e:
    print(f"Une erreur inattendue s'est produite : {e}")

import pandas as pd

# Chemin des fichiers d'entrée et de sortie
input_file = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\dataset\text\text_lang_detector.csv"
output_file = r"C:\Users\vikne\Documents\Master 2\Semestre 9\Intelligence artificielle\Travel-Order-Resolver\ai\nlp\dataset\text\dataset_sans_doublons_lang.csv"

try:
    # Chargement du fichier CSV avec gestion des erreurs de lecture
    data = pd.read_csv(input_file, sep=';', on_bad_lines='skip', encoding='utf-8')  # Ajout de l'encodage UTF-8
    print("Le fichier a été chargé avec succès.")
    
    # Afficher les colonnes disponibles pour s'assurer qu'elles sont correctes
    print("Colonnes du fichier CSV :")
    print(data.columns)  # Vérifie les noms des colonnes
    
    # Nettoyage des noms de colonnes (élimination des espaces ou caractères invisibles)
    data.columns = data.columns.str.strip()

    # Vérifier si les colonnes 'sentence' et 'is_not_french' existent
    required_columns = {'sentence', 'is_not_french'}
    if required_columns.issubset(data.columns):
        # Suppression des doublons basés sur la colonne 'sentence'
        data_sans_doublons = data.drop_duplicates(subset=['sentence'])
        print("Doublons supprimés avec succès.")
        
        # Sauvegarde du fichier nettoyé
        data_sans_doublons.to_csv(output_file, index=False, sep=';', encoding='utf-8')
        print(f"Fichier nettoyé sauvegardé sous le nom : {output_file}")
    else:
        print("Les colonnes requises ne sont pas présentes dans le fichier.")
        print("Colonnes disponibles :")
        print(data.columns)

except FileNotFoundError:
    print(f"Erreur : Le fichier spécifié '{input_file}' est introuvable.")
except pd.errors.EmptyDataError:
    print("Erreur : Le fichier est vide ou contient des données invalides.")
except Exception as e:
    print(f"Une erreur inattendue s'est produite : {e}")

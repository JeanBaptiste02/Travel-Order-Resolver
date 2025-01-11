import pandas as pd

# Chargement du fichier CSV avec un séparateur ; (point-virgule)
input_file = r"C:\Users\vikne\Desktop\token.csv"
output_file = r"C:\Users\vikne\Desktop\dataset_sans_doublons.csv"

# Charger le dataset avec gestion des lignes incorrectes
try:
    data = pd.read_csv(input_file, sep=';', on_bad_lines='skip')  # Spécification du séparateur
    print("Le fichier a été chargé avec succès.")
    
    # Vérification des noms de colonnes
    print("Colonnes du fichier CSV :")
    print(data.columns)  # Afficher les noms des colonnes
    
    # Affichage des premières lignes pour vérifier la structure du fichier
    print("Aperçu des 5 premières lignes du fichier :")
    print(data.head())

    # Nettoyer les noms de colonnes pour supprimer les espaces et s'assurer qu'il n'y a pas de caractères invisibles
    data.columns = data.columns.str.strip()
    
    # Vérifier si la colonne 'text' existe
    if 'text' in data.columns:
        data_sans_doublons = data.drop_duplicates(subset=['text'])
        print("Doublons supprimés avec succès.")
    else:
        print("La colonne 'text' n'est pas présente dans le fichier.")
        print("Colonnes disponibles :")
        print(data.columns)

except Exception as e:
    print(f"Erreur lors du chargement du fichier : {e}")

# Sauvegarde du fichier nettoyé
if 'text' in data.columns:
    data_sans_doublons.to_csv(output_file, index=False)
    print(f"Fichier nettoyé sauvegardé sous le nom : {output_file}")

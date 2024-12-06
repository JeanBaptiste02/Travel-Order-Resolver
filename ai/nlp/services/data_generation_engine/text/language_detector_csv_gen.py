import pandas as pd  # type: ignore

def filter_french_sentences(input_file, output_file):
    try:
        # Charger le fichier CSV avec le bon délimiteur et gérer les lignes mal formées
        df = pd.read_csv(input_file, sep=';', on_bad_lines='skip', encoding='utf-8')
        
        # Vérifier si les colonnes nécessaires existent
        if 'sentence' not in df.columns or 'is_not_french' not in df.columns:
            raise ValueError("Les colonnes 'sentence' et/ou 'is_not_french' sont manquantes dans le fichier.")
        
        # Garder uniquement les colonnes 'sentence' et 'is_not_french'
        filtered_df = df[['sentence', 'is_not_french']]
        
        # Sauvegarder dans un nouveau fichier CSV avec des colonnes séparées par un point-virgule
        filtered_df.to_csv(output_file, sep=';', index=False, encoding='utf-8')
        print(f"Fichier traité avec succès. Résultat enregistré dans : {output_file}")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

# Exemple d'utilisation
input_csv = r"C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/dataset/text/text.csv"  # Chemin d'entrée
output_csv = r"C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/dataset/text/text_lang_detector.csv"  # Chemin de sortie

filter_french_sentences(input_csv, output_csv)

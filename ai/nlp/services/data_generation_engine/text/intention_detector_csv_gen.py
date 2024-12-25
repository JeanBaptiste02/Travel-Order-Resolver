import pandas as pd  # type: ignore
import re

def clean_and_filter_columns(input_file, output_file):
    try:
        # Charger le fichier CSV avec le bon délimiteur et gérer les lignes mal formées
        df = pd.read_csv(input_file, sep=';', on_bad_lines='skip', encoding='utf-8')
        
        # Vérifier si les colonnes nécessaires existent
        required_columns = ['sentence', 'is_correct', 'is_not_trip', 'is_unknown']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Les colonnes suivantes sont manquantes dans le fichier : {[col for col in required_columns if col not in df.columns]}")
        
        # Garder uniquement les colonnes 'sentence', 'is_correct', 'is_not_trip' et 'is_unknown'
        filtered_df = df[['sentence', 'is_correct', 'is_not_trip', 'is_unknown']]
        
        # Nettoyage des phrases
        def process_sentence(sentence):
            # Séparer la ponctuation collée aux mots
            sentence = re.sub(r'([^\w\s])', r' \1', sentence)
            sentence = re.sub(r'\s+', ' ', sentence).strip()  # Nettoyer les espaces
            
            # Remplacement de "de" par "d’" avant une voyelle
            sentence = re.sub(r'\bde (?=[aeiouAEIOUéèêÉÈÊ])', "d’", sentence)
            return sentence
        
        # Appliquer le nettoyage sur les phrases
        filtered_df['sentence'] = filtered_df['sentence'].apply(process_sentence)
        
        # Sauvegarder dans un nouveau fichier CSV avec des colonnes séparées par un point-virgule
        filtered_df.to_csv(output_file, sep=';', index=False, encoding='utf-8')
        print(f"Fichier traité avec succès. Résultat enregistré dans : {output_file}")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

# Exemple d'utilisation
input_csv = r"C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/dataset/text/text.csv"  # Chemin d'entrée
output_csv = r"C:/Users/vikne/Documents/Master 2/Semestre 9/Intelligence artificielle/Travel-Order-Resolver/ai/nlp/dataset/text/text_intention_detector.csv"  # Chemin de sortie

clean_and_filter_columns(input_csv, output_csv)

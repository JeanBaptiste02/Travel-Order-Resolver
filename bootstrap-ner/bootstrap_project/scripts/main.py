import data_loading
import data_preprocessing
import spacy_model
import camembert_model
import evaluation
import annotation

def main():
    # Chargement des données
    ner_data = data_loading.load_ner_dataset_file()
    bottins_data = data_loading.load_bottins_file()

    print("Premières lignes du dataset ner_dataset.csv :\n")
    print(ner_data.head())

    print("\n######################################################################\n")

    print("Premières lignes du dataset bottins.csv :\n")
    print(bottins_data.head())

    # Prétraitement des données
    bottins_sentences = data_preprocessing.clean_bottins_data(bottins_data)
    print(f"Sentences prétraitées : {bottins_sentences[:5]}")

    # Tokenisation des phrases
    tokenizer = camembert_model.load_tokenizer()
    sample_sentence = bottins_sentences[0]
    tokenized_sentence = data_preprocessing.tokenize_and_preserve_labels(sample_sentence, tokenizer)
    print(f"Phrase tokenisée : {tokenized_sentence}")

    # Implémentation du modèle spaCy
    spacy_model.apply_spacy_model_cleaned(bottins_sentences[:5])

    # Évaluation des résultats du modèle spaCy
    evaluation.evaluate_spacy_model()

    # Implémentation du modèle CamemBERT
    model = camembert_model.load_camemBert_model()
    inputs = camembert_model.tokenize_sentence(tokenizer, bottins_sentences[0])
    outputs = camembert_model.apply_model(model, inputs)
    print("Résultats bruts du modèle:")
    print(outputs)

    # Évaluation et comparaison des modèles
    evaluation.compare_models_spaCy_and_camembert()

    # Annotation des données
    annotation.manual_annotation()

if __name__ == "__main__":
    main()

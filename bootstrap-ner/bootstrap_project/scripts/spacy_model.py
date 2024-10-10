import spacy
import re

nlp = spacy.load("fr_core_news_sm")
print("Le modele fr_core_news_sm a ete bien charge")

def clean_annotations(sentence):
    return re.sub(r'<.*?>', '', sentence)

def apply_spacy_model_cleaned(sentences):
    for sentence in sentences:
        cleaned_sentence = clean_annotations(sentence)
        doc = nlp(cleaned_sentence)
        print(f"Phrase : {cleaned_sentence}")
        print("Entités détectées :")
        for ent in doc.ents:
            print(ent.text, ent.label_)
        print("-" * 40)

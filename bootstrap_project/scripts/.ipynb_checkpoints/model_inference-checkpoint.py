import spacy
from transformers import pipeline

def spacy_inference(text):
    nlp = spacy.load("fr_core_news_sm")
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def transformers_inference(text):
    ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
    return ner_pipeline(text)
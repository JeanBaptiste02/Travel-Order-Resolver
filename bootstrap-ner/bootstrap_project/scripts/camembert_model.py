import torch
from transformers import CamembertTokenizer, CamembertForTokenClassification

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Utilisation du dispositif: {device} \n")

def load_camemBert_model():
    print("chargement du modele CamemBERT pour la classification des tokens ...")
    model = CamembertForTokenClassification.from_pretrained("camembert-base", num_labels=2)
    model.to(device)
    print("Modele CamemBERT a ete bien charge et deplace sur le dispositif \n")
    return model

def load_tokenizer():
    print("chargement du tokenizer ...")
    tokenizer = CamembertTokenizer.from_pretrained("camembert-base")
    print("Tokenizer CamemBERT a ete bien charge \n")
    return tokenizer

def tokenize_sentence(tokenizer, sentence):
    print("application du modele sur les données annotees ...")
    inputs = tokenizer(sentence, return_tensors="pt", truncation=True).to(device)
    print("Phrase tokenisée et convertie en tenseurs.")
    print(f"Inputs: {inputs}")
    return inputs

def apply_model(model, inputs):
    print("passage des inputs à travers le modele ...")
    outputs = model(**inputs)
    print("Modèle appliqué aux inputs.")
    return outputs

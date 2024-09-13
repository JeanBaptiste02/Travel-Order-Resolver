import spacy
from spacy.training import Example

def train_model(nlp, TRAIN_DATA):
    ner = nlp.get_pipe("ner")
    ner.add_label("DEP")
    net.add_label("ARR")
    optimizer = nlp.begin_training()
    for epoch in range(10):
        losses = {}
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], drop=0.5, losses=losses)
        print(f"Epoch {epoch}: {losses}")
    return nlp
        
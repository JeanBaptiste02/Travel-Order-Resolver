import pandas as pd

def load_ner_dataset_file():
    ner_data = pd.read_csv("../../../../students_bootstrap/corpus/ner_dataset.csv", encoding='latin1', delimiter=",")
    print("Loaded ner_dataset file\n")
    return ner_data

def load_bottins_file():
    bottins_data = pd.read_csv("../../../../students_bootstrap/bottins.csv", encoding="utf-8", delimiter=",", header=None)
    bottins_data.columns = ["Text", "Source"]
    print("Loaded bottins file \n")
    return bottins_data

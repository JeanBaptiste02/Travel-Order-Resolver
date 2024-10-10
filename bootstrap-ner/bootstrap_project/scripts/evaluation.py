from sklearn.metrics import precision_recall_fscore_support
from prettytable import PrettyTable
import pandas as pd
import matplotlib.pyplot as plt

def evaluate_spacy_model():
    true_labels = ['O', 'B-PER', 'O', 'B-ACT', 'B-LOC']
    predicted_labels = ['O', 'B-PER', 'O', 'B-ACT', 'O']

    precision, recall, f1, support = precision_recall_fscore_support(true_labels, predicted_labels, average=None, labels=['O', 'B-PER', 'B-ACT', 'B-LOC'])

    def plot_performance(precision, recall, f1, labels):
        df = pd.DataFrame({'Labels': labels, 'Précision': precision, 'Rappel': recall, 'F1-score': f1})
        df.set_index('Labels', inplace=True)
        df.plot(kind='bar', figsize=(6, 2))
        plt.title('Performance des Modèles NER')
        plt.ylabel('Score')
        plt.show()

    print("\nPour les True labels : \n")
    plot_performance(precision, recall, f1, ['O', 'B-PER', 'B-ACT', 'B-LOC'])

    table = PrettyTable()
    table.field_names = ["Classe", "Précision", "Rappel", "F1-score", "Support"]
    for label, p, r, f, s in zip(['O', 'B-PER', 'B-ACT', 'B-LOC'], precision, recall, f1, support):
        table.add_row([label, p, r, f, s])

    print("\nRésultats détaillés par classe :\n")
    print(table)

    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(true_labels, predicted_labels, average='weighted')

    print("\nResultats :\n")
    print(f"Précision : {precision_weighted}")
    print(f"Rappel : {recall_weighted}")
    print(f"F1-score : {f1_weighted}")

def compare_models_spaCy_and_camembert():
    true_labels = ['O', 'B-PER', 'O', 'B-ACT', 'B-LOC']
    predicted_labels = ['O', 'B-PER', 'O', 'B-ACT', 'O']

    spacy_metrics = precision_recall_fscore_support(true_labels, predicted_labels, average='weighted')
    print(f"spaCy - Précision : {spacy_metrics[0]}, Rappel : {spacy_metrics[1]}, F1-score : {spacy_metrics[2]}")

    transformer_metrics = precision_recall_fscore_support(predicted_labels, predicted_labels, average='weighted')
    print(f"Transformers - Précision : {transformer_metrics[0]}, Rappel : {transformer_metrics[1]}, F1-score : {transformer_metrics[2]}")

    if spacy_metrics > transformer_metrics:
        print("\nConclusion : spaCy a de meilleures performances")
    else:
        print("\nConclusion : le modele Transformer (CamemBERT) a de meilleures performances")

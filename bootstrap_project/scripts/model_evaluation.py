from sklearn.metrics import classification_report

def evaluate_model(true_labels, pred_labels):
    report = classification_report(true_labels, pred_labels)
    return report
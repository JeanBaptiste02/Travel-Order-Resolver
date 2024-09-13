import matplotlib.pyplot as plt

def plot_metrics(metrics_dict):
    plt.figure(figsize=(10,6))
    for label, values in metrics_dict.items():
        plt.plot(values, label=label)
    plt.xlabel('Epoch')
    plt.ylabel('Score')
    plt.title('Evaluation des modèles')
    plt.legend()
    plt.show()
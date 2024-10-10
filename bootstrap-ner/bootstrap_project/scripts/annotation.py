from tabulate import tabulate
import re

def load_sentences_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        sentences = f.readlines()
    return [sentence.strip() for sentence in sentences]

def manual_annotation(sentences):
    annotated_data = []

    for sentence in sentences:
        dep_match = re.search(r'<Dep>(.*?)<EndDep>', sentence)
        arr_match = re.search(r'<Arr>(.*?)<EndArr>', sentence)

        dep = dep_match.group(1) if dep_match else "Unknown"
        arr = arr_match.group(1) if arr_match else "Unknown"

        cleaned_sentence = re.sub(r'<.*?>', '', sentence).strip()

        annotation = [cleaned_sentence, dep, arr]
        annotated_data.append(annotation)

    headers = ["Phrase", "Départ", "Arrivée"]
    print(tabulate(annotated_data, headers=headers, tablefmt="grid"))

def main():
    bottins_sentences = load_sentences_from_txt('../data/bottins_sentences_jb.csv')
    manual_annotation(bottins_sentences)

if __name__ == "__main__":
    main()

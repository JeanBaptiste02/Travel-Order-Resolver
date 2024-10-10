from transformers import CamembertTokenizer

def clean_bottins_data(data):
    sentences = []
    max_display = 3
    for i, entry in enumerate(data["Text"]):
        if i < max_display:
            print(f"Original entry: {entry}")
        cleaned_sentence = entry.split(",")[0]
        if i < max_display:
            print(f"Cleaned sentence: {cleaned_sentence}")
        sentences.append(cleaned_sentence)
    return sentences

def tokenize_and_preserve_labels(sentence, tokenizer):
    tokenized_sentence = []
    for word in sentence.split():
        tokenized_word = tokenizer.tokenize(word)
        tokenized_sentence.extend(tokenized_word)
    return tokenized_sentence

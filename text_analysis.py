import os
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from textstat import textstat
import pandas as pd
import chardet

# Ensure necessary NLTK data is downloaded
nltk.download('punkt')

# Detect encoding using chardet
def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
    return result['encoding']

# Load stop words with proper encoding detection
def load_stop_words():
    stop_words = []
    for file in os.listdir("StopWords"):
        file_path = f"StopWords/{file}"
        encoding = detect_encoding(file_path)
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            stop_words.extend(f.read().splitlines())
    return set(stop_words)

# Load positive and negative words with proper encoding detection
def load_master_dictionary():
    positive_words = []
    negative_words = []
    
    # Detect encoding for each file
    positive_encoding = detect_encoding("MasterDictionary/positive-words.txt")
    negative_encoding = detect_encoding("MasterDictionary/negative-words.txt")
    
    # Read files with detected encoding
    with open("MasterDictionary/positive-words.txt", "r", encoding=positive_encoding, errors="replace") as f:
        positive_words = f.read().splitlines()
    with open("MasterDictionary/negative-words.txt", "r", encoding=negative_encoding, errors="replace") as f:
        negative_words = f.read().splitlines()

    return set(positive_words), set(negative_words)

# Count syllables in a word
def syllable_count(word):
    word = word.lower()
    vowels = "aeiou"
    count = sum(1 for char in word if char in vowels)
    if word.endswith(("es", "ed")):
        count -= 1
    return max(count, 1)

# Load stop words and master dictionary (positive and negative words)
stop_words = load_stop_words()
positive_words, negative_words = load_master_dictionary()

# Initialize output data
output_data = []

# Process each article
for file in os.listdir("extracted_articles"):
    with open(f"extracted_articles/{file}", "r", encoding="utf-8") as f:
        text = f.read()

    # Tokenize text
    words = word_tokenize(text)
    sentences = sent_tokenize(text)
    cleaned_words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]

    # Calculate sentiment scores
    positive_score = sum(1 for word in cleaned_words if word in positive_words)
    negative_score = sum(1 for word in cleaned_words if word in negative_words)
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (len(cleaned_words) + 0.000001)

    # Readability metrics
    avg_sentence_length = len(words) / len(sentences) if sentences else 0
    complex_word_count = sum(1 for word in cleaned_words if syllable_count(word) > 2)
    percentage_complex_words = (complex_word_count / len(cleaned_words)) * 100 if cleaned_words else 0
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)

    # Other metrics
    word_count = len(cleaned_words)
    syllables_per_word = sum(syllable_count(word) for word in cleaned_words) / len(cleaned_words) if cleaned_words else 0
    avg_word_length = sum(len(word) for word in cleaned_words) / len(cleaned_words) if cleaned_words else 0

    # Personal pronouns
    personal_pronouns = len(re.findall(r'\b(I|we|my|ours|us)\b', text, flags=re.IGNORECASE))

    # Append results
    output_data.append([
        file.split('.')[0],
        positive_score,
        negative_score,
        polarity_score,
        subjectivity_score,
        avg_sentence_length,
        percentage_complex_words,
        fog_index,
        complex_word_count,
        word_count,
        syllables_per_word,
        personal_pronouns,
        avg_word_length
    ])

# Save to Excel
columns = [
    "URL_ID", "Positive Score", "Negative Score", "Polarity Score",
    "Subjectivity Score", "Avg Sentence Length", "Percentage of Complex Words",
    "Fog Index", "Complex Word Count", "Word Count", "Syllables Per Word",
    "Personal Pronouns", "Avg Word Length"
]
output_df = pd.DataFrame(output_data, columns=columns)
output_df.to_excel("Output Data Structure.xlsx", index=False)

print("Text analysis completed and saved to 'Output Data Structure.xlsx'.")

import json
import re
import contractions

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


STOPWORDS = {
    "en": set(stopwords.words("english")),
    "de": set(stopwords.words("german")),
    "fr": set(stopwords.words("french")),
    "fi": set(stopwords.words("finnish"))
}

stemmer = PorterStemmer()


def preprocess_text(text, language):
    text = text.lower()

    # expand contractions before punctuation is removed
    text = contractions.fix(text)

    # remove urls
    text = re.sub(r"http\S+|www\S+", "", text)

    # normalize non-word characters to spaces
    text = re.sub(r"[^\w\s]", " ", text)

    # normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    tokens = word_tokenize(text)

    stop_words = STOPWORDS.get(language, set())

    tokens = [
        word
        for word in tokens
        if word not in stop_words
    ]

    # only stem English for now
    if language == "en":
        tokens = [stemmer.stem(word) for word in tokens]

    return tokens


def get_text():
    with open("books.jsonl", encoding="utf-8") as f:
        line = next(f)

    book = json.loads(line)

    text = book["text"]
    language = book["language"]

    processed = preprocess_text(text, language)

    print(processed[:100])

import re


def remove_gutenberg_boilerplate(text):
    start_match = re.search(r"\*\*\*\s*START OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*", text, flags=re.IGNORECASE)

    end_match = re.search(r"\*\*\*\s*END OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*", text, flags=re.IGNORECASE)

    if start_match:
        text = text[start_match.end():]

    if end_match:
        text = text[:end_match.start()]

    return text.strip()
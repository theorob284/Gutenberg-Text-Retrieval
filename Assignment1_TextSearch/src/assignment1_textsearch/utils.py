import re

from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

from functools import lru_cache

@lru_cache(maxsize=200000)
def stem_word(language, word):
    stemmer = STEMMERS.get(language)

    if stemmer:
        return stemmer.stem(word)

    return word

def remove_gutenberg_boilerplate(text):
    start_match = re.search(r"\*\*\*\s*START OF THE PROJECT GUTENBERG (?:EBOOK|ETEXT).*?\*\*\*", text, flags=re.IGNORECASE)

    end_match = re.search(r"\*\*\*\s*END OF THE PROJECT GUTENBERG (?:EBOOK|ETEXT).*?\*\*\*", text,flags=re.IGNORECASE)

    start_pos = start_match.end() if start_match else 0
    end_pos = end_match.start() if end_match else len(text)

    text = text[start_pos:end_pos]

    # Older Gutenberg format
    old_markers = list(re.finditer(r"\*{2,}\s*The Project Gutenberg Etext of .*?\*{2,}", text, flags=re.IGNORECASE))

    if old_markers:
        text = text[old_markers[-1].end():]

    return text.strip()

LANGUAGES = {
    "en": "english",
    "fr": "french",
    "de": "german",
    "fi": "finnish",
    "nl": "dutch",
    "it": "italian",
    "es": "spanish",
    "pt": "portuguese",
    "sv": "swedish",
    "da": "danish",
}

STEMMERS = {
    code: SnowballStemmer(language)
    for code, language in LANGUAGES.items()
}

STOPWORDS = {
    code: set(stopwords.words(language))
    for code, language in LANGUAGES.items()
}

def preprocess_text(normalized_text, language):
    tokens = normalized_text.split()

    stop_words = STOPWORDS.get(language, set())
    tokens = [word for word in tokens if word not in stop_words]

    stemmer = STEMMERS.get(language)

    if stemmer:
        tokens = [stem_word(language, word) for word in tokens]

    return tokens

def preprocess_phrase_text(text):
    text = normalize_text(text)

    return text

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text

def normalize_metadata(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

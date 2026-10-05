import json
import re
import contractions
from pathlib import Path

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from whoosh import index
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.index import create_in
from whoosh.analysis import RegexTokenizer
from whoosh.qparser import QueryParser

def remove_gutenberg_boilerplate(text):
    start_match = re.search(r"\*\*\*\s*START OF THE PROJECT GUTENBERG (?:EBOOK|ETEXT).*?\*\*\*", text, flags=re.IGNORECASE)

    end_match = re.search(r"\*\*\*\s*END OF THE PROJECT GUTENBERG (?:EBOOK|ETEXT).*?\*\*\*",text,flags=re.IGNORECASE)

    if start_match:
        text = text[start_match.end():]

    if end_match:
        text = text[:end_match.start()]

    # Handle older Gutenberg material that may still appear
    old_markers = list(re.finditer(r"\*{2,}\s*The Project Gutenberg Etext of .*?\*{2,}", text, flags=re.IGNORECASE))

    if old_markers:
        text = text[old_markers[-1].end():]

    return text.strip()

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

    tokens = [word for word in tokens if word not in stop_words]

    # only stem English for now
    if language == "en":
        tokens = [stemmer.stem(word) for word in tokens]

    return tokens

SCHEMA = Schema(
    gutenberg_id=ID(stored=True, unique=True),
    title=TEXT(stored=True),
    author=TEXT(stored=True),
    language=KEYWORD(stored=True),
    text=TEXT(stored=False)
)

def get_text_and_index():
    INDEX_DIR = Path("indexed_text")
    INDEX_DIR.mkdir(exist_ok=True)

    ix = create_in(INDEX_DIR, SCHEMA)
    writer = ix.writer()

    with open("books.jsonl", encoding="utf-8") as f:
        for i, line in enumerate(f):
            book = json.loads(line)

            language = book["language"]
            text = book["text"]

            processed_tokens = preprocess_text(text, language)
            processed_text = " ".join(processed_tokens)

            writer.add_document(
                gutenberg_id=book["gutenberg_id"],
                title=book["title"],
                author=book["author"],
                language=language,
                text=processed_text
            )

            if i >= 9:
                break

    writer.commit()
    #print(processed[:300])


def search_index():
    
    ix = index.open_dir("indexed_text")

    """test to see it worked
    with ix.reader() as reader:
        i = 0
        for term in reader.field_terms("text"):
            print(term)
            i += 1
            if i >= 50:
                break
    """

    with ix.searcher() as searcher:
        print("\n----------------\n Doc count: ", searcher.doc_count(), "\n----------------\n")
        parser = QueryParser("text", schema=ix.schema)

        query = parser.parse("independ")

        results = searcher.search(query)

        print(f"Results found: {len(results)}")

        for result in results:
            print("Gutenberg ID:", result["gutenberg_id"])
            print("Title:", result["title"])
            print("Author:", result["author"])
            print("Score:", result.score) 
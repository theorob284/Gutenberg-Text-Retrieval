import json
import time
from tqdm import tqdm
from pathlib import Path

from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.index import create_in
from whoosh.analysis import SimpleAnalyzer

from .utils import (normalize_text, normalize_metadata, preprocess_text)

SCHEMA = Schema(
    gutenberg_id=ID(stored=True, unique=True),
    title=TEXT(stored=True, analyzer=SimpleAnalyzer()),
    author=TEXT(stored=True, analyzer=SimpleAnalyzer()),
    language=KEYWORD(stored=True),
    text=TEXT(stored=False, analyzer=SimpleAnalyzer()),
    text_phrase=TEXT(stored=False, analyzer=SimpleAnalyzer())
)

def get_text_and_index():
    INDEX_DIR = Path("indexed_text")
    INDEX_DIR.mkdir(exist_ok=True)

    ix = create_in(INDEX_DIR, SCHEMA)

    writer = ix.writer(procs=4, limitmb=128, multisegment=True)

    start_time = time.time()

    with open("books.jsonl", encoding="utf-8") as f:
        for i, line in enumerate(tqdm(f, total=10000, desc="Indexing books",  ncols=80)):
            book = json.loads(line)

            language = book["language"]
            text = book["text"]

            normalized_text = normalize_text(text)

            processed_tokens = preprocess_text(normalized_text,language)

            processed_text = " ".join(processed_tokens)

            writer.add_document(
                gutenberg_id=book["gutenberg_id"],
                title=normalize_metadata(book["title"]),
                author=normalize_metadata(book["author"]),
                language=language,
                text=processed_text,
                text_phrase=normalized_text
            )


    start_commit = time.time()
    writer.commit()
    total_commit = time.time() - start_commit

    elapsed_time = time.time() - start_time
    print(f"Whoosh commit: {total_commit:.2f}s")
    print(f"\nIndexing completed in {elapsed_time:.2f} seconds.")
import json
from collections import Counter

from whoosh.qparser import QueryParser
from whoosh import index

from .utils import normalize_text, normalize_metadata, preprocess_text, preprocess_phrase_text

def get_and_count_languages():
    lang = Counter()
    
    with open("books.jsonl", "r", encoding="utf-8") as read_lang:
        for row in read_lang:
            book = json.loads(row)
            lang[book["language"]] += 1

    print(lang)

def count_gutenberg_appearences():
    count = 0
    examples = []

    with open("books.jsonl", encoding="utf-8") as f:
        for line in f:
            book = json.loads(line)

            if "gutenberg" in book["text"].lower():
                count += 1

                if len(examples) < 10:
                    examples.append((book["gutenberg_id"], book["title"]) )

    print("Books containing 'gutenberg':", count)

    for book_id, title in examples:
        print(book_id, "-", title)

def test_search_index():
    ix = index.open_dir("indexed_text")

    with ix.searcher() as searcher:
        print(f"\n----------------\nDoc count: {searcher.doc_count()}\n----------------\n")

        # Normal body search
        search_text = "independence"
        language = "en"

        normalized_query = normalize_text(search_text)

        processed_query = preprocess_text(normalized_query, language)
        processed_query = " ".join(processed_query)

        parser = QueryParser("text", schema=ix.schema)
        query = parser.parse(processed_query)

        results = searcher.search(query)

        print("\nNORMAL BODY SEARCH")
        print("Query:", search_text)
        print(f"Results found: {len(results)}")

        for result in results:
            print("Gutenberg ID:", result["gutenberg_id"])
            print("Title:", result["title"])
            print("Author:", result["author"])
            print("Score:", result.score)
            print()


        # Phrase search
        search_text = "he has plundered our seas"
        language = "en"

        processed_phrase = preprocess_phrase_text(search_text)

        parser = QueryParser("text_phrase", schema=ix.schema)
        query = parser.parse(f'"{processed_phrase}"')

        results = searcher.search(query)

        print("\nPHRASE SEARCH")
        print("Query:", search_text)
        print(f"Results found: {len(results)}")

        for result in results:
            print("Gutenberg ID:", result["gutenberg_id"])
            print("Title:", result["title"])
            print("Author:", result["author"])
            print("Score:", result.score)
            print()


        # Title search
        search_text = "Declaration of Independence"

        processed_title = normalize_metadata(search_text)

        parser = QueryParser("title", schema=ix.schema)
        query = parser.parse(processed_title)

        results = searcher.search(query)

        print("\nTITLE SEARCH")
        print("Query:", search_text)
        print(f"Results found: {len(results)}")

        for result in results:
            print("Gutenberg ID:", result["gutenberg_id"])
            print("Title:", result["title"])
            print("Author:", result["author"])
            print("Score:", result.score)
            print()


        # Author search
        search_text = "Thomas Jefferson"

        processed_author = normalize_metadata(search_text)

        parser = QueryParser("author", schema=ix.schema)
        query = parser.parse(processed_author)

        results = searcher.search(query)

        print("\nAUTHOR SEARCH")
        print("Query:", search_text)
        print(f"Results found: {len(results)}")

        for result in results:
            print("Gutenberg ID:", result["gutenberg_id"])
            print("Title:", result["title"])
            print("Author:", result["author"])
            print("Score:", result.score)
            print()

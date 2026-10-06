from pathlib import Path
import re

from whoosh.query import Or
from whoosh.qparser import QueryParser
from whoosh import index

from .utils import normalize_text, normalize_metadata, preprocess_phrase_text


def safe_filename(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text).strip("_")
    return text


def search_books(search_text, submission=False, query_id=None):
    ix = index.open_dir("indexed_text")

    # Language-neutral versions of the query
    normalized_query = normalize_text(search_text)
    metadata_query = normalize_metadata(search_text)
    phrase_query = preprocess_phrase_text(search_text)

    with ix.searcher() as searcher:
        queries = []

        # Normal body search
        # text_phrase contains normalized text without language-specific stemming
        if normalized_query:
            text_parser = QueryParser("text_phrase", schema=ix.schema)
            text_query = text_parser.parse(normalized_query)
            text_query.boost = 1.0
            queries.append(text_query)

        # Title search
        if metadata_query:
            title_parser = QueryParser("title", schema=ix.schema)
            title_query = title_parser.parse(metadata_query)
            title_query.boost = 2.5
            queries.append(title_query)

        # Author search
        if metadata_query:
            author_parser = QueryParser("author", schema=ix.schema)
            author_query = author_parser.parse(metadata_query)
            author_query.boost = 3.0
            queries.append(author_query)

        # Exact phrase search
        if phrase_query:
            phrase_parser = QueryParser("text_phrase", schema=ix.schema)
            phrase_search = phrase_parser.parse(f'"{phrase_query}"')
            phrase_search.boost = 1.5
            queries.append(phrase_search)

        # Combine all searches
        final_query = Or(queries)

        limit = 100 if submission else 20
        results = searcher.search(final_query, limit=limit)

        if submission:
            output_lines = []

            for rank, result in enumerate(results, start=1):
                output_lines.append(
                    f"{query_id} Q0 "
                    f"{result['gutenberg_id']} "
                    f"{rank} "
                    f"{result.score} "
                    f"theo.robin2@mail.dcu.ie"
                )

            return output_lines

        else:
            results_dir = Path("results")
            results_dir.mkdir(exist_ok=True)

            output_lines = []

            output_lines.append(f"Search: {search_text}")
            output_lines.append(f"Results found: {len(results)}")
            output_lines.append("")

            for rank, result in enumerate(results, start=1):
                output_lines.append(f"Rank: {rank}")
                output_lines.append(f"Gutenberg ID: {result['gutenberg_id']}")
                output_lines.append(f"Title: {result['title']}")
                output_lines.append(f"Author: {result['author']}")
                output_lines.append(f"Score: {result.score}")
                output_lines.append("----------------")

            output = "\n".join(output_lines)

            filename = safe_filename(search_text) + ".txt"
            output_path = results_dir / filename

            output_path.write_text(
                output,
                encoding="utf-8"
            )

            print(f"\nSaved results to: {output_path}")
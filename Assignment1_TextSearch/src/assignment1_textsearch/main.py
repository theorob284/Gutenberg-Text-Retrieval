import click
import json
import gzip
from pathlib import Path

from .read_files import read_books_csv, read_books_txt
from .utils import remove_gutenberg_boilerplate
from .index_text import get_text_and_index
from .search_index import search_books
from .tests import get_and_count_languages ,count_gutenberg_appearences, test_search_index
from .generate_results import generate_results
from .index_statistics import get_index_statistics

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = PROJECT_ROOT / "books_10k.csv"
BOOKS_DIR = PROJECT_ROOT / "books"

@click.command()
@click.option("--load_csv", is_flag=True, help="Test loads all the rows of the CSV file")
@click.option("--load_txt", is_flag=True, help="Test loads the text files of each book")
@click.option("--match_csv_book", is_flag=True, help="Matches csv row to its book and converts to jsonl")
@click.option("--index_text", is_flag=True, help="Preprocesses and indexes book text")
@click.option("--search", type=str,help="Search the Whoosh index - MAIN IDEA")
@click.option("--generate_submission", is_flag=True, help="Generates submission text file in the correct format")
# Test options
@click.option("--count_languages", is_flag=True, help="Returns a dict and count of the languages present")
@click.option("--count_gutenberg", is_flag=True, help="Returns a number of times gutenberg appears post pre-processing")
@click.option("--test_view_index", is_flag=True, help="View hard coded tests of different fields in the index")
@click.option("--index_statistics", is_flag=True, help="View the statistics of the index")
def main(load_csv, load_txt ,match_csv_book, index_text, search, generate_submission ,count_languages, count_gutenberg, test_view_index, index_statistics):

    if load_txt:
        read_books_txt(BOOKS_DIR)

    if load_csv:
        read_books_csv(CSV_PATH)

    if match_csv_book:
        with open("books.jsonl", "w", encoding="utf-8") as output_file:

            for row in read_books_csv(CSV_PATH):

                book_path = BOOKS_DIR / row["filename"]

                try:
                    text = remove_gutenberg_boilerplate(book_path.read_text(encoding="utf-8").strip())

                except UnicodeDecodeError:
                    with gzip.open(book_path, "rt", encoding="utf-8") as f:
                        text = remove_gutenberg_boilerplate(f.read().strip())
                        #print(text)

                book_data = {
                    "gutenberg_id": row["gutenberg_id"],
                    "filename": row["filename"],
                    "title": row["title"],
                    "author": row["author"],
                    "language": row["language"],
                    "text": text
                }

                output_file.write(json.dumps(book_data, ensure_ascii=False) + "\n")

    if index_text:
        get_text_and_index()

    if search: # main function, outputs to .txt files
        search_books(search)

    if generate_submission:
        generate_results()

    if count_languages:
        get_and_count_languages()

    if count_gutenberg:
        count_gutenberg_appearences()

    if test_view_index:
        test_search_index()

    if index_statistics:
        get_index_statistics()
        

if __name__ == "__main__":
    main()
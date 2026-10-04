import click
import json
import gzip
from pathlib import Path

from .read_files import read_books_csv, read_books_txt

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = PROJECT_ROOT / "books_10k.csv"
BOOKS_DIR = PROJECT_ROOT / "books"

@click.command()
@click.option("--load_csv", is_flag=True, help="Test loads all the rows of the CSV file")
@click.option("--load_txt", is_flag=True, help="Test loads the text files of each book")
@click.option("--match_csv_book", is_flag=True, help="Matches csv row to its book and converts to jsonl")
def main(load_csv, load_txt, match_csv_book):

    if load_txt:
        read_books_txt(BOOKS_DIR)

    if load_csv:
        read_books_csv(CSV_PATH)

    if match_csv_book:
        with open("books.jsonl", "w", encoding="utf-8") as output_file:

            for row in read_books_csv(CSV_PATH):

                book_path = BOOKS_DIR / row["filename"]

                try:
                    text = book_path.read_text(encoding="utf-8").strip()

                except UnicodeDecodeError as e:
                    with gzip.open(book_path, "rt", encoding="utf-8") as f:
                        text = f.read().strip()
                        print(text)

                book_data = {
                    "gutenberg_id": row["gutenberg_id"],
                    "filename": row["filename"],
                    "title": row["title"],
                    "author": row["author"],
                    "language": row["language"],
                    "text": text
                }

                output_file.write(json.dumps(book_data, ensure_ascii=False) + "\n")
        

if __name__ == "__main__":
    main()
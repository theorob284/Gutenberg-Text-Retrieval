import click
from pathlib import Path

from read_files import read_books_csv, read_books_txt

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = PROJECT_ROOT / "books_10k.csv"
BOOKS_DIR = PROJECT_ROOT / "books"

@click.command()
@click.option("--load_csv", is_flag=True, help="Loads all the rows of the CSV file")
@click.option("--load_txt", is_flag=True, help="Loads the text files of each book")
def main(load_csv, load_txt):
    if load_csv:
        read_books_csv(CSV_PATH)

    if load_txt:
        read_books_txt(BOOKS_DIR)

    if not load_csv and not load_txt:
        click.echo("You need to load at least one file")

if __name__ == "__main__":
    main()
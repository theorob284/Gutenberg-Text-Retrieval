import csv

def read_books_txt(path):
    for f in path.glob("*.txt"):
        try:
            text = f.read_text(encoding="utf-8").strip()

            yield {
                "filename": f.name,
                "text": text
            }

        except UnicodeDecodeError as e:
            print(f"Could not decode: {f.name}")
            print(e)


def read_books_csv(path):
    with open(path, encoding="utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            yield row
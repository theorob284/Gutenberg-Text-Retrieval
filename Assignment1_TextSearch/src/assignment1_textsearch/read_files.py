import csv


def read_books_txt(path):
    test_counter = 0
    for f in path.glob('*.txt'):
        print(f.read_text(encoding='utf-8').strip())

        test_counter += 1
        if test_counter >= 5:
            print(f"{test_counter} files were read")
            break

def read_books_csv(path):
    with open(path, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0

        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
            else:
                print(row)

            line_count += 1

        print(f"Processed {line_count} lines.")
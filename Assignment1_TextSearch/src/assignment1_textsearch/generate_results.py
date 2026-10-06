from .search_index import search_books
from pathlib import Path

def generate_results():
    queries = [
        ("Q1", "to be, or not to be"),
        ("Q2", "English Grammar"),
        ("Q3", "Philip K Dick"),
        ("Q4", "Jabberwocky"),
        ("Q5", "Gutenberg"),
        ("Q6", "Dornröschen"),
    ]

    submission_lines = []

    for query_id, query_text in queries:
        lines = search_books(
            query_text,
            submission=True,
            language="en",
            query_id=query_id
        )

        submission_lines.extend(lines)

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    output_path = results_dir / "results.txt"

    output_path.write_text(
        "\n".join(submission_lines),
        encoding="utf-8"
    )

    print(f"Submission saved to: {output_path}")
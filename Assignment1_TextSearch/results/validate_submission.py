#!/usr/bin/env python3
"""
Submission format validator (for students).

Usage:
    python3 validate_submission.py results.txt

Checks that results.txt conforms to the required TREC-like submission format:

    Q1 Q0 <gutenberg_id> <rank> <score> <team-name>
    ...

Rules:
  * Exactly 6 query blocks: Q1..Q6
  * At most 100 result lines per query (submit your top-100; fewer lines are
    accepted only if you believe fewer than 100 documents could be relevant)
  * Ranks must be consecutive 1..N, in order
  * Every gutenberg_id must exist in books_10k.csv
  * No duplicate documents within one query
  * Scores must be numeric; within a query they must be non-increasing with rank
  * Last field is your team name: use your DCU email address
    (e.g. s.studentname@mail.dcu.ie) as a single token, no spaces
Exit code 0 = valid, 1 = invalid.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS_CSV = os.path.join(HERE, "..", "books_10k.csv")

REQUIRED_QUERIES = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]
MAX_RUNS_PER_QUERY = 100


def load_valid_ids():
    ids = set()
    with open(BOOKS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ids.add(row["gutenberg_id"])
    return ids


def validate(path):
    errors = []
    warnings = []

    try:
        valid_ids = load_valid_ids()
    except FileNotFoundError:
        print("ERROR: cannot find books_10k.csv — run this script from the "
              "repository layout provided to you.", file=sys.stderr)
        return 1

    if not os.path.exists(path):
        print(f"ERROR: file not found: {path}")
        return 1

    entries = {}          # qid -> list of (gid, rank, score, team)
    with open(path, encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) != 6:
                errors.append(f"line {lineno}: expected 6 whitespace-separated "
                              f"fields, got {len(parts)}: {line!r}")
                continue
            qid, dash, gid, rank_s, score_s, team = parts
            if qid not in REQUIRED_QUERIES:
                errors.append(f"line {lineno}: unknown query id {qid!r} "
                              f"(must be one of {', '.join(REQUIRED_QUERIES)})")
                continue
            if dash != "Q0":
                errors.append(f"line {lineno}: second field must be 'Q0', got {dash!r}")
            if gid not in valid_ids:
                errors.append(f"line {lineno}: gutenberg_id {gid!r} is not part "
                              f"of the 10k collection")
            try:
                rank = int(rank_s)
            except ValueError:
                errors.append(f"line {lineno}: rank must be an integer, got {rank_s!r}")
                rank = -1
            try:
                score = float(score_s)
            except ValueError:
                errors.append(f"line {lineno}: score must be numeric, got {score_s!r}")
                score = float("nan")
            # team name is intentionally not validated beyond structure:
            # any single token is accepted (DCU email expected, see README).
            entries.setdefault(qid, []).append((gid, rank, score, team, lineno))

    # per-query structural checks
    for qid in REQUIRED_QUERIES:
        docs = entries.get(qid, [])
        if not (0 < len(docs) <= MAX_RUNS_PER_QUERY):
            errors.append(f"{qid}: expected 1..{MAX_RUNS_PER_QUERY} result lines, found {len(docs)}")
            continue
        ranks = [d[1] for d in docs]
        if ranks != list(range(1, len(docs) + 1)):
            errors.append(f"{qid}: ranks must be 1..{RUNS_PER_QUERY} in order, got {ranks}")
        gids = [d[0] for d in docs]
        dupes = {g for g in gids if gids.count(g) > 1}
        if dupes:
            errors.append(f"{qid}: duplicate document(s): {sorted(dupes)}")
        scores = [d[2] for d in docs]
        if any(scores[i] < scores[i + 1] - 1e-9 for i in range(len(scores) - 1)):
            errors.append(f"{qid}: scores are not non-increasing with rank")

    teams = {d[3] for ds in entries.values() for d in ds}
    if len(teams) > 1:
        warnings.append(f"multiple team names used: {sorted(teams)}")

    # ---- report ----
    print(f"Validating {path}")
    print(f"  queries found : {sorted(entries.keys())}")
    print(f"  total lines   : {sum(len(v) for v in entries.values())}")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  ! {w}")
    if errors:
        print(f"\nINVALID — {len(errors)} error(s):")
        for e in errors:
            print(f"  x {e}")
        return 1
    print("\nOK — submission format is valid.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(validate(sys.argv[1]))

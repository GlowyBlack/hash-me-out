import os
import pandas as pd

SHARD_DIR = "app/data/books"
TITLE_COL = "Book-Title"
AUTHOR_COL = "Book-Author"


def simple_titlecase(s: str) -> str:
    """Safely convert to title case without complex rules."""
    if not isinstance(s, str):
        return s

    # Lowercase entire string, then title-case normally
    s = s.strip().lower()
    return " ".join(word.capitalize() for word in s.split())


def read_shard(path: str):
    """Read semicolon CSV with fallback encoding."""
    try:
        return pd.read_csv(path, dtype=str, sep=";", encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, dtype=str, sep=";", encoding="ISO-8859-1")


def process_shard(file_path: str):
    file_path = os.path.normpath(file_path)
    print(f"\n📘 Processing {file_path} ...")

    df = read_shard(file_path)

    # Before preview
    if TITLE_COL in df.columns:
        print("Before (title):", df[TITLE_COL].head(3).tolist())
    if AUTHOR_COL in df.columns:
        print("Before (author):", df[AUTHOR_COL].head(3).tolist())

    # Apply simple title casing
    if TITLE_COL in df.columns:
        df[TITLE_COL] = df[TITLE_COL].fillna("").apply(simple_titlecase)
    if AUTHOR_COL in df.columns:
        df[AUTHOR_COL] = df[AUTHOR_COL].fillna("").apply(simple_titlecase)

    # After preview
    if TITLE_COL in df.columns:
        print("After  (title):", df[TITLE_COL].head(3).tolist())
    if AUTHOR_COL in df.columns:
        print("After  (author):", df[AUTHOR_COL].head(3).tolist())

    # Save back using semicolon separator (CRITICAL!)
    df.to_csv(file_path, index=False, sep=";", encoding="utf-8")

    print(f"✔ Updated {file_path}")


def process_all_shards():
    print("\n🔎 Scanning shard directory:", SHARD_DIR)

    for fname in sorted(os.listdir(SHARD_DIR)):
        if fname.lower().endswith(".csv"):
            process_shard(os.path.join(SHARD_DIR, fname))

    print("\n✨ All shard files processed successfully!\n")


process_all_shards()

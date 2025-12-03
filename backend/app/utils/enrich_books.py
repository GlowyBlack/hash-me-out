# app/utils/api_enrichment_resumable.py


import pandas as pd
import time
import os
from tqdm import tqdm
from app.utils.openlibrary_client import fetch_subjects_from_openlibrary
from app.utils.genre_util import map_subjects_to_genres

def enrich_books_resumable(
    input_file="app/data/splits/BX_Books_remaining_part1.csv",
    output_file="app/data/splits/Enriched_Books_remaining_part1.csv",
    sleep_time=0.2,
    save_every=25
):
    """
    Creates a new enriched books file:
    Columns: ISBN, Book-Title, Book-Author, Genre
    Resumable + retry-safe + tqdm progress bar.
    """

    print("Loading BX-Books.csv...")

    # Load original dataset (ISO-8859-1 encoding)
    df_raw = pd.read_csv(
        input_file,
        sep=";",
        encoding="ISO-8859-1",
        low_memory=False
    )

    # Build MINIMAL dataframe for enrichment
    df = pd.DataFrame({
        "ISBN": df_raw["ISBN"].astype(str),
        "Book-Title": df_raw["Book-Title"].astype(str),
        "Book-Author": df_raw["Book-Author"].astype(str),
        "Genre": [""] * len(df_raw)
    })

    # Resume progress if existing file found
    if os.path.exists(output_file):
        print(f"Found existing {output_file}. Resuming progress...")
        df_existing = pd.read_csv(output_file, encoding="utf-8")

        # Only load existing genre column
        df["Genre"] = df_existing["Genre"]

    total = len(df)
    print(f"Total books to enrich: {total}\n")

    # Iterate with tqdm progress bar
    for idx, row in tqdm(df.iterrows(), total=total, desc="Enriching Books", unit="book"):

        isbn = row["ISBN"].strip()
        current_genre = str(row["Genre"]).strip().lower()

        # Skip already enriched rows
        if current_genre not in ["", "nan"]:
            continue

        # Fetch subjects
        subjects, success = fetch_subjects_from_openlibrary(isbn)
        if not success:
            # Silent failure → user sees on next run
            continue

        # Map subjects → genres
        genres = map_subjects_to_genres(subjects)

        if not genres:
            df.at[idx, "Genre"] = "Unknown"
        else:
            df.at[idx, "Genre"] = ", ".join(genres)

        # Save progress every N rows
        if idx % save_every == 0:
            df.to_csv(output_file, index=False, encoding="utf-8")

        time.sleep(sleep_time)

    # Final save
    df.to_csv(output_file, index=False, encoding="utf-8")

    print("\n🎉 Enrichment complete!")
    print(f"Saved to: {output_file}")
    print(f"Total rows: {total}")

enrich_books_resumable()


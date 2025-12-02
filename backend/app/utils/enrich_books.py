# app/utils/api_enrichment_resumable.py

import pandas as pd
import time
import os
from app.utils.openlibrary_client import fetch_subjects_from_openlibrary
from app.utils.genre_util import map_subjects_to_genres

def enrich_books_resumable(
    input_file="app/data/BX_Books_remaining_part3.csv",
    output_file="app/data/Enriched_Books_remaining_part3.csv",
    sleep_time=0.2,
    save_every=25
):
    """
    Creates a new enriched books file:
    Columns: ISBN, Book-Title, Book-Author, Genre
    Resumable + retry-safe.
    """

    print("Loading BX-Books.csv...")

    # Load original dataset (ISO-8859-1 encoding)
    df_raw = pd.read_csv(
        input_file,
        sep=";",
        encoding="ISO-8859-1",
        low_memory=False
    )

    # Build a MINIMAL dataframe for enrichment
    df = pd.DataFrame({
        "ISBN": df_raw["ISBN"].astype(str),
        "Book-Title": df_raw["Book-Title"].astype(str),
        "Book-Author": df_raw["Book-Author"].astype(str),
        "Genre": [""] * len(df_raw)
    })

    # If enriched file exists, resume progress
    if os.path.exists(output_file):
        print(f"Found existing {output_file}. Resuming progress...")
        df_existing = pd.read_csv(output_file, encoding="utf-8")
        
        # Overwrite only the Genre column from previous progress
        df["Genre"] = df_existing["Genre"]

    total = len(df)
    print(f"Total books to enrich: {total}\n")

    for idx, row in df.iterrows():
        isbn = row["ISBN"].strip()

        # Skip already enriched rows
        # if str(row["Genre"]).strip():
        #     continue
        
        genre_val = str(row["Genre"]).strip().lower()

        if genre_val not in ["", "nan"]:  
            continue

        print(f"[{idx+1}/{total}]🔎 Fetching genre for ISBN {isbn}...")

        subjects, success = fetch_subjects_from_openlibrary(isbn)
        if not success:
            print("   ⚠️ Network error — keeping blank to retry next run.")
            continue


        genres = map_subjects_to_genres(subjects)


        if not genres:
            df.at[idx, "Genre"] = "Unknown"
        else:
            df.at[idx, "Genre"] = ", ".join(genres)

        # Save progress every N rows
        if idx % save_every == 0:
            print("   💾 Saving progress...")
            df.to_csv(output_file, index=False, encoding="utf-8")

        time.sleep(sleep_time)

    # Final save
    print("\nSaving final enriched file...")
    df.to_csv(output_file, index=False, encoding="utf-8")

    print("\n🎉 Enrichment complete!")
    print(f"Saved to: {output_file}")
    print(f"Total rows: {total}")

enrich_books_resumable()


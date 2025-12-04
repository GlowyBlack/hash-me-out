import pandas as pd

def load_enriched_books(file_path="app/data/Enriched_Books.csv"):
    """
    Loads the enriched books CSV and prepares text fields for TF-IDF.
    Returns a cleaned DataFrame.
    """

    df = pd.read_csv(file_path, dtype=str, low_memory=False)

    # Clean columns
    df["ISBN"] = df["ISBN"].astype(str)
    df["Book-Title"] = df["Book-Title"].fillna("").astype(str)
    df["Book-Author"] = df["Book-Author"].fillna("").astype(str)
    df["Genre"] = df["Genre"].fillna("Unknown").astype(str)

    # Combine fields for TF-IDF
    df["combined_text"] = (
        df["Book-Title"] + " " +
        df["Book-Title"] + " " +
        df["Genre"] + " " +
        df["Genre"] + " " +
        df["Genre"] + " " +
        df["Book-Author"] 

    ).str.lower()

    return df


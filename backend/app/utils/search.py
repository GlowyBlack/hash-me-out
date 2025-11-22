import csv
from pathlib import Path

"""Searches for books whose isbn or author or title matches the query"""
def search_books(query: str):
    if not query:
        return []
    filepath = Path(__file__).resolve().parents[1] / "data" / "BX_Books.csv"
    
    query = query.lower()
    results = []
    seen_isbn = set()
    with open(filepath, encoding="ISO-8859-1") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            title = row['Book-Title'].lower()
            author = row['Book-Author'].lower()
            isbn = row['ISBN']

            if isbn in seen_isbn:
                continue
            
            if (query in title or query in author or query in isbn):
                results.append({
                    "isbn": row["ISBN"],
                    "title": row["Book-Title"],
                    "author": row["Book-Author"],
                    "year": row["Year-Of-Publication"],
                    "publisher": row["Publisher"],
                    # "cover": row.get("Image-URL-M") 
                })     
                seen_isbn.add(isbn)
            if len(results)>=10:
                break
        
    return results


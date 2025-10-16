import csv

# Searches for books whose isbn or author or title matches the query
# Have it so that it only finds 10 books at a time
def search_books(query: str):
    if not query:
        return []
    
    results = []
    with open("./data/BX-Books.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            title = row['Book-Title'].lower()
            author = row['Book-Author'].lower()
            isbn = row['ISBN']
            
            if (query in title or query in author or query in isbn):
                results.append({
                    "title": row["Book-Title"],
                    "author": row["Book-Author"],
                    "isbn": row["ISBN"],
                    "year": row["Year-Of-Publication"],
                    "publisher": row["Publisher"]
                })            
            if len(results)>=10:
                break
        
    return results
        
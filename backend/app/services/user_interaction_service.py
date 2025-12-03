from app.repositories.csv_repository import CSVRepository
CSV_PATH_RATINGS = "app/data/Ratings.csv"
CSV_PATH_REVIEWS = "app/data/Reviews.csv"
CSV_PATH_READINGLIST = "app/data/ReadingList.csv"
class UserInteractionService:
    def __init__(self):
        self.csv = CSVRepository()

    def get_user_interactions(self, user_id: int):
        interactions = []

        # ----- Ratings -----
        ratings = self.csv.read_all(CSV_PATH_RATINGS)
        for r in ratings:
            if str(r["UserID"]) == str(user_id):
                interactions.append({
                    "isbn": r["ISBN"],
                    "type": "rating",
                    "rating_value": int(r["Book-Rating"])
                })

        # ----- Reviews -> comment -----
        reviews = self.csv.read_all(CSV_PATH_REVIEWS)
        for rv in reviews:
            if str(rv["UserID"]) == str(user_id):
                interactions.append({
                    "isbn": rv["ISBN"],
                    "type": "comment"
                })

        # ----- Reading List -----
        lists = self.csv.read_all(CSV_PATH_READINGLIST)
        for item in lists:
            if str(item["UserID"]) != str(user_id):
                continue

            raw_isbns = item.get("ISBNs", "")
            if not raw_isbns:
                continue

            # Parse "AAA|BBB|CCC"
            isbn_list = raw_isbns.split("|")

            for isbn in isbn_list:
                isbn = isbn.strip()
                if isbn:
                    interactions.append({
                        "isbn": isbn,
                        "type": "reading_list_add",
                    })


        # ----- Views (Future Use) -----
        try:
            views = self.csv.read_all("app/data/views.csv")
            for v in views:
                if str(v["UserID"]) == str(user_id):
                    duration = int(v["duration"])
                    interactions.append({
                        "isbn": v["ISBN"],
                        "type": "long_view" if duration >= 15 else "short_view"
                    })
        except FileNotFoundError:
            pass

        return interactions

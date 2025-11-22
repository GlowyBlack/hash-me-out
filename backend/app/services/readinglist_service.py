from pathlib import Path
from typing import List, Optional
from app.models.request import Request
from app.schemas.readinglist import ReadingListCreate, ReadingListDetail, ReadingListSummary 
from app.models.readinglist import ReadingList 
from app.repositories.base_repository import BaseRepository
from app.repositories.csv_repository import CSVRepository
from app.repositories.book_repository import BookRepository

class ReadingListService:
    def __init__(self, repo: BaseRepository, book_repo: BookRepository):
        self.repo = repo
        self.book_repo = book_repo
        self.path = Path(__file__).resolve().parents[1] / "data" / "ReadingLists.csv"
        self.fields = ["ListID", "UserID", "Name", "ISBNs", "IsPublic"]
        
    def __generate_next_id(self) -> int:
        """Generates the next available reading list ID."""
        rows = self.repo.read_all(self.path)
        if not rows:
            return 1
        ids = [int(r["ListID"]) for r in rows if r["ListID"].isdigit()]
        return max(ids, default = 0) + 1
    
    def __number_of_readinglist(self, user_id)-> int:
        """Counts how many reading lists a user currently has."""
        rows = self.repo.read_all(self.path)
        count = 0
        for row in rows:
            if str(user_id) == row["UserID"]: 
                count += 1
        
        return count
    
    def get_all_readinglist(self, user_id: int) -> List[ReadingListSummary]:
        """Returns all reading lists belonging to a user."""
        rows = self.repo.read_all(self.path)
        result = []
        for r in rows:
            if r["UserID"] == str(user_id):
                rl = ReadingList.from_dict(r)
                result.append(
                    ReadingListSummary(
                        list_id = rl.list_id,
                        name = rl.name,
                        total_books = len(rl.books),
                        is_public = rl.is_public
                    )
                )

        return result
    
    def create_list(self, data: ReadingListCreate, user_id: int) -> ReadingListDetail:
        """Creates a new reading list for the user."""
        if self.__number_of_readinglist(user_id) >= 10:
            raise ValueError("You can only have 10 reading lists")

        rows = self.repo.read_all(self.path)
        for r in rows:
            if r["UserID"] == str(user_id) and r["Name"].lower() == data.name.lower():
                raise ValueError(f'A reading list named "{data.name}" already exists.')

        next_id = self.__generate_next_id()
        rl = ReadingList(next_id, user_id, data.name)

        self.repo.append_row(self.path, self.fields, rl.to_csv_dict())
        books_info = []
        return ReadingListDetail(**rl.to_api_dict(books_info))

    
    def delete_list(self, list_id: int, user_id: int) -> bool:
        """Deletes a reading list if it belongs to the user."""
        rows = self.repo.read_all(self.path)
        original_count = len(rows)
        
        updated_rows = [
            r for r in rows if not (int(r["ListID"]) == list_id and int(r["UserID"]) == user_id)
        ]
        if len(updated_rows) == original_count:
            return False

        for i, row in enumerate(updated_rows, start=1):
            row["ListID"] = str(i)
        
        self.repo.write_all(self.path, self.fields, updated_rows)
        
        return True

    def rename(self, list_id: int, user_id: int, new_name: str) -> bool:
        """Renames an existing reading list."""
        rows = self.repo.read_all(self.path)
        all_names = [r["Name"].lower() for r in rows 
                     if r["UserID"] == str(user_id) and r["ListID"] != str(list_id)]
        
        if new_name.lower() in all_names:
            raise ValueError(f'A reading list named "{new_name}" already exists.')
        
        renamed = False
        for r in rows:
            if r["UserID"] == str(user_id) and r["ListID"] == str(list_id):
                readinglist = ReadingList.from_dict(r)
                readinglist.rename(new_name)
                r.update(readinglist.to_csv_dict())
                renamed = True
                break
            
        if not renamed:
            return False
        self.repo.write_all(self.path, self.fields, rows)
        return True

    def toggle_visibility(self, list_id: int, user_id: int):
        """Toggles a reading list’s public visibility setting."""
        rows = self.repo.read_all(self.path)

        for r in rows:
            if r["ListID"] == str(list_id) and r["UserID"] == str(user_id):
                rl = ReadingList.from_dict(r)
                rl.is_public = not rl.is_public
                r.update(rl.to_csv_dict())
                self.repo.write_all(self.path, self.fields, rows)
                return {
                    "list_id": list_id,
                    "is_public": rl.is_public,
                    "message": "Visibility toggled successfully",
                }
        return False

    def add_book(self, list_id: int, user_id: int, isbn: str) -> bool:
        """Adds a book to a reading list."""
        rows = self.repo.read_all(self.path)

        for r in rows:
            if r["ListID"] == str(list_id) and r["UserID"] == str(user_id):

                rl = ReadingList.from_dict(r)

                if isbn in rl.books:
                    raise ValueError(f"Book {isbn} already in the reading list.")

                rl.add_book(isbn)

                r.update(rl.to_csv_dict())

                self.repo.write_all(self.path, self.fields, rows)
                return True

        return False

    def remove_book(self, list_id: int, user_id: int, isbn: str) -> bool:
        """Removes a book from a reading list."""
        rows = self.repo.read_all(self.path)

        for r in rows:
            if r["ListID"] == str(list_id) and r["UserID"] == str(user_id):
                rl = ReadingList.from_dict(r)

                if isbn not in rl.books:
                    raise ValueError(f"Book {isbn} not found in the reading list.")

                rl.remove_book(isbn)

                r.update(rl.to_csv_dict())

                self.repo.write_all(self.path, self.fields, rows)
                return True

        return False

    def get_user_public_readinglists(self, user_id: int) -> Optional[ReadingListSummary]:
        """Returns all of a user's reading lists that are marked public."""
        rows = self.repo.read_all(self.path)
        result = []

        for r in rows:
            if (
                r["UserID"] == str(user_id) and 
                r.get("IsPublic", "false") == "true"
            ):
                rl = ReadingList.from_dict(r)
                result.append(
                    ReadingListSummary(
                        list_id = rl.list_id,
                        name = rl.name,
                        total_books = len(rl.books),
                        is_public = rl.is_public
                    )
                )

        if not result:
            return {"message": "User has no public reading lists"}

        return result

    def get_list_detail(self, list_id: int, user_id: int) -> Optional[ReadingListDetail]:
        """Returns full details for a specific reading list."""
        rows = self.repo.read_all(self.path)

        for r in rows:
            if r["ListID"] == str(list_id) and r["UserID"] == str(user_id):
                rl = ReadingList.from_dict(r)
                books_info = self.book_repo.get_books_by_isbn(rl.books)
                return ReadingListDetail(**rl.to_api_dict(books_info))

        return None

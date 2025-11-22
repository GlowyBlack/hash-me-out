import csv
import os
from app.repositories.csv_repository import CSVRepository

class BXBooksCSVAdapter(CSVRepository):
    """ Adapter for BX_Books.csv (semicolon + Latin-1 encoding). """

    def read_all(self, path):
        if not os.path.exists(path):
            return []
        lock = self._get_lock(path)
        with lock, open(path, "r", encoding="latin-1", newline="") as f:
            return list(csv.DictReader(f, delimiter=";"))

    def write_all(self, path, fieldnames, rows):
        lock = self._get_lock(path)
        with lock, open(path, "w", encoding="latin-1", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(rows)

    def append_row(self, path, fieldnames, row):
        file_exists = os.path.exists(path)
        lock = self._get_lock(path)
        with lock, open(path, "a", encoding="latin-1", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

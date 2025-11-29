import csv
import os
from pathlib import Path

from app.repositories.csv_repository import CSVRepository


class BXBooksCSVAdapter(CSVRepository):
    # -----------------------------
    # READ ALL
    # -----------------------------
    def read_all(self, path):
        path = os.path.abspath(path)
        rwlock = self._get_rwlock(path)

        # Shared (reader) lock
        rwlock.acquire_read()
        try:
            if not os.path.exists(path):
                return []
            with open(path, "r", encoding="latin-1", newline="") as f:
                return list(csv.DictReader(f, delimiter=";"))
        finally:
            rwlock.release_read()

    # -----------------------------
    # WRITE ALL (overwrite file)
    # -----------------------------
    def write_all(self, path, fieldnames, rows):
        path = os.path.abspath(path)
        rwlock = self._get_rwlock(path)

        # Exclusive lock
        rwlock.acquire_write()
        try:
            with open(path, "w", encoding="latin-1", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                    delimiter=";"
                )
                writer.writeheader()
                writer.writerows(rows)
        finally:
            rwlock.release_write()

    # -----------------------------
    # APPEND ROW
    # -----------------------------
    def append_row(self, path, fieldnames, row):
        path = os.path.abspath(path)
        rwlock = self._get_rwlock(path)

        # Exclusive lock
        rwlock.acquire_write()
        try:
            file_exists = os.path.exists(path)
            with open(path, "a", encoding="latin-1", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                    delimiter=";"
                )
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
        finally:
            rwlock.release_write()

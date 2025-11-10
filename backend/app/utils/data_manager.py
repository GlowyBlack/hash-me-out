import csv
import os
import threading
from typing import List, Dict
class CSVRepository:
    """Thread-safe CSV handler shared across all models."""
    _locks: Dict[str, threading.Lock] = {}

    def _get_lock(self, path: str) -> threading.Lock:
        if path not in self._locks:
            self._locks[path] = threading.Lock()
        return self._locks[path]

    def read_all(self, path: str) -> List[Dict]:
        """
        Reads all rows from a CSV file and returns them as a list of dictionaries.
        """
        if not os.path.exists(path):
            return []
        lock = self._get_lock(path)
        with lock, open(path, 'r', newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def write_all(self, path: str, fieldnames: List[str], rows: List[Dict]):
        """
        Overwrites the entire CSV file with the given rows.
        """
        lock = self._get_lock(path)
        with lock, open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def append_row(self, path: str, fieldnames: List[str], row: Dict):
        """
        Add a single row to the CSV file safely.
        """        
        file_exists = os.path.exists(path)
        lock = self._get_lock(path)
        with lock, open(path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

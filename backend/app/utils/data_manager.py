import csv
import os
import threading
from typing import List, Dict
"""
Thread Locking is to make sure that only one user action can read or write to a CSV file at a time.
For example, let's say we had 2 users trying to request at the same time. The first user to reach
the file gets a temporary "lock," allowing their request to write safely. The second user must
wait until the lock is released, at which point their request proceeds. This prevents both users
from writing at the same time, which could otherwise cause duplicate IDs, missing rows, or file
corruption. Once the first write is done, the second user's write runs normally, ensuring all
data stays consistent and in order.
"""

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
        If the file does not exist, returns an empty list instead of raising an error.
        """
        if not os.path.exists(path):
            return []
        lock = self._get_lock(path)
        with lock, open(path, 'r', newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def write_all(self, path: str, fieldnames: List[str], rows: List[Dict]):
        """
        Overwrites the entire CSV file with the given rows.
        This is used when we need to fully rewrite the file 
        (e.g., after deleting or reindexing so no jump in indexes).
        """
        lock = self._get_lock(path)
        with lock, open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def append_row(self, path: str, fieldnames: List[str], row: Dict):
        """
        Add a single row to the CSV file safely.
        - If the file does not exist, it creates the file and writes the header first.
        - Then, it appends the new row at the end.
        - Thread-safe: only one thread can write to a specific file at once.
        """        
        file_exists = os.path.exists(path)
        lock = self._get_lock(path)
        with lock, open(path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

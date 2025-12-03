import csv
import os
import threading
from typing import List, Dict
from app.repositories.base_repository import BaseRepository


class ReadWriteLock:
    def __init__(self):
        self._readers = 0
        self._writer = False
        self._lock = threading.Lock()
        self._read_ready = threading.Condition(self._lock)

    def acquire_read(self):
        with self._lock:
            while self._writer:
                self._read_ready.wait()
            self._readers += 1

    def release_read(self):
        with self._lock:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self):
        with self._lock:
            while self._writer or self._readers > 0:
                self._read_ready.wait()
            self._writer = True

    def release_write(self):
        with self._lock:
            self._writer = False
            self._read_ready.notify_all()


class CSVRepository(BaseRepository):
    """Thread-safe CSV handler with per-file read-write locks."""

    _rwlocks: Dict[str, ReadWriteLock] = {}
    _rwlocks_guard = threading.Lock()   # protects creation of locks

    def _get_rwlock(self, path: str) -> ReadWriteLock:
        path = os.path.abspath(path)
        with self._rwlocks_guard:
            if path not in self._rwlocks:
                self._rwlocks[path] = ReadWriteLock()
            return self._rwlocks[path]

    def read_all(self, path: str) -> List[Dict]:
        path = os.path.abspath(path)
        if not os.path.exists(path):
            return []

        rwlock = self._get_rwlock(path)
        rwlock.acquire_read()
        try:
            with open(path, 'r', newline = '', encoding = 'utf-8') as f:
                return list(csv.DictReader(f))
        finally:
            rwlock.release_read()

    def write_all(self, path: str, fieldnames: List[str], rows: List[Dict]):
        path = os.path.abspath(path)
        rwlock = self._get_rwlock(path)
        rwlock.acquire_write()
        try:
            with open(path, 'w', newline = '', encoding = 'utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        finally:
            rwlock.release_write()

    def append_row(self, path: str, fieldnames: List[str], row: Dict):
        path = os.path.abspath(path)
        rwlock = self._get_rwlock(path)
        rwlock.acquire_write()
        try:
            file_exists = os.path.exists(path)
            with open(path, 'a', newline = '', encoding = 'utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)
        finally:
            rwlock.release_write()

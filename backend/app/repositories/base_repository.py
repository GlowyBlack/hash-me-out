from typing import List, Dict
from abc import ABC, abstractmethod

class BaseRepository(ABC):
    @abstractmethod
    def read_all(self, path: str) -> List[Dict]: ...

    @abstractmethod
    def write_all(self, path: str, fieldnames: List[str], rows: List[Dict]): ...

    @abstractmethod
    def append_row(self, path: str, fieldnames: List[str], row: Dict): ...

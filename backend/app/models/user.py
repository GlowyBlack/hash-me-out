from typing import Optional
from readinglist import ReadingList


class User:
    def __init__(self, user_id: int, location: str, age: int, role: str):
        self.user_id = user_id
        self.location = location
        self.age = age
        self.role = role
        self.reading_lists: list[ReadingList] = []

    def add_reading_list(self, reading_list):
        self.reading_lists.append(reading_list)


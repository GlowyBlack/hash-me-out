from typing import Optional
from readinglist import ReadingList

class Profile:
    def __init__(self, email: str, username: str, password: str):
        self.email = email
        self.username = username
        self.password = password  # in production, hash the password

class User:
    def __init__(self, user_id: int, profile: Profile, location: str, age: int, role: str):
        self.user_id = user_id
        self.profile = profile
        self.location = location
        self.age = age
        self.role = role
        self.reading_lists: list[ReadingList] = []

    def add_reading_list(self, reading_list):
        self.reading_lists.append(reading_list)


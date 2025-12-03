import re

def validate_isbn(isbn: str) -> str:
    digits = "".join(ch for ch in isbn if ch.isdigit())
        
    if len(digits) not in (10, 13):
        raise ValueError("ISBN must contain exactly 10 or 13 digits.")
    return digits

def validate_list_name(name: str):
    letters = name.strip()
    if len(letters)<1:
        raise ValueError("Readinglist Name must be at least 1 letter.")
    
    return letters

def validate_comment(review: str):
    comment = review.strip()
    if len(comment)<8:
        raise ValueError("Review must be at least 8 characters.")
    
    return comment 

def validate_email(email: str):
    e = email.strip()
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(pattern, e):
        raise ValueError("Invalid email format. Please enter a valid email address.")

    return e

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

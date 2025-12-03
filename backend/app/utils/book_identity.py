import re

""" Patterns used to detect if a book title is part of a series """
SERIES_PATTERNS = [
    r"\bbook\s+\d+\b",
    r"\bbook\s+(one|two|three|four|five|six|seven|eight|nine|ten)\b",
    r"\bvolume\s+\d+\b",
    r"\bvol\.\s*\d+\b",
    r"\bpart\s+\d+\b",
    r"#\d+",
    r"\b(series|saga|chronicles)\b",
]

""" Normalize text for author/title comparisons """
def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()

    s = re.sub(r"\.", " ", s)

    s = re.sub(r"\s+", " ", s)

    return s
 
""" Normalize titles for identity matching (strip subtitles) """
def normalize_title_for_work(title: str) -> str:
    """
    Removes subtitles such as ': A Novel', '(Special Edition)',
    ': Book One', etc. to detect editions of the same underlying work.
    """
    if not title:
        return ""

    t = title.lower().strip()

    t = t.split(":", 1)[0]

    t = re.sub(r"\(.*?\)", "", t)

    t = re.sub(r"\s+", " ", t).strip()

    return t


""" Detect whether a book title indicates a series entry """
def is_series_title(title: str) -> bool:
    if not title:
        return False

    t = title.lower()
    for pattern in SERIES_PATTERNS:
        if re.search(pattern, t):
            return True

    return False


""" Determine if two books are the same underlying WORK """
def is_same_work(book_a: dict, book_b: dict) -> bool:
    """
    Returns True if two entries are essentially the same work/edition.
    Returns False if the second book is actually a SERIES book.
    """

    t1 = normalize_title_for_work(book_a.get("Book-Title", ""))
    t2 = normalize_title_for_work(book_b.get("Book-Title", ""))

    if t1 != t2:
        return False  # Different title → not same work

    if is_series_title(book_b.get("Book-Title", "")):
        return False

    # -------------------
    # Author identity check
    # -------------------
    a1 = normalize_text(book_a.get("Book-Author", ""))
    a2 = normalize_text(book_b.get("Book-Author", ""))

    if not a1 or not a2:
        return False

    # Last names must match
    ln1 = a1.split()[-1]
    ln2 = a2.split()[-1]
    if ln1 != ln2:
        return False

    # First initials must match
    if a1[0] != a2[0]:
        return False

    return True

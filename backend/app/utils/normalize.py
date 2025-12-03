import re

def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()

    # replace periods (.) between initials with a space
    s = re.sub(r"\.", " ", s)

    # collapse multiple spaces to single
    s = re.sub(r"\s+", " ", s)

    return s

"""
Negative + positive interaction weighting (final version)
"""

BASE_INTERACTION_WEIGHTS = {
    "reading_list_add": 3,    
    "comment": 5,
    "short_view": 1,           
    "long_view": 2,            
    "revisit": 2,
}


def rating_to_weight(rating: int) -> int:
    """A smooth negative-to-positive rating scale."""

    if rating <= 2:
        return -3 - (2 - rating)   # rating 1 → -4, rating 2 → -3
    if rating == 3:
        return -2
    if rating == 4:
        return -1
    if rating == 5:
        return 0
    if rating == 6:
        return 2
    if rating == 7:
        return 4
    if rating == 8:
        return 6
    if rating == 9:
        return 8
    return 10  # rating = 10

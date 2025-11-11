import pytest
from app.models.book import Book

@pytest.fixture
def sample_book():
    """Fixture providing a sample Book instance."""
    return Book(
        isbn="0195153448",
        book_title="Classical Mythology",
        author="Mark P. O. Morford",
        year_of_publication="2002",
        publisher="Oxford University Press",
        image_url_s="http://images.amazon.com/images/P/0195153448.01.THUMBZZZ.jpg",
        image_url_m="http://images.amazon.com/images/P/0195153448.01.MZZZZZZZ.jpg",
        image_url_l="http://images.amazon.com/images/P/0195153448.01.LZZZZZZZ.jpg",
    )

def test_to_api_dict(sample_book):
    """Check API dict conversion."""
    api_dict = sample_book.to_api_dict()

    assert api_dict["isbn"] == "0195153448"
    assert api_dict["book_title"] == "Classical Mythology"
    assert api_dict["author"] == "Mark P. O. Morford"
    assert "image_url_m" in api_dict
    assert api_dict["publisher"] == "Oxford University Press"
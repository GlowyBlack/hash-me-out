import pytest
from app.utils.search import search_books


def test_search_books_found():
    result = search_books("Nonexistent")
    assert len(result) == 1
    assert result == [{'isbn': '0156659751', 'title': 'The Nonexistent Knight and The Cloven Viscount', 
                      'author': 'Italo Calvino', 'year': '1977', 'publisher': 'Harcourt'}]

def test_search_books_found_multiple_result():
    result = search_books("Mark P. O. Morford")
    assert len(result) == 2
    assert result == [{'isbn': '0195153448', 'title': 'Classical Mythology', 'author': 'Mark P. O. Morford', 
                       'year': '2002', 'publisher': 'Oxford University Press'}, 
                      {'isbn': '0801319536', 'title': 'Classical Mythology', 'author': 'Mark P. O. Morford', 
                       'year': '1998', 'publisher': 'John Wiley & Sons'}]
    
def test_search_book_no_result():
    result = search_books("Percy Jackson")
    assert len(result) == 0
    assert result == []

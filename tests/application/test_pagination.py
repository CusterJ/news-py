import sys
sys.path.append('/home/max/Documents/Projects/news-py')

from application.pagination import get_pagination

def test_zero_total():
    result = get_pagination(1, 10, 0)
    assert result == []

def test_less_than_take():
    result = get_pagination(1, 10, 5)
    assert result == []

def test_two_pages():
    result = get_pagination(1, 10, 20)
    assert result == ['1', '2']

def test_first_page_ten_pages():
    result = get_pagination(1, 10, 100)
    assert result == ['1', '2', '3', '4', '10']

def test_last_page_ten_pages():
    result = get_pagination(10, 10, 100)
    assert result == ['1', '6', '7', '8', '9', '10']

def test_middle_page_ten_pages():
    result = get_pagination(5, 10, 100)
    assert result == ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

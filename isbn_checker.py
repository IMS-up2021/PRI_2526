import re


def is_isbn_13_valid(isbn):
    """
    Check if the provided ISBN-13 number is valid.
    """
    if len(isbn) != 13 or not isbn.isdigit():
        return False

    total = 0
    for i, digit in enumerate(isbn):
        n = int(digit)
        if i % 2 == 0:
            total += n
        else:
            total += n * 3

    return total % 10 == 0

def is_isbn_10_valid(isbn):
    """
    Check if the provided ISBN-10 number is valid.
    """
    if len(isbn) != 10 or not isbn[:-1].isdigit() or (isbn[-1] not in '0123456789X'):
        return False

    total = 0
    for i, digit in enumerate(isbn):
        if digit == 'X':
            n = 10
        else:
            n = int(digit)
        total += n * (10 - i)

    return total % 11 == 0

def is_isbn_valid(isbn):
    """
    Determine if the provided ISBN (either ISBN-10 or ISBN-13) is valid.
    """
    isbn = isbn.replace("-", "").replace(" ", "")
    if len(isbn) == 13:
        return is_isbn_13_valid(isbn)
    elif len(isbn) == 10:
        return is_isbn_10_valid(isbn)
    else:
        return False
    

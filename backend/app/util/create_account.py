
import re

def valid_email(email):
    pattern = r'^[^@]+@[^@]+\.[a-zA-Z]{2,4}$'
    return re.match(pattern, email) is not None


def valid_password():
    pass

def create_account(email, password):
    valid_email(email)
    valid_password(password)
    

import string
from secrets import choice

def generate_custom_id(length=11):
    alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(choice(alphabet) for _ in range(length))


import random
import string

def generate_custom_id(length=11):
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=length))
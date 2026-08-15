# zodiac_utils.py
from constants import ZODIAC_SIGNS_EN

def sign_to_number(sign_name):
    return ZODIAC_SIGNS_EN.index(sign_name) + 1

def number_to_sign(num):
    return ZODIAC_SIGNS_EN[num - 1]

def compute_nth_sign(from_sign_num, n):
    return ((from_sign_num - 1 + (n - 1)) % 12) + 1

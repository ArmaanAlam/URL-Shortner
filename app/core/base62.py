BASE62_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(BASE62_ALPHABET)

def encode_base62(num: int) -> str:
    """
    Bijective Base62 encoding:
    Converts a positive integer into a URL-safe Base62 string [0-9, a-z, A-Z].
    """
    if num == 0:
        return BASE62_ALPHABET[0]
    digits = []
    while num > 0:
        remainder = num % BASE
        digits.append(BASE62_ALPHABET[remainder])
        num //= BASE
    digits.reverse()
    return "".join(digits)

def decode_base62(key: str) -> int:
    """
    Converts a Base62 string back into its original integer ID.
    """
    num = 0
    for char in key:
        idx = BASE62_ALPHABET.find(char)
        if idx == -1:
            raise ValueError(f"Invalid character in Base62 string: {char}")
        num = num * BASE + idx
    return num

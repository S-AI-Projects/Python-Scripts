import random as rr
import string as ss

characters = ['@', '#', '$', '%', '&', '?']


def generate_password(pass_len):
    """
    Generate a password with uppercase, lowercase, digits, and special characters.

    Contract:
    - Precondition: pass_len (int) >= 4 (smallest valid input established by logic at lines 15-23 and main() line 64).
    - Returns: tuple (pass_word: str, total_cap: int, total_low: int, total_nums: int, total_symbols: int)
      where:
        len(pass_word) == pass_len
        total_cap >= 1
        total_low >= 1
        total_nums >= 1
        total_symbols >= 1
        total_cap + total_low + total_nums + total_symbols == pass_len
    - Mutation: Does not mutate the module-level `characters` anchor (line 4) or any input object.
    """
    # Initialize counters
    total_nums = 0
    total_symbols = 0
    total_cap = 0
    total_low = 0

    # Ensure at least one of each type
    tempx = rr.randint(2, max(2, pass_len - 2))  # at least 2 letters
    remaining = pass_len - tempx

    tempy = rr.randint(1, max(1, remaining - 1))  # at least 1 number
    remaining -= tempy
    total_nums = tempy

    tempz = remaining  # rest goes to special characters
    total_symbols = tempz

    # Generate password
    pass_word = ''

    # Add alphabets
    num_cap = rr.randint(1, tempx - 1)  # at least 1 uppercase
    num_low = tempx - num_cap  # rest lowercase
    total_cap = num_cap
    total_low = num_low

    # Add capitals
    pass_word += ''.join(chr(rr.randint(65, 90)) for _ in range(num_cap))

    # Add lowercase
    pass_word += ''.join(chr(rr.randint(97, 122)) for _ in range(num_low))

    # Add numbers
    pass_word += ''.join(str(rr.randint(0, 9)) for _ in range(tempy))

    # Add special characters
    pass_word += ''.join(rr.choice(characters) for _ in range(tempz))

    return pass_word, total_cap, total_low, total_nums, total_symbols


def shuffle_(alpha):
    str_temp = list(alpha)
    rr.shuffle(str_temp)
    return ''.join(str_temp)


def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


def main():
    pass_len = int(input('How lengthy do you want your password to be : '))

    if pass_len < 4:
        print("Password length must be at least 4 characters")
        return

    pass_word, total_cap, total_low, total_nums, total_symbols = generate_password(pass_len)

    # Shuffle multiple times
    final_pass = colored(200, 200, 50, shuffle_(shuffle_(shuffle_(pass_word))))

    result = """
Generate Password Summary:

Character Uppercase : {0}
Character Lowercase : {1}
Numbers : {2}
Symbols : {3}

Your computer generated password is:
{4}
""".format(total_cap, total_low, total_nums, total_symbols, final_pass)

    print(result)


if __name__ == "__main__":
    main()
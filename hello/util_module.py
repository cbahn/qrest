# Utilites functions used by app.py
import random


class Util(object):
    def generate_random_code(length):

        # Define the character set, excluding the specified characters
        char_set = "2346789BCDEFGHJKMNPQRTVWXYZ"  # Avoided characters: I, L, 1, 0, O, A

        random_code = ''.join(random.choice(char_set) for _ in range(length))
        return random_code


    def generate_new_userID():
        return 'A' + Util.generate_random_code(6)

    def generate_new_locationID():
        return 'L' + Util.generate_random_code(6)
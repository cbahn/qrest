# Utilites functions used by app.py
import random

class Util(object):

    def load_words(filename):
        words = []
        with open(filename, "r", encoding="utf-8") as file:
            words = [line.strip() for line in file if line.strip()]  # Read and clean words
        return words

    wordlist = None

    def generate_random_code(length):

        # Define the character set, excluding the specified characters
        char_set = "2346789BCDEFGHJKMNPQRTVWXYZ"  # Avoided characters: I, L, 1, 0, O, A, S

        random_code = ''.join(random.choice(char_set) for _ in range(length))
        return random_code

    def generate_session_code():
        return 'S' + Util.generate_random_code(15)

    def generate_new_userID():
        return 'A' + Util.generate_random_code(6)

    def generate_new_locationID():
        return 'L' + Util.generate_random_code(8)
    
    def generate_new_glyphID():
        return 'G' + Util.generate_random_code(8)
    
    def generate_new_localStorageData():
        if Util.wordlist is None:
           Util.wordlist = Util.load_words("marino/static/words.txt")

        words = random.sample(Util.wordlist, 3)
        return f"{words[0]}-{words[1]}-{words[2]}"

    def sanitize(data):
        # I am having trouble finding documentation related to what type of input
        #  sanitation is needed for pymongo queries. I'll do a basic character
        #  filter here and hope it's good enough.
        banned_chars = r'{},$;"'
        return data.translate(str.maketrans( {char: None for char in banned_chars} ))
import random

def generate_random_code(length=8):
    # Define the character set, excluding the specified characters
    char_set = "2346789ABCDEFGHJKMNPQRTVWXYZ"  # Avoided characters: I, L, 1, 0, O
    
    # Generate a random code of the specified length
    random_code = ''.join(random.choice(char_set) for _ in range(length))
    
    return random_code

# Example usage
for _ in range(10):
    code = generate_random_code()
    print(code)
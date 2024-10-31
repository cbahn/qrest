from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Random import get_random_bytes
import base64

class DecryptionError(Exception):
    """Custom exception for decryption errors."""
    pass

class CryptoManager:
    def __init__(self):
        self.key = None

    def random_key():
        """
        Prints a random 32byte base64 encoded key.
        """
        return base64.b64encode(get_random_bytes(32)).decode('utf-8')

    def init(self, key):
        """
        Initializes the cryptographic key.

        Args:
            key (bytes, optional): The encryption key in base64.
        """
        self.key = base64.b64decode(key)

    def encrypt_message(self, plaintext):
        """
        Encrypts a plaintext message using ChaCha20-Poly1305.

        Args:
            plaintext (str): The message to encrypt.

        Returns:
            str: The encrypted message encoded in base64.

        Raises:
            ValueError: If the encryption key has not been set.
        """
        if self.key is None:
            raise ValueError("Encryption key has not been set. Call init() first.")
        
        # Generate a random nonce (12 bytes)
        nonce = get_random_bytes(12)
        
        # Create a ChaCha20-Poly1305 cipher object with the key and nonce
        cipher = ChaCha20_Poly1305.new(key=self.key, nonce=nonce)
        
        # Encrypt the plaintext and generate the MAC tag
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
        
        # Concatenate nonce, tag, and ciphertext, and then encode in base64
        encrypted_data = nonce + tag + ciphertext
        encrypted_base64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        return encrypted_base64

    def decrypt_message(self, encrypted_base64):
        """
        Decrypts a base64 encoded message using ChaCha20-Poly1305.

        Args:
            encrypted_base64 (str): The encrypted message encoded in base64.

        Returns:
            str: The decrypted plaintext message.

        Raises:
            DecryptionError: If decryption fails or message authentication fails.
            ValueError: If the decryption key has not been set.
        """
        if self.key is None:
            raise ValueError("Decryption key has not been set. Call init() first.")
        
        # Decode the base64 data
        encrypted_data = base64.b64decode(encrypted_base64)
        
        # Extract nonce, tag, and ciphertext
        nonce = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        # Create a ChaCha20-Poly1305 cipher object with the key and nonce
        cipher = ChaCha20_Poly1305.new(key=self.key, nonce=nonce)
        
        # Decrypt and verify the ciphertext
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            return plaintext.decode('utf-8')
        except ValueError:
            raise DecryptionError("Decryption failed or message authentication failed.")


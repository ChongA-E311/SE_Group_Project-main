from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from Crypto.Util.number import getPrime
from os import urandom
import base64


class HybridEncryptor:
    """
    Class for encrypting messages using AES and securing the AES key with RSA encryption.
    If no keys are provided, the object generates new RSA and AES keys.
    """

    def __init__(self, encrypted_aes=None, combined_rsa_bytes=None):

        if combined_rsa_bytes is None:
            self.prime1, self.prime2 = getPrime(512), getPrime(512)
            self.generate_rsa_key(self.prime1, self.prime2)
        else:
            self.rsa_key = self.bytes_to_rsa_key(combined_rsa_bytes)

        if encrypted_aes is None:
            self.aes_key = urandom(32)
        else:
            self.aes_key = self.decrypt_rsa(encrypted_aes)

    def bytes_to_rsa_key(self, combined_rsa_bytes):
        """
        Method to convert the database stored bytes of the RSA key to the original structure, done on initialization
        """
        # Finds the length of the public exponent (2 bytes)
        public_exponent_length = int.from_bytes(combined_rsa_bytes[:2], 'big')
        public_exponent_bytes = combined_rsa_bytes[2:2 + public_exponent_length]

        # Finds the length of the modulus (2 bytes)
        modulus_length = int.from_bytes(combined_rsa_bytes[2 + public_exponent_length:4 + public_exponent_length],'big')
        modulus_bytes = combined_rsa_bytes[4 + public_exponent_length:4 + public_exponent_length + modulus_length]

        # Leftover bytes are the private exponent
        private_exponent_bytes = combined_rsa_bytes[4 + public_exponent_length + modulus_length:]

        # Convert bytes back to integers
        public_exponent = int.from_bytes(public_exponent_bytes, 'big')
        modulus = int.from_bytes(modulus_bytes, 'big')
        private_exponent = int.from_bytes(private_exponent_bytes, 'big')

        # Return RSA key
        return ((public_exponent, modulus), private_exponent)


    def rsa_key_to_bytes(self):
        """
        Method to convert the original structure of the RSA key to bytes to be stored in the database
        """
        # Separates public and private keys
        public_exponent, modulus = self.rsa_key[0]
        private_exponent = self.rsa_key[1]

        # Converts public and private keys to bytes
        public_exponent_bytes = public_exponent.to_bytes((public_exponent.bit_length() + 7) // 8, 'big')
        modulus_bytes = modulus.to_bytes((modulus.bit_length() + 7) // 8, 'big')
        private_exponent_bytes = private_exponent.to_bytes((private_exponent.bit_length() + 7) // 8, 'big')

        # Combines everything whilst keeping track of the lengths
        return (len(public_exponent_bytes).to_bytes(2, 'big') + public_exponent_bytes +
                len(modulus_bytes).to_bytes(2, 'big') + modulus_bytes + private_exponent_bytes)

    def generate_rsa_key(self, prime1, prime2):
        """
        Generate RSA key pair using given/generated primes and a common exponent (e = 65537).
        """
        n = prime1 * prime2
        eulers_phi = (prime1 - 1) * (prime2 - 1)
        e = 65537
        d = pow(e, -1, eulers_phi)
        self.rsa_key = (e, n), d  # Public and private keys

    def encrypt_aes(self, message):
        """
        Encrypt message with AES and return encrypted message, encrypted AES key, and RSA key in a list.
        """
        # Introduces randomness to encryptor (random initialization vector)
        iv = urandom(16)

        # Creates cipher and encryptor objects for AES (CBC mode)
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()

        # Apply PKCS7 padding
        padder = padding.PKCS7(128).padder()
        padded_message = padder.update(message.encode()) + padder.finalize()

        # Encrypts padded message with AES (update is for chunking message)
        encrypted_message = encryptor.update(padded_message) + encryptor.finalize()

        # Encrypt the AES key
        encrypted_aes = self.encrypt_rsa(self.aes_key)

        # Encodes encrypted message with base64 bytes then decodes it to a string (to be able to be used by JSON)
        return [base64.b64encode(iv + encrypted_message).decode(), encrypted_aes.to_bytes((encrypted_aes.bit_length() + 7) // 8, 'big'), self.rsa_key_to_bytes()]

    def encrypt_rsa(self, aes_key):
        """
        Encrypt AES key using RSA, return encrypted AES key.
        """
        # Retrieves public key
        e, n = self.rsa_key[0]

        # Converts AES key to integer
        aes_key_int = int.from_bytes(aes_key, 'big')
        return pow(aes_key_int, e, n)

    def decrypt_aes(self, encrypted_message):
        """
        Decrypt message using AES and return decrypted message.
        """
        # Decodes encrypted message from base64
        encrypted_message = base64.b64decode(encrypted_message)

        # Splits encrypted message into initialization vector and encrypted message
        iv, encrypted_message = encrypted_message[:16], encrypted_message[16:]

        # Creates cipher and decryptor objects for AES
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()

        # Decrypts encrypted message
        padded_message = decryptor.update(encrypted_message) + decryptor.finalize()

        # Remove PKCS7 padding
        unpadder = padding.PKCS7(128).unpadder()
        message = unpadder.update(padded_message) + unpadder.finalize()
        return message.decode()

    def decrypt_rsa(self, encrypted_aes_bytes):
        """
        Decrypt AES key using RSA, return decrypted AES key.
        """
        encrypted_aes = int.from_bytes(encrypted_aes_bytes, 'big')
        # Retrieves private key and modulus (n)
        d = self.rsa_key[1]
        n = self.rsa_key[0][1]

        # Decrypt AES key and converts back to bytes
        aes_key_int = pow(encrypted_aes, d, n)
        aes_key = aes_key_int.to_bytes((n.bit_length() + 7) // 8, 'big')

        # Ensure AES key is exactly 32 bytes
        return aes_key[-32:]

#encryptor1 = HybridEncryptor()
#message = "Hello, this is a secret message!"
#encrypted_message, encrypted_aes, rsa_key = encryptor1.encrypt_aes(message)
#message = "HiHiHiHi"
#encrypted_message2 = encryptor1.encrypt_aes(message)[0]
#encryptor2 = HybridEncryptor(encrypted_aes, rsa_key)
#decrypted_message = encryptor2.decrypt_aes(encrypted_message)
#decrypted_message2 = encryptor2.decrypt_aes(encrypted_message2)
#print("Decrypted Message:", decrypted_message)
#print("Decrypted Message 2:", decrypted_message2)
#print(encrypted_aes)
#print(rsa_key)

"""
References:

https://cryptography.io/en/latest/hazmat/primitives/ciphers/
https://cryptography.io/en/latest/hazmat/primitives/padding/
https://www.youtube.com/watch?v=kD6Pc3yu5e8
https://www.geeksforgeeks.org/advanced-encryption-standard-aes/
https://onboardbase.com/blog/aes-encryption-decryption/
"""
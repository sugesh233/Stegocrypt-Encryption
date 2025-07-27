from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
import base64

def generate_keys(key_size=2048):
    """Generate a new pair of RSA keys
    
    Args:
        key_size (int): Size of the RSA key in bits
        
    Returns:
        tuple: (private_key, public_key)
    """
    key = RSA.generate(key_size)
    private_key = key
    public_key = key.publickey()
    
    return private_key, public_key

def encrypt_text(plaintext, public_key):
    """Encrypt text using RSA public key
    
    Args:
        plaintext (str): Text to encrypt
        public_key (RsaKey): RSA public key
        
    Returns:
        str: Base64 encoded encrypted text
    """
    cipher = PKCS1_OAEP.new(public_key)
    
    # Convert text to bytes if it's not already
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')
    
    # For RSA encryption, we need to chunk the message if it's larger than the key size
    key_length_bytes = public_key.size_in_bytes()
    max_chunk_size = key_length_bytes - 42  # PKCS#1 OAEP has a 42-byte overhead
    
    chunks = [plaintext[i:i+max_chunk_size] for i in range(0, len(plaintext), max_chunk_size)]
    encrypted_chunks = []
    
    for chunk in chunks:
        encrypted_chunk = cipher.encrypt(chunk)
        encrypted_chunks.append(base64.b64encode(encrypted_chunk).decode('utf-8'))
    
    # Join encrypted chunks with a delimiter
    return "|".join(encrypted_chunks)

def decrypt_text(encrypted_text, private_key):
    """Decrypt text using RSA private key
    
    Args:
        encrypted_text (str): Base64 encoded encrypted text
        private_key (RsaKey): RSA private key
        
    Returns:
        str: Decrypted text
    """
    cipher = PKCS1_OAEP.new(private_key)
    
    # Split the encrypted text into chunks
    encrypted_chunks = encrypted_text.split("|")
    decrypted_chunks = []
    
    for chunk in encrypted_chunks:
        encrypted_data = base64.b64decode(chunk)
        decrypted_chunk = cipher.decrypt(encrypted_data)
        decrypted_chunks.append(decrypted_chunk)
    
    # Join all chunks and decode as UTF-8
    return b''.join(decrypted_chunks).decode('utf-8')

def export_keys(private_key, public_key):
    """Export RSA keys to a dictionary for storage
    
    Args:
        private_key (RsaKey): RSA private key
        public_key (RsaKey): RSA public key
        
    Returns:
        dict: Dictionary containing exported keys
    """
    export_data = {
        'private_key': private_key.export_key().decode('utf-8'),
        'public_key': public_key.export_key().decode('utf-8')
    }
    
    return export_data

def import_keys(keys_data):
    """Import RSA keys from exported dictionary
    
    Args:
        keys_data (dict): Dictionary containing exported keys
        
    Returns:
        tuple: (private_key, public_key)
    """
    private_key = RSA.import_key(keys_data['private_key'])
    public_key = RSA.import_key(keys_data['public_key'])
    
    return private_key, public_key

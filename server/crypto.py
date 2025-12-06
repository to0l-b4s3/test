import base64, hashlib, os, json, time, random
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import zlib, lzma

class CryptoHandler:
    def __init__(self, master_key=None):
        self.master_key = master_key or self.generate_master_key()
        self.fernet = Fernet(self.master_key)
        
        # AES key derived from master key
        self.aes_key = self.derive_aes_key(self.master_key)
        
        # RSA key pair for asymmetric encryption
        self.rsa_key = self.generate_rsa_keys()
        
        # Session keys cache
        self.session_keys = {}
    
    def generate_master_key(self):
        """Generate a master encryption key."""
        # Use system randomness combined with time
        random_bytes = os.urandom(32) + str(time.time()).encode() + str(random.getrandbits(256)).encode()
        return base64.urlsafe_b64encode(hashlib.sha256(random_bytes).digest())
    
    def derive_aes_key(self, master_key, salt=None, length=32):
        """Derive AES key from master key."""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            iterations=100000,
        )
        
        key = kdf.derive(master_key)
        return key
    
    def generate_rsa_keys(self, key_size=2048):
        """Generate RSA key pair."""
        key = RSA.generate(key_size)
        return {
            'private': key.export_key(),
            'public': key.publickey().export_key(),
            'key': key
        }
    
    def encrypt_fernet(self, data):
        """Encrypt data using Fernet (symmetric)."""
        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode()
        
        return self.fernet.encrypt(data)
    
    def decrypt_fernet(self, encrypted_data):
        """Decrypt Fernet encrypted data."""
        try:
            decrypted = self.fernet.decrypt(encrypted_data)
            
            # Try to parse as JSON, otherwise return string
            try:
                return json.loads(decrypted.decode())
            except:
                return decrypted.decode()
                
        except Exception as e:
            return None
    
    def encrypt_aes(self, data, iv=None):
        """Encrypt data using AES-GCM."""
        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode()
        
        if iv is None:
            iv = get_random_bytes(12)  # 96-bit IV for GCM
        
        cipher = AES.new(self.aes_key, AES.MODE_GCM, iv=iv, mac_len=16)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        
        # Return IV + ciphertext + tag
        return base64.b64encode(iv + ciphertext + tag).decode()
    
    def decrypt_aes(self, encrypted_data):
        """Decrypt AES-GCM encrypted data."""
        try:
            encrypted_data = base64.b64decode(encrypted_data)
            
            iv = encrypted_data[:12]
            ciphertext = encrypted_data[12:-16]
            tag = encrypted_data[-16:]
            
            cipher = AES.new(self.aes_key, AES.MODE_GCM, iv=iv)
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted.decode())
            except:
                return decrypted.decode()
                
        except Exception as e:
            return None
    
    def encrypt_rsa(self, data, public_key=None):
        """Encrypt data using RSA (asymmetric)."""
        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode()
        
        # Use provided public key or our own
        if public_key is None:
            public_key = self.rsa_key['public']
        
        rsa_key = RSA.import_key(public_key)
        cipher = PKCS1_OAEP.new(rsa_key)
        
        # RSA can only encrypt small amounts of data
        # For larger data, we encrypt a symmetric key
        if len(data) > 100:  # Rough limit for RSA-2048
            # Generate a random AES key for this encryption
            session_key = get_random_bytes(32)
            iv = get_random_bytes(16)
            
            # Encrypt the data with AES
            cipher_aes = AES.new(session_key, AES.MODE_CBC, iv)
            padded_data = self.pad(data)
            ciphertext = cipher_aes.encrypt(padded_data)
            
            # Encrypt the session key with RSA
            encrypted_key = cipher.encrypt(session_key)
            
            # Return IV + encrypted key + ciphertext
            result = iv + encrypted_key + ciphertext
        else:
            # Small data, encrypt directly
            result = cipher.encrypt(data)
        
        return base64.b64encode(result).decode()
    
    def decrypt_rsa(self, encrypted_data, private_key=None):
        """Decrypt RSA encrypted data."""
        try:
            encrypted_data = base64.b64decode(encrypted_data)
            
            # Use provided private key or our own
            if private_key is None:
                private_key = self.rsa_key['private']
            
            rsa_key = RSA.import_key(private_key)
            cipher = PKCS1_OAEP.new(rsa_key)
            
            # Check if it's a hybrid encryption (AES key encrypted with RSA)
            if len(encrypted_data) > 256:  # RSA-2048 ciphertext size is 256 bytes
                # Hybrid encryption: IV (16) + encrypted key (256) + ciphertext
                iv = encrypted_data[:16]
                encrypted_key = encrypted_data[16:272]
                ciphertext = encrypted_data[272:]
                
                # Decrypt the AES key
                session_key = cipher.decrypt(encrypted_key)
                
                # Decrypt the data with AES
                cipher_aes = AES.new(session_key, AES.MODE_CBC, iv)
                decrypted = cipher_aes.decrypt(ciphertext)
                decrypted = self.unpad(decrypted)
            else:
                # Direct RSA encryption
                decrypted = cipher.decrypt(encrypted_data)
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted.decode())
            except:
                return decrypted.decode()
                
        except Exception as e:
            return None
    
    def pad(self, data):
        """PKCS7 padding for AES-CBC."""
        block_size = AES.block_size
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length]) * padding_length
        return data + padding
    
    def unpad(self, data):
        """Remove PKCS7 padding."""
        padding_length = data[-1]
        return data[:-padding_length]
    
    def hybrid_encrypt(self, data, recipient_public_key=None):
        """Hybrid encryption: AES for data, RSA for AES key."""
        # Generate random session key
        session_key = get_random_bytes(32)
        iv = get_random_bytes(16)
        
        # Encrypt data with AES
        cipher_aes = AES.new(session_key, AES.MODE_CBC, iv)
        padded_data = self.pad(data.encode() if isinstance(data, str) else data)
        ciphertext = cipher_aes.encrypt(padded_data)
        
        # Encrypt session key with RSA
        if recipient_public_key is None:
            recipient_public_key = self.rsa_key['public']
        
        rsa_key = RSA.import_key(recipient_public_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        encrypted_key = cipher_rsa.encrypt(session_key)
        
        # Package everything
        package = {
            'iv': base64.b64encode(iv).decode(),
            'encrypted_key': base64.b64encode(encrypted_key).decode(),
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'algorithm': 'AES-256-CBC/RSA-2048-OAEP',
            'timestamp': time.time()
        }
        
        return package
    
    def hybrid_decrypt(self, package, private_key=None):
        """Decrypt hybrid encrypted package."""
        try:
            iv = base64.b64decode(package['iv'])
            encrypted_key = base64.b64decode(package['encrypted_key'])
            ciphertext = base64.b64decode(package['ciphertext'])
            
            # Decrypt session key
            if private_key is None:
                private_key = self.rsa_key['private']
            
            rsa_key = RSA.import_key(private_key)
            cipher_rsa = PKCS1_OAEP.new(rsa_key)
            session_key = cipher_rsa.decrypt(encrypted_key)
            
            # Decrypt data
            cipher_aes = AES.new(session_key, AES.MODE_CBC, iv)
            decrypted = cipher_aes.decrypt(ciphertext)
            decrypted = self.unpad(decrypted)
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted.decode())
            except:
                return decrypted.decode()
                
        except Exception as e:
            return None
    
    def compress_encrypt(self, data, compression='zlib'):
        """Compress then encrypt data."""
        # Compress
        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode()
        
        if compression == 'zlib':
            compressed = zlib.compress(data, level=9)
        elif compression == 'lzma':
            compressed = lzma.compress(data)
        else:
            compressed = data
        
        # Encrypt
        encrypted = self.encrypt_aes(compressed)
        
        return {
            'encrypted': encrypted,
            'compression': compression,
            'original_size': len(data),
            'compressed_size': len(compressed)
        }
    
    def decrypt_decompress(self, package):
        """Decrypt then decompress data."""
        try:
            # Decrypt
            decrypted = self.decrypt_aes(package['encrypted'])
            if decrypted is None:
                return None
            
            # Decompress
            if package.get('compression') == 'zlib':
                decompressed = zlib.decompress(decrypted)
            elif package.get('compression') == 'lzma':
                decompressed = lzma.decompress(decrypted)
            else:
                decompressed = decrypted
            
            # Try to parse as JSON
            try:
                return json.loads(decompressed.decode())
            except:
                return decompressed.decode()
                
        except Exception as e:
            return None
    
    def generate_session_key(self, session_id):
        """Generate a unique session key."""
        # Combine master key with session ID and timestamp
        seed = self.master_key + session_id.encode() + str(time.time()).encode()
        session_key = hashlib.sha256(seed).digest()
        
        self.session_keys[session_id] = {
            'key': session_key,
            'created': time.time(),
            'expires': time.time() + 3600  # 1 hour expiration
        }
        
        return base64.b64encode(session_key).decode()
    
    def get_session_key(self, session_id):
        """Get session key if valid."""
        if session_id in self.session_keys:
            session = self.session_keys[session_id]
            if time.time() < session['expires']:
                return session['key']
            else:
                # Expired, remove it
                del self.session_keys[session_id]
        
        return None
    
    def encrypt_with_session(self, session_id, data):
        """Encrypt data with session key."""
        session_key = self.get_session_key(session_id)
        if not session_key:
            return None
        
        # Use session key for AES encryption
        iv = get_random_bytes(12)
        cipher = AES.new(session_key, AES.MODE_GCM, iv=iv, mac_len=16)
        
        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode()
        
        ciphertext, tag = cipher.encrypt_and_digest(data)
        
        return base64.b64encode(iv + ciphertext + tag).decode()
    
    def decrypt_with_session(self, session_id, encrypted_data):
        """Decrypt data with session key."""
        session_key = self.get_session_key(session_id)
        if not session_key:
            return None
        
        try:
            encrypted_data = base64.b64decode(encrypted_data)
            
            iv = encrypted_data[:12]
            ciphertext = encrypted_data[12:-16]
            tag = encrypted_data[-16:]
            
            cipher = AES.new(session_key, AES.MODE_GCM, iv=iv)
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted.decode())
            except:
                return decrypted.decode()
                
        except Exception as e:
            return None
    
    def rotate_keys(self):
        """Rotate encryption keys (for forward secrecy)."""
        # Generate new master key
        old_key = self.master_key
        self.master_key = self.generate_master_key()
        self.fernet = Fernet(self.master_key)
        
        # Derive new AES key
        self.aes_key = self.derive_aes_key(self.master_key)
        
        # Generate new RSA keys
        self.rsa_key = self.generate_rsa_keys()
        
        # Clear session keys
        self.session_keys.clear()
        
        return {
            'old_key': base64.b64encode(old_key).decode()[:32] + '...',
            'new_key': base64.b64encode(self.master_key).decode()[:32] + '...',
            'timestamp': time.time()
        }
    
    def get_public_key(self):
        """Get public key for asymmetric encryption."""
        return self.rsa_key['public'].decode()
    
    def get_key_fingerprint(self):
        """Get fingerprint of master key."""
        return hashlib.sha256(self.master_key).hexdigest()[:16]
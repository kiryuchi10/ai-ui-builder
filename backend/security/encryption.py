"""
End-to-end encryption implementation for AI UI Builder
Provides secure data protection and API key management
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import secrets
import logging

logger = logging.getLogger(__name__)

class EncryptionManager:
    """Handles all encryption/decryption operations"""
    
    def __init__(self):
        self.master_key = self._get_or_create_master_key()
        self.fernet = Fernet(self.master_key)
    
    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key"""
        key_file = "backend/security/.master_key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new master key
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict permissions
            logger.info("Generated new master encryption key")
            return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def hash_password(self, password: str, salt: bytes = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = os.urandom(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key).decode(), base64.urlsafe_b64encode(salt).decode()
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify password against hash"""
        try:
            salt_bytes = base64.urlsafe_b64decode(salt.encode())
            expected_hash, _ = self.hash_password(password, salt_bytes)
            return expected_hash == hashed
        except Exception:
            return False

class APIKeyManager:
    """Secure API key management"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption = encryption_manager
        self.api_keys = {}
    
    def store_api_key(self, service: str, api_key: str, user_id: str) -> str:
        """Store encrypted API key"""
        try:
            encrypted_key = self.encryption.encrypt_data(api_key)
            key_id = self._generate_key_id()
            
            # Store in database (implementation depends on your DB choice)
            self._save_to_database(key_id, service, encrypted_key, user_id)
            
            logger.info(f"API key stored for service: {service}")
            return key_id
        except Exception as e:
            logger.error(f"Failed to store API key: {e}")
            raise
    
    def retrieve_api_key(self, key_id: str, user_id: str) -> str:
        """Retrieve and decrypt API key"""
        try:
            encrypted_key = self._get_from_database(key_id, user_id)
            if not encrypted_key:
                raise ValueError("API key not found")
            
            return self.encryption.decrypt_data(encrypted_key)
        except Exception as e:
            logger.error(f"Failed to retrieve API key: {e}")
            raise
    
    def rotate_api_key(self, key_id: str, new_api_key: str, user_id: str) -> bool:
        """Rotate API key"""
        try:
            encrypted_key = self.encryption.encrypt_data(new_api_key)
            self._update_in_database(key_id, encrypted_key, user_id)
            logger.info(f"API key rotated: {key_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to rotate API key: {e}")
            return False
    
    def _generate_key_id(self) -> str:
        """Generate unique key ID"""
        return secrets.token_urlsafe(32)
    
    def _save_to_database(self, key_id: str, service: str, encrypted_key: str, user_id: str):
        """Save encrypted key to database"""
        # Implementation depends on your database choice
        # This is a placeholder for the actual database operation
        pass
    
    def _get_from_database(self, key_id: str, user_id: str) -> str:
        """Get encrypted key from database"""
        # Implementation depends on your database choice
        # This is a placeholder for the actual database operation
        pass
    
    def _update_in_database(self, key_id: str, encrypted_key: str, user_id: str):
        """Update encrypted key in database"""
        # Implementation depends on your database choice
        # This is a placeholder for the actual database operation
        pass

class DataAnonymizer:
    """Data anonymization for compliance"""
    
    @staticmethod
    def anonymize_email(email: str) -> str:
        """Anonymize email address"""
        if '@' not in email:
            return "***@***.***"
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            anonymized_local = '*' * len(local)
        else:
            anonymized_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            anonymized_domain = '*' * len(domain_parts[0]) + '.' + domain_parts[-1]
        else:
            anonymized_domain = '*' * len(domain)
        
        return f"{anonymized_local}@{anonymized_domain}"
    
    @staticmethod
    def anonymize_ip(ip: str) -> str:
        """Anonymize IP address"""
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.***"
        return "***.***.***.*"
    
    @staticmethod
    def anonymize_user_data(data: dict) -> dict:
        """Anonymize user data for logging/analytics"""
        anonymized = data.copy()
        
        if 'email' in anonymized:
            anonymized['email'] = DataAnonymizer.anonymize_email(anonymized['email'])
        
        if 'ip_address' in anonymized:
            anonymized['ip_address'] = DataAnonymizer.anonymize_ip(anonymized['ip_address'])
        
        # Remove sensitive fields
        sensitive_fields = ['password', 'api_key', 'token', 'secret']
        for field in sensitive_fields:
            if field in anonymized:
                anonymized[field] = '***REDACTED***'
        
        return anonymized

# Global instances
encryption_manager = EncryptionManager()
api_key_manager = APIKeyManager(encryption_manager)
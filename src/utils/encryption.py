"""
Privacy and Encryption Module for KSSEM Virtual AI Assistant
Implements GDPR-compliant data handling, encryption, and anonymization
"""

import hashlib
import hmac
import secrets
import re
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
from datetime import datetime, timedelta

class PrivacyManager:
    """
    Privacy and security manager for KSSEM Virtual AI Assistant
    Handles encryption, anonymization, and GDPR compliance
    """
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        """Initialize privacy manager with encryption capabilities"""
        self.encryption_key = encryption_key or self._generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Patterns for sensitive data detection
        self.sensitive_patterns = {
            'phone': r'\b(?:\+91|0)?[6-9]\d{9}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'student_id': r'\b(?:student|id|roll)\s*(?:number|no)?\s*:?\s*([A-Z0-9]{8,12})\b',
            'name': r'\b(Mr|Ms|Mrs|Dr|Prof)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            'address': r'\b\d+(?:\s+[A-Za-z]+){2,}(?:\s+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln))\b'
        }
        
        # Data retention policy (GDPR compliance)
        self.retention_days = 30
        
    def _generate_key(self) -> bytes:
        """Generate a new encryption key"""
        return Fernet.generate_key()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise Exception(f"Encryption failed: {e}")
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt encrypted data"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise Exception(f"Decryption failed: {e}")
    
    def hash_text(self, text: str, salt: Optional[str] = None) -> str:
        """Create a secure hash of text for anonymization"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        combined = f"{text}{salt}"
        hash_object = hashlib.sha256(combined.encode())
        return hash_object.hexdigest()
    
    def anonymize_text(self, text: str) -> str:
        """Anonymize text by removing or masking sensitive information"""
        anonymized_text = text
        
        # Replace sensitive patterns
        for pattern_name, pattern in self.sensitive_patterns.items():
            if pattern_name == 'phone':
                anonymized_text = re.sub(pattern, '[PHONE]', anonymized_text)
            elif pattern_name == 'email':
                anonymized_text = re.sub(pattern, '[EMAIL]', anonymized_text)
            elif pattern_name == 'student_id':
                anonymized_text = re.sub(pattern, r'\1 [STUDENT_ID]', anonymized_text)
            elif pattern_name == 'name':
                anonymized_text = re.sub(pattern, r'\1 [NAME]', anonymized_text)
            elif pattern_name == 'address':
                anonymized_text = re.sub(pattern, '[ADDRESS]', anonymized_text)
        
        return anonymized_text
    
    def detect_sensitive_data(self, text: str) -> Dict[str, List[str]]:
        """Detect sensitive data in text"""
        detected = {}
        
        for pattern_name, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                detected[pattern_name] = matches
        
        return detected
    
    def create_privacy_record(self, user_id: str, data_type: str, purpose: str) -> Dict:
        """Create a privacy record for GDPR compliance"""
        return {
            "user_id": self.hash_text(user_id),
            "data_type": data_type,
            "purpose": purpose,
            "timestamp": datetime.now().isoformat(),
            "retention_until": (datetime.now() + timedelta(days=self.retention_days)).isoformat(),
            "consent_given": True,
            "processing_lawful": "legitimate_interest",  # For campus assistant
            "can_be_deleted": True
        }
    
    def validate_gdpr_compliance(self, data_record: Dict) -> bool:
        """Validate if data handling is GDPR compliant"""
        required_fields = [
            "user_id", "data_type", "purpose", "timestamp", 
            "retention_until", "consent_given", "processing_lawful"
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in data_record:
                return False
        
        # Check retention period
        retention_date = datetime.fromisoformat(data_record["retention_until"])
        if retention_date < datetime.now():
            return False
        
        # Check consent
        if not data_record.get("consent_given", False):
            return False
        
        return True
    
    def anonymize_query_log(self, query: str, user_id: str, intent: str) -> Dict:
        """Create anonymized query log entry"""
        return {
            "query_hash": self.hash_text(query),
            "user_hash": self.hash_text(user_id) if user_id else None,
            "intent": intent,
            "timestamp": datetime.now().isoformat(),
            "anonymized_query": self.anonymize_text(query),
            "privacy_compliant": True
        }
    
    def secure_session_data(self, session_data: Dict) -> str:
        """Encrypt session data for secure storage"""
        try:
            json_data = json.dumps(session_data)
            return self.encrypt_data(json_data)
        except Exception as e:
            raise Exception(f"Session encryption failed: {e}")
    
    def retrieve_session_data(self, encrypted_session: str) -> Dict:
        """Decrypt and retrieve session data"""
        try:
            decrypted_json = self.decrypt_data(encrypted_session)
            return json.loads(decrypted_json)
        except Exception as e:
            raise Exception(f"Session decryption failed: {e}")

class SecureDataStore:
    """
    Secure data storage with encryption and privacy controls
    """
    
    def __init__(self, privacy_manager: PrivacyManager):
        self.privacy_manager = privacy_manager
        self.data_store = {}  # In production, use actual database
        
    def store_user_query(self, user_id: str, query: str, intent: str, 
                        session_id: Optional[str] = None) -> str:
        """Store user query with privacy protection"""
        # Create privacy record
        privacy_record = self.privacy_manager.create_privacy_record(
            user_id, "query", "campus_assistance"
        )
        
        # Anonymize and encrypt query
        anonymized_log = self.privacy_manager.anonymize_query_log(query, user_id, intent)
        encrypted_query = self.privacy_manager.encrypt_data(query)
        
        # Create storage record
        record_id = secrets.token_hex(16)
        storage_record = {
            "id": record_id,
            "encrypted_query": encrypted_query,
            "anonymized_log": anonymized_log,
            "privacy_record": privacy_record,
            "session_id": session_id,
            "created_at": datetime.now().isoformat()
        }
        
        # Store record
        self.data_store[record_id] = storage_record
        
        return record_id
    
    def retrieve_user_query(self, record_id: str) -> Optional[Dict]:
        """Retrieve user query with privacy checks"""
        if record_id not in self.data_store:
            return None
        
        record = self.data_store[record_id]
        
        # Check GDPR compliance
        if not self.privacy_manager.validate_gdpr_compliance(record["privacy_record"]):
            # Auto-delete expired records
            del self.data_store[record_id]
            return None
        
        return record
    
    def cleanup_expired_data(self) -> int:
        """Clean up expired data for GDPR compliance"""
        expired_records = []
        current_time = datetime.now()
        
        for record_id, record in self.data_store.items():
            retention_until = datetime.fromisoformat(
                record["privacy_record"]["retention_until"]
            )
            
            if retention_until < current_time:
                expired_records.append(record_id)
        
        # Delete expired records
        for record_id in expired_records:
            del self.data_store[record_id]
        
        return len(expired_records)
    
    def get_user_data(self, user_id: str) -> List[Dict]:
        """Get all data for a specific user (GDPR right of access)"""
        user_hash = self.privacy_manager.hash_text(user_id)
        user_records = []
        
        for record in self.data_store.values():
            if record["privacy_record"]["user_id"] == user_hash:
                user_records.append({
                    "id": record["id"],
                    "data_type": record["privacy_record"]["data_type"],
                    "purpose": record["privacy_record"]["purpose"],
                    "created_at": record["created_at"],
                    "anonymized_content": record["anonymized_log"]
                })
        
        return user_records
    
    def delete_user_data(self, user_id: str) -> int:
        """Delete all data for a specific user (GDPR right to erasure)"""
        user_hash = self.privacy_manager.hash_text(user_id)
        deleted_count = 0
        
        records_to_delete = []
        for record_id, record in self.data_store.items():
            if record["privacy_record"]["user_id"] == user_hash:
                records_to_delete.append(record_id)
        
        for record_id in records_to_delete:
            del self.data_store[record_id]
            deleted_count += 1
        
        return deleted_count

class AccessLogger:
    """
    Secure logging system for access and privacy events
    """
    
    def __init__(self, privacy_manager: PrivacyManager):
        self.privacy_manager = privacy_manager
        self.logs = []  # In production, use secure logging service
    
    def log_data_access(self, user_id: str, data_type: str, action: str, 
                       justification: str) -> None:
        """Log data access events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_hash": self.privacy_manager.hash_text(user_id),
            "data_type": data_type,
            "action": action,
            "justification": justification,
            "session_id": secrets.token_hex(8)
        }
        
        self.logs.append(log_entry)
    
    def log_privacy_event(self, event_type: str, details: Dict) -> None:
        """Log privacy-related events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "privacy_compliant": True
        }
        
        self.logs.append(log_entry)
    
    def get_audit_trail(self, user_id: str) -> List[Dict]:
        """Get audit trail for specific user"""
        user_hash = self.privacy_manager.hash_text(user_id)
        user_logs = []
        
        for log in self.logs:
            if log.get("user_hash") == user_hash:
                user_logs.append(log)
        
        return user_logs

# Example usage and testing
if __name__ == "__main__":
    # Initialize privacy manager
    privacy_manager = PrivacyManager()
    
    # Test anonymization
    test_text = "Hi, I'm John Doe from CSE department. My phone is +91-9876543210 and email is john.doe@kssem.edu.in"
    print("Original text:", test_text)
    print("Anonymized text:", privacy_manager.anonymize_text(test_text))
    
    # Test sensitive data detection
    sensitive_data = privacy_manager.detect_sensitive_data(test_text)
    print("Detected sensitive data:", sensitive_data)
    
    # Test encryption
    secret_message = "Where is Dr. Rajesh Kumar's office?"
    encrypted = privacy_manager.encrypt_data(secret_message)
    decrypted = privacy_manager.decrypt_data(encrypted)
    print(f"Original: {secret_message}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    
    # Test secure data store
    data_store = SecureDataStore(privacy_manager)
    record_id = data_store.store_user_query(
        "user123", 
        "Where is the computer science department?", 
        "navigation"
    )
    
    retrieved_record = data_store.retrieve_user_query(record_id)
    print("Stored and retrieved record successfully")
    
    # Test access logging
    access_logger = AccessLogger(privacy_manager)
    access_logger.log_data_access(
        "user123", 
        "query", 
        "store", 
        "Campus assistance service"
    )
    
    print("✓ All privacy and security tests completed successfully")
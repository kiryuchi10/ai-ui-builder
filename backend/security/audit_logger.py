"""
Security audit logging system for AI UI Builder
Tracks all security-related events and user actions
"""

import json
import logging
import datetime
from typing import Dict, Any, Optional
from enum import Enum
import hashlib
import os
from dataclasses import dataclass, asdict

class AuditEventType(Enum):
    """Types of audit events"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTRATION = "user_registration"
    PASSWORD_CHANGE = "password_change"
    API_KEY_CREATED = "api_key_created"
    API_KEY_ROTATED = "api_key_rotated"
    API_KEY_DELETED = "api_key_deleted"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    SECURITY_VIOLATION = "security_violation"
    FAILED_LOGIN = "failed_login"
    PERMISSION_DENIED = "permission_denied"
    SYSTEM_ERROR = "system_error"
    COMPLIANCE_EVENT = "compliance_event"

class AuditSeverity(Enum):
    """Severity levels for audit events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    """Audit event data structure"""
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    resource: Optional[str]
    action: str
    result: str  # success, failure, error
    details: Dict[str, Any]
    timestamp: datetime.datetime
    event_id: str

class AuditLogger:
    """Security audit logging system"""
    
    def __init__(self, log_file: str = "backend/logs/security_audit.log"):
        self.log_file = log_file
        self.logger = self._setup_logger()
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup audit logger"""
        logger = logging.getLogger("security_audit")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler(self.log_file)
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        if not logger.handlers:
            logger.addHandler(handler)
        
        return logger
    
    def _generate_event_id(self, event: AuditEvent) -> str:
        """Generate unique event ID"""
        data = f"{event.timestamp}{event.user_id}{event.action}{event.resource}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def log_event(self, 
                  event_type: AuditEventType,
                  severity: AuditSeverity,
                  action: str,
                  result: str,
                  user_id: Optional[str] = None,
                  session_id: Optional[str] = None,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  resource: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None) -> str:
        """Log security audit event"""
        
        event = AuditEvent(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            action=action,
            result=result,
            details=details or {},
            timestamp=datetime.datetime.utcnow(),
            event_id=""
        )
        
        event.event_id = self._generate_event_id(event)
        
        # Log to file
        log_entry = {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type.value,
            "severity": event.severity.value,
            "user_id": event.user_id,
            "session_id": event.session_id,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "resource": event.resource,
            "action": event.action,
            "result": event.result,
            "details": event.details
        }
        
        self.logger.info(json.dumps(log_entry))
        
        # Store in database for querying (implementation depends on your DB)
        self._store_in_database(event)
        
        # Send alerts for critical events
        if severity == AuditSeverity.CRITICAL:
            self._send_security_alert(event)
        
        return event.event_id
    
    def log_user_login(self, user_id: str, ip_address: str, user_agent: str, success: bool):
        """Log user login attempt"""
        self.log_event(
            event_type=AuditEventType.USER_LOGIN if success else AuditEventType.FAILED_LOGIN,
            severity=AuditSeverity.LOW if success else AuditSeverity.MEDIUM,
            action="login",
            result="success" if success else "failure",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"login_method": "password"}
        )
    
    def log_api_key_operation(self, user_id: str, operation: str, service: str, success: bool):
        """Log API key operations"""
        event_type_map = {
            "create": AuditEventType.API_KEY_CREATED,
            "rotate": AuditEventType.API_KEY_ROTATED,
            "delete": AuditEventType.API_KEY_DELETED
        }
        
        self.log_event(
            event_type=event_type_map.get(operation, AuditEventType.API_KEY_CREATED),
            severity=AuditSeverity.MEDIUM,
            action=f"api_key_{operation}",
            result="success" if success else "failure",
            user_id=user_id,
            resource=f"api_key:{service}",
            details={"service": service, "operation": operation}
        )
    
    def log_data_access(self, user_id: str, resource: str, action: str, ip_address: str):
        """Log data access events"""
        self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.LOW,
            action=action,
            result="success",
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            details={"access_type": action}
        )
    
    def log_security_violation(self, user_id: Optional[str], violation_type: str, 
                             ip_address: str, details: Dict[str, Any]):
        """Log security violations"""
        self.log_event(
            event_type=AuditEventType.SECURITY_VIOLATION,
            severity=AuditSeverity.HIGH,
            action="security_violation",
            result="blocked",
            user_id=user_id,
            ip_address=ip_address,
            details={**details, "violation_type": violation_type}
        )
    
    def log_compliance_event(self, event_name: str, user_id: str, details: Dict[str, Any]):
        """Log compliance-related events"""
        self.log_event(
            event_type=AuditEventType.COMPLIANCE_EVENT,
            severity=AuditSeverity.MEDIUM,
            action=event_name,
            result="logged",
            user_id=user_id,
            details=details
        )
    
    def _store_in_database(self, event: AuditEvent):
        """Store audit event in database"""
        # Implementation depends on your database choice
        # This should store the event for querying and reporting
        pass
    
    def _send_security_alert(self, event: AuditEvent):
        """Send security alert for critical events"""
        # Implementation for sending alerts (email, Slack, etc.)
        print(f"SECURITY ALERT: {event.event_type.value} - {event.details}")
    
    def get_audit_trail(self, user_id: str, start_date: datetime.datetime, 
                       end_date: datetime.datetime) -> list:
        """Get audit trail for user"""
        # Implementation depends on your database choice
        # This should query and return audit events
        pass
    
    def generate_compliance_report(self, start_date: datetime.datetime, 
                                 end_date: datetime.datetime) -> Dict[str, Any]:
        """Generate compliance report"""
        # Implementation for generating compliance reports
        # Should include statistics, violations, access patterns, etc.
        pass

# Global audit logger instance
audit_logger = AuditLogger()
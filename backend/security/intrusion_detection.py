"""
Intrusion Detection System for AI UI Builder
Monitors and detects suspicious activities and potential security threats
"""

import time
import json
import hashlib
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from collections import defaultdict, deque
from datetime import datetime, timedelta
import ipaddress
import re
from .audit_logger import audit_logger, AuditEventType, AuditSeverity

@dataclass
class ThreatIndicator:
    """Threat indicator data structure"""
    indicator_type: str
    value: str
    severity: str
    description: str
    timestamp: datetime

class RateLimiter:
    """Rate limiting for API endpoints"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
        self.blocked_ips = defaultdict(float)
    
    def is_rate_limited(self, identifier: str, limit: int, window: int) -> bool:
        """Check if identifier is rate limited"""
        now = time.time()
        
        # Check if IP is temporarily blocked
        if identifier in self.blocked_ips:
            if now < self.blocked_ips[identifier]:
                return True
            else:
                del self.blocked_ips[identifier]
        
        # Clean old requests
        request_times = self.requests[identifier]
        while request_times and request_times[0] < now - window:
            request_times.popleft()
        
        # Check rate limit
        if len(request_times) >= limit:
            # Block IP for 5 minutes
            self.blocked_ips[identifier] = now + 300
            audit_logger.log_security_violation(
                user_id=None,
                violation_type="rate_limit_exceeded",
                ip_address=identifier,
                details={"limit": limit, "window": window, "requests": len(request_times)}
            )
            return True
        
        # Add current request
        request_times.append(now)
        return False

class AnomalyDetector:
    """Detects anomalous behavior patterns"""
    
    def __init__(self):
        self.user_patterns = defaultdict(dict)
        self.ip_patterns = defaultdict(dict)
        self.failed_logins = defaultdict(list)
    
    def analyze_login_pattern(self, user_id: str, ip_address: str, 
                            user_agent: str, success: bool) -> List[ThreatIndicator]:
        """Analyze login patterns for anomalies"""
        threats = []
        now = datetime.utcnow()
        
        # Track failed login attempts
        if not success:
            self.failed_logins[user_id].append({
                'timestamp': now,
                'ip_address': ip_address,
                'user_agent': user_agent
            })
            
            # Clean old failed attempts (last 1 hour)
            cutoff = now - timedelta(hours=1)
            self.failed_logins[user_id] = [
                attempt for attempt in self.failed_logins[user_id]
                if attempt['timestamp'] > cutoff
            ]
            
            # Check for brute force attack
            if len(self.failed_logins[user_id]) >= 5:
                threats.append(ThreatIndicator(
                    indicator_type="brute_force",
                    value=user_id,
                    severity="high",
                    description=f"Multiple failed login attempts for user {user_id}",
                    timestamp=now
                ))
        
        # Check for unusual IP address
        user_pattern = self.user_patterns[user_id]
        if 'known_ips' not in user_pattern:
            user_pattern['known_ips'] = set()
        
        if ip_address not in user_pattern['known_ips']:
            if len(user_pattern['known_ips']) > 0:  # Not first login
                threats.append(ThreatIndicator(
                    indicator_type="unusual_ip",
                    value=ip_address,
                    severity="medium",
                    description=f"Login from new IP address: {ip_address}",
                    timestamp=now
                ))
        
        user_pattern['known_ips'].add(ip_address)
        user_pattern['last_login'] = now
        
        return threats
    
    def analyze_api_usage(self, user_id: str, endpoint: str, 
                         ip_address: str) -> List[ThreatIndicator]:
        """Analyze API usage patterns"""
        threats = []
        now = datetime.utcnow()
        
        # Track API usage patterns
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = {}
        
        pattern = self.user_patterns[user_id]
        if 'api_usage' not in pattern:
            pattern['api_usage'] = defaultdict(list)
        
        pattern['api_usage'][endpoint].append(now)
        
        # Clean old usage data (last 1 hour)
        cutoff = now - timedelta(hours=1)
        pattern['api_usage'][endpoint] = [
            timestamp for timestamp in pattern['api_usage'][endpoint]
            if timestamp > cutoff
        ]
        
        # Check for unusual API usage
        usage_count = len(pattern['api_usage'][endpoint])
        if usage_count > 100:  # More than 100 requests per hour
            threats.append(ThreatIndicator(
                indicator_type="excessive_api_usage",
                value=f"{user_id}:{endpoint}",
                severity="medium",
                description=f"Excessive API usage: {usage_count} requests to {endpoint}",
                timestamp=now
            ))
        
        return threats

class SecurityScanner:
    """Scans for common security vulnerabilities"""
    
    def __init__(self):
        self.malicious_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'union\s+select',  # SQL injection
            r'drop\s+table',  # SQL injection
            r'exec\s*\(',  # Code injection
            r'eval\s*\(',  # Code injection
            r'\.\./',  # Path traversal
            r'<iframe[^>]*>',  # Iframe injection
        ]
        
        self.suspicious_user_agents = [
            'sqlmap',
            'nikto',
            'nmap',
            'burp',
            'owasp',
            'scanner'
        ]
    
    def scan_input(self, input_data: str, source: str) -> List[ThreatIndicator]:
        """Scan input for malicious patterns"""
        threats = []
        now = datetime.utcnow()
        
        input_lower = input_data.lower()
        
        for pattern in self.malicious_patterns:
            if re.search(pattern, input_lower, re.IGNORECASE):
                threats.append(ThreatIndicator(
                    indicator_type="malicious_input",
                    value=pattern,
                    severity="high",
                    description=f"Malicious pattern detected in {source}: {pattern}",
                    timestamp=now
                ))
        
        return threats
    
    def scan_user_agent(self, user_agent: str) -> List[ThreatIndicator]:
        """Scan user agent for suspicious tools"""
        threats = []
        now = datetime.utcnow()
        
        user_agent_lower = user_agent.lower()
        
        for suspicious in self.suspicious_user_agents:
            if suspicious in user_agent_lower:
                threats.append(ThreatIndicator(
                    indicator_type="suspicious_user_agent",
                    value=user_agent,
                    severity="medium",
                    description=f"Suspicious user agent detected: {user_agent}",
                    timestamp=now
                ))
        
        return threats

class IntrusionDetectionSystem:
    """Main intrusion detection system"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.anomaly_detector = AnomalyDetector()
        self.security_scanner = SecurityScanner()
        self.threat_indicators = deque(maxlen=10000)
        self.blocked_ips = set()
    
    def check_rate_limit(self, ip_address: str, endpoint: str) -> bool:
        """Check rate limit for IP and endpoint"""
        # Different limits for different endpoints
        limits = {
            '/api/auth/login': (5, 300),  # 5 attempts per 5 minutes
            '/api/generate': (10, 60),    # 10 requests per minute
            'default': (100, 3600)        # 100 requests per hour
        }
        
        limit, window = limits.get(endpoint, limits['default'])
        identifier = f"{ip_address}:{endpoint}"
        
        return self.rate_limiter.is_rate_limited(identifier, limit, window)
    
    def analyze_request(self, user_id: Optional[str], ip_address: str, 
                       user_agent: str, endpoint: str, 
                       request_data: Dict) -> List[ThreatIndicator]:
        """Analyze incoming request for threats"""
        threats = []
        
        # Check if IP is blocked
        if ip_address in self.blocked_ips:
            threats.append(ThreatIndicator(
                indicator_type="blocked_ip",
                value=ip_address,
                severity="high",
                description=f"Request from blocked IP: {ip_address}",
                timestamp=datetime.utcnow()
            ))
            return threats
        
        # Scan user agent
        threats.extend(self.security_scanner.scan_user_agent(user_agent))
        
        # Scan request data for malicious patterns
        for key, value in request_data.items():
            if isinstance(value, str):
                threats.extend(self.security_scanner.scan_input(value, f"request.{key}"))
        
        # Analyze API usage patterns
        if user_id:
            threats.extend(self.anomaly_detector.analyze_api_usage(
                user_id, endpoint, ip_address
            ))
        
        # Store threats
        for threat in threats:
            self.threat_indicators.append(threat)
            
            # Log security violations
            audit_logger.log_security_violation(
                user_id=user_id,
                violation_type=threat.indicator_type,
                ip_address=ip_address,
                details={
                    "severity": threat.severity,
                    "description": threat.description,
                    "endpoint": endpoint
                }
            )
            
            # Block IP for high severity threats
            if threat.severity == "high":
                self.blocked_ips.add(ip_address)
        
        return threats
    
    def analyze_login_attempt(self, user_id: str, ip_address: str, 
                            user_agent: str, success: bool) -> List[ThreatIndicator]:
        """Analyze login attempt"""
        threats = self.anomaly_detector.analyze_login_pattern(
            user_id, ip_address, user_agent, success
        )
        
        # Store threats
        for threat in threats:
            self.threat_indicators.append(threat)
        
        return threats
    
    def get_threat_summary(self, hours: int = 24) -> Dict:
        """Get threat summary for the last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent_threats = [
            threat for threat in self.threat_indicators
            if threat.timestamp > cutoff
        ]
        
        summary = {
            "total_threats": len(recent_threats),
            "by_type": defaultdict(int),
            "by_severity": defaultdict(int),
            "blocked_ips": len(self.blocked_ips),
            "top_threats": []
        }
        
        for threat in recent_threats:
            summary["by_type"][threat.indicator_type] += 1
            summary["by_severity"][threat.severity] += 1
        
        # Get top 10 most recent high severity threats
        high_threats = [
            threat for threat in recent_threats
            if threat.severity == "high"
        ]
        summary["top_threats"] = sorted(
            high_threats, 
            key=lambda x: x.timestamp, 
            reverse=True
        )[:10]
        
        return summary
    
    def unblock_ip(self, ip_address: str) -> bool:
        """Manually unblock an IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            audit_logger.log_event(
                event_type=AuditEventType.SECURITY_VIOLATION,
                severity=AuditSeverity.MEDIUM,
                action="ip_unblocked",
                result="success",
                details={"ip_address": ip_address}
            )
            return True
        return False

# Global IDS instance
ids = IntrusionDetectionSystem()
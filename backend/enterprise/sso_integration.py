"""
Single Sign-On (SSO) Integration for AI UI Builder
Supports LDAP/Active Directory, SAML, and OAuth2
"""

import ldap
import jwt
import xml.etree.ElementTree as ET
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import requests
import base64
import hashlib
import secrets
from dataclasses import dataclass
from ..security.audit_logger import audit_logger, AuditEventType, AuditSeverity

@dataclass
class UserInfo:
    """User information from SSO provider"""
    user_id: str
    email: str
    first_name: str
    last_name: str
    groups: List[str]
    attributes: Dict[str, Any]

class LDAPConnector:
    """LDAP/Active Directory integration"""
    
    def __init__(self, server_url: str, bind_dn: str, bind_password: str, 
                 base_dn: str, user_filter: str = "(uid={})"):
        self.server_url = server_url
        self.bind_dn = bind_dn
        self.bind_password = bind_password
        self.base_dn = base_dn
        self.user_filter = user_filter
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserInfo]:
        """Authenticate user against LDAP"""
        try:
            # Connect to LDAP server
            conn = ldap.initialize(self.server_url)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            
            # Bind with service account
            conn.simple_bind_s(self.bind_dn, self.bind_password)
            
            # Search for user
            search_filter = self.user_filter.format(username)
            result = conn.search_s(
                self.base_dn, 
                ldap.SCOPE_SUBTREE, 
                search_filter,
                ['cn', 'mail', 'givenName', 'sn', 'memberOf', 'userPrincipalName']
            )
            
            if not result:
                audit_logger.log_event(
                    event_type=AuditEventType.FAILED_LOGIN,
                    severity=AuditSeverity.MEDIUM,
                    action="ldap_auth",
                    result="user_not_found",
                    user_id=username,
                    details={"auth_method": "ldap"}
                )
                return None
            
            user_dn, user_attrs = result[0]
            
            # Try to bind with user credentials
            try:
                user_conn = ldap.initialize(self.server_url)
                user_conn.simple_bind_s(user_dn, password)
                user_conn.unbind()
            except ldap.INVALID_CREDENTIALS:
                audit_logger.log_event(
                    event_type=AuditEventType.FAILED_LOGIN,
                    severity=AuditSeverity.MEDIUM,
                    action="ldap_auth",
                    result="invalid_credentials",
                    user_id=username,
                    details={"auth_method": "ldap"}
                )
                return None
            
            # Extract user information
            user_info = UserInfo(
                user_id=username,
                email=self._get_attr_value(user_attrs, 'mail') or 
                      self._get_attr_value(user_attrs, 'userPrincipalName'),
                first_name=self._get_attr_value(user_attrs, 'givenName', ''),
                last_name=self._get_attr_value(user_attrs, 'sn', ''),
                groups=self._get_attr_values(user_attrs, 'memberOf'),
                attributes=user_attrs
            )
            
            audit_logger.log_event(
                event_type=AuditEventType.USER_LOGIN,
                severity=AuditSeverity.LOW,
                action="ldap_auth",
                result="success",
                user_id=username,
                details={"auth_method": "ldap", "groups": user_info.groups}
            )
            
            conn.unbind()
            return user_info
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="ldap_auth",
                result="error",
                user_id=username,
                details={"auth_method": "ldap", "error": str(e)}
            )
            return None
    
    def _get_attr_value(self, attrs: Dict, key: str, default: str = None) -> str:
        """Get single attribute value"""
        values = attrs.get(key, [])
        if values and isinstance(values[0], bytes):
            return values[0].decode('utf-8')
        elif values:
            return str(values[0])
        return default
    
    def _get_attr_values(self, attrs: Dict, key: str) -> List[str]:
        """Get multiple attribute values"""
        values = attrs.get(key, [])
        result = []
        for value in values:
            if isinstance(value, bytes):
                result.append(value.decode('utf-8'))
            else:
                result.append(str(value))
        return result

class SAMLProvider:
    """SAML 2.0 SSO provider"""
    
    def __init__(self, entity_id: str, sso_url: str, certificate: str, 
                 private_key: str, acs_url: str):
        self.entity_id = entity_id
        self.sso_url = sso_url
        self.certificate = certificate
        self.private_key = private_key
        self.acs_url = acs_url
    
    def generate_auth_request(self, relay_state: str = None) -> str:
        """Generate SAML authentication request"""
        request_id = self._generate_id()
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        saml_request = f"""
        <samlp:AuthnRequest 
            xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
            xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
            ID="{request_id}"
            Version="2.0"
            IssueInstant="{timestamp}"
            Destination="{self.sso_url}"
            AssertionConsumerServiceURL="{self.acs_url}"
            ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
            <saml:Issuer>{self.entity_id}</saml:Issuer>
        </samlp:AuthnRequest>
        """
        
        # Encode and compress the request
        encoded_request = base64.b64encode(saml_request.encode()).decode()
        
        return encoded_request
    
    def process_saml_response(self, saml_response: str) -> Optional[UserInfo]:
        """Process SAML response and extract user info"""
        try:
            # Decode the response
            decoded_response = base64.b64decode(saml_response)
            
            # Parse XML
            root = ET.fromstring(decoded_response)
            
            # Extract assertion
            assertion = root.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}Assertion')
            if assertion is None:
                return None
            
            # Extract user attributes
            subject = assertion.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}Subject')
            name_id = subject.find('.//{urn:oasis:names:tc:SAML:2.0:assertion}NameID')
            
            user_id = name_id.text if name_id is not None else None
            
            # Extract attributes
            attributes = {}
            attr_statements = assertion.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeStatement')
            
            for attr_statement in attr_statements:
                attrs = attr_statement.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}Attribute')
                for attr in attrs:
                    name = attr.get('Name')
                    values = [val.text for val in attr.findall('.//{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue')]
                    attributes[name] = values[0] if len(values) == 1 else values
            
            user_info = UserInfo(
                user_id=user_id,
                email=attributes.get('email', ''),
                first_name=attributes.get('firstName', ''),
                last_name=attributes.get('lastName', ''),
                groups=attributes.get('groups', []) if isinstance(attributes.get('groups'), list) else [attributes.get('groups', '')],
                attributes=attributes
            )
            
            audit_logger.log_event(
                event_type=AuditEventType.USER_LOGIN,
                severity=AuditSeverity.LOW,
                action="saml_auth",
                result="success",
                user_id=user_id,
                details={"auth_method": "saml", "groups": user_info.groups}
            )
            
            return user_info
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="saml_auth",
                result="error",
                details={"auth_method": "saml", "error": str(e)}
            )
            return None
    
    def _generate_id(self) -> str:
        """Generate unique request ID"""
        return f"_{secrets.token_hex(16)}"

class OAuth2Provider:
    """OAuth2/OpenID Connect provider"""
    
    def __init__(self, client_id: str, client_secret: str, 
                 authorization_url: str, token_url: str, userinfo_url: str,
                 redirect_uri: str, scopes: List[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.userinfo_url = userinfo_url
        self.redirect_uri = redirect_uri
        self.scopes = scopes or ['openid', 'profile', 'email']
    
    def get_authorization_url(self, state: str = None) -> str:
        """Get OAuth2 authorization URL"""
        if state is None:
            state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'state': state
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.authorization_url}?{query_string}"
    
    def exchange_code_for_token(self, code: str, state: str = None) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        try:
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="oauth2_token_exchange",
                result="error",
                details={"auth_method": "oauth2", "error": str(e)}
            )
            return None
    
    def get_user_info(self, access_token: str) -> Optional[UserInfo]:
        """Get user information using access token"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(self.userinfo_url, headers=headers)
            response.raise_for_status()
            
            user_data = response.json()
            
            user_info = UserInfo(
                user_id=user_data.get('sub') or user_data.get('id'),
                email=user_data.get('email', ''),
                first_name=user_data.get('given_name', ''),
                last_name=user_data.get('family_name', ''),
                groups=user_data.get('groups', []),
                attributes=user_data
            )
            
            audit_logger.log_event(
                event_type=AuditEventType.USER_LOGIN,
                severity=AuditSeverity.LOW,
                action="oauth2_auth",
                result="success",
                user_id=user_info.user_id,
                details={"auth_method": "oauth2", "groups": user_info.groups}
            )
            
            return user_info
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="oauth2_userinfo",
                result="error",
                details={"auth_method": "oauth2", "error": str(e)}
            )
            return None

class SSOManager:
    """Main SSO management class"""
    
    def __init__(self):
        self.providers = {}
        self.user_sessions = {}
    
    def register_ldap_provider(self, name: str, **config) -> None:
        """Register LDAP provider"""
        self.providers[name] = {
            'type': 'ldap',
            'provider': LDAPConnector(**config)
        }
    
    def register_saml_provider(self, name: str, **config) -> None:
        """Register SAML provider"""
        self.providers[name] = {
            'type': 'saml',
            'provider': SAMLProvider(**config)
        }
    
    def register_oauth2_provider(self, name: str, **config) -> None:
        """Register OAuth2 provider"""
        self.providers[name] = {
            'type': 'oauth2',
            'provider': OAuth2Provider(**config)
        }
    
    def authenticate(self, provider_name: str, **credentials) -> Optional[UserInfo]:
        """Authenticate user with specified provider"""
        if provider_name not in self.providers:
            return None
        
        provider_config = self.providers[provider_name]
        provider = provider_config['provider']
        provider_type = provider_config['type']
        
        if provider_type == 'ldap':
            return provider.authenticate_user(
                credentials.get('username'),
                credentials.get('password')
            )
        elif provider_type == 'saml':
            return provider.process_saml_response(
                credentials.get('saml_response')
            )
        elif provider_type == 'oauth2':
            token_data = provider.exchange_code_for_token(
                credentials.get('code'),
                credentials.get('state')
            )
            if token_data:
                return provider.get_user_info(token_data.get('access_token'))
        
        return None
    
    def create_session(self, user_info: UserInfo, provider_name: str) -> str:
        """Create user session"""
        session_id = secrets.token_urlsafe(32)
        
        self.user_sessions[session_id] = {
            'user_info': user_info,
            'provider': provider_name,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow()
        }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get user session"""
        session = self.user_sessions.get(session_id)
        if session:
            # Update last activity
            session['last_activity'] = datetime.utcnow()
            return session
        return None
    
    def invalidate_session(self, session_id: str) -> bool:
        """Invalidate user session"""
        if session_id in self.user_sessions:
            user_info = self.user_sessions[session_id]['user_info']
            del self.user_sessions[session_id]
            
            audit_logger.log_event(
                event_type=AuditEventType.USER_LOGOUT,
                severity=AuditSeverity.LOW,
                action="session_invalidated",
                result="success",
                user_id=user_info.user_id,
                details={"session_id": session_id}
            )
            
            return True
        return False

# Global SSO manager instance
sso_manager = SSOManager()
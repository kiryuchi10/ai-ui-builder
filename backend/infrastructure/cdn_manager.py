"""
Global CDN Management for AI UI Builder
Handles content distribution, caching, and regional optimization
"""

import boto3
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib
import os
from ..security.audit_logger import audit_logger, AuditEventType, AuditSeverity

@dataclass
class CDNDistribution:
    """CDN distribution configuration"""
    distribution_id: str
    domain_name: str
    origin_domain: str
    status: str
    regions: List[str]
    cache_behaviors: Dict[str, Any]
    created_at: datetime

@dataclass
class CacheStats:
    """CDN cache statistics"""
    hit_rate: float
    miss_rate: float
    total_requests: int
    bandwidth_gb: float
    top_regions: List[Dict[str, Any]]
    timestamp: datetime

class CloudFrontManager:
    """AWS CloudFront CDN management"""
    
    def __init__(self, aws_access_key: str, aws_secret_key: str, region: str = 'us-east-1'):
        self.client = boto3.client(
            'cloudfront',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
    
    def create_distribution(self, origin_domain: str, aliases: List[str] = None,
                          cache_policy: str = 'default') -> Optional[CDNDistribution]:
        """Create CloudFront distribution"""
        try:
            # Define cache behaviors based on policy
            cache_behaviors = self._get_cache_behaviors(cache_policy)
            
            distribution_config = {
                'CallerReference': f"ai-ui-builder-{int(datetime.utcnow().timestamp())}",
                'Comment': 'AI UI Builder CDN Distribution',
                'DefaultRootObject': 'index.html',
                'Origins': {
                    'Quantity': 1,
                    'Items': [
                        {
                            'Id': 'origin1',
                            'DomainName': origin_domain,
                            'CustomOriginConfig': {
                                'HTTPPort': 80,
                                'HTTPSPort': 443,
                                'OriginProtocolPolicy': 'https-only',
                                'OriginSslProtocols': {
                                    'Quantity': 1,
                                    'Items': ['TLSv1.2']
                                }
                            }
                        }
                    ]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': 'origin1',
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'TrustedSigners': {
                        'Enabled': False,
                        'Quantity': 0
                    },
                    'ForwardedValues': {
                        'QueryString': False,
                        'Cookies': {'Forward': 'none'}
                    },
                    'MinTTL': 0,
                    'DefaultTTL': 86400,  # 24 hours
                    'MaxTTL': 31536000,   # 1 year
                    'Compress': True
                },
                'Enabled': True,
                'PriceClass': 'PriceClass_All'
            }
            
            # Add aliases if provided
            if aliases:
                distribution_config['Aliases'] = {
                    'Quantity': len(aliases),
                    'Items': aliases
                }
            
            response = self.client.create_distribution(
                DistributionConfig=distribution_config
            )
            
            distribution_data = response['Distribution']
            
            distribution = CDNDistribution(
                distribution_id=distribution_data['Id'],
                domain_name=distribution_data['DomainName'],
                origin_domain=origin_domain,
                status=distribution_data['Status'],
                regions=self._get_enabled_regions(),
                cache_behaviors=cache_behaviors,
                created_at=datetime.utcnow()
            )
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.MEDIUM,
                action="create_cdn_distribution",
                result="success",
                resource=f"cdn:{distribution.distribution_id}",
                details={
                    "distribution_id": distribution.distribution_id,
                    "origin_domain": origin_domain,
                    "aliases": aliases or []
                }
            )
            
            return distribution
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="create_cdn_distribution",
                result="error",
                details={"error": str(e), "origin_domain": origin_domain}
            )
            return None
    
    def update_distribution(self, distribution_id: str, 
                          config_updates: Dict[str, Any]) -> bool:
        """Update CloudFront distribution configuration"""
        try:
            # Get current configuration
            response = self.client.get_distribution_config(Id=distribution_id)
            current_config = response['DistributionConfig']
            etag = response['ETag']
            
            # Apply updates
            for key, value in config_updates.items():
                if key in current_config:
                    current_config[key] = value
            
            # Update distribution
            self.client.update_distribution(
                Id=distribution_id,
                DistributionConfig=current_config,
                IfMatch=etag
            )
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.MEDIUM,
                action="update_cdn_distribution",
                result="success",
                resource=f"cdn:{distribution_id}",
                details={"distribution_id": distribution_id, "updates": config_updates}
            )
            
            return True
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="update_cdn_distribution",
                result="error",
                details={"error": str(e), "distribution_id": distribution_id}
            )
            return False
    
    def invalidate_cache(self, distribution_id: str, paths: List[str]) -> bool:
        """Invalidate CDN cache for specific paths"""
        try:
            response = self.client.create_invalidation(
                DistributionId=distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': f"invalidation-{int(datetime.utcnow().timestamp())}"
                }
            )
            
            invalidation_id = response['Invalidation']['Id']
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.LOW,
                action="cdn_cache_invalidation",
                result="success",
                resource=f"cdn:{distribution_id}",
                details={
                    "distribution_id": distribution_id,
                    "invalidation_id": invalidation_id,
                    "paths": paths
                }
            )
            
            return True
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="cdn_cache_invalidation",
                result="error",
                details={"error": str(e), "distribution_id": distribution_id}
            )
            return False
    
    def get_distribution_stats(self, distribution_id: str, 
                             start_date: datetime, end_date: datetime) -> Optional[CacheStats]:
        """Get CDN distribution statistics"""
        try:
            # Get CloudWatch metrics
            cloudwatch = boto3.client('cloudwatch')
            
            # Get cache hit rate
            hit_rate_response = cloudwatch.get_metric_statistics(
                Namespace='AWS/CloudFront',
                MetricName='CacheHitRate',
                Dimensions=[
                    {'Name': 'DistributionId', 'Value': distribution_id}
                ],
                StartTime=start_date,
                EndTime=end_date,
                Period=3600,  # 1 hour
                Statistics=['Average']
            )
            
            # Get request count
            requests_response = cloudwatch.get_metric_statistics(
                Namespace='AWS/CloudFront',
                MetricName='Requests',
                Dimensions=[
                    {'Name': 'DistributionId', 'Value': distribution_id}
                ],
                StartTime=start_date,
                EndTime=end_date,
                Period=3600,
                Statistics=['Sum']
            )
            
            # Calculate statistics
            hit_rate = 0.0
            total_requests = 0
            
            if hit_rate_response['Datapoints']:
                hit_rate = sum(dp['Average'] for dp in hit_rate_response['Datapoints']) / len(hit_rate_response['Datapoints'])
            
            if requests_response['Datapoints']:
                total_requests = sum(dp['Sum'] for dp in requests_response['Datapoints'])
            
            stats = CacheStats(
                hit_rate=hit_rate,
                miss_rate=100.0 - hit_rate,
                total_requests=int(total_requests),
                bandwidth_gb=0.0,  # Would need additional metrics
                top_regions=[],    # Would need additional analysis
                timestamp=datetime.utcnow()
            )
            
            return stats
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.MEDIUM,
                action="get_cdn_stats",
                result="error",
                details={"error": str(e), "distribution_id": distribution_id}
            )
            return None
    
    def _get_cache_behaviors(self, policy: str) -> Dict[str, Any]:
        """Get cache behavior configuration based on policy"""
        policies = {
            'default': {
                'static_assets': {'ttl': 31536000},  # 1 year
                'api_responses': {'ttl': 300},       # 5 minutes
                'html_pages': {'ttl': 3600}          # 1 hour
            },
            'aggressive': {
                'static_assets': {'ttl': 31536000},  # 1 year
                'api_responses': {'ttl': 3600},      # 1 hour
                'html_pages': {'ttl': 86400}         # 24 hours
            },
            'minimal': {
                'static_assets': {'ttl': 86400},     # 24 hours
                'api_responses': {'ttl': 60},        # 1 minute
                'html_pages': {'ttl': 300}           # 5 minutes
            }
        }
        
        return policies.get(policy, policies['default'])
    
    def _get_enabled_regions(self) -> List[str]:
        """Get list of enabled CloudFront regions"""
        return [
            'us-east-1', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-central-1', 'ap-southeast-1',
            'ap-northeast-1', 'ap-south-1', 'sa-east-1'
        ]

class CloudflareManager:
    """Cloudflare CDN management"""
    
    def __init__(self, api_token: str, zone_id: str):
        self.api_token = api_token
        self.zone_id = zone_id
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def create_page_rule(self, url_pattern: str, actions: Dict[str, Any]) -> bool:
        """Create Cloudflare page rule for caching"""
        try:
            data = {
                'targets': [
                    {
                        'target': 'url',
                        'constraint': {
                            'operator': 'matches',
                            'value': url_pattern
                        }
                    }
                ],
                'actions': [
                    {'id': key, 'value': value}
                    for key, value in actions.items()
                ],
                'status': 'active'
            }
            
            response = requests.post(
                f"{self.base_url}/zones/{self.zone_id}/pagerules",
                headers=self.headers,
                json=data
            )
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="create_cloudflare_page_rule",
                result="error",
                details={"error": str(e), "url_pattern": url_pattern}
            )
            return False
    
    def purge_cache(self, urls: List[str] = None) -> bool:
        """Purge Cloudflare cache"""
        try:
            data = {}
            if urls:
                data['files'] = urls
            else:
                data['purge_everything'] = True
            
            response = requests.post(
                f"{self.base_url}/zones/{self.zone_id}/purge_cache",
                headers=self.headers,
                json=data
            )
            
            response.raise_for_status()
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.LOW,
                action="cloudflare_cache_purge",
                result="success",
                details={"urls": urls or ["all"]}
            )
            
            return True
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="cloudflare_cache_purge",
                result="error",
                details={"error": str(e)}
            )
            return False

class CDNManager:
    """Main CDN management class"""
    
    def __init__(self):
        self.providers = {}
        self.distributions = {}
    
    def register_cloudfront(self, name: str, aws_access_key: str, 
                          aws_secret_key: str, region: str = 'us-east-1'):
        """Register CloudFront provider"""
        self.providers[name] = {
            'type': 'cloudfront',
            'provider': CloudFrontManager(aws_access_key, aws_secret_key, region)
        }
    
    def register_cloudflare(self, name: str, api_token: str, zone_id: str):
        """Register Cloudflare provider"""
        self.providers[name] = {
            'type': 'cloudflare',
            'provider': CloudflareManager(api_token, zone_id)
        }
    
    def create_distribution(self, provider_name: str, origin_domain: str,
                          aliases: List[str] = None, 
                          cache_policy: str = 'default') -> Optional[str]:
        """Create CDN distribution"""
        if provider_name not in self.providers:
            return None
        
        provider_config = self.providers[provider_name]
        provider = provider_config['provider']
        
        if provider_config['type'] == 'cloudfront':
            distribution = provider.create_distribution(
                origin_domain, aliases, cache_policy
            )
            if distribution:
                distribution_key = f"{provider_name}:{distribution.distribution_id}"
                self.distributions[distribution_key] = distribution
                return distribution_key
        
        return None
    
    def invalidate_cache(self, distribution_key: str, paths: List[str]) -> bool:
        """Invalidate cache for distribution"""
        if distribution_key not in self.distributions:
            return False
        
        provider_name, distribution_id = distribution_key.split(':', 1)
        if provider_name not in self.providers:
            return False
        
        provider_config = self.providers[provider_name]
        provider = provider_config['provider']
        
        if provider_config['type'] == 'cloudfront':
            return provider.invalidate_cache(distribution_id, paths)
        elif provider_config['type'] == 'cloudflare':
            return provider.purge_cache(paths)
        
        return False
    
    def get_distribution_stats(self, distribution_key: str,
                             start_date: datetime, 
                             end_date: datetime) -> Optional[CacheStats]:
        """Get distribution statistics"""
        if distribution_key not in self.distributions:
            return None
        
        provider_name, distribution_id = distribution_key.split(':', 1)
        if provider_name not in self.providers:
            return None
        
        provider_config = self.providers[provider_name]
        provider = provider_config['provider']
        
        if provider_config['type'] == 'cloudfront':
            return provider.get_distribution_stats(
                distribution_id, start_date, end_date
            )
        
        return None
    
    def optimize_for_region(self, distribution_key: str, region: str) -> bool:
        """Optimize CDN configuration for specific region"""
        # Implementation would depend on the specific optimizations needed
        # This could include adjusting cache policies, adding regional origins, etc.
        
        audit_logger.log_event(
            event_type=AuditEventType.DATA_MODIFICATION,
            severity=AuditSeverity.LOW,
            action="cdn_region_optimization",
            result="success",
            resource=distribution_key,
            details={"region": region}
        )
        
        return True

# Global CDN manager instance
cdn_manager = CDNManager()
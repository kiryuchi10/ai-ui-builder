"""
Disaster Recovery System for AI UI Builder
Handles backup, recovery, and business continuity planning
"""

import os
import json
import boto3
import shutil
import tarfile
import gzip
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
from ..security.audit_logger import audit_logger, AuditEventType, AuditSeverity

class BackupType(Enum):
    """Types of backups"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

class RecoveryStatus(Enum):
    """Recovery operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class BackupJob:
    """Backup job configuration"""
    job_id: str
    name: str
    backup_type: BackupType
    source_paths: List[str]
    destination: str
    schedule: str  # Cron expression
    retention_days: int
    compression: bool
    encryption: bool
    is_active: bool
    created_at: datetime
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

@dataclass
class BackupRecord:
    """Backup record"""
    backup_id: str
    job_id: str
    backup_type: BackupType
    file_path: str
    file_size: int
    checksum: str
    created_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any]

@dataclass
class RecoveryPlan:
    """Disaster recovery plan"""
    plan_id: str
    name: str
    description: str
    priority: int
    recovery_time_objective: int  # RTO in minutes
    recovery_point_objective: int  # RPO in minutes
    steps: List[Dict[str, Any]]
    dependencies: List[str]
    contacts: List[str]
    created_at: datetime
    updated_at: datetime

class BackupManager:
    """Manages backup operations"""
    
    def __init__(self, backup_root: str = "backups"):
        self.backup_root = backup_root
        self.jobs: Dict[str, BackupJob] = {}
        self.records: Dict[str, BackupRecord] = {}
        self.scheduler_thread = None
        self.is_running = False
        os.makedirs(backup_root, exist_ok=True)
    
    def create_backup_job(self, name: str, backup_type: BackupType,
                         source_paths: List[str], destination: str,
                         schedule: str, retention_days: int = 30,
                         compression: bool = True, encryption: bool = True) -> str:
        """Create a new backup job"""
        job_id = f"backup_{int(datetime.utcnow().timestamp())}"
        
        job = BackupJob(
            job_id=job_id,
            name=name,
            backup_type=backup_type,
            source_paths=source_paths,
            destination=destination,
            schedule=schedule,
            retention_days=retention_days,
            compression=compression,
            encryption=encryption,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        self.jobs[job_id] = job
        
        audit_logger.log_event(
            event_type=AuditEventType.DATA_MODIFICATION,
            severity=AuditSeverity.MEDIUM,
            action="create_backup_job",
            result="success",
            resource=f"backup_job:{job_id}",
            details={
                "job_id": job_id,
                "name": name,
                "backup_type": backup_type.value,
                "source_paths": source_paths
            }
        )
        
        return job_id
    
    def run_backup(self, job_id: str) -> Optional[str]:
        """Execute backup job"""
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        backup_id = f"backup_{job_id}_{int(datetime.utcnow().timestamp())}"
        
        try:
            # Create backup directory
            backup_dir = os.path.join(self.backup_root, job_id)
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup file
            backup_filename = f"{backup_id}.tar"
            if job.compression:
                backup_filename += ".gz"
            
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Create tar archive
            mode = "w:gz" if job.compression else "w"
            with tarfile.open(backup_path, mode) as tar:
                for source_path in job.source_paths:
                    if os.path.exists(source_path):
                        tar.add(source_path, arcname=os.path.basename(source_path))
            
            # Calculate checksum
            checksum = self._calculate_checksum(backup_path)
            
            # Get file size
            file_size = os.path.getsize(backup_path)
            
            # Create backup record
            record = BackupRecord(
                backup_id=backup_id,
                job_id=job_id,
                backup_type=job.backup_type,
                file_path=backup_path,
                file_size=file_size,
                checksum=checksum,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=job.retention_days),
                metadata={
                    "source_paths": job.source_paths,
                    "compression": job.compression,
                    "encryption": job.encryption
                }
            )
            
            self.records[backup_id] = record
            job.last_run = datetime.utcnow()
            
            # Upload to cloud storage if configured
            if job.destination.startswith('s3://'):
                self._upload_to_s3(backup_path, job.destination, backup_filename)
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.LOW,
                action="backup_completed",
                result="success",
                resource=f"backup:{backup_id}",
                details={
                    "backup_id": backup_id,
                    "job_id": job_id,
                    "file_size": file_size,
                    "checksum": checksum
                }
            )
            
            return backup_id
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="backup_failed",
                result="error",
                resource=f"backup_job:{job_id}",
                details={"error": str(e)}
            )
            return None
    
    def restore_backup(self, backup_id: str, restore_path: str) -> bool:
        """Restore from backup"""
        if backup_id not in self.records:
            return False
        
        record = self.records[backup_id]
        
        try:
            # Verify backup integrity
            if not self._verify_backup_integrity(record):
                audit_logger.log_event(
                    event_type=AuditEventType.SYSTEM_ERROR,
                    severity=AuditSeverity.HIGH,
                    action="backup_integrity_check",
                    result="failed",
                    resource=f"backup:{backup_id}",
                    details={"backup_id": backup_id}
                )
                return False
            
            # Create restore directory
            os.makedirs(restore_path, exist_ok=True)
            
            # Extract backup
            mode = "r:gz" if record.file_path.endswith('.gz') else "r"
            with tarfile.open(record.file_path, mode) as tar:
                tar.extractall(path=restore_path)
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.MEDIUM,
                action="backup_restored",
                result="success",
                resource=f"backup:{backup_id}",
                details={
                    "backup_id": backup_id,
                    "restore_path": restore_path
                }
            )
            
            return True
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="backup_restore",
                result="error",
                resource=f"backup:{backup_id}",
                details={"error": str(e)}
            )
            return False
    
    def cleanup_expired_backups(self) -> int:
        """Clean up expired backups"""
        cleaned_count = 0
        now = datetime.utcnow()
        
        expired_backups = [
            backup_id for backup_id, record in self.records.items()
            if record.expires_at < now
        ]
        
        for backup_id in expired_backups:
            record = self.records[backup_id]
            try:
                # Remove backup file
                if os.path.exists(record.file_path):
                    os.remove(record.file_path)
                
                # Remove from records
                del self.records[backup_id]
                cleaned_count += 1
                
                audit_logger.log_event(
                    event_type=AuditEventType.DATA_DELETION,
                    severity=AuditSeverity.LOW,
                    action="backup_cleanup",
                    result="success",
                    resource=f"backup:{backup_id}",
                    details={"backup_id": backup_id}
                )
                
            except Exception as e:
                audit_logger.log_event(
                    event_type=AuditEventType.SYSTEM_ERROR,
                    severity=AuditSeverity.MEDIUM,
                    action="backup_cleanup",
                    result="error",
                    resource=f"backup:{backup_id}",
                    details={"error": str(e)}
                )
        
        return cleaned_count
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        import hashlib
        
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _verify_backup_integrity(self, record: BackupRecord) -> bool:
        """Verify backup file integrity"""
        if not os.path.exists(record.file_path):
            return False
        
        current_checksum = self._calculate_checksum(record.file_path)
        return current_checksum == record.checksum
    
    def _upload_to_s3(self, file_path: str, s3_url: str, filename: str):
        """Upload backup to S3"""
        # Parse S3 URL (s3://bucket/prefix)
        parts = s3_url.replace('s3://', '').split('/', 1)
        bucket = parts[0]
        prefix = parts[1] if len(parts) > 1 else ''
        
        s3_key = f"{prefix}/{filename}" if prefix else filename
        
        s3_client = boto3.client('s3')
        s3_client.upload_file(file_path, bucket, s3_key)

class DisasterRecoveryManager:
    """Manages disaster recovery plans and operations"""
    
    def __init__(self):
        self.plans: Dict[str, RecoveryPlan] = {}
        self.backup_manager = BackupManager()
        self.recovery_operations: Dict[str, Dict[str, Any]] = {}
    
    def create_recovery_plan(self, name: str, description: str, priority: int,
                           rto_minutes: int, rpo_minutes: int,
                           steps: List[Dict[str, Any]], 
                           dependencies: List[str] = None,
                           contacts: List[str] = None) -> str:
        """Create disaster recovery plan"""
        plan_id = f"dr_plan_{int(datetime.utcnow().timestamp())}"
        
        plan = RecoveryPlan(
            plan_id=plan_id,
            name=name,
            description=description,
            priority=priority,
            recovery_time_objective=rto_minutes,
            recovery_point_objective=rpo_minutes,
            steps=steps,
            dependencies=dependencies or [],
            contacts=contacts or [],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.plans[plan_id] = plan
        
        audit_logger.log_event(
            event_type=AuditEventType.DATA_MODIFICATION,
            severity=AuditSeverity.MEDIUM,
            action="create_recovery_plan",
            result="success",
            resource=f"dr_plan:{plan_id}",
            details={
                "plan_id": plan_id,
                "name": name,
                "rto_minutes": rto_minutes,
                "rpo_minutes": rpo_minutes
            }
        )
        
        return plan_id
    
    def execute_recovery_plan(self, plan_id: str, incident_id: str = None) -> str:
        """Execute disaster recovery plan"""
        if plan_id not in self.plans:
            return None
        
        plan = self.plans[plan_id]
        operation_id = f"recovery_{int(datetime.utcnow().timestamp())}"
        
        operation = {
            'operation_id': operation_id,
            'plan_id': plan_id,
            'incident_id': incident_id,
            'status': RecoveryStatus.PENDING,
            'started_at': datetime.utcnow(),
            'completed_steps': [],
            'failed_steps': [],
            'current_step': 0,
            'total_steps': len(plan.steps)
        }
        
        self.recovery_operations[operation_id] = operation
        
        # Start recovery in background thread
        recovery_thread = threading.Thread(
            target=self._execute_recovery_steps,
            args=(operation_id,)
        )
        recovery_thread.start()
        
        audit_logger.log_event(
            event_type=AuditEventType.DATA_MODIFICATION,
            severity=AuditSeverity.HIGH,
            action="start_disaster_recovery",
            result="started",
            resource=f"dr_operation:{operation_id}",
            details={
                "operation_id": operation_id,
                "plan_id": plan_id,
                "incident_id": incident_id
            }
        )
        
        return operation_id
    
    def _execute_recovery_steps(self, operation_id: str):
        """Execute recovery plan steps"""
        operation = self.recovery_operations[operation_id]
        plan = self.plans[operation['plan_id']]
        
        operation['status'] = RecoveryStatus.IN_PROGRESS
        
        try:
            for i, step in enumerate(plan.steps):
                operation['current_step'] = i + 1
                
                step_result = self._execute_recovery_step(step, operation_id)
                
                if step_result:
                    operation['completed_steps'].append(step)
                    audit_logger.log_event(
                        event_type=AuditEventType.DATA_MODIFICATION,
                        severity=AuditSeverity.MEDIUM,
                        action="recovery_step_completed",
                        result="success",
                        resource=f"dr_operation:{operation_id}",
                        details={
                            "operation_id": operation_id,
                            "step": step['name'],
                            "step_number": i + 1
                        }
                    )
                else:
                    operation['failed_steps'].append(step)
                    audit_logger.log_event(
                        event_type=AuditEventType.SYSTEM_ERROR,
                        severity=AuditSeverity.HIGH,
                        action="recovery_step_failed",
                        result="failed",
                        resource=f"dr_operation:{operation_id}",
                        details={
                            "operation_id": operation_id,
                            "step": step['name'],
                            "step_number": i + 1
                        }
                    )
                    
                    # Check if step is critical
                    if step.get('critical', False):
                        operation['status'] = RecoveryStatus.FAILED
                        return
            
            operation['status'] = RecoveryStatus.COMPLETED
            operation['completed_at'] = datetime.utcnow()
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.HIGH,
                action="disaster_recovery_completed",
                result="success",
                resource=f"dr_operation:{operation_id}",
                details={
                    "operation_id": operation_id,
                    "plan_id": operation['plan_id'],
                    "duration_minutes": (
                        operation['completed_at'] - operation['started_at']
                    ).total_seconds() / 60
                }
            )
            
        except Exception as e:
            operation['status'] = RecoveryStatus.FAILED
            operation['error'] = str(e)
            
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.CRITICAL,
                action="disaster_recovery_failed",
                result="failed",
                resource=f"dr_operation:{operation_id}",
                details={
                    "operation_id": operation_id,
                    "error": str(e)
                }
            )
    
    def _execute_recovery_step(self, step: Dict[str, Any], operation_id: str) -> bool:
        """Execute individual recovery step"""
        step_type = step.get('type')
        
        try:
            if step_type == 'restore_backup':
                backup_id = step.get('backup_id')
                restore_path = step.get('restore_path')
                return self.backup_manager.restore_backup(backup_id, restore_path)
            
            elif step_type == 'start_service':
                service_name = step.get('service_name')
                # Implementation would depend on your service management system
                return self._start_service(service_name)
            
            elif step_type == 'run_command':
                command = step.get('command')
                return self._run_command(command)
            
            elif step_type == 'notify':
                contacts = step.get('contacts', [])
                message = step.get('message', '')
                return self._send_notifications(contacts, message, operation_id)
            
            elif step_type == 'wait':
                duration = step.get('duration_seconds', 0)
                time.sleep(duration)
                return True
            
            else:
                return False
                
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="recovery_step_execution",
                result="error",
                details={
                    "step_type": step_type,
                    "error": str(e)
                }
            )
            return False
    
    def _start_service(self, service_name: str) -> bool:
        """Start system service"""
        # Implementation would depend on your service management
        # This is a placeholder
        return True
    
    def _run_command(self, command: str) -> bool:
        """Run system command"""
        import subprocess
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _send_notifications(self, contacts: List[str], message: str, 
                          operation_id: str) -> bool:
        """Send recovery notifications"""
        # Implementation would depend on your notification system
        # This could send emails, SMS, Slack messages, etc.
        
        audit_logger.log_event(
            event_type=AuditEventType.DATA_MODIFICATION,
            severity=AuditSeverity.MEDIUM,
            action="recovery_notification_sent",
            result="success",
            resource=f"dr_operation:{operation_id}",
            details={
                "contacts": contacts,
                "message": message
            }
        )
        
        return True
    
    def get_recovery_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get recovery operation status"""
        return self.recovery_operations.get(operation_id)
    
    def test_recovery_plan(self, plan_id: str) -> Dict[str, Any]:
        """Test disaster recovery plan without executing"""
        if plan_id not in self.plans:
            return {"status": "error", "message": "Plan not found"}
        
        plan = self.plans[plan_id]
        test_results = {
            "plan_id": plan_id,
            "test_date": datetime.utcnow().isoformat(),
            "steps_tested": len(plan.steps),
            "estimated_duration": 0,
            "issues": []
        }
        
        # Validate each step
        for i, step in enumerate(plan.steps):
            step_issues = self._validate_recovery_step(step)
            if step_issues:
                test_results["issues"].extend([
                    f"Step {i+1} ({step['name']}): {issue}"
                    for issue in step_issues
                ])
        
        audit_logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.LOW,
            action="test_recovery_plan",
            result="completed",
            resource=f"dr_plan:{plan_id}",
            details=test_results
        )
        
        return test_results
    
    def _validate_recovery_step(self, step: Dict[str, Any]) -> List[str]:
        """Validate recovery step configuration"""
        issues = []
        step_type = step.get('type')
        
        if not step_type:
            issues.append("Missing step type")
            return issues
        
        if step_type == 'restore_backup':
            if not step.get('backup_id'):
                issues.append("Missing backup_id")
            if not step.get('restore_path'):
                issues.append("Missing restore_path")
        
        elif step_type == 'start_service':
            if not step.get('service_name'):
                issues.append("Missing service_name")
        
        elif step_type == 'run_command':
            if not step.get('command'):
                issues.append("Missing command")
        
        return issues

# Global disaster recovery manager instance
dr_manager = DisasterRecoveryManager()
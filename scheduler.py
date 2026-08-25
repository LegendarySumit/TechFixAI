"""
Background tasks and scheduling for data retention and cleanup.
Runs automatic data deletion based on retention policy.
"""

import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path

from app.core.config import settings
from app.core.metrics import MetricsRecorder
from audit import audit_log_action, cleanup_old_audit_logs


def cleanup_old_audio_files(retention_days: int = None):
    """
    Delete audio files older than the retention period.
    
    Args:
        retention_days: Number of days to retain files (from settings if None)
    """
    if retention_days is None:
        retention_days = settings.DATA_RETENTION_DAYS
    
    cutoff_time = datetime.utcnow() - timedelta(days=retention_days)
    audio_path = Path(settings.AUDIO_STORAGE_PATH)
    
    if not audio_path.exists():
        return 0
    
    deleted_count = 0
    total_size_mb = 0
    
    for file_path in audio_path.glob("*"):
        try:
            # Check file modification time
            mtime = datetime.utcfromtimestamp(file_path.stat().st_mtime)
            if mtime < cutoff_time:
                file_size_bytes = file_path.stat().st_size
                file_path.unlink()
                deleted_count += 1
                total_size_mb += file_size_bytes / (1024 * 1024)
        except Exception as e:
            print(f"⚠️ Error deleting old audio file {file_path}: {str(e)}")
    
    if deleted_count > 0:
        audit_log_action(
            action="CLEANUP_OLD_AUDIO_FILES",
            resource_id="file_system",
            details={
                "deleted_count": deleted_count,
                "total_size_mb": round(total_size_mb, 2),
                "retention_days": retention_days
            }
        )
        print(f"🧹 Cleaned up {deleted_count} old audio files ({total_size_mb:.2f} MB)")

    return deleted_count


def cleanup_old_database_records(retention_days: int = None):
    """
    Delete conversation records older than the retention period from the database.
    
    Args:
        retention_days: Number of days to retain records (from settings if None)
    """
    if retention_days is None:
        retention_days = settings.DATA_RETENTION_DAYS
    
    from app.db.session import SessionLocal
    from app.models.conversation import Conversation
    from app.models.ticket import Ticket
    
    cutoff_datetime = datetime.utcnow() - timedelta(days=retention_days)
    
    db = SessionLocal()
    try:
        # Find old conversations
        old_conversations = db.query(Conversation).filter(
            Conversation.created_at < cutoff_datetime
        ).all()
        
        deleted_count = len(old_conversations)
        
        for conversation in old_conversations:
            # Must delete linked ticket first (it holds the FK to conversations)
            if conversation.ticket:
                db.delete(conversation.ticket)
            db.delete(conversation)
        
        db.commit()
        
        if deleted_count > 0:
            audit_log_action(
                action="CLEANUP_OLD_DATABASE_RECORDS",
                resource_id="database",
                details={
                    "deleted_count": deleted_count,
                    "retention_days": retention_days
                }
            )
            print(f"🧹 Cleaned up {deleted_count} old database records")

        return deleted_count
    
    except Exception as e:
        print(f"❌ Error during database cleanup: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def cleanup_old_audit_records(retention_days: int = None):
    """Delete audit-log entries older than the configured retention period."""
    if retention_days is None:
        retention_days = settings.AUDIT_LOG_RETENTION_DAYS

    removed = cleanup_old_audit_logs(retention_days)
    if removed > 0:
        audit_log_action(
            action="CLEANUP_OLD_AUDIT_LOGS",
            resource_id="audit_log",
            details={
                "deleted_count": removed,
                "retention_days": retention_days,
            },
        )
        print(f"🧹 Cleaned up {removed} old audit log entries")

    return removed


def start_cleanup_scheduler():
    """
    Start background cleanup tasks.
    Runs cleanup daily at midnight UTC.
    """
    def run_daily_cleanup():
        while True:
            try:
                # Calculate time until next midnight UTC
                now = datetime.utcnow()
                next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                seconds_until_midnight = (next_midnight - now).total_seconds()
                
                pass  # Next cleanup scheduled
                MetricsRecorder.set_queue_length(1)
                MetricsRecorder.record_queue_wait("daily_cleanup", seconds_until_midnight)
                
                # Sleep until next midnight
                time.sleep(seconds_until_midnight)
                
                # Run cleanup
                pass  # Running cleanup
                MetricsRecorder.set_queue_length(0)

                step_start = time.time()
                deleted_audio = cleanup_old_audio_files()
                MetricsRecorder.record_cleanup(
                    task_type="audio",
                    duration=time.time() - step_start,
                    items_deleted=deleted_audio,
                    success=True,
                )

                step_start = time.time()
                try:
                    deleted_db = cleanup_old_database_records()
                    MetricsRecorder.record_cleanup(
                        task_type="database",
                        duration=time.time() - step_start,
                        items_deleted=deleted_db,
                        success=True,
                    )
                except Exception:
                    MetricsRecorder.record_cleanup(
                        task_type="database",
                        duration=time.time() - step_start,
                        items_deleted=0,
                        success=False,
                    )

                step_start = time.time()
                deleted_audit = cleanup_old_audit_records()
                MetricsRecorder.record_cleanup(
                    task_type="audit_logs",
                    duration=time.time() - step_start,
                    items_deleted=deleted_audit,
                    success=True,
                )
                
            except Exception as e:
                print(f"❌ Error in cleanup scheduler: {str(e)}")
    
    # Start cleanup thread as daemon
    cleanup_thread = threading.Thread(target=run_daily_cleanup, daemon=True)
    cleanup_thread.start()
    pass  # Scheduler started silently

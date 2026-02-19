"""
Background tasks and scheduling for data retention and cleanup.
Runs automatic data deletion based on retention policy.
"""

import os
import asyncio
import threading
from datetime import datetime, timedelta
from pathlib import Path

from app.core.config import settings
from audit import audit_log_action


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
        return
    
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
    
    cutoff_datetime = datetime.utcnow() - timedelta(days=retention_days)
    
    db = SessionLocal()
    try:
        # Find and delete old conversations
        old_conversations = db.query(Conversation).filter(
            Conversation.created_at < cutoff_datetime
        ).all()
        
        deleted_count = len(old_conversations)
        
        for conversation in old_conversations:
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
    
    except Exception as e:
        print(f"❌ Error during database cleanup: {str(e)}")
        db.rollback()
    finally:
        db.close()


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
                
                print(f"⏰ Next cleanup scheduled in {seconds_until_midnight / 3600:.1f} hours")
                
                # Wait until next midnight
                threading.Event().wait(seconds_until_midnight)
                
                # Run cleanup
                print("🧹 Running scheduled data cleanup...")
                cleanup_old_audio_files()
                cleanup_old_database_records()
                
            except Exception as e:
                print(f"❌ Error in cleanup scheduler: {str(e)}")
    
    # Start cleanup thread as daemon
    cleanup_thread = threading.Thread(target=run_daily_cleanup, daemon=True)
    cleanup_thread.start()
    print(f"✅ Data retention cleanup scheduler started (retention: {settings.DATA_RETENTION_DAYS} days)")

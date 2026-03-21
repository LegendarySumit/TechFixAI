"""
Health check endpoint with dependency status.
Returns 200 if healthy, 503 if any dependency unhealthy.
"""

import time
from typing import Dict, Any
from enum import Enum
from datetime import datetime
from sqlalchemy import text


class HealthStatus(str, Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    """Health check for service dependencies."""
    
    @staticmethod
    async def check_database() -> Dict[str, Any]:
        """Check database connectivity."""
        start = time.time()
        try:
            from app.db.session import SessionLocal
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            duration = time.time() - start
            return {
                "status": "up",
                "duration_seconds": duration,
            }
        except Exception as e:
            return {
                "status": "down",
                "error": str(e),
                "duration_seconds": time.time() - start,
            }
    
    @staticmethod
    async def check_filesystem() -> Dict[str, Any]:
        """Check filesystem accessibility."""
        import os
        from pathlib import Path
        from app.core.config import settings
        
        start = time.time()
        try:
            audio_path = Path(settings.AUDIO_STORAGE_PATH)
            # Check if directory exists and is writable
            if not audio_path.exists():
                audio_path.mkdir(parents=True, exist_ok=True)
            
            # Try to create a temporary test file
            test_file = audio_path / ".health_check_test"
            test_file.write_text("test")
            test_file.unlink()
            
            duration = time.time() - start
            return {
                "status": "up",
                "path": str(audio_path),
                "duration_seconds": duration,
            }
        except Exception as e:
            return {
                "status": "down",
                "error": str(e),
                "duration_seconds": time.time() - start,
            }
    
    @staticmethod
    async def check_api_keys() -> Dict[str, Any]:
        """Check API key configuration."""
        from app.core.config import settings

        keys = {
            "groq": bool(settings.GROQ_API_KEY),
            "google_oauth": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        }

        # CAPTCHA secret is required only when CAPTCHA protection is enabled.
        if settings.CAPTCHA_ENABLED:
            keys["captcha"] = bool(settings.CAPTCHA_SECRET_KEY)

        missing = [k for k, v in keys.items() if not v]
        
        return {
            "status": "up" if not missing else ("degraded" if len(missing) <= 1 else "down"),
            "configured": {k: v for k, v in keys.items() if v},
            "missing": missing,
        }
    
    @staticmethod
    async def get_health_status() -> Dict[str, Any]:
        """Get overall health status."""
        checks = {
            "database": await HealthChecker.check_database(),
            "filesystem": await HealthChecker.check_filesystem(),
            "api_keys": await HealthChecker.check_api_keys(),
        }
        
        # Determine overall status
        statuses = [check.get("status") for check in checks.values()]
        
        if "down" in statuses:
            overall_status = HealthStatus.UNHEALTHY
        elif "degraded" in statuses:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0",
            "dependencies": checks,
        }

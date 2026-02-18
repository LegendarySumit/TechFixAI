"""
Quick verification script to check if the system is properly configured.
"""

import sys
import os


def check_mark(condition, message):
    """Print check mark or X based on condition."""
    symbol = "✅" if condition else "❌"
    print(f"{symbol} {message}")
    return condition


def main():
    """Run system checks."""
    print("\n" + "="*60)
    print("VOICE-TO-TICKET AI - SYSTEM VERIFICATION")
    print("="*60 + "\n")
    
    all_checks_passed = True
    
    # Check 1: Python version
    python_ok = check_mark(
        sys.version_info >= (3, 10),
        f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    all_checks_passed &= python_ok
    
    # Check 2: Virtual environment
    venv_ok = check_mark(
        sys.prefix != sys.base_prefix,
        "Running in virtual environment"
    )
    all_checks_passed &= venv_ok
    
    # Check 3: Required packages
    try:
        import fastapi
        import sqlalchemy
        import whisper
        import openai
        packages_ok = True
    except ImportError as e:
        packages_ok = False
    
    all_checks_passed &= check_mark(
        packages_ok,
        "Required packages installed"
    )
    
    # Check 4: Environment file
    env_ok = check_mark(
        os.path.exists(".env"),
        ".env file exists"
    )
    all_checks_passed &= env_ok
    
    # Check 5: Storage directory
    storage_ok = check_mark(
        os.path.exists("storage/audio"),
        "Storage directory exists"
    )
    all_checks_passed &= storage_ok
    
    # Check 6: Environment variables
    if env_ok:
        from dotenv import load_dotenv
        load_dotenv()
        
        openai_key = os.getenv("OPENAI_API_KEY")
        db_url = os.getenv("DATABASE_URL")
        
        check_mark(
            openai_key and openai_key != "sk-your-openai-api-key-here",
            "OPENAI_API_KEY configured"
        )
        
        check_mark(
            db_url and db_url != "postgresql://user:password@localhost:5432/voice_ticket_db",
            "DATABASE_URL configured"
        )
    
    # Check 7: Application structure
    required_files = [
        "app/main.py",
        "app/core/config.py",
        "app/models/ticket.py",
        "app/services/stt_service.py",
        "app/api/voice.py"
    ]
    
    structure_ok = all(os.path.exists(f) for f in required_files)
    all_checks_passed &= check_mark(
        structure_ok,
        "Application structure complete"
    )
    
    # Summary
    print("\n" + "="*60)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - System ready to run!")
        print("\nStart the server with:")
        print("  uvicorn app.main:app --reload")
    else:
        print("❌ SOME CHECKS FAILED - Please fix issues above")
        print("\nRun setup script:")
        print("  python setup.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

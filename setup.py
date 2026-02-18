"""
System setup and quick start script.
Run this after cloning the repository.
"""

import os
import subprocess
import sys


def print_step(step_number, message):
    """Print formatted step message."""
    print(f"\n{'='*60}")
    print(f"STEP {step_number}: {message}")
    print('='*60)


def run_command(command, description):
    """Run a shell command with error handling."""
    print(f"\n→ {description}")
    try:
        subprocess.run(command, shell=True, check=True)
        print("✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        return False


def main():
    """Main setup function."""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║         VOICE-TO-TICKET AI SYSTEM - SETUP SCRIPT          ║
║                                                            ║
║  Automated incident intake + routing system                ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check Python version
    print_step(1, "Checking Python version")
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 10:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    else:
        print("❌ Python 3.10+ required")
        return
    
    # Step 2: Create virtual environment
    print_step(2, "Creating virtual environment")
    if not os.path.exists("venv"):
        run_command("python -m venv venv", "Creating venv")
    else:
        print("ℹ️  Virtual environment already exists")
    
    # Step 3: Activate environment message
    print_step(3, "Activate virtual environment")
    if os.name == 'nt':  # Windows
        print("Run: venv\\Scripts\\activate")
    else:  # Unix/MacOS
        print("Run: source venv/bin/activate")
    
    print("\n⚠️  Please activate the virtual environment and run this script again")
    
    # Check if running in venv
    if sys.prefix == sys.base_prefix:
        print("\n❌ Not running in virtual environment. Please activate and retry.")
        return
    
    # Step 4: Install dependencies
    print_step(4, "Installing dependencies")
    run_command("pip install --upgrade pip", "Upgrading pip")
    run_command("pip install -r requirements.txt", "Installing requirements")
    
    # Step 5: Create .env file
    print_step(5, "Setting up environment configuration")
    if not os.path.exists(".env"):
        import shutil
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file from .env.example")
        print("⚠️  IMPORTANT: Edit .env and add your API keys!")
    else:
        print("ℹ️  .env file already exists")
    
    # Step 6: Create storage directories
    print_step(6, "Creating storage directories")
    os.makedirs("storage/audio", exist_ok=True)
    print("✅ Storage directories created")
    
    # Step 7: Database setup instructions
    print_step(7, "Database setup")
    print("""
To set up the database:

1. Install PostgreSQL if not already installed
2. Create database:
   createdb voice_ticket_db

3. Run database initialization:
   python -m app.db.init_db

4. (Optional) Set up migrations:
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
    """)
    
    # Step 8: Download Whisper model
    print_step(8, "Downloading Whisper model (optional, will download on first use)")
    download_whisper = input("Download Whisper 'base' model now? (y/n): ")
    if download_whisper.lower() == 'y':
        print("Downloading... (this may take a few minutes)")
        run_command(
            'python -c "import whisper; whisper.load_model(\'base\')"',
            "Downloading Whisper model"
        )
    
    # Final instructions
    print(f"\n{'='*60}")
    print("🎉 SETUP COMPLETE!")
    print('='*60)
    print("""
Next steps:

1. Edit .env and add your API keys (OPENAI_API_KEY, etc.)
2. Set up the database (see STEP 7 above)
3. Run the application:
   uvicorn app.main:app --reload

4. Access API documentation:
   http://localhost:8000/docs

5. Read README.md for detailed usage instructions

Happy coding! 🚀
    """)


if __name__ == "__main__":
    main()

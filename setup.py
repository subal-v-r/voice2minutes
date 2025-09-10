#!/usr/bin/env python3
"""
Setup script for Smart Meeting Minutes Generator
Automates the installation and configuration process
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = "venv"
    
    if os.path.exists(venv_path):
        print(f"✓ Virtual environment already exists at {venv_path}")
        return True
    
    return run_command(f"python -m venv {venv_path}", "Creating virtual environment")

def get_activation_command():
    """Get the correct activation command for the platform"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Install Python dependencies"""
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu", "Installing PyTorch (CPU)"),
        ("pip install -r requirements.txt", "Installing requirements"),
        ("python -m spacy download en_core_web_sm", "Installing spaCy English model")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def setup_environment_file():
    """Create .env file template"""
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"✓ Environment file {env_file} already exists")
        return True
    
    env_template = """# Smart Meeting Minutes Generator Environment Variables

# Required for speaker diarization (get from https://huggingface.co/settings/tokens)
HUGGINGFACE_TOKEN=your_huggingface_token_here

# Optional API keys for future features
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_template)
        print(f"✓ Created environment file template: {env_file}")
        print("  Please edit this file and add your HuggingFace token")
        return True
    except Exception as e:
        print(f"✗ Failed to create environment file: {e}")
        return False

def setup_database():
    """Initialize the database"""
    return run_command("python scripts/run_database_setup.py", "Setting up database")

def create_directories():
    """Create necessary directories"""
    directories = ["uploads", "outputs", "models"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    return True

def main():
    """Main setup function"""
    print("Smart Meeting Minutes Generator - Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("✗ Failed to create virtual environment")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("✗ Failed to create directories")
        sys.exit(1)
    
    # Setup environment file
    if not setup_environment_file():
        print("✗ Failed to setup environment file")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    print(f"   {get_activation_command()}")
    print("\n2. Edit .env file and add your HuggingFace token")
    print("\n3. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("   python -m spacy download en_core_web_sm")
    print("\n4. Initialize database:")
    print("   python scripts/run_database_setup.py")
    print("\n5. Start the application:")
    print("   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload")
    print("\n6. Open http://127.0.0.1:8000 in your browser")
    
    print("\nFor detailed instructions, see run_instructions.txt")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Setup script for Apple Photos Management Tool.

This script provides automated setup and installation functionality
for the Apple Photos Management Tool.

Author: AI Assistant
Version: 2.0.0
License: MIT
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def run_command(command: List[str], cwd: Optional[Path] = None) -> bool:
    """
    Run a command and return success status.
    
    Args:
        command: Command to run as list of strings
        cwd: Working directory for the command
        
    Returns:
        True if command succeeded, False otherwise
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {command[0]} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command[0]} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {command[0]}")
        return False


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True


def check_pip() -> bool:
    """Check if pip is available."""
    print("📦 Checking pip...")
    
    try:
        import pip
        print("✅ pip is available")
        return True
    except ImportError:
        print("❌ pip not found")
        return False


def create_virtual_environment(venv_path: Path) -> bool:
    """Create virtual environment."""
    print(f"🔧 Creating virtual environment at {venv_path}...")
    
    if venv_path.exists():
        print(f"⚠️  Virtual environment already exists at {venv_path}")
        return True
    
    return run_command([sys.executable, "-m", "venv", str(venv_path)])


def activate_virtual_environment(venv_path: Path) -> str:
    """Get virtual environment activation command."""
    if os.name == 'nt':  # Windows
        return str(venv_path / "Scripts" / "activate")
    else:  # Unix-like
        return f"source {venv_path / 'bin' / 'activate'}"


def install_dependencies(venv_path: Path) -> bool:
    """Install Python dependencies."""
    print("📚 Installing dependencies...")
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip"
    else:  # Unix-like
        pip_path = venv_path / "bin" / "pip"
    
    # Upgrade pip first
    if not run_command([str(pip_path), "install", "--upgrade", "pip"]):
        return False
    
    # Install requirements
    requirements_file = Path(__file__).parent.parent / "requirements.txt"
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    return run_command([str(pip_path), "install", "-r", str(requirements_file)])


def create_env_file(project_root: Path) -> bool:
    """Create .env file from template."""
    print("⚙️  Creating .env file...")
    
    env_file = project_root / ".env"
    env_example = project_root / "env.example"
    
    if env_file.exists():
        print(f"⚠️  .env file already exists at {env_file}")
        return True
    
    if not env_example.exists():
        print(f"❌ Environment template not found: {env_example}")
        return False
    
    try:
        # Copy example to .env
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        
        print(f"✅ Created .env file at {env_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def create_directories(project_root: Path) -> bool:
    """Create necessary directories."""
    print("📁 Creating project directories...")
    
    directories = [
        "output",
        "output/reports",
        "logs",
        "temp"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True


def run_tests(venv_path: Path) -> bool:
    """Run test suite."""
    print("🧪 Running tests...")
    
    # Determine python path
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python"
    else:  # Unix-like
        python_path = venv_path / "bin" / "python"
    
    project_root = Path(__file__).parent.parent
    
    return run_command([
        str(python_path), "-m", "pytest", "tests/", "-v", "--tb=short"
    ], cwd=project_root)


def create_launcher_scripts(project_root: Path, venv_path: Path) -> bool:
    """Create launcher scripts for different platforms."""
    print("🚀 Creating launcher scripts...")
    
    # Get activation command
    activation_cmd = activate_virtual_environment(venv_path)
    
    # Create shell script for Unix-like systems
    shell_script = project_root / "run.sh"
    try:
        with open(shell_script, 'w') as f:
            f.write(f"""#!/bin/bash
# Apple Photos Management Tool Launcher

# Activate virtual environment
{activation_cmd}

# Run the application
python main.py "$@"
""")
        shell_script.chmod(0o755)
        print(f"✅ Created launcher script: {shell_script}")
    except Exception as e:
        print(f"❌ Failed to create shell launcher: {e}")
        return False
    
    # Create batch script for Windows
    batch_script = project_root / "run.bat"
    try:
        with open(batch_script, 'w') as f:
            f.write(f"""@echo off
REM Apple Photos Management Tool Launcher

REM Activate virtual environment
call {venv_path / "Scripts" / "activate.bat"}

REM Run the application
python main.py %*
""")
        print(f"✅ Created launcher script: {batch_script}")
    except Exception as e:
        print(f"❌ Failed to create batch launcher: {e}")
        return False
    
    return True


def print_setup_summary(project_root: Path, venv_path: Path):
    """Print setup completion summary."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"📁 Project directory: {project_root}")
    print(f"🐍 Virtual environment: {venv_path}")
    print(f"⚙️  Configuration: {project_root / '.env'}")
    print("\n🚀 Quick Start:")
    print(f"1. Activate virtual environment:")
    print(f"   {activate_virtual_environment(venv_path)}")
    print("\n2. Run the application:")
    print("   python main.py --help")
    print("\n3. Or use launcher scripts:")
    print("   ./run.sh --help  (Unix/Linux/Mac)")
    print("   run.bat --help   (Windows)")
    print("\n📚 Documentation:")
    print("   README.md - Main documentation")
    print("   docs/ - Detailed documentation")
    print("\n🧪 Testing:")
    print("   python -m pytest tests/ -v")
    print("\n" + "="*60)


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description="Setup Apple Photos Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup.py                    # Full setup
  python setup.py --no-tests        # Skip running tests
  python setup.py --venv-path ./venv # Custom venv location
        """
    )
    
    parser.add_argument(
        '--venv-path',
        type=Path,
        default=Path('venv'),
        help='Virtual environment path (default: ./venv)'
    )
    
    parser.add_argument(
        '--no-tests',
        action='store_true',
        help='Skip running tests during setup'
    )
    
    parser.add_argument(
        '--no-deps',
        action='store_true',
        help='Skip dependency installation'
    )
    
    args = parser.parse_args()
    
    print("🚀 Apple Photos Management Tool Setup")
    print("="*40)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment(args.venv_path):
        sys.exit(1)
    
    # Install dependencies
    if not args.no_deps:
        if not install_dependencies(args.venv_path):
            sys.exit(1)
    
    # Create project structure
    if not create_directories(project_root):
        sys.exit(1)
    
    # Create configuration
    if not create_env_file(project_root):
        sys.exit(1)
    
    # Create launcher scripts
    if not create_launcher_scripts(project_root, args.venv_path):
        sys.exit(1)
    
    # Run tests
    if not args.no_tests:
        if not run_tests(args.venv_path):
            print("⚠️  Tests failed, but setup completed")
    
    # Print summary
    print_setup_summary(project_root, args.venv_path)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Deployment script for Apple Photos Management Tool.

This script provides automated deployment functionality
for the Apple Photos Management Tool.

Author: AI Assistant
Version: 2.0.0
License: MIT
"""

import argparse
import json
import shutil
import subprocess
import sys
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


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


def get_version() -> str:
    """Get current version from main.py."""
    main_py = Path(__file__).parent.parent / "main.py"
    
    try:
        with open(main_py, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if 'Version:' in line:
                    return line.split('Version:')[1].strip()
    except Exception:
        pass
    
    return "2.0.0"


def create_build_info(project_root: Path) -> Dict[str, str]:
    """Create build information."""
    return {
        "version": get_version(),
        "build_date": datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": sys.platform,
        "build_type": "production"
    }


def clean_build_directory(build_dir: Path) -> bool:
    """Clean build directory."""
    print(f"🧹 Cleaning build directory: {build_dir}")
    
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
        except Exception as e:
            print(f"❌ Failed to clean build directory: {e}")
            return False
    
    try:
        build_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created build directory: {build_dir}")
        return True
    except Exception as e:
        print(f"❌ Failed to create build directory: {e}")
        return False


def copy_source_files(project_root: Path, build_dir: Path) -> bool:
    """Copy source files to build directory."""
    print("📁 Copying source files...")
    
    # Files and directories to include
    include_items = [
        "main.py",
        "requirements.txt",
        "README.md",
        "env.example",
        ".gitignore",
        "src/",
        "docs/",
        "examples/",
        "tests/",
        "scripts/"
    ]
    
    # Files and directories to exclude
    exclude_items = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".git",
        ".pytest_cache",
        "venv",
        "build",
        "dist",
        "*.egg-info",
        ".env",
        "logs",
        "temp",
        "output"
    ]
    
    try:
        for item in include_items:
            src = project_root / item
            dst = build_dir / item
            
            if src.is_file():
                shutil.copy2(src, dst)
                print(f"✅ Copied file: {item}")
            elif src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*exclude_items))
                print(f"✅ Copied directory: {item}")
            else:
                print(f"⚠️  Item not found: {item}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to copy source files: {e}")
        return False


def create_launcher_scripts(build_dir: Path) -> bool:
    """Create launcher scripts for different platforms."""
    print("🚀 Creating launcher scripts...")
    
    # Unix/Linux/Mac launcher
    unix_launcher = build_dir / "run.sh"
    try:
        with open(unix_launcher, 'w') as f:
            f.write("""#!/bin/bash
# Apple Photos Management Tool Launcher

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    echo "   python scripts/setup.py"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the application
python main.py "$@"
""")
        unix_launcher.chmod(0o755)
        print("✅ Created Unix launcher: run.sh")
    except Exception as e:
        print(f"❌ Failed to create Unix launcher: {e}")
        return False
    
    # Windows launcher
    windows_launcher = build_dir / "run.bat"
    try:
        with open(windows_launcher, 'w') as f:
            f.write("""@echo off
REM Apple Photos Management Tool Launcher

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup first.
    echo    python scripts/setup.py
    exit /b 1
)

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Run the application
python main.py %*
""")
        print("✅ Created Windows launcher: run.bat")
    except Exception as e:
        print(f"❌ Failed to create Windows launcher: {e}")
        return False
    
    return True


def create_installer_script(build_dir: Path) -> bool:
    """Create installer script."""
    print("📦 Creating installer script...")
    
    installer = build_dir / "install.py"
    try:
        with open(installer, 'w') as f:
            f.write("""#!/usr/bin/env python3
\"\"\"
Installer for Apple Photos Management Tool.

This script installs the Apple Photos Management Tool
on the target system.

Author: AI Assistant
Version: 2.0.0
License: MIT
\"\"\"

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Apple Photos Management Tool Installer")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    
    # Run setup script
    setup_script = Path(__file__).parent / "scripts" / "setup.py"
    if not setup_script.exists():
        print("❌ Setup script not found")
        sys.exit(1)
    
    print("🔧 Running setup...")
    result = subprocess.run([sys.executable, str(setup_script)])
    
    if result.returncode == 0:
        print("✅ Installation completed successfully!")
        print("\\n🚀 Quick Start:")
        print("   python main.py --help")
        print("   ./run.sh --help  (Unix/Linux/Mac)")
        print("   run.bat --help   (Windows)")
    else:
        print("❌ Installation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
""")
        installer.chmod(0o755)
        print("✅ Created installer script: install.py")
        return True
    except Exception as e:
        print(f"❌ Failed to create installer script: {e}")
        return False


def create_dockerfile(build_dir: Path) -> bool:
    """Create Dockerfile for containerization."""
    print("🐳 Creating Dockerfile...")
    
    dockerfile = build_dir / "Dockerfile"
    try:
        with open(dockerfile, 'w') as f:
            f.write("""# Apple Photos Management Tool Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    libheif-dev \\
    libjpeg-dev \\
    libpng-dev \\
    libtiff-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port (if needed for web interface)
EXPOSE 8000

# Default command
CMD ["python", "main.py", "--help"]
""")
        print("✅ Created Dockerfile")
        return True
    except Exception as e:
        print(f"❌ Failed to create Dockerfile: {e}")
        return False


def create_docker_compose(build_dir: Path) -> bool:
    """Create docker-compose.yml for easy deployment."""
    print("🐳 Creating docker-compose.yml...")
    
    compose_file = build_dir / "docker-compose.yml"
    try:
        with open(compose_file, 'w') as f:
            f.write("""version: '3.8'

services:
  apple-photos-management:
    build: .
    container_name: apple-photos-management
    volumes:
      - ./input:/app/input:ro
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - LOG_LEVEL=INFO
      - EXPORT_WORKERS=4
      - EXPORT_BATCH_SIZE=50
    command: ["python", "main.py", "run", "/app/input", "/app/output"]
    restart: unless-stopped

  # Optional: Web interface (if implemented)
  # web:
  #   build: .
  #   container_name: apple-photos-management-web
  #   ports:
  #     - "8000:8000"
  #   volumes:
  #     - ./input:/app/input:ro
  #     - ./output:/app/output
  #     - ./logs:/app/logs
  #   environment:
  #     - LOG_LEVEL=INFO
  #   command: ["python", "web_app.py"]
  #   restart: unless-stopped
""")
        print("✅ Created docker-compose.yml")
        return True
    except Exception as e:
        print(f"❌ Failed to create docker-compose.yml: {e}")
        return False


def create_package_archive(build_dir: Path, output_dir: Path, format: str = "tar.gz") -> bool:
    """Create package archive."""
    print(f"📦 Creating {format} archive...")
    
    version = get_version()
    archive_name = f"apple-photos-management-{version}.{format}"
    archive_path = output_dir / archive_name
    
    try:
        if format == "tar.gz":
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(build_dir, arcname=f"apple-photos-management-{version}")
        elif format == "zip":
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(build_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(build_dir)
                        zipf.write(file_path, arcname)
        
        print(f"✅ Created archive: {archive_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create archive: {e}")
        return False


def create_checksums(output_dir: Path) -> bool:
    """Create checksums for all files in output directory."""
    print("🔐 Creating checksums...")
    
    try:
        checksums = {}
        
        for file_path in output_dir.iterdir():
            if file_path.is_file():
                with open(file_path, 'rb') as f:
                    content = f.read()
                    checksum = hashlib.sha256(content).hexdigest()
                    checksums[file_path.name] = checksum
        
        checksum_file = output_dir / "checksums.sha256"
        with open(checksum_file, 'w') as f:
            for filename, checksum in checksums.items():
                f.write(f"{checksum}  {filename}\\n")
        
        print(f"✅ Created checksums: {checksum_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create checksums: {e}")
        return False


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(
        description="Deploy Apple Photos Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deploy.py                    # Full deployment
  python deploy.py --format zip      # Create ZIP archive
  python deploy.py --no-docker       # Skip Docker files
  python deploy.py --output ./dist   # Custom output directory
        """
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('dist'),
        help='Output directory for deployment packages (default: ./dist)'
    )
    
    parser.add_argument(
        '--format',
        choices=['tar.gz', 'zip'],
        default='tar.gz',
        help='Archive format (default: tar.gz)'
    )
    
    parser.add_argument(
        '--no-docker',
        action='store_true',
        help='Skip creating Docker files'
    )
    
    parser.add_argument(
        '--no-archive',
        action='store_true',
        help='Skip creating archive'
    )
    
    args = parser.parse_args()
    
    print("🚀 Apple Photos Management Tool Deployment")
    print("=" * 45)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    build_dir = project_root / "build"
    
    # Create output directory
    try:
        args.output.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created output directory: {args.output}")
    except Exception as e:
        print(f"❌ Failed to create output directory: {e}")
        sys.exit(1)
    
    # Clean and create build directory
    if not clean_build_directory(build_dir):
        sys.exit(1)
    
    # Copy source files
    if not copy_source_files(project_root, build_dir):
        sys.exit(1)
    
    # Create launcher scripts
    if not create_launcher_scripts(build_dir):
        sys.exit(1)
    
    # Create installer script
    if not create_installer_script(build_dir):
        sys.exit(1)
    
    # Create Docker files
    if not args.no_docker:
        if not create_dockerfile(build_dir):
            sys.exit(1)
        
        if not create_docker_compose(build_dir):
            sys.exit(1)
    
    # Create package archive
    if not args.no_archive:
        if not create_package_archive(build_dir, args.output, args.format):
            sys.exit(1)
    
    # Create checksums
    if not create_checksums(args.output):
        sys.exit(1)
    
    # Print deployment summary
    print("\\n" + "="*60)
    print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"📁 Build directory: {build_dir}")
    print(f"📦 Output directory: {args.output}")
    print(f"📋 Archive format: {args.format}")
    print(f"🐳 Docker files: {'Created' if not args.no_docker else 'Skipped'}")
    print("\\n📚 Deployment packages:")
    for file_path in args.output.iterdir():
        if file_path.is_file():
            size = file_path.stat().st_size
            size_str = f"{size / 1024 / 1024:.1f} MB" if size > 1024*1024 else f"{size / 1024:.1f} KB"
            print(f"   {file_path.name} ({size_str})")
    print("\\n" + "="*60)


if __name__ == "__main__":
    main()

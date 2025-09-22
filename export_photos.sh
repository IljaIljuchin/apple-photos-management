#!/bin/bash

# Apple Photos Export Tool - Shell Wrapper
# Usage: ./export_photos.sh [source_dir] [target_dir] [run_mode]
#   source_dir: Directory with exported photos and XMP files (optional, defaults to current dir)
#   target_dir: Directory where organized photos will be saved (optional, defaults to current dir)
#   run_mode: "run" to execute, anything else or empty for dry-run test

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/export_photos.py"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Python script exists
check_python_script() {
    if [[ ! -f "$PYTHON_SCRIPT" ]]; then
        print_error "Python script not found: $PYTHON_SCRIPT"
        exit 1
    fi
}

# Function to check if directory exists
check_directory() {
    local dir="$1"
    local description="$2"
    
    if [[ ! -d "$dir" ]]; then
        print_error "$description does not exist: $dir"
        exit 1
    fi
    
    if [[ ! -r "$dir" ]]; then
        print_error "$description is not readable: $dir"
        exit 1
    fi
}

# Function to check Python dependencies
check_dependencies() {
    print_info "Checking Python dependencies..."
    
    if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        print_error "Python 3.8+ is required"
        exit 1
    fi
    
    # Check if required packages are installed
    local missing_packages=()
    local packages=("PIL" "lxml" "dateutil" "colorlog" "tqdm")
    
    for package in "${packages[@]}"; do
        if ! python3 -c "import $package" 2>/dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [[ ${#missing_packages[@]} -gt 0 ]]; then
        print_warning "Missing Python packages: ${missing_packages[*]}"
        print_info "Installing missing packages..."
        pip3 install -r "$SCRIPT_DIR/requirements.txt" --user
    fi
}

# Function to show usage
show_usage() {
    echo "Apple Photos Export Tool"
    echo ""
    echo "Usage: $0 [source_dir] [target_dir] [run_mode]"
    echo ""
    echo "Arguments:"
    echo "  source_dir  Directory with exported photos and XMP files (optional, defaults to current dir)"
    echo "  target_dir  Directory where organized photos will be saved (optional, defaults to current dir)"
    echo "  run_mode    'run' to execute, anything else or empty for dry-run test"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Dry-run in current directory"
    echo "  $0 /path/to/photos /path/to/output   # Dry-run with specified directories"
    echo "  $0 /path/to/photos /path/to/output run  # Execute with specified directories"
    echo ""
    echo "The tool will:"
    echo "  - Read photos and XMP files from source directory"
    echo "  - Extract creation dates from EXIF and XMP metadata"
    echo "  - Choose earlier date between EXIF and XMP"
    echo "  - Organize photos into YEAR/MM/DD structure"
    echo "  - Rename files to YYYYMMDD-HHMMSS-SSS.ext format"
    echo "  - Handle duplicates with sequential numbering"
}

# Main function
main() {
    # Check if help is requested
    if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
        show_usage
        exit 0
    fi
    
    # Check Python script exists
    check_python_script
    
    # Check dependencies
    check_dependencies
    
    # Parse arguments
    local source_dir="${1:-$(pwd)}"
    local target_dir="${2:-$(pwd)}"
    local run_mode="${3:-test}"
    
    # Validate source directory
    check_directory "$source_dir" "Source directory"
    
    # Create target directory if it doesn't exist
    if [[ ! -d "$target_dir" ]]; then
        print_info "Target directory does not exist, creating: $target_dir"
        mkdir -p "$target_dir"
        if [[ $? -eq 0 ]]; then
            print_success "Target directory created successfully"
        else
            print_error "Failed to create target directory: $target_dir"
            exit 1
        fi
    else
        print_info "Using existing target directory: $target_dir"
    fi
    
    # Check if target directory is writable
    if [[ ! -w "$target_dir" ]]; then
        print_error "Target directory is not writable: $target_dir"
        exit 1
    fi
    
    # Determine if this is a dry-run or actual run
    local is_dry_run="true"
    if [[ "$run_mode" == "run" ]]; then
        is_dry_run="false"
        print_warning "EXECUTING ACTUAL EXPORT - This will create and copy files!"
    else
        print_info "DRY-RUN MODE - No files will be created or copied"
    fi
    
    # Show configuration
    print_info "Configuration:"
    print_info "  Source directory: $source_dir"
    print_info "  Target directory: $target_dir"
    print_info "  Mode: $([ "$is_dry_run" == "true" ] && echo "DRY-RUN" || echo "EXECUTE")"
    print_info "  Python script: $PYTHON_SCRIPT"
    
    # Run Python script
    print_info "Starting photo export process..."
    echo ""
    
    if python3 "$PYTHON_SCRIPT" "$source_dir" "$target_dir" "$is_dry_run"; then
        print_success "Photo export process completed successfully!"
    else
        print_error "Photo export process failed!"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"

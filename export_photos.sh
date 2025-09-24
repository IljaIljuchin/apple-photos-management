#!/bin/bash

# Apple Photos Export Tool - Shell Wrapper
# Usage: ./export_photos.sh [mode] <input_directory>
#   mode: run, delete, help, or dry (optional, defaults to help)
#   input_directory: Directory with exported photos and XMP files (required)
#   output_directory: Always input_directory + "_export" (automatic)

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/src/core/export_photos.py"

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
    local packages=("PIL" "lxml" "dateutil" "loguru" "tqdm")
    
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
    echo "Usage: $0 [mode] <input_directory>"
    echo ""
    echo "Arguments:"
    echo "  mode            run, delete, help, or dry (optional, defaults to help)"
    echo "  input_directory Directory with exported photos and XMP files (required)"
    echo ""
    echo "Output:"
    echo "  output_directory Always input_directory + '_export' (automatic)"
    echo ""
    echo "Modes:"
    echo "  help            Show this help message"
    echo "  dry             Dry-run test (no files created or modified)"
    echo "  run             Execute actual export (creates organized photos)"
    echo "  delete          Remove duplicates from output directory only"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Show help"
    echo "  $0 help                               # Show help"
    echo "  $0 dry /path/to/photos                # Dry-run test"
    echo "  $0 run /path/to/photos                # Execute export to /path/to/photos_export"
    echo "  $0 delete /path/to/photos             # Remove duplicates from /path/to/photos_export"
    echo ""
    echo "The tool will:"
    echo "  - Read photos and XMP files from input directory (READ-ONLY)"
    echo "  - Extract creation dates from EXIF and XMP metadata"
    echo "  - Choose earlier date between EXIF and XMP"
        echo "  - Organize photos into YEAR structure in output directory"
    echo "  - Rename files to YYYYMMDD-HHMMSS-SSS.ext format"
    echo "  - Handle duplicates with sequential numbering"
    echo "  - NEVER modify the input directory"
}

# Main function
main() {
    # Check if help is requested or no arguments provided
    if [[ $# -eq 0 || "${1:-}" == "-h" || "${1:-}" == "--help" || "${1:-}" == "help" ]]; then
        show_usage
        exit 0
    fi
    
    # Check Python script exists
    check_python_script
    
    # Check dependencies
    check_dependencies
    
    # Parse arguments
    local mode="${1:-help}"
    local input_dir="${2:-}"
    
    # Validate mode
    if [[ "$mode" != "run" && "$mode" != "delete" && "$mode" != "dry" && "$mode" != "help" ]]; then
        print_error "Invalid mode: $mode"
        print_error "Valid modes are: run, delete, dry, help"
        show_usage
        exit 1
    fi
    
    # If mode is help, show usage and exit
    if [[ "$mode" == "help" ]]; then
        show_usage
        exit 0
    fi
    
    # Check if input directory is provided
    if [[ -z "$input_dir" ]]; then
        print_error "Input directory is required"
        show_usage
        exit 1
    fi
    
    # Validate input directory
    check_directory "$input_dir" "Input directory"
    
    # Create output directory (input_dir + "_export")
    local output_dir="${input_dir}_export"
    
    # Create output directory if it doesn't exist
    if [[ ! -d "$output_dir" ]]; then
        print_info "Output directory does not exist, creating: $output_dir"
        mkdir -p "$output_dir"
        if [[ $? -eq 0 ]]; then
            print_success "Output directory created successfully"
        else
            print_error "Failed to create output directory: $output_dir"
            exit 1
        fi
    else
        print_info "Using existing output directory: $output_dir"
    fi
    
    # Check if output directory is writable
    if [[ ! -w "$output_dir" ]]; then
        print_error "Output directory is not writable: $output_dir"
        exit 1
    fi
    
    # Determine if this is a dry-run, actual run, or delete mode
    local is_dry_run="true"
    local duplicate_strategy="keep_first"
    
    if [[ "$mode" == "run" ]]; then
        is_dry_run="false"
        print_warning "EXECUTING ACTUAL EXPORT - This will create and copy files!"
    elif [[ "$mode" == "delete" ]]; then
        is_dry_run="false"
        duplicate_strategy="!delete!"
        print_warning "DELETE DUPLICATES MODE - This will permanently delete duplicate files from OUTPUT directory!"
    else
        print_info "DRY-RUN MODE - No files will be created or copied"
    fi
    
    # Show configuration
    # Determine mode display
    if [[ "$is_dry_run" == "true" ]]; then
        mode_display="DRY-RUN"
    elif [[ "$mode" == "delete" ]]; then
        mode_display="DELETE DUPLICATES"
    else
        mode_display="EXECUTE"
    fi
    
    print_info "Configuration:"
    print_info "  📁 Input: $input_dir (READ-ONLY)"
    print_info "  📁 Output: $output_dir"
    print_info "  ⚙️  Mode: $mode_display"
    
    # Run Python script
    print_info "🚀 Starting photo export process..."
    echo ""
    
    if python3 "$PYTHON_SCRIPT" "$input_dir" "$output_dir" "$is_dry_run" "$duplicate_strategy" --max-workers 8; then
        print_success "✅ Photo export process completed successfully!"
    else
        print_error "❌ Photo export process failed!"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"

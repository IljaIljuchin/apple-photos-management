"""
Utility functions for Apple Photos Management Tool.

This module provides common utility functions used throughout the application,
including file operations, data validation, and helper functions.

Author: AI Assistant
Version: 2.0.0
License: MIT
"""

import hashlib
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from urllib.parse import quote, unquote

from .models import FileType, PhotoMetadata


def calculate_file_hash(file_path: Path, algorithm: str = 'md5', chunk_size: int = 8192) -> str:
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (md5, sha1, sha256)
        chunk_size: Size of chunks to read at a time
        
    Returns:
        Hexadecimal hash string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.is_file():
        raise IOError(f"Path is not a file: {file_path}")
    
    hash_obj = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except IOError as e:
        raise IOError(f"Cannot read file {file_path}: {e}")


def get_file_type_category(file_path: Path) -> FileType:
    """
    Determine file type category based on file extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        FileType enum value
    """
    extension = file_path.suffix.lower()
    
    image_extensions = {'.heic', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.raw', '.cr2', '.nef', '.arw'}
    video_extensions = {'.mov', '.mp4', '.avi', '.mkv', '.m4v'}
    metadata_extensions = {'.xmp', '.aae'}
    
    if extension in image_extensions:
        return FileType.IMAGE
    elif extension in video_extensions:
        return FileType.VIDEO
    elif extension in metadata_extensions:
        return FileType.METADATA
    else:
        return FileType.OTHER


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB", "2.3 GB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(size_bytes)
    i = 0
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    if i == 0:
        return f"{int(size)} {size_names[i]}"
    else:
        return f"{size:.1f} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "2m 30s", "1h 15m")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = seconds % 60
        return f"{hours}h {minutes}m {remaining_seconds:.1f}s"


def format_percentage(value: float, total: float) -> str:
    """
    Format percentage value.
    
    Args:
        value: Current value
        total: Total value
        
    Returns:
        Formatted percentage string (e.g., "75.5%")
    """
    if total == 0:
        return "0.0%"
    
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe filesystem usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'unnamed'
    
    # Limit length (reserve space for extension)
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename


def create_safe_path(base_path: Path, relative_path: str) -> Path:
    """
    Create a safe path by joining base and relative paths.
    
    Args:
        base_path: Base directory path
        relative_path: Relative path string
        
    Returns:
        Safe joined path
        
    Raises:
        ValueError: If path would escape base directory
    """
    # Normalize the relative path
    relative_path = relative_path.strip('/\\')
    
    # Split into parts and filter out empty parts
    parts = [part for part in relative_path.split('/') if part and part != '.']
    
    # Check for path traversal attempts
    if '..' in parts:
        raise ValueError("Path traversal detected in relative path")
    
    # Join the paths
    safe_path = base_path
    for part in parts:
        safe_path = safe_path / part
    
    return safe_path


def ensure_directory_exists(path: Path) -> None:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        path: Directory path to ensure
        
    Raises:
        OSError: If directory cannot be created
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise OSError(f"Cannot create directory {path}: {e}")


def copy_file_safe(source: Path, destination: Path) -> bool:
    """
    Safely copy a file with error handling.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure destination directory exists
        ensure_directory_exists(destination.parent)
        
        # Copy the file
        shutil.copy2(source, destination)
        return True
    except Exception:
        return False


def move_file_safe(source: Path, destination: Path) -> bool:
    """
    Safely move a file with error handling.
    
    Args:
        source: Source file path
        destination: Destination file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure destination directory exists
        ensure_directory_exists(destination.parent)
        
        # Move the file
        shutil.move(str(source), str(destination))
        return True
    except Exception:
        return False


def delete_file_safe(file_path: Path) -> bool:
    """
    Safely delete a file with error handling.
    
    Args:
        file_path: File path to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if file_path.exists():
            file_path.unlink()
        return True
    except Exception:
        return False


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """
    Get comprehensive file information.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    try:
        stat = file_path.stat()
        return {
            'path': str(file_path),
            'name': file_path.name,
            'stem': file_path.stem,
            'suffix': file_path.suffix,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'accessed': datetime.fromtimestamp(stat.st_atime),
            'is_file': file_path.is_file(),
            'is_dir': file_path.is_dir(),
            'exists': file_path.exists(),
            'file_type': get_file_type_category(file_path).value
        }
    except Exception as e:
        return {
            'path': str(file_path),
            'error': str(e),
            'exists': False
        }


def find_files_by_pattern(directory: Path, pattern: str, recursive: bool = True) -> List[Path]:
    """
    Find files matching a pattern in a directory.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern to match
        recursive: Whether to search recursively
        
    Returns:
        List of matching file paths
    """
    if not directory.exists() or not directory.is_dir():
        return []
    
    try:
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))
    except Exception:
        return []


def find_associated_files(photo_path: Path) -> Dict[str, Optional[Path]]:
    """
    Find associated XMP and AAE files for a photo.
    
    Args:
        photo_path: Path to the photo file
        
    Returns:
        Dictionary with 'xmp' and 'aae' keys containing file paths or None
    """
    result = {'xmp': None, 'aae': None}
    
    # Find XMP file
    xmp_patterns = [
        photo_path.with_suffix(photo_path.suffix + '.xmp'),
        photo_path.with_suffix(photo_path.suffix + '.XMP'),
        photo_path.with_suffix('.xmp'),
        photo_path.with_suffix('.XMP')
    ]
    
    for xmp_path in xmp_patterns:
        if xmp_path.exists():
            result['xmp'] = xmp_path
            break
    
    # Find AAE file
    aae_patterns = [
        photo_path.with_suffix('.aae'),
        photo_path.with_suffix('.AAE')
    ]
    
    # Try Apple Photos pattern (IMG_1234.HEIC -> IMG_O1234.aae)
    photo_name = photo_path.stem
    if photo_name.startswith('IMG_'):
        number_part = photo_name[4:]
        aae_patterns.extend([
            photo_path.parent / f"IMG_O{number_part}.aae",
            photo_path.parent / f"IMG_O{number_part}.AAE"
        ])
    elif photo_name.isdigit():
        aae_patterns.extend([
            photo_path.parent / f"{photo_name}O.aae",
            photo_path.parent / f"{photo_name}O.AAE"
        ])
    
    for aae_path in aae_patterns:
        if aae_path.exists():
            result['aae'] = aae_path
            break
    
    return result


def validate_file_path(file_path: Path) -> bool:
    """
    Validate that a file path is safe and accessible.
    
    Args:
        file_path: Path to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check if path exists
        if not file_path.exists():
            return False
        
        # Check if it's a file
        if not file_path.is_file():
            return False
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            return False
        
        # Check file size (avoid empty files)
        if file_path.stat().st_size == 0:
            return False
        
        return True
    except Exception:
        return False


def get_directory_size(directory: Path) -> int:
    """
    Calculate total size of a directory.
    
    Args:
        directory: Directory path
        
    Returns:
        Total size in bytes
    """
    total_size = 0
    
    try:
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
    except Exception:
        pass
    
    return total_size


def get_directory_file_count(directory: Path) -> int:
    """
    Count files in a directory.
    
    Args:
        directory: Directory path
        
    Returns:
        Number of files
    """
    count = 0
    
    try:
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                count += 1
    except Exception:
        pass
    
    return count


def create_timestamped_filename(base_name: str, extension: str) -> str:
    """
    Create a filename with timestamp.
    
    Args:
        base_name: Base name for the file
        extension: File extension (with or without dot)
        
    Returns:
        Timestamped filename
    """
    # Ensure extension starts with dot
    if not extension.startswith('.'):
        extension = '.' + extension
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create filename
    filename = f"{base_name}_{timestamp}{extension}"
    
    return sanitize_filename(filename)


def parse_boolean(value: Any) -> bool:
    """
    Parse boolean value from various formats.
    
    Args:
        value: Value to parse
        
    Returns:
        Boolean value
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled', 'y')
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    return False


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")
    
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def flatten_list(nested_list: List[List[Any]]) -> List[Any]:
    """
    Flatten a nested list.
    
    Args:
        nested_list: List of lists
        
    Returns:
        Flattened list
    """
    return [item for sublist in nested_list for item in sublist]


def remove_duplicates_preserve_order(items: List[Any]) -> List[Any]:
    """
    Remove duplicates from a list while preserving order.
    
    Args:
        items: List with potential duplicates
        
    Returns:
        List without duplicates
    """
    seen = set()
    result = []
    
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    
    return result


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

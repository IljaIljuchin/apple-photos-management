#!/usr/bin/env python3
"""
Security utilities for Apple Photos Export Tool

This module provides path validation and sanitization functions to prevent
path traversal attacks and ensure secure file operations.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.logging.logger_config import log_error, log_warning


class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass


def validate_path(path: Path, base_path: Path, operation: str = "access") -> Path:
    """
    Validate and sanitize a file path to prevent path traversal attacks.
    
    For photo export operations, this allows access to common user directories
    (Downloads, Pictures, Desktop) while preventing malicious path traversal.
    
    Args:
        path: The path to validate
        base_path: The base directory that the path must be within
        operation: Description of the operation for logging
        
    Returns:
        The validated and resolved path
        
    Raises:
        SecurityError: If the path is invalid or potentially malicious
    """
    try:
        # Convert to Path if not already
        if isinstance(path, str):
            path = Path(path)
        if isinstance(base_path, str):
            base_path = Path(base_path)
            
        # Resolve both paths to absolute paths
        path = path.resolve()
        base_path = base_path.resolve()
        
        # For photo export, allow access to common user directories
        if _is_allowed_user_directory(path):
            # Additional security checks for user directories
            if not _is_safe_path(path):
                raise SecurityError(f"Unsafe path detected: {path}")
            return path
        
        # Check if the path is within the base directory (for project files)
        try:
            path.relative_to(base_path)
        except ValueError:
            # Path is outside the base directory
            raise SecurityError(
                f"Path traversal attempt detected: {path} is outside allowed base directory {base_path}"
            )
        
        # Additional security checks
        if not _is_safe_path(path):
            raise SecurityError(f"Unsafe path detected: {path}")
            
        return path
        
    except Exception as e:
        log_error(f"Path validation failed for {operation}: {e}")
        raise SecurityError(f"Path validation failed: {e}")


def _is_allowed_user_directory(path: Path) -> bool:
    """
    Check if a path is within allowed user directories for photo export.
    
    Args:
        path: The path to check
        
    Returns:
        True if the path is within allowed user directories
    """
    try:
        # Get the user's home directory
        home_dir = Path.home()
        
        # Define allowed subdirectories within the user's home
        allowed_dirs = [
            'Downloads',
            'Pictures', 
            'Desktop',
            'Documents',
            'Movies',
            'Music',
            'Public'
        ]
        
        # Check if path is within user's home directory
        try:
            relative_path = path.relative_to(home_dir)
            # Check if it's in an allowed subdirectory
            return any(relative_path.parts[0] == allowed_dir for allowed_dir in allowed_dirs)
        except ValueError:
            # Path is not within home directory
            return False
            
    except Exception:
        return False


def _is_safe_path(path: Path) -> bool:
    """
    Check if a path is safe (no suspicious patterns).
    
    Args:
        path: The path to check
        
    Returns:
        True if the path is safe, False otherwise
    """
    path_str = str(path)
    
    # Check for suspicious patterns
    suspicious_patterns = [
        '..',  # Parent directory traversal
        '//',  # Multiple slashes (potential bypass)
        '\\',  # Windows path separators in Unix
        '\x00',  # Null bytes
        '\x01',  # Control characters
        '\x02',
        '\x03',
        '\x04',
        '\x05',
        '\x06',
        '\x07',
        '\x08',
        '\x0b',  # Vertical tab
        '\x0c',  # Form feed
        '\x0e',  # Shift out
        '\x0f',  # Shift in
        '\x10',
        '\x11',
        '\x12',
        '\x13',
        '\x14',
        '\x15',
        '\x16',
        '\x17',
        '\x18',
        '\x19',
        '\x1a',
        '\x1b',
        '\x1c',
        '\x1d',
        '\x1e',
        '\x1f',
        '\x7f',  # DEL character
    ]
    
    for pattern in suspicious_patterns:
        if pattern in path_str:
            log_warning(f"Suspicious pattern '{pattern}' found in path: {path_str}")
            return False
    
    # Check for overly long paths (potential DoS)
    if len(path_str) > 4096:  # Common filesystem limit
        log_warning(f"Path too long: {len(path_str)} characters")
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to remove potentially dangerous characters.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        The sanitized filename
    """
    if not filename:
        return "unnamed"
    
    # Remove or replace dangerous characters
    dangerous_chars = '<>:"/\\|?*'
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Remove control characters
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure filename is not empty after sanitization
    if not filename:
        filename = "unnamed"
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def validate_directory_access(directory: Path, operation: str = "access") -> bool:
    """
    Validate that a directory can be safely accessed.
    
    Args:
        directory: The directory to validate
        operation: Description of the operation for logging
        
    Returns:
        True if the directory is safe to access, False otherwise
    """
    try:
        # Check if directory exists
        if not directory.exists():
            log_warning(f"Directory does not exist: {directory}")
            return False
        
        # Check if it's actually a directory
        if not directory.is_dir():
            log_error(f"Path is not a directory: {directory}")
            return False
        
        # Check if we can read the directory
        try:
            list(directory.iterdir())
        except PermissionError:
            log_error(f"Permission denied accessing directory: {directory}")
            return False
        except OSError as e:
            log_error(f"OS error accessing directory {directory}: {e}")
            return False
        
        return True
        
    except Exception as e:
        log_error(f"Directory validation failed for {operation}: {e}")
        return False


def create_safe_path(base_path: Path, *path_parts: str) -> Path:
    """
    Create a safe path by joining path parts and validating the result.
    
    Args:
        base_path: The base directory
        *path_parts: Path components to join
        
    Returns:
        A validated safe path
        
    Raises:
        SecurityError: If the resulting path is unsafe
    """
    try:
        # Sanitize each path part
        safe_parts = [sanitize_filename(part) for part in path_parts]
        
        # Join the parts
        full_path = base_path
        for part in safe_parts:
            full_path = full_path / part
        
        # Validate the resulting path
        return validate_path(full_path, base_path, "path creation")
        
    except Exception as e:
        log_error(f"Safe path creation failed: {e}")
        raise SecurityError(f"Failed to create safe path: {e}")


def get_relative_safe_path(path: Path, base_path: Path) -> Path:
    """
    Get a relative path from base_path to path, ensuring it's safe.
    
    Args:
        path: The target path
        base_path: The base path
        
    Returns:
        A safe relative path
        
    Raises:
        SecurityError: If the path is unsafe or outside base_path
    """
    try:
        # Validate the path first
        validated_path = validate_path(path, base_path, "relative path calculation")
        
        # Get relative path
        relative_path = validated_path.relative_to(base_path)
        
        return relative_path
        
    except Exception as e:
        log_error(f"Relative path calculation failed: {e}")
        raise SecurityError(f"Failed to calculate relative path: {e}")

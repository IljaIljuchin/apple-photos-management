#!/usr/bin/env python3
"""
File utility functions for Apple Photos Export Tool

This module provides utility functions for finding associated files
(XMP, AAE) and other file operations.
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.logging.logger_config import log_debug


def find_xmp_file(photo_path: Path) -> Optional[Path]:
    """
    Find the associated XMP file for a photo.
    
    Args:
        photo_path: Path to the photo file
        
    Returns:
        Path to the XMP file if found, None otherwise
    """
    # Try different XMP file naming patterns
    patterns = [
        photo_path.with_suffix(photo_path.suffix + '.xmp'),
        photo_path.with_suffix(photo_path.suffix + '.XMP'),
        photo_path.with_suffix('.xmp'),
        photo_path.with_suffix('.XMP')
    ]
    
    for pattern in patterns:
        if pattern.exists():
            log_debug(f"Found XMP file: {pattern.name}")
            return pattern
    
    return None


def find_aae_file(photo_path: Path) -> Optional[Path]:
    """
    Find the associated AAE file for a photo.
    
    Args:
        photo_path: Path to the photo file
        
    Returns:
        Path to the AAE file if found, None otherwise
    """
    # Pattern 1: Direct match (photo.jpg -> photo.aae)
    aae_path = photo_path.with_suffix('.aae')
    if aae_path.exists():
        log_debug(f"Found AAE file (direct): {aae_path.name}")
        return aae_path
    
    aae_path = photo_path.with_suffix('.AAE')
    if aae_path.exists():
        log_debug(f"Found AAE file (direct): {aae_path.name}")
        return aae_path
    
    # Pattern 2: Apple Photos pattern (IMG_1234.HEIC -> IMG_O1234.aae)
    photo_name = photo_path.stem
    if photo_name.startswith('IMG_'):
        number_part = photo_name[4:]
        aae_name = f"IMG_O{number_part}.aae"
        test_path = photo_path.parent / aae_name
        if test_path.exists():
            log_debug(f"Found AAE file (IMG_O pattern): {aae_name}")
            return test_path
        
        aae_name = f"IMG_O{number_part}.AAE"
        test_path = photo_path.parent / aae_name
        if test_path.exists():
            log_debug(f"Found AAE file (IMG_O pattern): {aae_name}")
            return test_path
    
    # Pattern 3: Numeric pattern (1470.HEIC -> 1470O.aae)
    if photo_name.isdigit():
        aae_name = f"{photo_name}O.aae"
        test_path = photo_path.parent / aae_name
        if test_path.exists():
            log_debug(f"Found AAE file (numeric O pattern): {aae_name}")
            return test_path
        
        aae_name = f"{photo_name}O.AAE"
        test_path = photo_path.parent / aae_name
        if test_path.exists():
            log_debug(f"Found AAE file (numeric O pattern): {aae_name}")
            return test_path
    
    return None


def get_file_extension(file_path: Path) -> str:
    """
    Get file extension in lowercase.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension in lowercase
    """
    return file_path.suffix.lower()


def is_supported_format(file_path: Path, supported_formats: set) -> bool:
    """
    Check if file format is supported.
    
    Args:
        file_path: Path to the file
        supported_formats: Set of supported file extensions
        
    Returns:
        True if format is supported, False otherwise
    """
    return get_file_extension(file_path) in supported_formats


def generate_unique_filename(base_path: Path, filename: str) -> str:
    """
    Generate a unique filename by adding a counter if the file exists.
    
    Args:
        base_path: Directory where the file will be placed
        filename: Base filename
        
    Returns:
        Unique filename
    """
    if not (base_path / filename).exists():
        return filename
    
    # Split filename and extension
    name_part, ext_part = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    if ext_part:
        ext_part = '.' + ext_part
    
    # Generate unique filename
    counter = 1
    while True:
        unique_filename = f"{name_part}-{counter:03d}{ext_part}"
        if not (base_path / unique_filename).exists():
            return unique_filename
        counter += 1

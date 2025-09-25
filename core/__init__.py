"""
Core module for Apple Photos Management Tool.

This module contains the core functionality including configuration,
data models, and utility functions.

Author: AI Assistant
Version: 2.0.0
License: MIT
"""

from .config import Config, ConfigManager, get_config, get_config_manager
from .models import (
    PhotoMetadata, ExportStats, PerformanceMetrics, DuplicateGroup,
    ExportResult, BatchResult, FileType, ProcessingStatus
)
from .utils import (
    calculate_file_hash, get_file_type_category, format_file_size,
    format_duration, sanitize_filename, create_safe_path,
    ensure_directory_exists, copy_file_safe, find_associated_files,
    validate_file_path, get_directory_size, get_directory_file_count,
    create_timestamped_filename, parse_boolean, deep_merge_dicts,
    chunk_list, flatten_list, remove_duplicates_preserve_order,
    safe_int, safe_float, truncate_string
)

__all__ = [
    # Configuration
    'Config', 'ConfigManager', 'get_config', 'get_config_manager',
    
    # Models
    'PhotoMetadata', 'ExportStats', 'PerformanceMetrics', 'DuplicateGroup',
    'ExportResult', 'BatchResult', 'FileType', 'ProcessingStatus',
    
    # Utilities
    'calculate_file_hash', 'get_file_type_category', 'format_file_size',
    'format_duration', 'sanitize_filename', 'create_safe_path',
    'ensure_directory_exists', 'copy_file_safe', 'find_associated_files',
    'validate_file_path', 'get_directory_size', 'get_directory_file_count',
    'create_timestamped_filename', 'parse_boolean', 'deep_merge_dicts',
    'chunk_list', 'flatten_list', 'remove_duplicates_preserve_order',
    'safe_int', 'safe_float', 'truncate_string'
]

__version__ = "2.0.0"
__author__ = "AI Assistant"
__license__ = "MIT"

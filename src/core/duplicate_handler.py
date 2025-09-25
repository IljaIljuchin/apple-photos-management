#!/usr/bin/env python3
"""
Duplicate handling module for Apple Photos Export Tool

This module provides comprehensive duplicate detection and handling strategies
for photo and video files during the export process.
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

# Add the project root to the Python path
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.logging.logger_config import log_info, log_warning, log_debug, log_error
from src.core.config import get_config


@dataclass
class DuplicateStats:
    """Statistics for duplicate handling operations"""
    duplicate_files_found: int = 0
    duplicate_files_resolved: int = 0
    duplicate_files_preserved: int = 0
    duplicate_files_discarded: int = 0
    files_skipped_duplicates: int = 0


class DuplicateHandler:
    """
    Handles duplicate detection and resolution for photo and video files.
    
    Supports multiple strategies:
    - keep_first: Keep only the first occurrence
    - skip_duplicates: Skip all files that have duplicates
    - preserve_duplicates: Keep first + preserve one duplicate
    - cleanup_duplicates: Remove duplicates folder
    - !delete!: Delete duplicates from output directory
    """
    
    def __init__(self, duplicate_strategy: str = 'keep_first'):
        """
        Initialize the duplicate handler.
        
        Args:
            duplicate_strategy: Strategy for handling duplicates
        """
        self.duplicate_strategy = duplicate_strategy
        self.stats = DuplicateStats()
        self.config = get_config()
        self.duplicates_to_preserve: Dict[str, List[Path]] = {}
        
    def detect_duplicates(self, photo_files: List[Path]) -> Dict[str, List[Path]]:
        """
        Detect duplicate files based on file content (hash) and file type.
        
        Args:
            photo_files: List of photo file paths to check for duplicates
            
        Returns:
            Dictionary mapping composite keys to lists of duplicate file paths
        """
        seen_files = {}
        duplicates = {}

        for photo_path in photo_files:
            try:
                # Calculate file hash
                with open(photo_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                # Get file type (extension) for better duplicate detection
                file_extension = photo_path.suffix.lower()
                file_type = self._get_file_type_category(file_extension)
                
                # Create a composite key: hash + file_type
                # This ensures that MOV and HEIC files with same content are treated as different
                composite_key = f"{file_hash}_{file_type}"
                
                if composite_key in seen_files:
                    if composite_key not in duplicates:
                        duplicates[composite_key] = [seen_files[composite_key]]
                    duplicates[composite_key].append(photo_path)
                else:
                    seen_files[composite_key] = photo_path
            except Exception as e:
                log_warning(f"Could not calculate hash for {photo_path}: {e}")
                # Fallback to filename-based detection with file type consideration
                filename = photo_path.name
                file_extension = photo_path.suffix.lower()
                file_type = self._get_file_type_category(file_extension)
                composite_filename = f"{filename}_{file_type}"
                
                if composite_filename in seen_files:
                    if composite_filename not in duplicates:
                        duplicates[composite_filename] = [seen_files[composite_filename]]
                    duplicates[composite_filename].append(photo_path)
                else:
                    seen_files[composite_filename] = photo_path

        return duplicates

    def _get_file_type_category(self, extension: str) -> str:
        """
        Get file type category for duplicate detection.
        
        Args:
            extension: File extension (e.g., '.heic', '.mov')
            
        Returns:
            File type category ('image', 'video', or 'other')
        """
        if extension in self.config.file_formats.IMAGE_FORMATS:
            return "image"
        elif extension in self.config.file_formats.VIDEO_FORMATS:
            return "video"
        else:
            return "other"

    def handle_duplicates(self, duplicates: Dict[str, List[Path]]) -> List[Path]:
        """
        Handle duplicates based on the configured strategy.
        
        Args:
            duplicates: Dictionary of duplicate file groups
            
        Returns:
            List of file paths to process (after duplicate resolution)
        """
        if not duplicates:
            return []
        
        self.stats.duplicate_files_found = len(duplicates)
        log_info(f"Found {len(duplicates)} duplicate files")
        
        if self.duplicate_strategy == 'keep_first':
            return self._handle_keep_first(duplicates)
        elif self.duplicate_strategy == 'skip_duplicates':
            return self._handle_skip_duplicates(duplicates)
        elif self.duplicate_strategy == 'preserve_duplicates':
            return self._handle_preserve_duplicates(duplicates)
        elif self.duplicate_strategy == 'cleanup_duplicates':
            return self._handle_cleanup_duplicates(duplicates)
        elif self.duplicate_strategy == '!delete!':
            return self._handle_delete_duplicates(duplicates)
        else:
            # Default: keep first
            log_warning(f"Unknown duplicate strategy '{self.duplicate_strategy}', using 'keep_first'")
            self.duplicate_strategy = 'keep_first'
            return self._handle_keep_first(duplicates)

    def _handle_keep_first(self, duplicates: Dict[str, List[Path]]) -> List[Path]:
        """Keep only the first occurrence of each duplicate."""
        resolved_files = []
        for filename, paths in duplicates.items():
            resolved_files.append(paths[0])
            self.stats.duplicate_files_resolved += len(paths) - 1
            log_debug(f"Duplicate '{filename}': keeping first occurrence, skipping {len(paths) - 1} duplicates")
        return resolved_files

    def _handle_skip_duplicates(self, duplicates: Dict[str, List[Path]]) -> List[Path]:
        """Skip all files that have duplicates."""
        for filename, paths in duplicates.items():
            self.stats.files_skipped_duplicates += len(paths)
            log_debug(f"Duplicate '{filename}': skipping all {len(paths)} occurrences")
        return []

    def _handle_preserve_duplicates(self, duplicates: Dict[str, List[Path]]) -> List[Path]:
        """Keep first occurrence for main export, preserve others in duplicates folder."""
        resolved_files = []
        for filename, paths in duplicates.items():
            # Keep first occurrence for main export
            resolved_files.append(paths[0])
            self.stats.duplicate_files_resolved += 1
            
            # Store duplicates for later processing
            self.duplicates_to_preserve[filename] = paths
            
            # Preserve up to 2 copies total (first + one duplicate)
            if len(paths) > 1:
                self.stats.duplicate_files_preserved += 1
                log_debug(f"Duplicate '{filename}': preserving 1 duplicate")
            
            # Discard additional copies (3rd, 4th, etc.)
            if len(paths) > 2:
                discarded_count = len(paths) - 2
                self.stats.duplicate_files_discarded += discarded_count
                log_warning(f"Duplicate '{filename}': discarding {discarded_count} additional copies (keeping only 2 total)")
        
        return resolved_files

    def _handle_cleanup_duplicates(self, duplicates: Dict[str, List[Path]]) -> List[Path]:
        """Remove duplicates folder and keep only main export."""
        log_info("Cleanup mode: removing duplicates folder...")
        # Note: Actual cleanup logic would be implemented here
        # This is a placeholder for the cleanup functionality
        return []

    def _handle_delete_duplicates(self, duplicates: Dict[str, List[Path]]) -> List[Path]:
        """Delete duplicate files from output directory (not source!)."""
        log_warning("DELETE mode: will delete duplicate files from OUTPUT directory!")
        # Note: Actual deletion logic would be implemented here
        # This is a placeholder for the deletion functionality
        return []

    def has_preserved_duplicates(self) -> bool:
        """Check if there are duplicates to preserve."""
        return bool(self.duplicates_to_preserve)

    def get_duplicate_stats(self) -> DuplicateStats:
        """Get current duplicate handling statistics."""
        return self.stats

    def reset_stats(self):
        """Reset duplicate handling statistics."""
        self.stats = DuplicateStats()
        self.duplicates_to_preserve.clear()

    def get_supported_strategies(self) -> List[str]:
        """Get list of supported duplicate handling strategies."""
        return [
            'keep_first',
            'skip_duplicates', 
            'preserve_duplicates',
            'cleanup_duplicates',
            '!delete!'
        ]

    def validate_strategy(self, strategy: str) -> bool:
        """Validate if a duplicate handling strategy is supported."""
        return strategy in self.get_supported_strategies()

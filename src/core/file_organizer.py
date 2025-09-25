#!/usr/bin/env python3
"""
File organization module for Apple Photos Export Tool

This module handles file organization, directory structure creation,
filename generation, and file copying operations.
"""

import shutil
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
from collections import defaultdict

# Add the project root to the Python path
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.logging.logger_config import log_info, log_warning, log_debug, log_error
from src.security.security_utils import create_safe_path, sanitize_filename, SecurityError
from src.core.metadata_extractor import PhotoMetadata
from src.core.config import get_config


class FileOrganizer:
    """
    Handles file organization, directory structure creation, and file copying.
    
    Responsibilities:
    - Generate standardized filenames
    - Create YEAR-based directory structure
    - Copy photos and associated files (XMP, AAE)
    - Handle filename conflicts and duplicates
    """
    
    def __init__(self, export_dir: Path, is_dry_run: bool = True):
        """
        Initialize the file organizer.
        
        Args:
            export_dir: Base export directory
            is_dry_run: Whether to simulate operations without actually copying files
        """
        self.export_dir = export_dir
        self.is_dry_run = is_dry_run
        self.file_timestamps: dict = defaultdict(int)
        self.config = get_config()
        
    def generate_filename(self, creation_date: datetime, extension: str) -> str:
        """
        Generate filename in format YYYYMMDD-HHMMSS-SSS.ext.
        
        Args:
            creation_date: Creation date of the file
            extension: File extension (e.g., '.heic', '.mov')
            
        Returns:
            Generated filename with timestamp and extension
        """
        # Format: YYYYMMDD-HHMMSS
        base_timestamp = creation_date.strftime(self.config.date_formats.FILENAME_TIMESTAMP)
        
        # Add milliseconds if available, otherwise use counter
        if creation_date.microsecond > 0:
            milliseconds = str(creation_date.microsecond // 1000).zfill(3)
        else:
            # Use counter for same timestamp
            self.file_timestamps[base_timestamp] += 1
            milliseconds = str(self.file_timestamps[base_timestamp]).zfill(3)
        
        # Sanitize the filename
        filename = f"{base_timestamp}-{milliseconds}{extension}"
        return sanitize_filename(filename)

    def create_directory_structure(self, year: int, month: int, day: int) -> Path:
        """
        Create YEAR directory structure (flat structure).
        
        Args:
            year: Year for the directory
            month: Month (for validation)
            day: Day (for validation)
            
        Returns:
            Path to the created directory
            
        Raises:
            ValueError: If directory path is invalid
        """
        if self.export_dir is None:
            raise ValueError("Export directory not set")
        
        # Use secure path creation
        try:
            dir_path = create_safe_path(self.export_dir, str(year))
        except SecurityError as e:
            log_error(f"Failed to create safe directory path: {e}")
            raise ValueError(f"Invalid directory path: {e}")
        
        if not self.is_dry_run:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        return dir_path

    def copy_photo_with_metadata(self, metadata: PhotoMetadata, target_dir: Path) -> bool:
        """
        Copy photo file and its associated metadata files (XMP, AAE).
        
        Args:
            metadata: Photo metadata containing file information
            target_dir: Target directory for the files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not metadata.is_valid or not metadata.creation_date:
                log_warning(f"Skipping invalid photo: {metadata.original_filename}")
                return False

            # Generate filename
            new_filename = self.generate_filename(metadata.creation_date, metadata.file_extension)
            target_path = target_dir / new_filename

            # Handle potential filename duplicates
            target_path = self._resolve_filename_conflict(target_path)

            if self.is_dry_run:
                # Dry run mode - just log what would be done
                log_debug(f"DRY-RUN: Would copy: {metadata.original_filename} -> {target_path}")
                
                # Log associated files that would be copied
                self._log_associated_files(metadata.original_path, target_path)
                
                return True
            else:
                # Real mode - actually copy the file
                shutil.copy2(metadata.original_path, target_path)
                log_debug(f"Copied: {metadata.original_filename} -> {target_path}")
                
                # Copy associated files
                self._copy_associated_files(metadata.original_path, target_path, target_dir)
                
                return True
                
        except Exception as e:
            error_msg = f"Error copying {metadata.original_filename}: {e}"
            log_error(error_msg)
            return False

    def copy_duplicate_photo(self, metadata: PhotoMetadata, duplicates_dir: Path) -> bool:
        """
        Copy duplicate photo to duplicates directory with same naming logic.
        
        Args:
            metadata: Photo metadata containing file information
            duplicates_dir: Duplicates directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not metadata.is_valid or not metadata.creation_date:
                log_warning(f"Skipping invalid duplicate: {metadata.original_filename}")
                return False

            year, month, day = metadata.creation_date.year, metadata.creation_date.month, metadata.creation_date.day
            target_dir = duplicates_dir / str(year) / f"{month:02d}" / f"{day:02d}"
            
            if not self.is_dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
            
            new_filename = self.generate_filename(metadata.creation_date, metadata.file_extension)
            target_path = target_dir / new_filename

            # Handle potential filename duplicates
            target_path = self._resolve_filename_conflict(target_path)

            if not self.is_dry_run:
                shutil.copy2(metadata.original_path, target_path)
                log_debug(f"Copied duplicate: {metadata.original_filename} -> {target_path}")
            else:
                log_debug(f"Would copy duplicate: {metadata.original_filename} -> {target_path}")

            # Copy associated files
            self._copy_associated_files(metadata.original_path, target_path, target_dir)

            return True
                
        except Exception as e:
            error_msg = f"Error copying duplicate {metadata.original_filename}: {e}"
            log_error(error_msg)
            return False

    def _resolve_filename_conflict(self, target_path: Path) -> Path:
        """
        Resolve filename conflicts by adding a counter.
        
        Args:
            target_path: Original target path
            
        Returns:
            Resolved path with counter if needed
        """
        counter = 1
        original_target_path = target_path
        while target_path.exists():
            stem = original_target_path.stem
            ext = original_target_path.suffix
            target_path = target_path.parent / f"{stem}-{counter:03d}{ext}"
            counter += 1
        return target_path

    def _log_associated_files(self, original_path: Path, target_path: Path):
        """
        Log associated files that would be copied in dry run mode.
        
        Args:
            original_path: Original file path
            target_path: Target file path
        """
        # Ensure original_path is a Path object
        if isinstance(original_path, str):
            original_path = Path(original_path)
        
        # Log XMP file
        xmp_path = self._find_xmp_file(original_path)
        if xmp_path:
            log_debug(f"DRY-RUN: Would copy XMP: {xmp_path.name}")
        
        # Log AAE file
        aae_path = self._find_aae_file(original_path)
        if aae_path:
            log_debug(f"DRY-RUN: Would copy AAE: {aae_path.name}")

    def _copy_associated_files(self, original_path: Path, target_path: Path, target_dir: Path):
        """
        Copy associated files (XMP, AAE) for a photo.
        
        Args:
            original_path: Original photo path
            target_path: Target photo path
            target_dir: Target directory
        """
        # Ensure original_path is a Path object
        if isinstance(original_path, str):
            original_path = Path(original_path)
        
        # Copy XMP file
        xmp_path = self._find_xmp_file(original_path)
        if xmp_path:
            xmp_filename = target_path.stem + '.xmp'
            xmp_target_path = target_dir / xmp_filename
            shutil.copy2(xmp_path, xmp_target_path)
            log_debug(f"Copied XMP: {xmp_path.name} -> {xmp_target_path}")
        
        # Copy AAE file
        aae_path = self._find_aae_file(original_path)
        if aae_path:
            aae_filename = target_path.stem + '.aae'
            aae_target_path = target_dir / aae_filename
            shutil.copy2(aae_path, aae_target_path)
            log_debug(f"Copied AAE: {aae_path.name} -> {aae_target_path}")

    def _find_xmp_file(self, photo_path: Path) -> Optional[Path]:
        """
        Find associated XMP file for a photo.
        
        Args:
            photo_path: Path to the photo file
            
        Returns:
            Path to XMP file if found, None otherwise
        """
        # Ensure photo_path is a Path object
        if isinstance(photo_path, str):
            photo_path = Path(photo_path)
        
        # Try different XMP file patterns
        xmp_patterns = [
            photo_path.with_suffix(photo_path.suffix + '.xmp'),
            photo_path.with_suffix(photo_path.suffix + '.XMP'),
            photo_path.with_suffix('.xmp'),
            photo_path.with_suffix('.XMP')
        ]
        
        for xmp_path in xmp_patterns:
            if xmp_path.exists():
                return xmp_path
        
        return None

    def _find_aae_file(self, photo_path: Path) -> Optional[Path]:
        """
        Find associated AAE file for a photo.
        
        Args:
            photo_path: Path to the photo file
            
        Returns:
            Path to AAE file if found, None otherwise
        """
        # Ensure photo_path is a Path object
        if isinstance(photo_path, str):
            photo_path = Path(photo_path)
        
        original_path = photo_path
        
        # Try standard AAE patterns
        aae_patterns = [
            original_path.with_suffix('.aae'),
            original_path.with_suffix('.AAE')
        ]
        
        for aae_path in aae_patterns:
            if aae_path.exists():
                return aae_path
        
        # Try Apple Photos pattern (IMG_1234.HEIC -> IMG_O1234.aae)
        photo_name = original_path.stem
        if photo_name.startswith('IMG_'):
            number_part = photo_name[4:]
            aae_patterns = [
                original_path.parent / f"IMG_O{number_part}.aae",
                original_path.parent / f"IMG_O{number_part}.AAE"
            ]
            
            for aae_path in aae_patterns:
                if aae_path.exists():
                    return aae_path
        
        # Try numeric pattern (1470.HEIC -> 1470O.aae)
        elif photo_name.isdigit():
            aae_patterns = [
                original_path.parent / f"{photo_name}O.aae",
                original_path.parent / f"{photo_name}O.AAE"
            ]
            
            for aae_path in aae_patterns:
                if aae_path.exists():
                    return aae_path
        
        return None

    def set_export_directory(self, export_dir: Path):
        """Set the export directory."""
        self.export_dir = export_dir

    def set_dry_run(self, is_dry_run: bool):
        """Set dry run mode."""
        self.is_dry_run = is_dry_run

    def reset_timestamps(self):
        """Reset the file timestamp counter."""
        self.file_timestamps.clear()

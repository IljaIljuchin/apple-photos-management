#!/usr/bin/env python3
"""
Apple Photos Export Tool

This tool exports and organizes photos from Apple Photos library export.
It reads photos and XMP files, extracts creation dates from EXIF and XMP metadata,
chooses the earlier date, and organizes photos into YEAR/MM/DD structure.

Usage:
    python3 export_photos.py <source_dir> <target_dir> <is_dry_run>

Author: AI Assistant
Version: 1.0.0
"""

import os
import sys
import json
import shutil
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

# Third-party imports
try:
    from PIL import Image, ExifTags
    from PIL.ExifTags import TAGS
except ImportError:
    print("ERROR: Pillow library not found. Install with: pip install Pillow")
    sys.exit(1)

try:
    from lxml import etree
except ImportError:
    print("ERROR: lxml library not found. Install with: pip install lxml")
    sys.exit(1)

try:
    from dateutil import parser as date_parser
except ImportError:
    print("ERROR: python-dateutil library not found. Install with: pip install python-dateutil")
    sys.exit(1)

try:
    import colorlog
except ImportError:
    print("ERROR: colorlog library not found. Install with: pip install colorlog")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    print("ERROR: tqdm library not found. Install with: pip install tqdm")
    sys.exit(1)


@dataclass
class PhotoMetadata:
    """Container for photo metadata"""
    original_path: str
    original_filename: str
    creation_date: Optional[datetime]
    date_source: str  # 'exif', 'xmp', 'file', 'fallback'
    file_size: int
    file_extension: str
    is_valid: bool = True
    error_message: Optional[str] = None


@dataclass
class ExportStats:
    """Statistics for export operation"""
    total_files_processed: int = 0
    photos_processed: int = 0
    xmp_files_processed: int = 0
    aae_files_processed: int = 0
    successful_exports: int = 0
    failed_exports: int = 0
    duplicates_handled: int = 0
    duplicate_files_found: int = 0
    duplicate_files_resolved: int = 0
    files_skipped_duplicates: int = 0
    total_size_bytes: int = 0
    supported_formats: Counter = None
    unsupported_formats: Counter = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = Counter()
        if self.unsupported_formats is None:
            self.unsupported_formats = Counter()
        if self.errors is None:
            self.errors = []


class PhotoExporter:
    """Main class for photo export and organization"""
    
    # Supported file formats
    SUPPORTED_IMAGE_FORMATS = {'.heic', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.raw', '.cr2', '.nef', '.arw'}
    SUPPORTED_VIDEO_FORMATS = {'.mov', '.mp4', '.avi', '.mkv', '.m4v'}
    SUPPORTED_METADATA_FORMATS = {'.aae'}  # Apple Adjustment Export files
    SUPPORTED_FORMATS = SUPPORTED_IMAGE_FORMATS | SUPPORTED_VIDEO_FORMATS | SUPPORTED_METADATA_FORMATS
    
    def __init__(self, source_dir: str, target_dir: str, is_dry_run: bool = True, 
                 duplicate_strategy: str = 'keep_first'):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.is_dry_run = is_dry_run
        self.duplicate_strategy = duplicate_strategy
        
        # Setup logging
        self._setup_logging()
        
        # Statistics
        self.stats = ExportStats()
        
        # File tracking for duplicates
        self.file_timestamps: Dict[str, int] = defaultdict(int)
        
        # Export directory (will be created with timestamp)
        self.export_dir = None
        
        self.logger.info(f"PhotoExporter initialized:")
        self.logger.info(f"  Source: {self.source_dir}")
        self.logger.info(f"  Target: {self.target_dir}")
        self.logger.info(f"  Mode: {'DRY-RUN' if is_dry_run else 'EXECUTE'}")

    def _setup_logging(self):
        """Setup colored logging"""
        # Create logger
        self.logger = logging.getLogger('PhotoExporter')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create console handler with colors
        console_handler = colorlog.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(levelname)-8s%(reset)s %(message)s',
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Create file handler for detailed logging
        if not self.is_dry_run:
            log_file = self.target_dir / f"export_log_{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def _create_export_directory(self) -> Path:
        """Create timestamped export directory"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        export_dir_name = f"export_{timestamp}"
        export_path = self.target_dir / export_dir_name
        
        if not self.is_dry_run:
            export_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created export directory: {export_path}")
        else:
            self.logger.info(f"Would create export directory: {export_path}")
        
        self.export_dir = export_path
        return export_path

    def _get_file_extension(self, file_path: Path) -> str:
        """Get file extension in lowercase"""
        return file_path.suffix.lower()

    def _is_supported_format(self, file_path: Path) -> bool:
        """Check if file format is supported"""
        return self._get_file_extension(file_path) in self.SUPPORTED_FORMATS

    def _extract_exif_date(self, image_path: Path) -> Optional[datetime]:
        """Extract creation date from EXIF data"""
        try:
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data is None:
                    return None
                
                # Look for DateTime or DateTimeOriginal
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                        try:
                            # Parse EXIF date format: "YYYY:MM:DD HH:MM:SS"
                            dt = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                            return dt.replace(tzinfo=timezone.utc)
                        except ValueError:
                            continue
                            
        except Exception as e:
            self.logger.debug(f"Error reading EXIF from {image_path}: {e}")
            
        return None

    def _extract_xmp_date(self, xmp_path: Path) -> Optional[datetime]:
        """Extract creation date from XMP file"""
        try:
            tree = etree.parse(str(xmp_path))
            root = tree.getroot()
            
            # Define namespaces
            namespaces = {
                'xmp': 'http://ns.adobe.com/xap/1.0/',
                'exif': 'http://ns.adobe.com/exif/1.0/',
                'photoshop': 'http://ns.adobe.com/photoshop/1.0/',
                'xmp': 'http://ns.adobe.com/xap/1.0/',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'xmpMM': 'http://ns.adobe.com/xap/1.0/mm/',
                'stEvt': 'http://ns.adobe.com/xap/1.0/sType/ResourceEvent#',
                'stRef': 'http://ns.adobe.com/xap/1.0/sType/ResourceRef#'
            }
            
            # Try different XMP date fields
            date_fields = [
                '//photoshop:DateCreated',
                '//xmp:CreateDate',
                '//exif:DateTimeOriginal',
                '//exif:DateTimeDigitized',
                '//dc:date',
                '//xmp:ModifyDate'
            ]
            
            for field in date_fields:
                elements = root.xpath(field, namespaces=namespaces)
                if elements:
                    date_str = elements[0].text
                    if date_str:
                        try:
                            # Try different date formats
                            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S.%fZ']:
                                try:
                                    dt = datetime.strptime(date_str, fmt)
                                    return dt.replace(tzinfo=timezone.utc)
                                except ValueError:
                                    continue
                            
                            # Try dateutil parser as fallback
                            dt = date_parser.parse(date_str)
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            return dt
                        except Exception:
                            continue
                            
        except Exception as e:
            self.logger.debug(f"Error reading XMP from {xmp_path}: {e}")
            
        return None

    def _get_file_creation_date(self, file_path: Path) -> datetime:
        """Get file creation date as fallback"""
        try:
            stat = file_path.stat()
            # Use st_mtime (modification time) as it's more reliable than st_ctime on macOS
            timestamp = stat.st_mtime
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except Exception as e:
            self.logger.warning(f"Error getting file date for {file_path}: {e}")
            return datetime.now(timezone.utc)

    def _choose_best_date(self, exif_date: Optional[datetime], xmp_date: Optional[datetime], file_date: datetime) -> Tuple[datetime, str]:
        """Choose the best creation date from available sources"""
        # Strategy: Choose the earlier date between EXIF and XMP, fallback to file date
        if exif_date and xmp_date:
            if exif_date <= xmp_date:
                return exif_date, 'exif'
            else:
                return xmp_date, 'xmp'
        elif exif_date:
            return exif_date, 'exif'
        elif xmp_date:
            return xmp_date, 'xmp'
        else:
            return file_date, 'file'

    def _generate_filename(self, creation_date: datetime, extension: str) -> str:
        """Generate filename in format YYYYMMDD-HHMMSS-SSS.ext"""
        # Format: YYYYMMDD-HHMMSS
        base_timestamp = creation_date.strftime('%Y%m%d-%H%M%S')
        
        # Add milliseconds if available, otherwise use counter
        if creation_date.microsecond > 0:
            milliseconds = str(creation_date.microsecond // 1000).zfill(3)
        else:
            # Use counter for same timestamp
            self.file_timestamps[base_timestamp] += 1
            milliseconds = str(self.file_timestamps[base_timestamp]).zfill(3)
        
        return f"{base_timestamp}-{milliseconds}{extension}"

    def _create_directory_structure(self, year: int, month: int, day: int) -> Path:
        """Create YEAR/MM/DD directory structure"""
        if self.export_dir is None:
            self._create_export_directory()
        
        dir_path = self.export_dir / str(year) / f"{month:02d}" / f"{day:02d}"
        
        if not self.is_dry_run:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        return dir_path

    def _process_photo_file(self, photo_path: Path) -> Optional[PhotoMetadata]:
        """Process a single photo file and extract metadata"""
        try:
            self.stats.total_files_processed += 1
            
            # Check if format is supported
            if not self._is_supported_format(photo_path):
                ext = self._get_file_extension(photo_path)
                self.stats.unsupported_formats[ext] += 1
                self.logger.warning(f"Unsupported format: {photo_path}")
                return None
            
            # Track supported format
            ext = self._get_file_extension(photo_path)
            self.stats.supported_formats[ext] += 1
            
            # Get file size
            file_size = photo_path.stat().st_size
            self.stats.total_size_bytes += file_size
            
            # Look for corresponding XMP file (try both .xmp and .XMP)
            # First try with original extension, then without
            xmp_path = photo_path.with_suffix(photo_path.suffix + '.xmp')
            if not xmp_path.exists():
                xmp_path = photo_path.with_suffix(photo_path.suffix + '.XMP')
                if not xmp_path.exists():
                    # Try without original extension
                    xmp_path = photo_path.with_suffix('.xmp')
                    if not xmp_path.exists():
                        xmp_path = photo_path.with_suffix('.XMP')
                        if not xmp_path.exists():
                            xmp_path = None
            
            # Look for corresponding AAE file (Apple Adjustment Export)
            # Try different naming patterns that Apple Photos uses
            aae_path = None
            
            # Pattern 1: Direct match (IMG_1234.HEIC -> IMG_1234.aae)
            test_path = photo_path.with_suffix('.aae')
            if test_path.exists():
                aae_path = test_path
            else:
                test_path = photo_path.with_suffix('.AAE')
                if test_path.exists():
                    aae_path = test_path
            
            # Pattern 2: Apple Photos pattern (IMG_1234.HEIC -> IMG_O1234.aae)
            if aae_path is None:
                photo_name = photo_path.stem
                if photo_name.startswith('IMG_'):
                    # Extract number from IMG_XXXX
                    number_part = photo_name[4:]  # Remove 'IMG_' prefix
                    aae_name = f"IMG_O{number_part}.aae"
                    test_path = photo_path.parent / aae_name
                    if test_path.exists():
                        aae_path = test_path
                    else:
                        # Try uppercase
                        aae_name = f"IMG_O{number_part}.AAE"
                        test_path = photo_path.parent / aae_name
                        if test_path.exists():
                            aae_path = test_path
            
            # Extract dates from different sources
            exif_date = None
            xmp_date = None
            
            # Count all supported files as photos (including videos)
            self.stats.photos_processed += 1
            
            if photo_path.suffix.lower() in self.SUPPORTED_IMAGE_FORMATS:
                exif_date = self._extract_exif_date(photo_path)
            
            if xmp_path:
                xmp_date = self._extract_xmp_date(xmp_path)
                self.stats.xmp_files_processed += 1
            
            if aae_path:
                self.stats.aae_files_processed += 1
                self.logger.debug(f"Found AAE file: {aae_path}")
            
            # Get file date as fallback
            file_date = self._get_file_creation_date(photo_path)
            
            # Choose best date
            creation_date, date_source = self._choose_best_date(exif_date, xmp_date, file_date)
            
            # Create metadata object
            metadata = PhotoMetadata(
                original_path=str(photo_path),
                original_filename=photo_path.name,
                creation_date=creation_date,
                date_source=date_source,
                file_size=file_size,
                file_extension=ext
            )
            
            self.logger.debug(f"Processed {photo_path.name}: {creation_date} (from {date_source})")
            return metadata
            
        except Exception as e:
            error_msg = f"Error processing {photo_path}: {e}"
            self.logger.error(error_msg)
            self.stats.errors.append(error_msg)
            self.stats.failed_exports += 1
            
            return PhotoMetadata(
                original_path=str(photo_path),
                original_filename=photo_path.name,
                creation_date=None,
                date_source='error',
                file_size=0,
                file_extension=self._get_file_extension(photo_path),
                is_valid=False,
                error_message=str(e)
            )
    
    def _detect_duplicates(self, photo_files: List[Path]) -> Dict[str, List[Path]]:
        """Detect duplicate files based on filename"""
        seen_files = {}
        duplicates = {}
        
        for photo_path in photo_files:
            filename = photo_path.name
            if filename in seen_files:
                if filename not in duplicates:
                    duplicates[filename] = [seen_files[filename]]
                duplicates[filename].append(photo_path)
            else:
                seen_files[filename] = photo_path
        
        return duplicates
    
    def _handle_duplicates(self, duplicates: Dict[str, List[Path]]) -> List[Path]:
        """Handle duplicates based on strategy"""
        if not duplicates:
            return []
        
        self.stats.duplicate_files_found = len(duplicates)
        self.logger.info(f"Found {len(duplicates)} duplicate files")
        
        if self.duplicate_strategy == 'keep_first':
            # Keep only the first occurrence of each duplicate
            resolved_files = []
            for filename, paths in duplicates.items():
                resolved_files.append(paths[0])
                self.stats.duplicate_files_resolved += len(paths) - 1
                self.logger.debug(f"Duplicate '{filename}': keeping first occurrence, skipping {len(paths) - 1} duplicates")
            return resolved_files
            
        elif self.duplicate_strategy == 'skip_duplicates':
            # Skip all files that have duplicates
            skipped_files = []
            for filename, paths in duplicates.items():
                skipped_files.extend(paths)
                self.stats.files_skipped_duplicates += len(paths)
                self.logger.debug(f"Duplicate '{filename}': skipping all {len(paths)} occurrences")
            return []
        
        else:
            # Default: keep first
            self.duplicate_strategy = 'keep_first'
            return self._handle_duplicates(duplicates)

    def _copy_photo(self, metadata: PhotoMetadata) -> bool:
        """Copy photo to organized directory structure"""
        try:
            if not metadata.is_valid or not metadata.creation_date:
                self.logger.warning(f"Skipping invalid photo: {metadata.original_filename}")
                return False
            
            # Create directory structure
            year = metadata.creation_date.year
            month = metadata.creation_date.month
            day = metadata.creation_date.day
            
            target_dir = self._create_directory_structure(year, month, day)
            
            # Generate new filename
            new_filename = self._generate_filename(metadata.creation_date, metadata.file_extension)
            target_path = target_dir / new_filename
            
            # Check for duplicates
            if target_path.exists():
                self.stats.duplicates_handled += 1
                self.logger.warning(f"Duplicate filename detected: {new_filename}")
                # Generate unique filename
                counter = 1
                while target_path.exists():
                    name_part = new_filename.rsplit('.', 1)[0]
                    ext_part = '.' + new_filename.rsplit('.', 1)[1]
                    new_filename = f"{name_part}-{counter:03d}{ext_part}"
                    target_path = target_dir / new_filename
                    counter += 1
            
            # Copy main file
            if not self.is_dry_run:
                shutil.copy2(metadata.original_path, target_path)
                self.logger.debug(f"Copied: {metadata.original_filename} -> {target_path}")
            else:
                self.logger.debug(f"Would copy: {metadata.original_filename} -> {target_path}")
            
            # Copy AAE file if it exists
            original_path = Path(metadata.original_path)
            aae_path = original_path.with_suffix('.aae')
            if not aae_path.exists():
                aae_path = original_path.with_suffix('.AAE')
            
            if aae_path.exists():
                aae_filename = new_filename.rsplit('.', 1)[0] + '.aae'
                aae_target_path = target_dir / aae_filename
                
                if not self.is_dry_run:
                    shutil.copy2(aae_path, aae_target_path)
                    self.logger.debug(f"Copied AAE: {aae_path.name} -> {aae_target_path}")
                else:
                    self.logger.debug(f"Would copy AAE: {aae_path.name} -> {aae_target_path}")
                
                self.stats.aae_files_processed += 1
            
            self.stats.successful_exports += 1
            return True
            
        except Exception as e:
            error_msg = f"Error copying {metadata.original_filename}: {e}"
            self.logger.error(error_msg)
            self.stats.errors.append(error_msg)
            self.stats.failed_exports += 1
            return False

    def _save_export_metadata(self):
        """Save export metadata and statistics"""
        if self.is_dry_run:
            return
        
        metadata = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'source_directory': str(self.source_dir),
                'target_directory': str(self.target_dir),
                'is_dry_run': self.is_dry_run,
                'export_directory': str(self.export_dir)
            },
            'statistics': {
                'total_files_processed': self.stats.total_files_processed,
                'photos_processed': self.stats.photos_processed,
                'xmp_files_processed': self.stats.xmp_files_processed,
                'successful_exports': self.stats.successful_exports,
                'failed_exports': self.stats.failed_exports,
                'duplicates_handled': self.stats.duplicates_handled,
                'total_size_bytes': self.stats.total_size_bytes,
                'supported_formats': dict(self.stats.supported_formats),
                'unsupported_formats': dict(self.stats.unsupported_formats),
                'errors': self.stats.errors
            },
            'file_timestamps': dict(self.file_timestamps)
        }
        
        metadata_file = self.export_dir / 'export_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Create summary file
        summary_file = self.export_dir / 'export_summary.txt'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Apple Photos Export Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source: {self.source_dir}\n")
            f.write(f"Target: {self.export_dir}\n\n")
            f.write(f"Files Processed: {self.stats.total_files_processed}\n")
            f.write(f"Photos Processed: {self.stats.photos_processed}\n")
            f.write(f"XMP Files Processed: {self.stats.xmp_files_processed}\n")
            f.write(f"AAE Files Processed: {self.stats.aae_files_processed}\n")
            f.write(f"Successful Exports: {self.stats.successful_exports}\n")
            f.write(f"Failed Exports: {self.stats.failed_exports}\n")
            f.write(f"Duplicates Handled: {self.stats.duplicates_handled}\n")
            f.write(f"Duplicate Files Found: {self.stats.duplicate_files_found}\n")
            f.write(f"Duplicate Files Resolved: {self.stats.duplicate_files_resolved}\n")
            f.write(f"Files Skipped (Duplicates): {self.stats.files_skipped_duplicates}\n")
            f.write(f"Total Size: {self.stats.total_size_bytes / (1024*1024*1024):.2f} GB\n\n")
            
            f.write("Supported Formats:\n")
            for fmt, count in self.stats.supported_formats.most_common():
                f.write(f"  {fmt}: {count}\n")
            
            if self.stats.unsupported_formats:
                # Filter out XMP files from unsupported formats display
                filtered_unsupported = {fmt: count for fmt, count in self.stats.unsupported_formats.items() 
                                      if fmt.lower() not in ['.xmp']}
                if filtered_unsupported:
                    f.write("\nUnsupported Formats:\n")
                    for fmt, count in sorted(filtered_unsupported.items()):
                        f.write(f"  {fmt}: {count}\n")
            
            if self.stats.errors:
                f.write(f"\nErrors ({len(self.stats.errors)}):\n")
                for error in self.stats.errors:
                    f.write(f"  - {error}\n")

    def run_export(self):
        """Main export process"""
        self.logger.info("Starting photo export process...")
        
        # Create export directory
        self._create_export_directory()
        
        # Find all files (supported and unsupported) - recursively scan subdirectories
        all_files = list(self.source_dir.rglob("*"))
        photo_files = []
        
        for file_path in all_files:
            if file_path.is_file() and not file_path.name.startswith('.'):
                if self._is_supported_format(file_path):
                    # Add photos/videos and AAE files (metadata files that need processing)
                    if file_path.suffix.lower() in self.SUPPORTED_IMAGE_FORMATS | self.SUPPORTED_VIDEO_FORMATS:
                        photo_files.append(file_path)
                    elif file_path.suffix.lower() in self.SUPPORTED_METADATA_FORMATS:
                        # AAE files will be processed alongside their corresponding photos
                        pass
                else:
                    # Process unsupported file for statistics
                    self.stats.total_files_processed += 1
                    ext = self._get_file_extension(file_path)
                    self.stats.unsupported_formats[ext] += 1
                    
                    # Don't warn about XMP files as they are expected
                    if ext.lower() not in ['.xmp']:
                        self.logger.warning(f"Unsupported format: {file_path}")
        
        self.logger.info(f"Found {len(photo_files)} photo files to process")

        if not photo_files:
            self.logger.warning("No supported photo files found in source directory")
            return
        
        # Detect and handle duplicates
        duplicates = self._detect_duplicates(photo_files)
        if duplicates:
            self.logger.info(f"Duplicate strategy: {self.duplicate_strategy}")
            duplicate_files_to_process = self._handle_duplicates(duplicates)
            
            if self.duplicate_strategy == 'skip_duplicates':
                # Remove all duplicate files from processing
                all_duplicate_files = []
                for paths in duplicates.values():
                    all_duplicate_files.extend(paths)
                photo_files = [f for f in photo_files if f not in all_duplicate_files]
            else:
                # Remove duplicate files from processing list and add back resolved files
                all_duplicate_files = []
                for paths in duplicates.values():
                    all_duplicate_files.extend(paths)
                photo_files = [f for f in photo_files if f not in all_duplicate_files]
                photo_files.extend(duplicate_files_to_process)
            
            self.logger.info(f"After duplicate handling: {len(photo_files)} files to process")
        
        # Process files with progress bar
        with tqdm(photo_files, desc="Processing photos", unit="file") as pbar:
            for photo_path in pbar:
                pbar.set_postfix(file=photo_path.name[:30])
                
                # Process photo
                metadata = self._process_photo_file(photo_path)
                
                if metadata and metadata.is_valid:
                    # Copy photo
                    self._copy_photo(metadata)
        
        # Save metadata
        self._save_export_metadata()
        
        # Print summary
        self._print_summary()

    def _print_summary(self):
        """Print export summary"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("EXPORT SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Files Processed: {self.stats.total_files_processed}")
        self.logger.info(f"Photos Processed: {self.stats.photos_processed}")
        self.logger.info(f"XMP Files Processed: {self.stats.xmp_files_processed}")
        self.logger.info(f"AAE Files Processed: {self.stats.aae_files_processed}")
        self.logger.info(f"Successful Exports: {self.stats.successful_exports}")
        self.logger.info(f"Failed Exports: {self.stats.failed_exports}")
        self.logger.info(f"Duplicates Handled: {self.stats.duplicates_handled}")
        self.logger.info(f"Duplicate Files Found: {self.stats.duplicate_files_found}")
        self.logger.info(f"Duplicate Files Resolved: {self.stats.duplicate_files_resolved}")
        self.logger.info(f"Files Skipped (Duplicates): {self.stats.files_skipped_duplicates}")
        self.logger.info(f"Total Size: {self.stats.total_size_bytes / (1024*1024*1024):.2f} GB")
        
        if self.stats.supported_formats:
            self.logger.info("\nSupported Formats:")
            for fmt, count in self.stats.supported_formats.most_common():
                self.logger.info(f"  {fmt}: {count}")
        
        if self.stats.unsupported_formats:
            # Filter out XMP files from unsupported formats display
            filtered_unsupported = {fmt: count for fmt, count in self.stats.unsupported_formats.items() 
                                  if fmt.lower() not in ['.xmp']}
            if filtered_unsupported:
                self.logger.info("\nUnsupported Formats:")
                for fmt, count in sorted(filtered_unsupported.items()):
                    self.logger.info(f"  {fmt}: {count}")
        
        if self.stats.errors:
            self.logger.warning(f"\nErrors ({len(self.stats.errors)}):")
            for error in self.stats.errors[:10]:  # Show first 10 errors
                self.logger.warning(f"  - {error}")
            if len(self.stats.errors) > 10:
                self.logger.warning(f"  ... and {len(self.stats.errors) - 10} more errors")
        
        if self.is_dry_run:
            self.logger.info(f"\nDRY-RUN COMPLETED - No files were actually copied")
            self.logger.info(f"To execute the export, run with 'run' parameter")
        else:
            self.logger.info(f"\nEXPORT COMPLETED - Files saved to: {self.export_dir}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Apple Photos Export Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 export_photos.py /path/to/photos /path/to/output test
  python3 export_photos.py /path/to/photos /path/to/output run
        """
    )
    
    parser.add_argument('source_dir', help='Source directory with photos and XMP files')
    parser.add_argument('target_dir', help='Target directory for organized photos')
    parser.add_argument('is_dry_run', help='"true" for dry-run, "false" for actual execution')
    parser.add_argument('duplicate_strategy', nargs='?', default='keep_first', 
                       choices=['keep_first', 'skip_duplicates'],
                       help='Strategy for handling duplicates: keep_first (default) or skip_duplicates')
    
    args = parser.parse_args()
    
    # Convert string to boolean
    is_dry_run = args.is_dry_run.lower() in ('true', '1', 'yes', 'on')
    
    try:
        # Create exporter and run
        exporter = PhotoExporter(args.source_dir, args.target_dir, is_dry_run, args.duplicate_strategy)
        exporter.run_export()
        
    except KeyboardInterrupt:
        print("\nExport interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

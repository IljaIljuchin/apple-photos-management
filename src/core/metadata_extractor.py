#!/usr/bin/env python3
"""
Metadata extraction functionality for Apple Photos Export Tool

This module handles extraction of creation dates from EXIF, XMP, and AAE files.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.logging.logger_config import log_debug, log_warning, log_error


class MetadataExtractionError(Exception):
    """Exception raised during metadata extraction"""
    pass


try:
    from PIL import Image, ExifTags
    from PIL.ExifTags import TAGS
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    raise ImportError("Pillow library not found. Install with: pip install Pillow pillow-heif")

try:
    from lxml import etree
except ImportError:
    raise ImportError("lxml library not found. Install with: pip install lxml")

try:
    from dateutil import parser as date_parser
except ImportError:
    raise ImportError("python-dateutil library not found. Install with: pip install python-dateutil")


@dataclass
class PhotoMetadata:
    """Container for photo metadata"""
    original_path: str
    original_filename: str
    file_extension: str
    creation_date: Optional[datetime] = None
    date_source: str = 'unknown'
    is_valid: bool = False
    error_message: Optional[str] = None


class MetadataExtractor:
    """Handles extraction of metadata from photos and associated files"""
    
    def __init__(self):
        self.file_timestamps = {}
    
    def extract_exif_date(self, image_path: Path) -> Optional[datetime]:
        """Extract creation date from EXIF data"""
        try:
            with Image.open(image_path) as img:
                exif_data = img.getexif()
                
                # Look for DateTimeOriginal first, then DateTime
                date_fields = ['DateTimeOriginal', 'DateTime']
                
                for field in date_fields:
                    if field in exif_data:
                        value = exif_data[field]
                        if isinstance(value, str):
                            try:
                                dt = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                                return dt.replace(tzinfo=timezone.utc)
                            except ValueError:
                                continue
                                
        except (OSError, IOError, ValueError, TypeError) as e:
            log_debug(f"Error reading EXIF from {image_path}: {e}")
            raise MetadataExtractionError(f"Failed to extract EXIF data from {image_path}: {e}") from e
        except Exception as e:
            log_error(f"Unexpected error reading EXIF from {image_path}: {e}")
            raise MetadataExtractionError(f"Unexpected error extracting EXIF from {image_path}: {e}") from e
            
        return None

    def extract_xmp_date(self, xmp_path: Path) -> Optional[datetime]:
        """Extract creation date from XMP file"""
        try:
            tree = etree.parse(xmp_path)
            root = tree.getroot()
            
            # Look for DateTimeOriginal in XMP
            namespaces = {
                'exif': 'http://ns.adobe.com/exif/1.0/',
                'xmp': 'http://ns.adobe.com/xap/1.0/',
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
            }
            
            # Try different XPath patterns
            xpath_patterns = [
                ".//exif:DateTimeOriginal",
                ".//xmp:CreateDate",
                ".//rdf:Description[@exif:DateTimeOriginal]",
                ".//rdf:Description[@xmp:CreateDate]"
            ]
            
            for pattern in xpath_patterns:
                elements = root.xpath(pattern, namespaces=namespaces)
                for element in elements:
                    if element.text:
                        try:
                            dt = date_parser.parse(element.text)
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            return dt
                        except Exception:
                            continue
                            
        except (OSError, IOError, etree.XMLSyntaxError, ValueError, TypeError) as e:
            log_debug(f"Error reading XMP from {xmp_path}: {e}")
            raise MetadataExtractionError(f"Failed to extract XMP data from {xmp_path}: {e}") from e
        except Exception as e:
            log_error(f"Unexpected error reading XMP from {xmp_path}: {e}")
            raise MetadataExtractionError(f"Unexpected error extracting XMP from {xmp_path}: {e}") from e
            
        return None

    def get_file_creation_date(self, file_path: Path) -> datetime:
        """Get file creation date as fallback"""
        try:
            stat = file_path.stat()
            timestamp = stat.st_mtime
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except Exception as e:
            log_warning(f"Error getting file date for {file_path}: {e}")
            return datetime.now(timezone.utc)

    def choose_best_date(self, exif_date: Optional[datetime], xmp_date: Optional[datetime], file_date: datetime) -> Tuple[datetime, str]:
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

    def extract_metadata(self, photo_path: Path, supported_formats: set) -> PhotoMetadata:
        """Extract comprehensive metadata from a photo file"""
        try:
            # Check if format is supported
            from src.utils.file_utils import get_file_extension, is_supported_format
            
            if not is_supported_format(photo_path, supported_formats):
                return PhotoMetadata(
                    original_path=str(photo_path),
                    original_filename=photo_path.name,
                    file_extension=get_file_extension(photo_path),
                    is_valid=False,
                    error_message=f"Unsupported format: {get_file_extension(photo_path)}"
                )
            
            # Extract EXIF date
            exif_date = None
            if get_file_extension(photo_path) in {'.jpg', '.jpeg', '.png', '.tiff', '.tif'}:
                try:
                    exif_date = self.extract_exif_date(photo_path)
                except MetadataExtractionError:
                    # Continue without EXIF data
                    pass
            
            # Extract XMP date
            from src.utils.file_utils import find_xmp_file
            xmp_path = find_xmp_file(photo_path)
            xmp_date = None
            if xmp_path:
                try:
                    xmp_date = self.extract_xmp_date(xmp_path)
                except MetadataExtractionError:
                    # Continue without XMP data
                    pass
            
            # Get file date as fallback
            file_date = self.get_file_creation_date(photo_path)
            
            # Choose the best date
            creation_date, date_source = self.choose_best_date(exif_date, xmp_date, file_date)
            
            return PhotoMetadata(
                original_path=str(photo_path),
                original_filename=photo_path.name,
                file_extension=get_file_extension(photo_path),
                creation_date=creation_date,
                date_source=date_source,
                is_valid=True
            )
            
        except Exception as e:
            log_error(f"Error extracting metadata from {photo_path}: {e}")
            return PhotoMetadata(
                original_path=str(photo_path),
                original_filename=photo_path.name,
                file_extension=get_file_extension(photo_path) if 'get_file_extension' in locals() else '.unknown',
                is_valid=False,
                error_message=f"Metadata extraction failed: {e}"
            )

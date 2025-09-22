#!/usr/bin/env python3
"""
Test suite for Apple Photos Export Tool

This module contains comprehensive tests for the photo export functionality,
including unit tests, integration tests, and mock data generation.

Usage:
    python3 -m pytest test_export_photos.py -v
    python3 -m pytest test_export_photos.py::TestPhotoExporter::test_basic_functionality -v
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from export_photos import PhotoExporter, PhotoMetadata, ExportStats


class TestPhotoExporter:
    """Test cases for PhotoExporter class"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.target_dir = Path(self.temp_dir) / "target"
        
        # Create test directories
        self.source_dir.mkdir(parents=True)
        self.target_dir.mkdir(parents=True)
        
        # Create exporter instance
        self.exporter = PhotoExporter(str(self.source_dir), str(self.target_dir), is_dry_run=True)
    
    def teardown_method(self):
        """Cleanup after each test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test PhotoExporter initialization"""
        assert self.exporter.source_dir == self.source_dir
        assert self.exporter.target_dir == self.target_dir
        assert self.exporter.is_dry_run is True
        assert isinstance(self.exporter.stats, ExportStats)
        assert self.exporter.file_timestamps == {}
    
    def test_supported_formats(self):
        """Test supported format detection"""
        # Test supported image formats
        assert self.exporter._is_supported_format(Path("test.heic"))
        assert self.exporter._is_supported_format(Path("test.jpg"))
        assert self.exporter._is_supported_format(Path("test.jpeg"))
        assert self.exporter._is_supported_format(Path("test.png"))
        assert self.exporter._is_supported_format(Path("test.mov"))
        assert self.exporter._is_supported_format(Path("test.mp4"))
        
        # Test unsupported formats
        assert not self.exporter._is_supported_format(Path("test.txt"))
        assert not self.exporter._is_supported_format(Path("test.pdf"))
        assert not self.exporter._is_supported_format(Path("test.doc"))
    
    def test_file_extension_extraction(self):
        """Test file extension extraction"""
        assert self.exporter._get_file_extension(Path("test.heic")) == ".heic"
        assert self.exporter._get_file_extension(Path("test.JPG")) == ".jpg"
        assert self.exporter._get_file_extension(Path("test.MOV")) == ".mov"
        assert self.exporter._get_file_extension(Path("test")) == ""
    
    def test_generate_filename(self):
        """Test filename generation"""
        test_date = datetime(2023, 12, 15, 14, 30, 22, 123000, tzinfo=timezone.utc)
        
        # Test with milliseconds
        filename = self.exporter._generate_filename(test_date, ".heic")
        assert filename == "20231215-143022-123.heic"
        
        # Test without milliseconds
        test_date_no_ms = datetime(2023, 12, 15, 14, 30, 22, 0, tzinfo=timezone.utc)
        filename = self.exporter._generate_filename(test_date_no_ms, ".jpg")
        assert filename == "20231215-143022-001.jpg"
        
        # Test duplicate handling
        filename2 = self.exporter._generate_filename(test_date_no_ms, ".jpg")
        assert filename2 == "20231215-143022-002.jpg"
    
    def test_choose_best_date(self):
        """Test date selection logic"""
        exif_date = datetime(2023, 6, 15, 14, 30, 22, tzinfo=timezone.utc)
        xmp_date = datetime(2023, 12, 1, 9, 15, 33, tzinfo=timezone.utc)
        file_date = datetime(2023, 12, 15, 16, 20, 44, tzinfo=timezone.utc)
        
        # Test with both EXIF and XMP (should choose earlier - EXIF)
        date, source = self.exporter._choose_best_date(exif_date, xmp_date, file_date)
        assert date == exif_date
        assert source == "exif"
        
        # Test with only EXIF
        date, source = self.exporter._choose_best_date(exif_date, None, file_date)
        assert date == exif_date
        assert source == "exif"
        
        # Test with only XMP
        date, source = self.exporter._choose_best_date(None, xmp_date, file_date)
        assert date == xmp_date
        assert source == "xmp"
        
        # Test with neither (fallback to file date)
        date, source = self.exporter._choose_best_date(None, None, file_date)
        assert date == file_date
        assert source == "file"
    
    def test_create_directory_structure(self):
        """Test directory structure creation"""
        # Test dry run (should not create directories)
        dir_path = self.exporter._create_directory_structure(2023, 12, 15)
        expected_path = self.exporter.export_dir / "2023" / "12" / "15"
        assert dir_path == expected_path
        assert not dir_path.exists()  # Should not exist in dry run
    
    def test_get_file_creation_date(self):
        """Test file creation date extraction"""
        # Create a test file
        test_file = self.source_dir / "test.txt"
        test_file.write_text("test content")
        
        # Get creation date
        file_date = self.exporter._get_file_creation_date(test_file)
        assert isinstance(file_date, datetime)
        assert file_date.tzinfo == timezone.utc
    
    @patch('export_photos.Image.open')
    def test_extract_exif_date(self, mock_image_open):
        """Test EXIF date extraction"""
        # Mock EXIF data
        mock_img = Mock()
        mock_img._getexif.return_value = {
            306: '2023:06:15 14:30:22',  # DateTime
            36867: '2023:06:15 14:30:22',  # DateTimeOriginal
        }
        mock_image_open.return_value.__enter__.return_value = mock_img
        
        # Test EXIF extraction
        test_file = self.source_dir / "test.jpg"
        test_file.write_text("fake image")
        
        exif_date = self.exporter._extract_exif_date(test_file)
        assert exif_date is not None
        assert exif_date.year == 2023
        assert exif_date.month == 6
        assert exif_date.day == 15
    
    def test_extract_xmp_date(self):
        """Test XMP date extraction"""
        # Create test XMP file
        xmp_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <x:xmpmeta xmlns:x="adobe:ns:meta/">
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                <rdf:Description rdf:about=""
                    xmlns:xmp="http://ns.adobe.com/xap/1.0/"
                    xmlns:exif="http://ns.adobe.com/exif/1.0/">
                    <exif:DateTimeOriginal>2023-06-15T14:30:22</exif:DateTimeOriginal>
                </rdf:Description>
            </rdf:RDF>
        </x:xmpmeta>'''
        
        xmp_file = self.source_dir / "test.jpg.xmp"
        xmp_file.write_text(xmp_content)
        
        # Test XMP extraction
        xmp_date = self.exporter._extract_xmp_date(xmp_file)
        assert xmp_date is not None
        assert xmp_date.year == 2023
        assert xmp_date.month == 6
        assert xmp_date.day == 15
    
    def test_process_photo_file(self):
        """Test photo file processing"""
        # Create test photo file
        test_photo = self.source_dir / "test.jpg"
        test_photo.write_text("fake image data")
        
        # Create corresponding XMP file
        xmp_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <x:xmpmeta xmlns:x="adobe:ns:meta/">
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                <rdf:Description rdf:about=""
                    xmlns:xmp="http://ns.adobe.com/xap/1.0/"
                    xmlns:exif="http://ns.adobe.com/exif/1.0/">
                    <exif:DateTimeOriginal>2023-06-15T14:30:22</exif:DateTimeOriginal>
                </rdf:Description>
            </rdf:RDF>
        </x:xmpmeta>'''
        
        xmp_file = self.source_dir / "test.jpg.xmp"
        xmp_file.write_text(xmp_content)
        
        # Process photo
        metadata = self.exporter._process_photo_file(test_photo)
        
        assert metadata is not None
        assert metadata.original_path == str(test_photo)
        assert metadata.original_filename == "test.jpg"
        assert metadata.creation_date is not None
        assert metadata.date_source in ["exif", "xmp", "file"]
        assert metadata.file_extension == ".jpg"
        assert metadata.is_valid is True
    
    def test_process_unsupported_file(self):
        """Test processing of unsupported file format"""
        # Create unsupported file
        test_file = self.source_dir / "test.txt"
        test_file.write_text("text content")
        
        # Process file
        metadata = self.exporter._process_photo_file(test_file)
        
        assert metadata is None
        assert ".txt" in self.exporter.stats.unsupported_formats
    
    def test_copy_photo_dry_run(self):
        """Test photo copying in dry run mode"""
        # Create test metadata
        test_date = datetime(2023, 12, 15, 14, 30, 22, tzinfo=timezone.utc)
        metadata = PhotoMetadata(
            original_path=str(self.source_dir / "test.jpg"),
            original_filename="test.jpg",
            creation_date=test_date,
            date_source="test",
            file_size=1024,
            file_extension=".jpg"
        )
        
        # Create source file
        source_file = self.source_dir / "test.jpg"
        source_file.write_text("fake image")
        
        # Copy photo (dry run)
        result = self.exporter._copy_photo(metadata)
        
        assert result is True
        assert self.exporter.stats.successful_exports == 1
        # In dry run, no actual file should be created
        assert not (self.exporter.export_dir / "2023" / "12" / "15" / "20231215-143022-001.jpg").exists()
    
    def test_duplicate_handling(self):
        """Test duplicate filename handling"""
        # Create test metadata with same timestamp
        test_date = datetime(2023, 12, 15, 14, 30, 22, tzinfo=timezone.utc)
        
        metadata1 = PhotoMetadata(
            original_path=str(self.source_dir / "test1.jpg"),
            original_filename="test1.jpg",
            creation_date=test_date,
            date_source="test",
            file_size=1024,
            file_extension=".jpg"
        )
        
        metadata2 = PhotoMetadata(
            original_path=str(self.source_dir / "test2.jpg"),
            original_filename="test2.jpg",
            creation_date=test_date,
            date_source="test",
            file_size=1024,
            file_extension=".jpg"
        )
        
        # Generate filenames
        filename1 = self.exporter._generate_filename(test_date, ".jpg")
        filename2 = self.exporter._generate_filename(test_date, ".jpg")
        
        assert filename1 == "20231215-143022-001.jpg"
        assert filename2 == "20231215-143022-002.jpg"
    
    def test_export_stats(self):
        """Test export statistics tracking"""
        stats = ExportStats()
        
        # Test initial values
        assert stats.total_files_processed == 0
        assert stats.successful_exports == 0
        assert stats.failed_exports == 0
        
        # Test counter updates
        stats.supported_formats[".jpg"] += 1
        stats.unsupported_formats[".txt"] += 1
        stats.errors.append("Test error")
        
        assert stats.supported_formats[".jpg"] == 1
        assert stats.unsupported_formats[".txt"] == 1
        assert len(stats.errors) == 1


class TestMockDataGeneration:
    """Test mock data generation for testing"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir) / "test_data"
        self.test_dir.mkdir(parents=True)
    
    def teardown_method(self):
        """Cleanup after test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_mock_photo(self, filename: str, creation_date: datetime) -> Path:
        """Create a mock photo file with metadata"""
        photo_path = self.test_dir / filename
        photo_path.write_text("fake image data")
        
        # Create XMP file
        xmp_content = f'''<?xml version="1.0" encoding="UTF-8"?>
        <x:xmpmeta xmlns:x="adobe:ns:meta/">
            <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                <rdf:Description rdf:about=""
                    xmlns:xmp="http://ns.adobe.com/xap/1.0/"
                    xmlns:exif="http://ns.adobe.com/exif/1.0/">
                    <exif:DateTimeOriginal>{creation_date.strftime('%Y-%m-%dT%H:%M:%S')}</exif:DateTimeOriginal>
                </rdf:Description>
            </rdf:RDF>
        </x:xmpmeta>'''
        
        xmp_path = self.test_dir / f"{filename}.xmp"
        xmp_path.write_text(xmp_content)
        
        return photo_path
    
    def test_create_mock_photos(self):
        """Test creation of mock photo data"""
        # Create photos from different years
        photos = []
        photos.append(self.create_mock_photo("photo_2023_01.jpg", 
                                           datetime(2023, 1, 15, 14, 30, 22, tzinfo=timezone.utc)))
        photos.append(self.create_mock_photo("photo_2023_06.heic", 
                                           datetime(2023, 6, 20, 9, 15, 33, tzinfo=timezone.utc)))
        photos.append(self.create_mock_photo("photo_2024_03.png", 
                                           datetime(2024, 3, 10, 16, 45, 11, tzinfo=timezone.utc)))
        
        # Verify files were created
        assert len(photos) == 3
        for photo in photos:
            assert photo.exists()
            assert photo.with_suffix(photo.suffix + '.xmp').exists()
    
    def test_create_test_dataset(self):
        """Test creation of comprehensive test dataset"""
        # Create photos for different scenarios
        test_photos = [
            ("normal_photo.jpg", datetime(2023, 6, 15, 14, 30, 22, tzinfo=timezone.utc)),
            ("duplicate_time1.heic", datetime(2023, 6, 15, 14, 30, 22, tzinfo=timezone.utc)),
            ("duplicate_time2.heic", datetime(2023, 6, 15, 14, 30, 22, tzinfo=timezone.utc)),
            ("old_photo.png", datetime(2020, 3, 10, 9, 15, 33, tzinfo=timezone.utc)),
            ("recent_photo.mov", datetime(2024, 12, 25, 20, 0, 0, tzinfo=timezone.utc)),
            ("unsupported.txt", datetime(2023, 6, 15, 14, 30, 22, tzinfo=timezone.utc)),
        ]
        
        created_photos = []
        for filename, date in test_photos:
            if filename.endswith(('.jpg', '.heic', '.png', '.mov')):
                photo = self.create_mock_photo(filename, date)
                created_photos.append(photo)
            else:
                # Create unsupported file
                unsupported_file = self.test_dir / filename
                unsupported_file.write_text("unsupported content")
                created_photos.append(unsupported_file)
        
        # Verify test dataset
        assert len(created_photos) == 6
        assert len(list(self.test_dir.glob("*.xmp"))) == 5  # Only supported formats have XMP


class TestIntegration:
    """Integration tests for the complete export process"""
    
    def setup_method(self):
        """Setup integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = Path(self.temp_dir) / "source"
        self.target_dir = Path(self.temp_dir) / "target"
        
        self.source_dir.mkdir(parents=True)
        self.target_dir.mkdir(parents=True)
    
    def teardown_method(self):
        """Cleanup after integration test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_photos(self):
        """Create a set of test photos with various scenarios"""
        test_data = [
            ("IMG_001.jpg", datetime(2023, 6, 15, 14, 30, 22, tzinfo=timezone.utc)),
            ("IMG_002.heic", datetime(2023, 6, 15, 14, 30, 22, tzinfo=timezone.utc)),  # Duplicate time
            ("IMG_003.png", datetime(2023, 6, 20, 9, 15, 33, tzinfo=timezone.utc)),
            ("IMG_004.mov", datetime(2024, 3, 10, 16, 45, 11, tzinfo=timezone.utc)),
            ("IMG_005.jpg", datetime(2024, 12, 25, 20, 0, 0, tzinfo=timezone.utc)),
        ]
        
        for filename, date in test_data:
            # Create photo file
            photo_path = self.source_dir / filename
            photo_path.write_text("fake image data")
            
            # Create XMP file
            xmp_content = f'''<?xml version="1.0" encoding="UTF-8"?>
            <x:xmpmeta xmlns:x="adobe:ns:meta/">
                <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                    <rdf:Description rdf:about=""
                        xmlns:xmp="http://ns.adobe.com/xap/1.0/"
                        xmlns:exif="http://ns.adobe.com/exif/1.0/">
                        <exif:DateTimeOriginal>{date.strftime('%Y-%m-%dT%H:%M:%S')}</exif:DateTimeOriginal>
                    </rdf:Description>
                </rdf:RDF>
            </x:xmpmeta>'''
            
            xmp_path = self.source_dir / f"{filename}.xmp"
            xmp_path.write_text(xmp_content)
    
    def test_full_export_process_dry_run(self):
        """Test complete export process in dry run mode"""
        # Create test photos
        self.create_test_photos()
        
        # Create exporter
        exporter = PhotoExporter(str(self.source_dir), str(self.target_dir), is_dry_run=True)
        
        # Run export
        exporter.run_export()
        
        # Verify statistics
        assert exporter.stats.total_files_processed == 10  # 5 photos + 5 XMP files
        assert exporter.stats.photos_processed == 5
        assert exporter.stats.xmp_files_processed == 5
        assert exporter.stats.successful_exports == 5
        assert exporter.stats.failed_exports == 0
        
        # Verify no actual files were created (dry run)
        assert not any(self.target_dir.rglob("*"))
    
    def test_export_with_unsupported_files(self):
        """Test export with unsupported file formats"""
        # Create mixed file types
        self.create_test_photos()
        
        # Add unsupported files
        unsupported_files = ["readme.txt", "config.json", "script.py"]
        for filename in unsupported_files:
            (self.source_dir / filename).write_text("unsupported content")
        
        # Create exporter and run
        exporter = PhotoExporter(str(self.source_dir), str(self.target_dir), is_dry_run=True)
        exporter.run_export()
        
        # Verify statistics
        assert exporter.stats.total_files_processed == 13  # 5 photos + 5 XMP + 3 unsupported
        assert exporter.stats.photos_processed == 5
        assert len(exporter.stats.unsupported_formats) > 0
        assert ".txt" in exporter.stats.unsupported_formats
        assert ".json" in exporter.stats.unsupported_formats
        assert ".py" in exporter.stats.unsupported_formats


def run_tests():
    """Run all tests"""
    import subprocess
    import sys
    
    # Run pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        __file__, 
        "-v", 
        "--tb=short",
        "--color=yes"
    ], capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    return result.returncode == 0


if __name__ == "__main__":
    # Run tests when script is executed directly
    success = run_tests()
    sys.exit(0 if success else 1)

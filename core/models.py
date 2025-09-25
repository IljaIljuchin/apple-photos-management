"""
Data models for Apple Photos Management Tool.

This module defines all data structures used throughout the application,
including metadata, statistics, and configuration models.

Author: AI Assistant
Version: 2.0.0
License: MIT
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum


class FileType(Enum):
    """File type categories."""
    IMAGE = "image"
    VIDEO = "video"
    METADATA = "metadata"
    OTHER = "other"


class ProcessingStatus(Enum):
    """Processing status for files."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PhotoMetadata:
    """
    Metadata for a photo file.
    
    This class holds all metadata extracted from a photo file,
    including creation date, file information, and processing status.
    """
    original_path: Path
    original_filename: str
    file_extension: str
    file_size: int
    creation_date: Optional[datetime] = None
    is_valid: bool = True
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None
    
    # Metadata sources
    exif_date: Optional[datetime] = None
    xmp_date: Optional[datetime] = None
    aae_date: Optional[datetime] = None
    file_date: Optional[datetime] = None
    
    # File type information
    file_type: FileType = FileType.IMAGE
    
    # Associated files
    xmp_path: Optional[Path] = None
    aae_path: Optional[Path] = None
    
    # Processing information
    processing_time: float = 0.0
    worker_id: Optional[int] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Normalize file extension to lowercase
        self.file_extension = self.file_extension.lower()
        
        # Determine file type based on extension
        self.file_type = self._determine_file_type()
        
        # Choose best creation date
        if self.creation_date is None:
            self.creation_date = self._choose_best_date()
    
    def _determine_file_type(self) -> FileType:
        """Determine file type based on extension."""
        image_extensions = {'.heic', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.raw', '.cr2', '.nef', '.arw'}
        video_extensions = {'.mov', '.mp4', '.avi', '.mkv', '.m4v'}
        metadata_extensions = {'.xmp', '.aae'}
        
        if self.file_extension in image_extensions:
            return FileType.IMAGE
        elif self.file_extension in video_extensions:
            return FileType.VIDEO
        elif self.file_extension in metadata_extensions:
            return FileType.METADATA
        else:
            return FileType.OTHER
    
    def _choose_best_date(self) -> Optional[datetime]:
        """Choose the best available date from all sources."""
        # Priority order: EXIF > XMP > AAE > file date
        for date in [self.exif_date, self.xmp_date, self.aae_date, self.file_date]:
            if date is not None:
                return date
        return None
    
    def has_metadata(self) -> bool:
        """Check if file has any metadata."""
        return any([self.exif_date, self.xmp_date, self.aae_date])
    
    def has_associated_files(self) -> bool:
        """Check if file has associated XMP or AAE files."""
        return any([self.xmp_path, self.aae_path])
    
    def get_associated_files(self) -> List[Path]:
        """Get list of associated files."""
        files = []
        if self.xmp_path:
            files.append(self.xmp_path)
        if self.aae_path:
            files.append(self.aae_path)
        return files


@dataclass
class ExportStats:
    """
    Statistics for export operations.
    
    This class tracks various metrics during the export process,
    including file counts, processing times, and error information.
    """
    # File counts
    total_files: int = 0
    processed_files: int = 0
    successful_exports: int = 0
    failed_exports: int = 0
    skipped_files: int = 0
    
    # Duplicate handling
    duplicate_files_found: int = 0
    duplicate_files_resolved: int = 0
    duplicate_files_preserved: int = 0
    duplicate_files_discarded: int = 0
    files_skipped_duplicates: int = 0
    
    # File types
    image_files: int = 0
    video_files: int = 0
    metadata_files: int = 0
    xmp_files: int = 0
    aae_files: int = 0
    
    # Size information
    total_size_bytes: int = 0
    processed_size_bytes: int = 0
    
    # Timing information
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    average_processing_time: float = 0.0
    
    # Performance metrics
    files_per_second: float = 0.0
    bytes_per_second: float = 0.0
    
    # Error information
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Worker information
    max_workers: int = 0
    active_workers: int = 0
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.start_time and self.end_time:
            self.total_duration = (self.end_time - self.start_time).total_seconds()
        
        if self.total_duration > 0:
            self.files_per_second = self.processed_files / self.total_duration
            self.bytes_per_second = self.processed_size_bytes / self.total_duration
        
        if self.processed_files > 0:
            self.average_processing_time = self.total_duration / self.processed_files
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.failed_exports += 1
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def increment_processed(self) -> None:
        """Increment processed files count."""
        self.processed_files += 1
    
    def increment_successful(self) -> None:
        """Increment successful exports count."""
        self.successful_exports += 1
    
    def increment_skipped(self) -> None:
        """Increment skipped files count."""
        self.skipped_files += 1
    
    def add_file_size(self, size: int) -> None:
        """Add file size to total."""
        self.total_size_bytes += size
        self.processed_size_bytes += size
    
    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.processed_files == 0:
            return 0.0
        return (self.successful_exports / self.processed_files) * 100
    
    def get_error_rate(self) -> float:
        """Get error rate as percentage."""
        if self.processed_files == 0:
            return 0.0
        return (self.failed_exports / self.processed_files) * 100
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics as dictionary."""
        return {
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'successful_exports': self.successful_exports,
            'failed_exports': self.failed_exports,
            'skipped_files': self.skipped_files,
            'duplicate_files_found': self.duplicate_files_found,
            'duplicate_files_resolved': self.duplicate_files_resolved,
            'duplicate_files_preserved': self.duplicate_files_preserved,
            'duplicate_files_discarded': self.duplicate_files_discarded,
            'files_skipped_duplicates': self.files_skipped_duplicates,
            'image_files': self.image_files,
            'video_files': self.video_files,
            'metadata_files': self.metadata_files,
            'xmp_files': self.xmp_files,
            'aae_files': self.aae_files,
            'total_size_bytes': self.total_size_bytes,
            'processed_size_bytes': self.processed_size_bytes,
            'total_duration': self.total_duration,
            'average_processing_time': self.average_processing_time,
            'files_per_second': self.files_per_second,
            'bytes_per_second': self.bytes_per_second,
            'success_rate': self.get_success_rate(),
            'error_rate': self.get_error_rate(),
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'max_workers': self.max_workers,
            'active_workers': self.active_workers
        }


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for monitoring and optimization.
    
    This class tracks system and application performance metrics
    during the export process.
    """
    # System metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_io_read: float = 0.0
    disk_io_write: float = 0.0
    
    # Application metrics
    files_processed: int = 0
    files_per_second: float = 0.0
    bytes_processed: int = 0
    bytes_per_second: float = 0.0
    
    # Timing metrics
    operation_times: Dict[str, float] = field(default_factory=dict)
    total_operations: int = 0
    average_operation_time: float = 0.0
    
    # Cache metrics
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0
    
    # Worker metrics
    active_workers: int = 0
    idle_workers: int = 0
    worker_utilization: float = 0.0
    
    # Error metrics
    error_count: int = 0
    warning_count: int = 0
    retry_count: int = 0
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.cache_hits + self.cache_misses > 0:
            self.cache_hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses)
        
        if self.active_workers + self.idle_workers > 0:
            self.worker_utilization = self.active_workers / (self.active_workers + self.idle_workers)
        
        if self.total_operations > 0:
            self.average_operation_time = sum(self.operation_times.values()) / self.total_operations


@dataclass
class DuplicateGroup:
    """
    A group of duplicate files.
    
    This class represents a collection of files that are considered duplicates
    based on their content hash and file type.
    """
    hash_value: str
    file_type: FileType
    files: List[Path] = field(default_factory=list)
    resolved_files: List[Path] = field(default_factory=list)
    preserved_files: List[Path] = field(default_factory=list)
    discarded_files: List[Path] = field(default_factory=list)
    
    def add_file(self, file_path: Path) -> None:
        """Add a file to the duplicate group."""
        if file_path not in self.files:
            self.files.append(file_path)
    
    def resolve_duplicates(self, strategy: str) -> List[Path]:
        """
        Resolve duplicates based on strategy.
        
        Args:
            strategy: Duplicate resolution strategy
            
        Returns:
            List of files to process after resolution
        """
        if not self.files:
            return []
        
        if strategy == 'keep_first':
            # Keep only the first file
            self.resolved_files = [self.files[0]]
            self.discarded_files = self.files[1:]
            return self.resolved_files
        
        elif strategy == 'skip_duplicates':
            # Skip all files in this group
            self.discarded_files = self.files.copy()
            return []
        
        elif strategy == 'preserve_duplicates':
            # Keep first file and preserve one duplicate
            self.resolved_files = [self.files[0]]
            if len(self.files) > 1:
                self.preserved_files = [self.files[1]]
            if len(self.files) > 2:
                self.discarded_files = self.files[2:]
            return self.resolved_files
        
        else:
            # Default to keep_first
            return self.resolve_duplicates('keep_first')
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics for this duplicate group."""
        return {
            'total_files': len(self.files),
            'resolved_files': len(self.resolved_files),
            'preserved_files': len(self.preserved_files),
            'discarded_files': len(self.discarded_files)
        }


@dataclass
class ExportResult:
    """
    Result of an export operation.
    
    This class contains the result of a single file export operation,
    including success status, metadata, and any errors.
    """
    success: bool
    source_path: Path
    target_path: Optional[Path] = None
    metadata: Optional[PhotoMetadata] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0
    file_size: int = 0
    worker_id: Optional[int] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.metadata:
            self.file_size = self.metadata.file_size
            self.processing_time = self.metadata.processing_time
            self.worker_id = self.metadata.worker_id


@dataclass
class BatchResult:
    """
    Result of a batch processing operation.
    
    This class contains the results of processing a batch of files,
    including individual results and batch-level statistics.
    """
    batch_id: int
    total_files: int
    successful_files: int
    failed_files: int
    skipped_files: int
    results: List[ExportResult] = field(default_factory=list)
    processing_time: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def add_result(self, result: ExportResult) -> None:
        """Add a result to the batch."""
        self.results.append(result)
        
        if result.success:
            self.successful_files += 1
        else:
            self.failed_files += 1
    
    def get_success_rate(self) -> float:
        """Get success rate for this batch."""
        if self.total_files == 0:
            return 0.0
        return (self.successful_files / self.total_files) * 100
    
    def get_processing_speed(self) -> float:
        """Get processing speed (files per second) for this batch."""
        if self.processing_time <= 0:
            return 0.0
        return self.total_files / self.processing_time

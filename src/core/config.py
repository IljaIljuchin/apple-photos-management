"""
Centralized configuration management for Apple Photos Management Tool.

This module provides a single source of truth for all configuration values,
replacing hardcoded values scattered throughout the codebase.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Set, Dict, Any, Optional
import os


@dataclass
class FileFormats:
    """Supported file formats configuration."""
    
    # Image formats
    IMAGE_FORMATS: Set[str] = field(default_factory=lambda: {
        '.heic', '.jpg', '.jpeg', '.png', '.tiff', '.tif', 
        '.raw', '.cr2', '.nef', '.arw'
    })
    
    # Video formats
    VIDEO_FORMATS: Set[str] = field(default_factory=lambda: {
        '.mov', '.mp4', '.avi', '.mkv', '.m4v'
    })
    
    # Metadata formats
    METADATA_FORMATS: Set[str] = field(default_factory=lambda: {
        '.aae'  # Apple Adjustment Export files
    })
    
    # Sidecar formats
    SIDECAR_FORMATS: Set[str] = field(default_factory=lambda: {
        '.xmp'  # Extensible Metadata Platform
    })
    
    @property
    def ALL_SUPPORTED_FORMATS(self) -> Set[str]:
        """All supported formats combined."""
        return self.IMAGE_FORMATS | self.VIDEO_FORMATS | self.METADATA_FORMATS
    
    @property
    def PROCESSABLE_FORMATS(self) -> Set[str]:
        """Formats that can be processed (images + videos)."""
        return self.IMAGE_FORMATS | self.VIDEO_FORMATS


@dataclass
class ProcessingConfig:
    """Processing-related configuration."""
    
    # Worker configuration
    DEFAULT_WORKERS: int = 8
    MAX_WORKERS: int = 16
    MIN_WORKERS: int = 1
    
    # Batch processing
    DEFAULT_BATCH_SIZE: int = 100
    MIN_BATCH_SIZE: int = 10
    MAX_BATCH_SIZE: int = 500
    
    # Memory management
    DEFAULT_CACHE_SIZE: int = 10000
    MAX_CACHE_SIZE: int = 50000
    MEMORY_OPTIMIZATION_THRESHOLD: int = 1000  # Files threshold for streaming
    
    # Progress reporting
    PROGRESS_LOG_INTERVAL: int = 50  # Log every N files
    WORKER_ADJUSTMENT_INTERVAL: int = 100  # Adjust workers every N files
    
    # File operations
    CHUNK_SIZE: int = 8192  # For file hashing and copying
    MAX_FILENAME_LENGTH: int = 255


@dataclass
class DateFormats:
    """Date and time formatting configuration."""
    
    # Filename timestamp format
    FILENAME_TIMESTAMP: str = '%Y%m%d-%H%M%S'
    
    # Log timestamp format
    LOG_TIMESTAMP: str = '%Y-%m-%d %H:%M:%S.%f'
    
    # Metadata timestamp format
    METADATA_TIMESTAMP: str = '%Y-%m-%d %H:%M:%S'
    
    # Export directory timestamp format
    EXPORT_DIR_TIMESTAMP: str = '%Y%m%d-%H%M%S'


@dataclass
class SystemConfig:
    """System resource configuration."""
    
    # Memory thresholds
    MEMORY_WARNING_THRESHOLD: float = 80.0  # CPU/Memory usage percentage
    MEMORY_CRITICAL_THRESHOLD: float = 90.0
    
    # Disk space buffer
    DISK_SPACE_BUFFER: float = 1.1  # 10% buffer for disk space calculations
    
    # Performance thresholds
    SLOW_OPERATION_MS: int = 1000  # Operations slower than 1 second
    HIGH_CPU_PERCENT: float = 80.0
    HIGH_MEMORY_PERCENT: float = 85.0
    
    # Metrics retention
    METRICS_RETENTION: int = 1000  # Number of metrics to keep in memory


@dataclass
class LoggingConfig:
    """Logging configuration."""
    
    # Log levels
    DEFAULT_LOG_LEVEL: str = 'INFO'
    AVAILABLE_LOG_LEVELS: Set[str] = field(default_factory=lambda: {
        'DEBUG', 'INFO', 'WARNING', 'ERROR'
    })
    
    # Log formatting
    CONSOLE_FORMAT: str = "<level>{level: <8}</level> | <level>{message}</level>"
    FILE_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
    
    # Log file settings
    LOG_ENCODING: str = 'utf-8'
    LOG_ROTATION: Optional[str] = None  # Disabled for consistency
    LOG_RETENTION: Optional[str] = None  # Disabled for consistency
    LOG_COMPRESSION: Optional[str] = None  # Disabled for consistency


@dataclass
class SecurityConfig:
    """Security-related configuration."""
    
    # Path validation
    ALLOWED_USER_DIRECTORIES: Set[str] = field(default_factory=lambda: {
        'Downloads', 'Pictures', 'Desktop', 'Documents', 
        'Movies', 'Music', 'Public'
    })
    
    # Filename sanitization
    MAX_FILENAME_LENGTH: int = 255
    SUSPICIOUS_PATTERNS: Set[str] = field(default_factory=lambda: {
        '..', '//', '\\\\', '~', '$', '`', '|', '&', ';', 
        '(', ')', '<', '>', '"', "'", '\\n', '\\r', '\\t',
        '\\x00', '\\x01', '\\x02', '\\x03', '\\x04', '\\x05', 
        '\\x06', '\\x07', '\\x08', '\\x0b', '\\x0c', '\\x0e', 
        '\\x0f', '\\x10', '\\x11', '\\x12', '\\x13', '\\x14', 
        '\\x15', '\\x16', '\\x17', '\\x18', '\\x19', '\\x1a', 
        '\\x1b', '\\x1c', '\\x1d', '\\x1e', '\\x1f'
    })


@dataclass
class DuplicateConfig:
    """Duplicate handling configuration."""
    
    # Duplicate strategies
    DEFAULT_STRATEGY: str = 'keep_first'
    AVAILABLE_STRATEGIES: Set[str] = field(default_factory=lambda: {
        'keep_first', 'skip_duplicates', 'preserve_duplicates', 
        'cleanup_duplicates', '!delete!'
    })
    
    # Duplicate preservation limits
    MAX_DUPLICATES_TO_PRESERVE: int = 2  # Keep original + 1 duplicate
    DUPLICATES_CLEANUP_THRESHOLD: int = 1000  # Cleanup if more than N duplicates


@dataclass
class AppConfig:
    """Main application configuration."""
    
    # Application info
    APP_NAME: str = "Apple Photos Management Tool"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = "Professional photo export and organization tool"
    
    # File formats
    file_formats: FileFormats = field(default_factory=FileFormats)
    
    # Processing
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    
    # Date formats
    date_formats: DateFormats = field(default_factory=DateFormats)
    
    # System
    system: SystemConfig = field(default_factory=SystemConfig)
    
    # Logging
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Security
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Duplicates
    duplicates: DuplicateConfig = field(default_factory=DuplicateConfig)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values."""
        # Validate worker counts
        if self.processing.MIN_WORKERS > self.processing.MAX_WORKERS:
            raise ValueError("MIN_WORKERS cannot be greater than MAX_WORKERS")
        
        if self.processing.DEFAULT_WORKERS < self.processing.MIN_WORKERS:
            self.processing.DEFAULT_WORKERS = self.processing.MIN_WORKERS
        elif self.processing.DEFAULT_WORKERS > self.processing.MAX_WORKERS:
            self.processing.DEFAULT_WORKERS = self.processing.MAX_WORKERS
        
        # Validate batch sizes
        if self.processing.MIN_BATCH_SIZE > self.processing.MAX_BATCH_SIZE:
            raise ValueError("MIN_BATCH_SIZE cannot be greater than MAX_BATCH_SIZE")
        
        if self.processing.DEFAULT_BATCH_SIZE < self.processing.MIN_BATCH_SIZE:
            self.processing.DEFAULT_BATCH_SIZE = self.processing.MIN_BATCH_SIZE
        elif self.processing.DEFAULT_BATCH_SIZE > self.processing.MAX_BATCH_SIZE:
            self.processing.DEFAULT_BATCH_SIZE = self.processing.MAX_BATCH_SIZE
        
        # Validate log level
        if self.logging.DEFAULT_LOG_LEVEL not in self.logging.AVAILABLE_LOG_LEVELS:
            raise ValueError(f"Invalid log level: {self.logging.DEFAULT_LOG_LEVEL}")
        
        # Validate duplicate strategy
        if self.duplicates.DEFAULT_STRATEGY not in self.duplicates.AVAILABLE_STRATEGIES:
            raise ValueError(f"Invalid duplicate strategy: {self.duplicates.DEFAULT_STRATEGY}")
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        # Override with environment variables if present
        if os.getenv('PHOTO_EXPORT_WORKERS'):
            config.processing.DEFAULT_WORKERS = int(os.getenv('PHOTO_EXPORT_WORKERS'))
        
        if os.getenv('PHOTO_EXPORT_BATCH_SIZE'):
            config.processing.DEFAULT_BATCH_SIZE = int(os.getenv('PHOTO_EXPORT_BATCH_SIZE'))
        
        if os.getenv('PHOTO_EXPORT_CACHE_SIZE'):
            config.processing.DEFAULT_CACHE_SIZE = int(os.getenv('PHOTO_EXPORT_CACHE_SIZE'))
        
        if os.getenv('PHOTO_EXPORT_LOG_LEVEL'):
            config.logging.DEFAULT_LOG_LEVEL = os.getenv('PHOTO_EXPORT_LOG_LEVEL').upper()
        
        if os.getenv('PHOTO_EXPORT_DUPLICATE_STRATEGY'):
            config.duplicates.DEFAULT_STRATEGY = os.getenv('PHOTO_EXPORT_DUPLICATE_STRATEGY')
        
        return config


# Global configuration instance
config = AppConfig.from_env()


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    return config


def reload_config() -> AppConfig:
    """Reload configuration from environment variables."""
    global config
    config = AppConfig.from_env()
    return config

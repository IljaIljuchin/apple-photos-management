"""
Configuration management for Apple Photos Management Tool.

This module provides centralized configuration management with support for
environment variables, configuration files, and default values.

Author: AI Assistant
Version: 2.0.0
License: MIT
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class DuplicateStrategy(Enum):
    """Duplicate handling strategies."""
    KEEP_FIRST = "keep_first"
    SKIP_DUPLICATES = "skip_duplicates"
    PRESERVE_DUPLICATES = "preserve_duplicates"
    CLEANUP_DUPLICATES = "cleanup_duplicates"
    DELETE = "!delete!"


class DirectoryStructure(Enum):
    """Directory structure options."""
    YEAR = "YEAR"
    YEAR_MONTH = "YEAR_MONTH"
    YEAR_MONTH_DAY = "YEAR_MONTH_DAY"


class HashAlgorithm(Enum):
    """Hash algorithms for duplicate detection."""
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"


@dataclass
class ExportConfig:
    """Export configuration settings."""
    workers: int = 8
    batch_size: int = 100
    cache_size: int = 10000
    memory_optimization: bool = True
    performance_monitoring: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: LogLevel = LogLevel.INFO
    colored_output: bool = True
    structured: bool = False
    max_size_mb: int = 10
    backup_count: int = 5


@dataclass
class PerformanceConfig:
    """Performance configuration settings."""
    monitor_interval: float = 1.0
    metrics_interval: float = 30.0
    auto_optimization: bool = True
    analysis_threshold: int = 100


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    path_validation: bool = True
    sanitize_filenames: bool = True
    allowed_dirs: List[str] = field(default_factory=lambda: [
        "Downloads", "Pictures", "Desktop", "Documents", 
        "Movies", "Music", "Public"
    ])


@dataclass
class DuplicateConfig:
    """Duplicate handling configuration settings."""
    strategy: DuplicateStrategy = DuplicateStrategy.KEEP_FIRST
    optimization: bool = True
    hash_algorithm: HashAlgorithm = HashAlgorithm.MD5


@dataclass
class FileConfig:
    """File organization configuration settings."""
    directory_structure: DirectoryStructure = DirectoryStructure.YEAR
    conflict_resolution: bool = True
    extension_normalization: bool = True


@dataclass
class MetadataConfig:
    """Metadata extraction configuration settings."""
    extract_exif: bool = True
    extract_xmp: bool = True
    extract_aae: bool = True
    fallback_file_date: bool = True


@dataclass
class AdvancedConfig:
    """Advanced configuration settings."""
    experimental_features: bool = False
    debug_mode: bool = False
    verbose_output: bool = False


@dataclass
class Config:
    """Main configuration class."""
    export: ExportConfig = field(default_factory=ExportConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    duplicate: DuplicateConfig = field(default_factory=DuplicateConfig)
    file: FileConfig = field(default_factory=FileConfig)
    metadata: MetadataConfig = field(default_factory=MetadataConfig)
    advanced: AdvancedConfig = field(default_factory=AdvancedConfig)
    
    def __post_init__(self):
        """Post-initialization validation."""
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration values."""
        # Validate export config
        if self.export.workers < 1:
            raise ValueError("Number of workers must be at least 1")
        if self.export.batch_size < 1:
            raise ValueError("Batch size must be at least 1")
        if self.export.cache_size < 1:
            raise ValueError("Cache size must be at least 1")
        
        # Validate performance config
        if self.performance.monitor_interval <= 0:
            raise ValueError("Monitor interval must be positive")
        if self.performance.metrics_interval <= 0:
            raise ValueError("Metrics interval must be positive")
        if self.performance.analysis_threshold < 0:
            raise ValueError("Analysis threshold must be non-negative")
        
        # Validate logging config
        if self.logging.max_size_mb < 1:
            raise ValueError("Max log size must be at least 1 MB")
        if self.logging.backup_count < 0:
            raise ValueError("Backup count must be non-negative")


class ConfigManager:
    """Configuration manager for loading and managing settings."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file
        self._config: Optional[Config] = None
    
    def load_config(self) -> Config:
        """
        Load configuration from environment variables and config file.
        
        Returns:
            Loaded configuration object
        """
        if self._config is None:
            self._config = self._load_from_sources()
        return self._config
    
    def _load_from_sources(self) -> Config:
        """Load configuration from all sources."""
        # Start with defaults
        config = Config()
        
        # Load from environment variables
        config = self._load_from_env(config)
        
        # Load from config file if provided
        if self.config_file and self.config_file.exists():
            config = self._load_from_file(config)
        
        return config
    
    def _load_from_env(self, config: Config) -> Config:
        """Load configuration from environment variables."""
        # Export configuration
        config.export.workers = int(os.getenv('EXPORT_WORKERS', config.export.workers))
        config.export.batch_size = int(os.getenv('EXPORT_BATCH_SIZE', config.export.batch_size))
        config.export.cache_size = int(os.getenv('EXPORT_CACHE_SIZE', config.export.cache_size))
        config.export.memory_optimization = self._parse_bool(
            os.getenv('EXPORT_MEMORY_OPTIMIZATION', str(config.export.memory_optimization))
        )
        config.export.performance_monitoring = self._parse_bool(
            os.getenv('EXPORT_PERFORMANCE_MONITORING', str(config.export.performance_monitoring))
        )
        
        # Logging configuration
        log_level = os.getenv('LOG_LEVEL', config.logging.level.value)
        try:
            config.logging.level = LogLevel(log_level)
        except ValueError:
            config.logging.level = LogLevel.INFO
        
        config.logging.colored_output = self._parse_bool(
            os.getenv('LOG_COLORED_OUTPUT', str(config.logging.colored_output))
        )
        config.logging.structured = self._parse_bool(
            os.getenv('LOG_STRUCTURED', str(config.logging.structured))
        )
        config.logging.max_size_mb = int(os.getenv('LOG_MAX_SIZE', config.logging.max_size_mb))
        config.logging.backup_count = int(os.getenv('LOG_BACKUP_COUNT', config.logging.backup_count))
        
        # Performance configuration
        config.performance.monitor_interval = float(
            os.getenv('PERF_MONITOR_INTERVAL', config.performance.monitor_interval)
        )
        config.performance.metrics_interval = float(
            os.getenv('PERF_METRICS_INTERVAL', config.performance.metrics_interval)
        )
        config.performance.auto_optimization = self._parse_bool(
            os.getenv('PERF_AUTO_OPTIMIZATION', str(config.performance.auto_optimization))
        )
        config.performance.analysis_threshold = int(
            os.getenv('PERF_ANALYSIS_THRESHOLD', config.performance.analysis_threshold)
        )
        
        # Security configuration
        config.security.path_validation = self._parse_bool(
            os.getenv('SECURITY_PATH_VALIDATION', str(config.security.path_validation))
        )
        config.security.sanitize_filenames = self._parse_bool(
            os.getenv('SECURITY_SANITIZE_FILENAMES', str(config.security.sanitize_filenames))
        )
        
        allowed_dirs = os.getenv('SECURITY_ALLOWED_DIRS')
        if allowed_dirs:
            config.security.allowed_dirs = [d.strip() for d in allowed_dirs.split(',')]
        
        # Duplicate configuration
        duplicate_strategy = os.getenv('DUPLICATE_STRATEGY', config.duplicate.strategy.value)
        try:
            config.duplicate.strategy = DuplicateStrategy(duplicate_strategy)
        except ValueError:
            config.duplicate.strategy = DuplicateStrategy.KEEP_FIRST
        
        config.duplicate.optimization = self._parse_bool(
            os.getenv('DUPLICATE_OPTIMIZATION', str(config.duplicate.optimization))
        )
        
        hash_algorithm = os.getenv('DUPLICATE_HASH_ALGORITHM', config.duplicate.hash_algorithm.value)
        try:
            config.duplicate.hash_algorithm = HashAlgorithm(hash_algorithm)
        except ValueError:
            config.duplicate.hash_algorithm = HashAlgorithm.MD5
        
        # File configuration
        dir_structure = os.getenv('FILE_DIRECTORY_STRUCTURE', config.file.directory_structure.value)
        try:
            config.file.directory_structure = DirectoryStructure(dir_structure)
        except ValueError:
            config.file.directory_structure = DirectoryStructure.YEAR
        
        config.file.conflict_resolution = self._parse_bool(
            os.getenv('FILE_CONFLICT_RESOLUTION', str(config.file.conflict_resolution))
        )
        config.file.extension_normalization = self._parse_bool(
            os.getenv('FILE_EXTENSION_NORMALIZATION', str(config.file.extension_normalization))
        )
        
        # Metadata configuration
        config.metadata.extract_exif = self._parse_bool(
            os.getenv('METADATA_EXTRACT_EXIF', str(config.metadata.extract_exif))
        )
        config.metadata.extract_xmp = self._parse_bool(
            os.getenv('METADATA_EXTRACT_XMP', str(config.metadata.extract_xmp))
        )
        config.metadata.extract_aae = self._parse_bool(
            os.getenv('METADATA_EXTRACT_AAE', str(config.metadata.extract_aae))
        )
        config.metadata.fallback_file_date = self._parse_bool(
            os.getenv('METADATA_FALLBACK_FILE_DATE', str(config.metadata.fallback_file_date))
        )
        
        # Advanced configuration
        config.advanced.experimental_features = self._parse_bool(
            os.getenv('EXPERIMENTAL_FEATURES', str(config.advanced.experimental_features))
        )
        config.advanced.debug_mode = self._parse_bool(
            os.getenv('DEBUG_MODE', str(config.advanced.debug_mode))
        )
        config.advanced.verbose_output = self._parse_bool(
            os.getenv('VERBOSE_OUTPUT', str(config.advanced.verbose_output))
        )
        
        return config
    
    def _load_from_file(self, config: Config) -> Config:
        """Load configuration from file (placeholder for future implementation)."""
        # TODO: Implement configuration file loading
        # This could support JSON, YAML, TOML, or INI files
        return config
    
    def _parse_bool(self, value: str) -> bool:
        """Parse boolean value from string."""
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        
        return bool(value)
    
    def get_config(self) -> Config:
        """Get current configuration."""
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def reload_config(self) -> Config:
        """Reload configuration from sources."""
        self._config = None
        return self.load_config()
    
    def save_config(self, config: Config, file_path: Path) -> None:
        """Save configuration to file (placeholder for future implementation)."""
        # TODO: Implement configuration file saving
        pass


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> Config:
    """Get current configuration."""
    return get_config_manager().get_config()


def reload_config() -> Config:
    """Reload configuration from sources."""
    return get_config_manager().reload_config()

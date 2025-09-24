#!/usr/bin/env python3
"""
Centralized logging configuration for Apple Photos Export Tool

This module provides a standardized logging setup using Loguru,
replacing the previous colorlog-based implementation.

Features:
- Structured logging with context
- Automatic log rotation
- Colored console output
- File logging with timestamps
- Performance metrics logging
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger
import json
from datetime import datetime


class PhotoExportLogger:
    """Centralized logger for photo export operations"""
    
    def __init__(self, log_dir: Optional[Path] = None, log_level: str = "INFO", timestamp: str = None, is_dry_run: bool = False):
        self.log_dir = log_dir
        self.log_level = log_level
        self.timestamp = timestamp
        self.is_dry_run = is_dry_run
        self._error_log_created = False
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure Loguru logger with console and file outputs"""
        # Remove default handler
        logger.remove()
        
        # Console output with colors - simplified format
        logger.add(
            sys.stderr,
            format="<level>{level: <8}</level> | <level>{message}</level>",
            level=self.log_level,
            colorize=True,
            backtrace=False,
            diagnose=False
        )
        
        # File output if log directory is provided
        if self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine log file names based on timestamp and mode
            if self.timestamp:
                if self.is_dry_run:
                    # Dry-run mode: only create dry.log and errors.log
                    main_log_name = f"{self.timestamp}_dry.log"
                else:
                    # Run mode: only create export.log and errors.log
                    main_log_name = f"{self.timestamp}_export.log"
                errors_log_name = f"{self.timestamp}_errors.log"
            else:
                if self.is_dry_run:
                    main_log_name = "dry.log"
                else:
                    main_log_name = "export.log"
                errors_log_name = "errors.log"
            
            # Main log file (dry.log for dry-run, export.log for actual export)
            logger.add(
                self.log_dir / main_log_name,
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
                level="DEBUG",
                rotation="10 MB",
                retention="30 days",
                compression="zip",
                encoding="utf-8"
            )
            
            # Error log file will be created on-demand when first error occurs
    
    def _ensure_error_log(self):
        """Create error log file on-demand when first error occurs"""
        if not self._error_log_created and self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine error log file name based on timestamp
            if self.timestamp:
                errors_log_name = f"{self.timestamp}_errors.log"
            else:
                errors_log_name = "errors.log"
            
            # Add error log handler
            logger.add(
                self.log_dir / errors_log_name,
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
                level="ERROR",
                rotation="5 MB",
                retention="90 days",
                compression="zip",
                encoding="utf-8"
            )
            
            self._error_log_created = True

    def get_logger(self):
        """Get the configured logger instance"""
        return logger
    
    def log_export_start(self, source_dir: Path, target_dir: Path, is_dry_run: bool, 
                        max_workers: int, duplicate_strategy: str):
        """Log export operation start with context"""
        logger.info("=" * 60)
        logger.info("PHOTO EXPORT STARTED")
        logger.info("=" * 60)
        logger.info(f"Source directory: {source_dir}")
        logger.info(f"Target directory: {target_dir}")
        logger.info(f"Mode: {'DRY-RUN' if is_dry_run else 'EXECUTE'}")
        logger.info(f"Max workers: {max_workers}")
        logger.info(f"Duplicate strategy: {duplicate_strategy}")
        logger.info(f"Start time: {datetime.now().isoformat()}")
        logger.info("=" * 60)
    
    def log_export_end(self, stats: dict, duration: float):
        """Log export operation completion with statistics"""
        logger.info("=" * 60)
        logger.info("PHOTO EXPORT COMPLETED")
        logger.info("=" * 60)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Files processed: {stats.get('total_files_processed', 0)}")
        logger.info(f"Photos processed: {stats.get('photos_processed', 0)}")
        logger.info(f"Successful exports: {stats.get('successful_exports', 0)}")
        logger.info(f"Failed exports: {stats.get('failed_exports', 0)}")
        logger.info(f"Duplicates handled: {stats.get('duplicates_handled', 0)}")
        logger.info("=" * 60)
    
    def log_photo_processing(self, photo_path: Path, metadata: dict, success: bool):
        """Log individual photo processing with structured data"""
        context = {
            "photo_path": str(photo_path),
            "filename": photo_path.name,
            "file_size": metadata.get('file_size', 0),
            "creation_date": metadata.get('creation_date'),
            "date_source": metadata.get('date_source'),
            "success": success
        }
        
        if success:
            logger.debug("Photo processed successfully", **context)
        else:
            logger.warning("Photo processing failed", **context)
    
    def log_duplicate_detection(self, duplicates: dict):
        """Log duplicate detection results"""
        if duplicates:
            logger.warning(f"Found {len(duplicates)} duplicate groups")
            for filename, paths in duplicates.items():
                logger.warning(f"Duplicate group '{filename}': {len(paths)} files")
        else:
            logger.info("No duplicates found")
    
    def log_performance_metrics(self, operation: str, duration: float, **kwargs):
        """Log performance metrics for analysis"""
        metrics = {
            "operation": operation,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        logger.info("Performance metrics", **metrics)
    
    def log_error_with_context(self, error: Exception, context: dict):
        """Log error with additional context"""
        # Ensure error log file is created when first error occurs
        self._ensure_error_log()
        logger.error(f"Error occurred: {str(error)}", **context)
        logger.exception("Full traceback:")


# Global logger instance
_photo_logger: Optional[PhotoExportLogger] = None


def get_logger() -> PhotoExportLogger:
    """Get the global logger instance"""
    global _photo_logger
    if _photo_logger is None:
        _photo_logger = PhotoExportLogger()
    return _photo_logger


def setup_logging(log_dir: Optional[Path] = None, log_level: str = "INFO", timestamp: str = None, is_dry_run: bool = False) -> PhotoExportLogger:
    """Setup logging configuration"""
    global _photo_logger
    _photo_logger = PhotoExportLogger(log_dir, log_level, timestamp, is_dry_run)
    return _photo_logger


# Convenience functions for common logging operations
def log_info(message: str, **kwargs):
    """Log info message with optional context"""
    logger.info(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Log warning message with optional context"""
    logger.warning(message, **kwargs)


def log_error(message: str, **kwargs):
    """Log error message with optional context"""
    # Ensure error log file is created when first error occurs
    global _photo_logger
    if _photo_logger and hasattr(_photo_logger, '_ensure_error_log'):
        _photo_logger._ensure_error_log()
    logger.error(message, **kwargs)


def log_debug(message: str, **kwargs):
    """Log debug message with optional context"""
    logger.debug(message, **kwargs)


def log_success(message: str, **kwargs):
    """Log success message with optional context"""
    logger.success(message, **kwargs)

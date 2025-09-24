#!/usr/bin/env python3
"""
Performance Optimization Module

This module provides specific optimizations for the Apple Photos Export Tool
based on performance analysis and best practices.

Optimizations:
- Lazy loading and caching
- Batch processing
- Memory optimization
- I/O optimization
- Parallel processing improvements
"""

import os
import sys
import hashlib
import threading
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.logging.logger_config import log_debug, log_info, log_warning, log_error
from src.utils.performance_monitor import get_performance_monitor, timed_operation


class FileCache:
    """Intelligent file system cache to reduce I/O operations"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._cache: Dict[Path, Dict[str, Any]] = {}
        self._access_times: Dict[Path, float] = {}
        self._lock = threading.RLock()
    
    def get_file_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Get cached file information"""
        with self._lock:
            if file_path in self._cache:
                self._access_times[file_path] = time.time()
                return self._cache[file_path]
            return None
    
    def set_file_info(self, file_path: Path, info: Dict[str, Any]):
        """Cache file information"""
        with self._lock:
            # Remove oldest entries if cache is full
            if len(self._cache) >= self.max_size:
                self._evict_oldest()
            
            self._cache[file_path] = info
            self._access_times[file_path] = time.time()
    
    def _evict_oldest(self):
        """Remove the least recently used entry"""
        if not self._access_times:
            return
        
        oldest_path = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        self._cache.pop(oldest_path, None)
        self._access_times.pop(oldest_path, None)
    
    def clear(self):
        """Clear the cache"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()


class BatchProcessor:
    """Process files in optimized batches"""
    
    def __init__(self, batch_size: int = 100, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.file_cache = FileCache()
    
    def process_files_in_batches(self, files: List[Path], processor_func, 
                                progress_callback=None) -> List[Any]:
        """Process files in optimized batches"""
        results = []
        total_files = len(files)
        
        # Split files into batches
        batches = [files[i:i + self.batch_size] for i in range(0, total_files, self.batch_size)]
        
        log_info(f"Processing {total_files} files in {len(batches)} batches of {self.batch_size}")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit batches
            future_to_batch = {
                executor.submit(self._process_batch, batch, processor_func): batch 
                for batch in batches
            }
            
            # Collect results
            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    batch_results = future.result()
                    results.extend(batch_results)
                    
                    if progress_callback:
                        progress_callback(len(results), total_files)
                        
                except Exception as e:
                    log_error(f"Error processing batch: {e}")
                    # Add None results for failed batch
                    results.extend([None] * len(batch))
        
        return results
    
    def _process_batch(self, batch: List[Path], processor_func) -> List[Any]:
        """Process a single batch of files"""
        results = []
        for file_path in batch:
            try:
                result = processor_func(file_path)
                results.append(result)
            except Exception as e:
                log_error(f"Error processing {file_path}: {e}")
                results.append(None)
        return results


class OptimizedFileOperations:
    """Optimized file operations with caching and batching"""
    
    def __init__(self):
        self.file_cache = FileCache()
        self.batch_processor = BatchProcessor()
    
    @lru_cache(maxsize=1000)
    def get_file_extension_cached(self, file_path_str: str) -> str:
        """Cached file extension lookup"""
        return Path(file_path_str).suffix.lower()
    
    @lru_cache(maxsize=1000)
    def is_supported_format_cached(self, file_path_str: str, supported_formats: frozenset) -> bool:
        """Cached format checking"""
        return Path(file_path_str).suffix.lower() in supported_formats
    
    def get_file_info_optimized(self, file_path: Path) -> Dict[str, Any]:
        """Get file information with caching"""
        # Check cache first
        cached_info = self.file_cache.get_file_info(file_path)
        if cached_info:
            return cached_info
        
        # Get file info
        try:
            stat = file_path.stat()
            info = {
                'size': stat.st_size,
                'mtime': stat.st_mtime,
                'exists': True,
                'is_file': file_path.is_file(),
                'extension': file_path.suffix.lower()
            }
            
            # Cache the result
            self.file_cache.set_file_info(file_path, info)
            return info
            
        except (OSError, IOError) as e:
            info = {
                'size': 0,
                'mtime': 0,
                'exists': False,
                'is_file': False,
                'extension': file_path.suffix.lower(),
                'error': str(e)
            }
            self.file_cache.set_file_info(file_path, info)
            return info
    
    def calculate_hash_optimized(self, file_path: Path, chunk_size: int = 8192) -> Optional[str]:
        """Calculate file hash with optimized chunking"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                # Read in chunks to avoid memory issues with large files
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (OSError, IOError) as e:
            log_debug(f"Error calculating hash for {file_path}: {e}")
            return None


class MemoryOptimizer:
    """Memory usage optimization utilities"""
    
    @staticmethod
    def optimize_photo_metadata_list(metadata_list: List[Any]) -> List[Any]:
        """Optimize memory usage of photo metadata list"""
        # Remove unnecessary data and compress
        optimized = []
        for metadata in metadata_list:
            if hasattr(metadata, '__dict__'):
                # Keep only essential fields
                essential_data = {
                    'original_path': getattr(metadata, 'original_path', ''),
                    'original_filename': getattr(metadata, 'original_filename', ''),
                    'creation_date': getattr(metadata, 'creation_date', None),
                    'date_source': getattr(metadata, 'date_source', ''),
                    'file_extension': getattr(metadata, 'file_extension', ''),
                    'is_valid': getattr(metadata, 'is_valid', True)
                }
                optimized.append(essential_data)
            else:
                optimized.append(metadata)
        return optimized
    
    @staticmethod
    def clear_large_objects(*objects):
        """Clear large objects from memory"""
        for obj in objects:
            if hasattr(obj, 'clear'):
                obj.clear()
            elif isinstance(obj, list):
                obj.clear()
            elif isinstance(obj, dict):
                obj.clear()


class IOOptimizer:
    """I/O operation optimizations"""
    
    @staticmethod
    def batch_file_operations(operations: List[Tuple[callable, tuple, dict]], 
                            max_workers: int = 4) -> List[Any]:
        """Execute file operations in parallel batches"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all operations
            future_to_op = {
                executor.submit(op[0], *op[1], **op[2]): i 
                for i, op in enumerate(operations)
            }
            
            # Collect results in order
            results = [None] * len(operations)
            for future in as_completed(future_to_op):
                index = future_to_op[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    log_error(f"Error in batch operation {index}: {e}")
                    results[index] = None
        
        return results
    
    @staticmethod
    def preload_directory_structure(directory: Path) -> Set[Path]:
        """Preload directory structure to reduce I/O during processing"""
        files = set()
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    files.add(file_path)
        except (OSError, IOError) as e:
            log_warning(f"Error preloading directory {directory}: {e}")
        
        return files


class PerformanceOptimizer:
    """Main performance optimization coordinator"""
    
    def __init__(self, enable_optimizations: bool = True):
        self.enable_optimizations = enable_optimizations
        self.file_ops = OptimizedFileOperations()
        self.memory_opt = MemoryOptimizer()
        self.io_opt = IOOptimizer()
        self.batch_processor = BatchProcessor()
        
        # Performance monitoring
        self.monitor = get_performance_monitor()
    
    @timed_operation("optimize_file_processing")
    def optimize_file_processing(self, files: List[Path], 
                               processor_func, 
                               batch_size: int = 100) -> List[Any]:
        """Optimize file processing with batching and caching"""
        if not self.enable_optimizations:
            # Fallback to simple processing
            return [processor_func(f) for f in files]
        
        # Use batch processing
        return self.batch_processor.process_files_in_batches(
            files, processor_func, self._progress_callback
        )
    
    def _progress_callback(self, processed: int, total: int):
        """Progress callback for batch processing"""
        if processed % 100 == 0:  # Log every 100 files
            log_debug(f"Processed {processed}/{total} files ({processed/total*100:.1f}%)")
    
    @timed_operation("optimize_memory_usage")
    def optimize_memory_usage(self, data_structures: List[Any]):
        """Optimize memory usage of data structures"""
        if not self.enable_optimizations:
            return data_structures
        
        optimized = []
        for ds in data_structures:
            if isinstance(ds, list):
                optimized.append(self.memory_opt.optimize_photo_metadata_list(ds))
            else:
                optimized.append(ds)
        
        return optimized
    
    @timed_operation("optimize_io_operations")
    def optimize_io_operations(self, operations: List[Tuple[callable, tuple, dict]]) -> List[Any]:
        """Optimize I/O operations with parallel processing"""
        if not self.enable_optimizations:
            # Fallback to sequential processing
            return [op[0](*op[1], **op[2]) for op in operations]
        
        return self.io_opt.batch_file_operations(operations)
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        # Get current performance stats
        stats = self.monitor.get_overall_stats()
        if not stats:
            return recommendations
        
        # Throughput recommendations
        throughput = stats.get('throughput_files_per_sec', 0)
        if throughput < 20:
            recommendations.append("Consider increasing batch size for better throughput")
        
        if throughput < 10:
            recommendations.append("Consider increasing worker count for parallel processing")
        
        # Memory recommendations
        system_stats = self.monitor.get_system_metrics_summary()
        if system_stats:
            memory_usage = system_stats.get('avg_memory_percent', 0)
            if memory_usage > 80:
                recommendations.append("High memory usage detected. Consider reducing batch size or enabling memory optimization")
        
        # Operation-specific recommendations
        if 'operation_breakdown' in stats:
            for operation, op_stats in stats['operation_breakdown'].items():
                if op_stats['avg_duration'] > 1.0:
                    recommendations.append(f"Slow operation '{operation}' detected. Consider optimizing this operation")
        
        return recommendations
    
    def enable_optimization(self, optimization: str, enabled: bool = True):
        """Enable or disable specific optimizations"""
        if optimization == "caching":
            # Enable/disable file caching
            pass
        elif optimization == "batching":
            # Enable/disable batch processing
            pass
        elif optimization == "memory":
            # Enable/disable memory optimization
            pass
        elif optimization == "io":
            # Enable/disable I/O optimization
            pass
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance optimization summary"""
        stats = self.monitor.get_overall_stats()
        system_stats = self.monitor.get_system_metrics_summary()
        
        return {
            'optimizations_enabled': self.enable_optimizations,
            'performance_stats': stats,
            'system_stats': system_stats,
            'recommendations': self.get_optimization_recommendations(),
            'cache_stats': {
                'file_cache_size': len(self.file_ops.file_cache._cache),
                'lru_cache_info': {
                    'file_extension_cache': self.file_ops.get_file_extension_cached.cache_info(),
                    'format_check_cache': self.file_ops.is_supported_format_cached.cache_info()
                }
            }
        }


# Global optimizer instance
_performance_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer

#!/usr/bin/env python3
"""
Performance Monitoring and Telemetry System

This module provides comprehensive performance monitoring, metrics collection,
and debugging capabilities for the Apple Photos Export Tool.

Features:
- Real-time performance metrics
- Bottleneck identification
- Memory usage tracking
- I/O operation monitoring
- Automatic performance optimization suggestions
"""

import time
import psutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.logging.logger_config import log_debug, log_info, log_warning, log_error


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationTiming:
    """Timing information for a specific operation"""
    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def finish(self, success: bool = True, error_message: Optional[str] = None, **metadata):
        """Finish timing the operation"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error_message = error_message
        self.metadata.update(metadata)


@dataclass
class SystemMetrics:
    """System resource metrics"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    timestamp: datetime


class PerformanceMonitor:
    """Comprehensive performance monitoring system"""
    
    def __init__(self, enable_monitoring: bool = True, metrics_retention: int = 1000):
        self.enable_monitoring = enable_monitoring
        self.metrics_retention = metrics_retention
        
        # Metrics storage
        self.metrics: deque = deque(maxlen=metrics_retention)
        self.operation_timings: Dict[str, List[OperationTiming]] = defaultdict(list)
        self.current_operations: Dict[str, OperationTiming] = {}
        
        # System metrics
        self.system_metrics: deque = deque(maxlen=100)  # Keep last 100 system snapshots
        
        # Performance thresholds
        self.thresholds = {
            'slow_operation_ms': 1000,  # Operations slower than 1 second
            'very_slow_operation_ms': 5000,  # Operations slower than 5 seconds
            'high_cpu_percent': 80,  # CPU usage above 80%
            'high_memory_percent': 85,  # Memory usage above 85%
            'low_throughput_files_per_sec': 10,  # Less than 10 files per second
        }
        
        # Statistics
        self.total_operations = 0
        self.failed_operations = 0
        self.total_processing_time = 0.0
        
        # Monitoring thread
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        
        if self.enable_monitoring:
            self._start_system_monitoring()
    
    def _start_system_monitoring(self):
        """Start background system monitoring"""
        def monitor_system():
            while not self._stop_monitoring.is_set():
                try:
                    # Get system metrics
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk_io = psutil.disk_io_counters()
                    
                    system_metric = SystemMetrics(
                        cpu_percent=cpu_percent,
                        memory_percent=memory.percent,
                        memory_used_mb=memory.used / (1024 * 1024),
                        memory_available_mb=memory.available / (1024 * 1024),
                        disk_io_read_mb=disk_io.read_bytes / (1024 * 1024) if disk_io else 0,
                        disk_io_write_mb=disk_io.write_bytes / (1024 * 1024) if disk_io else 0,
                        timestamp=datetime.now(timezone.utc)
                    )
                    
                    self.system_metrics.append(system_metric)
                    
                    # Check for performance issues
                    self._check_performance_issues(system_metric)
                    
                except Exception as e:
                    log_debug(f"Error in system monitoring: {e}")
                
                time.sleep(2)  # Monitor every 2 seconds
        
        self._monitoring_thread = threading.Thread(target=monitor_system, daemon=True)
        self._monitoring_thread.start()
    
    def _check_performance_issues(self, metrics: SystemMetrics):
        """Check for performance issues and log warnings"""
        issues = []
        
        if metrics.cpu_percent > self.thresholds['high_cpu_percent']:
            issues.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > self.thresholds['high_memory_percent']:
            issues.append(f"High memory usage: {metrics.memory_percent:.1f}%")
        
        if issues:
            log_warning(f"Performance issues detected: {'; '.join(issues)}")
    
    def start_operation(self, operation: str, **metadata) -> OperationTiming:
        """Start timing an operation"""
        if not self.enable_monitoring:
            return OperationTiming(operation, time.time())
        
        timing = OperationTiming(
            operation=operation,
            start_time=time.time(),
            metadata=metadata
        )
        
        self.current_operations[operation] = timing
        self.total_operations += 1
        
        log_debug(f"Started operation: {operation}")
        return timing
    
    def finish_operation(self, operation: str, success: bool = True, 
                        error_message: Optional[str] = None, **metadata):
        """Finish timing an operation"""
        if not self.enable_monitoring:
            return
        
        if operation not in self.current_operations:
            log_warning(f"Operation '{operation}' was not started")
            return
        
        timing = self.current_operations.pop(operation)
        timing.finish(success, error_message, **metadata)
        
        self.operation_timings[operation].append(timing)
        
        if not success:
            self.failed_operations += 1
        
        if timing.duration:
            self.total_processing_time += timing.duration
            
            # Check for slow operations
            duration_ms = timing.duration * 1000
            if duration_ms > self.thresholds['very_slow_operation_ms']:
                log_warning(f"Very slow operation '{operation}': {duration_ms:.1f}ms")
            elif duration_ms > self.thresholds['slow_operation_ms']:
                log_debug(f"Slow operation '{operation}': {duration_ms:.1f}ms")
        
        log_debug(f"Finished operation: {operation} ({timing.duration:.3f}s)")
    
    def record_metric(self, name: str, value: float, unit: str = "", **context):
        """Record a custom metric"""
        if not self.enable_monitoring:
            return
        
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(timezone.utc),
            context=context
        )
        
        self.metrics.append(metric)
        log_debug(f"Recorded metric: {name} = {value} {unit}")
    
    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation"""
        if operation not in self.operation_timings:
            return {}
        
        timings = self.operation_timings[operation]
        if not timings:
            return {}
        
        durations = [t.duration for t in timings if t.duration is not None]
        if not durations:
            return {}
        
        return {
            'count': len(timings),
            'success_count': sum(1 for t in timings if t.success),
            'failure_count': sum(1 for t in timings if not t.success),
            'total_duration': sum(durations),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'success_rate': sum(1 for t in timings if t.success) / len(timings) * 100
        }
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall performance statistics"""
        if not self.operation_timings:
            return {}
        
        all_timings = []
        for timings in self.operation_timings.values():
            all_timings.extend(timings)
        
        if not all_timings:
            return {}
        
        durations = [t.duration for t in all_timings if t.duration is not None]
        if not durations:
            return {}
        
        # Calculate throughput
        total_files = sum(len(timings) for timings in self.operation_timings.values())
        throughput = total_files / self.total_processing_time if self.total_processing_time > 0 else 0
        
        return {
            'total_operations': self.total_operations,
            'failed_operations': self.failed_operations,
            'success_rate': (self.total_operations - self.failed_operations) / self.total_operations * 100 if self.total_operations > 0 else 0,
            'total_processing_time': self.total_processing_time,
            'avg_operation_duration': sum(durations) / len(durations),
            'throughput_files_per_sec': throughput,
            'operation_breakdown': {op: self.get_operation_stats(op) for op in self.operation_timings.keys()}
        }
    
    def get_system_metrics_summary(self) -> Dict[str, Any]:
        """Get system metrics summary"""
        if not self.system_metrics:
            return {}
        
        cpu_values = [m.cpu_percent for m in self.system_metrics]
        memory_values = [m.memory_percent for m in self.system_metrics]
        
        return {
            'avg_cpu_percent': sum(cpu_values) / len(cpu_values),
            'max_cpu_percent': max(cpu_values),
            'avg_memory_percent': sum(memory_values) / len(memory_values),
            'max_memory_percent': max(memory_values),
            'current_memory_mb': self.system_metrics[-1].memory_used_mb if self.system_metrics else 0,
            'samples_count': len(self.system_metrics)
        }
    
    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report"""
        overall_stats = self.get_overall_stats()
        system_stats = self.get_system_metrics_summary()
        
        report = []
        report.append("=" * 60)
        report.append("PERFORMANCE REPORT")
        report.append("=" * 60)
        
        # Overall statistics
        if overall_stats:
            report.append(f"Total Operations: {overall_stats['total_operations']}")
            report.append(f"Success Rate: {overall_stats['success_rate']:.1f}%")
            report.append(f"Total Processing Time: {overall_stats['total_processing_time']:.2f}s")
            report.append(f"Average Operation Duration: {overall_stats['avg_operation_duration']:.3f}s")
            report.append(f"Throughput: {overall_stats['throughput_files_per_sec']:.1f} files/sec")
            report.append("")
        
        # System metrics
        if system_stats:
            report.append("SYSTEM METRICS:")
            report.append(f"  Average CPU: {system_stats['avg_cpu_percent']:.1f}%")
            report.append(f"  Peak CPU: {system_stats['max_cpu_percent']:.1f}%")
            report.append(f"  Average Memory: {system_stats['avg_memory_percent']:.1f}%")
            report.append(f"  Peak Memory: {system_stats['max_memory_percent']:.1f}%")
            report.append(f"  Current Memory: {system_stats['current_memory_mb']:.1f} MB")
            report.append("")
        
        # Operation breakdown
        if overall_stats and 'operation_breakdown' in overall_stats:
            report.append("OPERATION BREAKDOWN:")
            for operation, stats in overall_stats['operation_breakdown'].items():
                report.append(f"  {operation}:")
                report.append(f"    Count: {stats['count']}")
                report.append(f"    Success Rate: {stats['success_rate']:.1f}%")
                report.append(f"    Avg Duration: {stats['avg_duration']:.3f}s")
                report.append(f"    Min/Max: {stats['min_duration']:.3f}s / {stats['max_duration']:.3f}s")
                report.append("")
        
        # Performance recommendations
        recommendations = self._generate_recommendations(overall_stats, system_stats)
        if recommendations:
            report.append("PERFORMANCE RECOMMENDATIONS:")
            for rec in recommendations:
                report.append(f"  • {rec}")
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def _generate_recommendations(self, overall_stats: Dict, system_stats: Dict) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if not overall_stats:
            return recommendations
        
        # Throughput recommendations
        throughput = overall_stats.get('throughput_files_per_sec', 0)
        if throughput < self.thresholds['low_throughput_files_per_sec']:
            recommendations.append(f"Low throughput detected ({throughput:.1f} files/sec). Consider increasing worker count or optimizing I/O operations.")
        
        # Memory recommendations
        if system_stats:
            avg_memory = system_stats.get('avg_memory_percent', 0)
            if avg_memory > 80:
                recommendations.append(f"High memory usage ({avg_memory:.1f}%). Consider reducing batch sizes or implementing memory optimization.")
        
        # CPU recommendations
        if system_stats:
            avg_cpu = system_stats.get('avg_cpu_percent', 0)
            if avg_cpu > 90:
                recommendations.append(f"Very high CPU usage ({avg_cpu:.1f}%). Consider reducing worker count or optimizing CPU-intensive operations.")
            elif avg_cpu < 30:
                recommendations.append(f"Low CPU usage ({avg_cpu:.1f}%). Consider increasing worker count for better parallelization.")
        
        # Operation-specific recommendations
        if 'operation_breakdown' in overall_stats:
            for operation, stats in overall_stats['operation_breakdown'].items():
                if stats['avg_duration'] > 2.0:  # More than 2 seconds average
                    recommendations.append(f"Slow operation '{operation}' ({stats['avg_duration']:.2f}s avg). Consider optimizing this operation.")
        
        return recommendations
    
    def save_metrics_to_file(self, filepath: Path):
        """Save metrics to a JSON file"""
        if not self.enable_monitoring:
            return
        
        data = {
            'overall_stats': self.get_overall_stats(),
            'system_metrics': self.get_system_metrics_summary(),
            'operation_breakdown': {op: self.get_operation_stats(op) for op in self.operation_timings.keys()},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        log_info(f"Performance metrics saved to: {filepath}")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if self._monitoring_thread:
            self._stop_monitoring.set()
            self._monitoring_thread.join(timeout=5)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_monitoring()


# Context manager for timing operations
class TimedOperation:
    """Context manager for timing operations"""
    
    def __init__(self, monitor: PerformanceMonitor, operation: str, **metadata):
        self.monitor = monitor
        self.operation = operation
        self.metadata = metadata
        self.timing = None
    
    def __enter__(self):
        self.timing = self.monitor.start_operation(self.operation, **self.metadata)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timing:
            success = exc_type is None
            error_message = str(exc_val) if exc_val else None
            self.monitor.finish_operation(self.operation, success, error_message, **self.metadata)


# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def timed_operation(operation: str, **metadata):
    """Decorator for timing operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            if not monitor.enable_monitoring:
                return func(*args, **kwargs)
            
            timing = monitor.start_operation(operation, **metadata)
            try:
                result = func(*args, **kwargs)
                monitor.finish_operation(operation, success=True, **metadata)
                return result
            except Exception as e:
                monitor.finish_operation(operation, success=False, error_message=str(e), **metadata)
                raise
        return wrapper
    return decorator

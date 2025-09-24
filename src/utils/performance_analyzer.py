#!/usr/bin/env python3
"""
Performance Analysis Module

This module analyzes performance bottlenecks and provides specific recommendations
for optimizing the Apple Photos Export Tool.

Analysis includes:
- I/O bottleneck identification
- Memory usage patterns
- CPU utilization analysis
- Parallel processing efficiency
- File processing bottlenecks
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.logging.logger_config import log_debug, log_info, log_warning, log_error
from src.utils.performance_monitor import get_performance_monitor


@dataclass
class BottleneckAnalysis:
    """Analysis of a specific performance bottleneck"""
    category: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    impact: str
    recommendation: str
    metrics: Dict[str, Any]


@dataclass
class PerformanceProfile:
    """Complete performance profile of the application"""
    overall_score: float  # 0-100
    bottlenecks: List[BottleneckAnalysis]
    recommendations: List[str]
    optimization_potential: str  # 'low', 'medium', 'high'
    critical_issues: List[str]


class PerformanceAnalyzer:
    """Analyzes performance data and identifies bottlenecks"""
    
    def __init__(self):
        self.monitor = get_performance_monitor()
        self.analysis_history: List[PerformanceProfile] = []
    
    def analyze_performance(self) -> PerformanceProfile:
        """Perform comprehensive performance analysis"""
        log_info("Starting performance analysis...")
        
        # Get current performance data
        overall_stats = self.monitor.get_overall_stats()
        system_stats = self.monitor.get_system_metrics_summary()
        operation_stats = self._get_operation_breakdown()
        
        # Analyze different aspects
        bottlenecks = []
        bottlenecks.extend(self._analyze_io_bottlenecks(overall_stats, operation_stats))
        bottlenecks.extend(self._analyze_memory_bottlenecks(system_stats))
        bottlenecks.extend(self._analyze_cpu_bottlenecks(system_stats, operation_stats))
        bottlenecks.extend(self._analyze_parallelization_efficiency(overall_stats, operation_stats))
        bottlenecks.extend(self._analyze_file_processing_bottlenecks(operation_stats))
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(bottlenecks, overall_stats, system_stats)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(bottlenecks, overall_stats, system_stats)
        
        # Determine optimization potential
        optimization_potential = self._assess_optimization_potential(bottlenecks)
        
        # Identify critical issues
        critical_issues = [b.description for b in bottlenecks if b.severity == 'critical']
        
        profile = PerformanceProfile(
            overall_score=overall_score,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            optimization_potential=optimization_potential,
            critical_issues=critical_issues
        )
        
        self.analysis_history.append(profile)
        return profile
    
    def _get_operation_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed operation breakdown"""
        operation_stats = {}
        for operation in self.monitor.operation_timings.keys():
            stats = self.monitor.get_operation_stats(operation)
            if stats:
                operation_stats[operation] = stats
        return operation_stats
    
    def _analyze_io_bottlenecks(self, overall_stats: Dict, operation_stats: Dict) -> List[BottleneckAnalysis]:
        """Analyze I/O related bottlenecks"""
        bottlenecks = []
        
        # Check file processing throughput
        throughput = overall_stats.get('throughput_files_per_sec', 0)
        if throughput < 10:
            bottlenecks.append(BottleneckAnalysis(
                category="I/O",
                severity="critical" if throughput < 5 else "high",
                description=f"Low file processing throughput: {throughput:.1f} files/sec",
                impact="Significantly slower processing times",
                recommendation="Optimize file I/O operations, increase worker count, or implement batch processing",
                metrics={"throughput": throughput, "threshold": 10}
            ))
        
        # Check for slow file operations
        for operation, stats in operation_stats.items():
            if 'file' in operation.lower() or 'copy' in operation.lower():
                avg_duration = stats.get('avg_duration', 0)
                if avg_duration > 2.0:
                    bottlenecks.append(BottleneckAnalysis(
                        category="I/O",
                        severity="high" if avg_duration > 5.0 else "medium",
                        description=f"Slow file operation '{operation}': {avg_duration:.2f}s average",
                        impact="Reduced overall processing speed",
                        recommendation="Optimize file operations, use faster storage, or implement caching",
                        metrics={"operation": operation, "avg_duration": avg_duration}
                    ))
        
        return bottlenecks
    
    def _analyze_memory_bottlenecks(self, system_stats: Dict) -> List[BottleneckAnalysis]:
        """Analyze memory related bottlenecks"""
        bottlenecks = []
        
        if not system_stats:
            return bottlenecks
        
        # Check memory usage
        avg_memory = system_stats.get('avg_memory_percent', 0)
        max_memory = system_stats.get('max_memory_percent', 0)
        
        if max_memory > 90:
            bottlenecks.append(BottleneckAnalysis(
                category="Memory",
                severity="critical",
                description=f"Very high memory usage: {max_memory:.1f}% peak",
                impact="Risk of out-of-memory errors and system instability",
                recommendation="Implement memory optimization, reduce batch sizes, or increase available memory",
                metrics={"max_memory_percent": max_memory, "avg_memory_percent": avg_memory}
            ))
        elif avg_memory > 80:
            bottlenecks.append(BottleneckAnalysis(
                category="Memory",
                severity="high",
                description=f"High memory usage: {avg_memory:.1f}% average",
                impact="Potential memory pressure and reduced performance",
                recommendation="Optimize memory usage patterns or increase available memory",
                metrics={"avg_memory_percent": avg_memory, "max_memory_percent": max_memory}
            ))
        
        return bottlenecks
    
    def _analyze_cpu_bottlenecks(self, system_stats: Dict, operation_stats: Dict) -> List[BottleneckAnalysis]:
        """Analyze CPU related bottlenecks"""
        bottlenecks = []
        
        if not system_stats:
            return bottlenecks
        
        # Check CPU usage
        avg_cpu = system_stats.get('avg_cpu_percent', 0)
        max_cpu = system_stats.get('max_cpu_percent', 0)
        
        if max_cpu > 95:
            bottlenecks.append(BottleneckAnalysis(
                category="CPU",
                severity="critical",
                description=f"Very high CPU usage: {max_cpu:.1f}% peak",
                impact="System may become unresponsive",
                recommendation="Reduce worker count, optimize CPU-intensive operations, or upgrade hardware",
                metrics={"max_cpu_percent": max_cpu, "avg_cpu_percent": avg_cpu}
            ))
        elif avg_cpu > 90:
            bottlenecks.append(BottleneckAnalysis(
                category="CPU",
                severity="high",
                description=f"High CPU usage: {avg_cpu:.1f}% average",
                impact="Reduced system responsiveness and potential throttling",
                recommendation="Optimize CPU usage or reduce parallel processing",
                metrics={"avg_cpu_percent": avg_cpu, "max_cpu_percent": max_cpu}
            ))
        elif avg_cpu < 30:
            bottlenecks.append(BottleneckAnalysis(
                category="CPU",
                severity="low",
                description=f"Low CPU usage: {avg_cpu:.1f}% average",
                impact="Underutilized CPU resources",
                recommendation="Increase worker count or parallelization for better performance",
                metrics={"avg_cpu_percent": avg_cpu, "max_cpu_percent": max_cpu}
            ))
        
        return bottlenecks
    
    def _analyze_parallelization_efficiency(self, overall_stats: Dict, operation_stats: Dict) -> List[BottleneckAnalysis]:
        """Analyze parallel processing efficiency"""
        bottlenecks = []
        
        # Check if operations are running in parallel effectively
        total_operations = overall_stats.get('total_operations', 0)
        total_time = overall_stats.get('total_processing_time', 0)
        
        if total_operations > 0 and total_time > 0:
            # Calculate theoretical vs actual speedup
            # This is a simplified calculation
            avg_operation_time = total_time / total_operations
            
            # If average operation time is very high, parallelization might not be effective
            if avg_operation_time > 5.0:
                bottlenecks.append(BottleneckAnalysis(
                    category="Parallelization",
                    severity="medium",
                    description=f"High average operation time: {avg_operation_time:.2f}s",
                    impact="Parallelization may not be effective due to long-running operations",
                    recommendation="Break down long operations into smaller chunks or optimize individual operations",
                    metrics={"avg_operation_time": avg_operation_time, "total_operations": total_operations}
                ))
        
        return bottlenecks
    
    def _analyze_file_processing_bottlenecks(self, operation_stats: Dict) -> List[BottleneckAnalysis]:
        """Analyze file processing specific bottlenecks"""
        bottlenecks = []
        
        # Look for specific slow operations
        slow_operations = []
        for operation, stats in operation_stats.items():
            avg_duration = stats.get('avg_duration', 0)
            count = stats.get('count', 0)
            
            if avg_duration > 1.0 and count > 10:  # Only consider operations with significant usage
                slow_operations.append((operation, avg_duration, count))
        
        # Sort by duration
        slow_operations.sort(key=lambda x: x[1], reverse=True)
        
        for operation, duration, count in slow_operations[:3]:  # Top 3 slowest
            severity = "high" if duration > 3.0 else "medium" if duration > 1.5 else "low"
            
            bottlenecks.append(BottleneckAnalysis(
                category="File Processing",
                severity=severity,
                description=f"Slow operation '{operation}': {duration:.2f}s average ({count} calls)",
                impact="Reduced overall processing speed",
                recommendation=f"Optimize '{operation}' operation or consider caching",
                metrics={"operation": operation, "avg_duration": duration, "count": count}
            ))
        
        return bottlenecks
    
    def _calculate_overall_score(self, bottlenecks: List[BottleneckAnalysis], 
                               overall_stats: Dict, system_stats: Dict) -> float:
        """Calculate overall performance score (0-100)"""
        base_score = 100.0
        
        # Deduct points for bottlenecks
        for bottleneck in bottlenecks:
            if bottleneck.severity == "critical":
                base_score -= 25
            elif bottleneck.severity == "high":
                base_score -= 15
            elif bottleneck.severity == "medium":
                base_score -= 8
            elif bottleneck.severity == "low":
                base_score -= 3
        
        # Bonus points for good performance
        throughput = overall_stats.get('throughput_files_per_sec', 0)
        if throughput > 50:
            base_score += 10
        elif throughput > 20:
            base_score += 5
        
        success_rate = overall_stats.get('success_rate', 0)
        if success_rate > 95:
            base_score += 5
        
        return max(0, min(100, base_score))
    
    def _generate_recommendations(self, bottlenecks: List[BottleneckAnalysis], 
                                overall_stats: Dict, system_stats: Dict) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Categorize bottlenecks
        io_bottlenecks = [b for b in bottlenecks if b.category == "I/O"]
        memory_bottlenecks = [b for b in bottlenecks if b.category == "Memory"]
        cpu_bottlenecks = [b for b in bottlenecks if b.category == "CPU"]
        parallelization_bottlenecks = [b for b in bottlenecks if b.category == "Parallelization"]
        
        # I/O recommendations
        if io_bottlenecks:
            recommendations.append("I/O Optimization:")
            if any(b.severity in ["critical", "high"] for b in io_bottlenecks):
                recommendations.append("  • Implement file caching to reduce repeated I/O operations")
                recommendations.append("  • Use batch processing for file operations")
                recommendations.append("  • Consider using faster storage (SSD)")
            recommendations.append("  • Increase worker count for parallel I/O operations")
        
        # Memory recommendations
        if memory_bottlenecks:
            recommendations.append("Memory Optimization:")
            if any(b.severity in ["critical", "high"] for b in memory_bottlenecks):
                recommendations.append("  • Implement memory-efficient data structures")
                recommendations.append("  • Reduce batch sizes to lower memory usage")
                recommendations.append("  • Clear unused objects from memory")
            recommendations.append("  • Consider increasing available memory")
        
        # CPU recommendations
        if cpu_bottlenecks:
            recommendations.append("CPU Optimization:")
            if any(b.severity in ["critical", "high"] for b in cpu_bottlenecks):
                recommendations.append("  • Reduce worker count to avoid CPU overload")
                recommendations.append("  • Optimize CPU-intensive operations")
            elif any(b.severity == "low" for b in cpu_bottlenecks):
                recommendations.append("  • Increase worker count to better utilize CPU")
        
        # Parallelization recommendations
        if parallelization_bottlenecks:
            recommendations.append("Parallelization Optimization:")
            recommendations.append("  • Break down long-running operations into smaller chunks")
            recommendations.append("  • Optimize individual operations before parallelizing")
            recommendations.append("  • Consider using ProcessPoolExecutor for CPU-bound tasks")
        
        # General recommendations
        throughput = overall_stats.get('throughput_files_per_sec', 0)
        if throughput < 20:
            recommendations.append("General Optimization:")
            recommendations.append("  • Profile the application to identify specific bottlenecks")
            recommendations.append("  • Consider implementing lazy loading for large datasets")
            recommendations.append("  • Use more efficient algorithms and data structures")
        
        return recommendations
    
    def _assess_optimization_potential(self, bottlenecks: List[BottleneckAnalysis]) -> str:
        """Assess the potential for performance optimization"""
        critical_count = sum(1 for b in bottlenecks if b.severity == "critical")
        high_count = sum(1 for b in bottlenecks if b.severity == "high")
        medium_count = sum(1 for b in bottlenecks if b.severity == "medium")
        
        if critical_count > 0:
            return "high"
        elif high_count >= 2 or (high_count >= 1 and medium_count >= 2):
            return "high"
        elif high_count >= 1 or medium_count >= 3:
            return "medium"
        else:
            return "low"
    
    def generate_analysis_report(self, profile: PerformanceProfile) -> str:
        """Generate a comprehensive analysis report"""
        report = []
        report.append("=" * 80)
        report.append("PERFORMANCE ANALYSIS REPORT")
        report.append("=" * 80)
        
        # Overall score
        report.append(f"Overall Performance Score: {profile.overall_score:.1f}/100")
        report.append(f"Optimization Potential: {profile.optimization_potential.upper()}")
        report.append("")
        
        # Critical issues
        if profile.critical_issues:
            report.append("🚨 CRITICAL ISSUES:")
            for issue in profile.critical_issues:
                report.append(f"  • {issue}")
            report.append("")
        
        # Bottlenecks by category
        categories = {}
        for bottleneck in profile.bottlenecks:
            if bottleneck.category not in categories:
                categories[bottleneck.category] = []
            categories[bottleneck.category].append(bottleneck)
        
        for category, bottlenecks in categories.items():
            report.append(f"{category.upper()} BOTTLENECKS:")
            for bottleneck in bottlenecks:
                severity_icon = {
                    "critical": "🔴",
                    "high": "🟠", 
                    "medium": "🟡",
                    "low": "🟢"
                }.get(bottleneck.severity, "⚪")
                
                report.append(f"  {severity_icon} {bottleneck.description}")
                report.append(f"    Impact: {bottleneck.impact}")
                report.append(f"    Recommendation: {bottleneck.recommendation}")
                report.append("")
        
        # Recommendations
        if profile.recommendations:
            report.append("RECOMMENDATIONS:")
            for rec in profile.recommendations:
                report.append(f"  {rec}")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_analysis_report(self, profile: PerformanceProfile, filepath: Path):
        """Save analysis report to file"""
        report = self.generate_analysis_report(profile)
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        log_info(f"Performance analysis report saved to: {filepath}")


# Global analyzer instance
_performance_analyzer = None

def get_performance_analyzer() -> PerformanceAnalyzer:
    """Get the global performance analyzer instance"""
    global _performance_analyzer
    if _performance_analyzer is None:
        _performance_analyzer = PerformanceAnalyzer()
    return _performance_analyzer

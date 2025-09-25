#!/usr/bin/env python3
"""
Apple Photos Management Tool - Main Entry Point

Profesionální nástroj pro export a organizaci fotografií z Apple Photos
s pokročilými funkcemi optimalizace výkonu a modulární architekturou.

Author: AI Assistant
Version: 2.0.0
License: MIT
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List, Any

# Add src to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.export_photos import PhotoExporter
from src.logging.logger_config import setup_logging, log_info, log_error, log_warning
from src.utils.performance_monitor import get_performance_monitor


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Apple Photos Management Tool - Export and organize photos from Apple Photos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dry /path/to/photos                    # Dry-run simulation
  %(prog)s run /path/to/photos /path/to/output    # Actual export
  %(prog)s run /path/to/photos --duplicate-strategy preserve_duplicates
  %(prog)s run /path/to/photos --workers 16 --batch-size 200

For more information, see README.md or docs/requirements.md
        """
    )
    
    # Positional arguments
    parser.add_argument(
        'mode',
        choices=['dry', 'run'],
        help='Operation mode: dry (simulation) or run (actual export)'
    )
    
    parser.add_argument(
        'source_dir',
        type=Path,
        help='Source directory containing photos to export'
    )
    
    parser.add_argument(
        'target_dir',
        type=Path,
        nargs='?',
        help='Target directory for exported photos (optional, defaults to source_dir + "_export")'
    )
    
    # Optional arguments
    parser.add_argument(
        '--duplicate-strategy',
        choices=['keep_first', 'skip_duplicates', 'preserve_duplicates', 'cleanup_duplicates', '!delete!'],
        default='keep_first',
        help='Strategy for handling duplicate files (default: keep_first)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=8,
        help='Number of worker threads for parallel processing (default: 8)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for file processing (default: 100)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--cache-size',
        type=int,
        default=10000,
        help='Maximum cache size for file metadata (default: 10000)'
    )
    
    parser.add_argument(
        '--memory-optimization',
        action='store_true',
        help='Enable memory optimization for large datasets'
    )
    
    parser.add_argument(
        '--performance-monitoring',
        action='store_true',
        default=True,
        help='Enable performance monitoring and optimization (default: True)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Apple Photos Management Tool 2.0.0'
    )
    
    return parser


def validate_arguments(args: argparse.Namespace) -> bool:
    """Validate command line arguments."""
    try:
        # Validate source directory
        if not args.source_dir.exists():
            log_error(f"Source directory does not exist: {args.source_dir}")
            return False
        
        if not args.source_dir.is_dir():
            log_error(f"Source path is not a directory: {args.source_dir}")
            return False
        
        # Validate target directory
        if args.target_dir is None:
            args.target_dir = args.source_dir.parent / f"{args.source_dir.name}_export"
        
        # Validate numeric arguments
        if args.workers < 1:
            log_error("Number of workers must be at least 1")
            return False
        
        if args.batch_size < 1:
            log_error("Batch size must be at least 1")
            return False
        
        if args.cache_size < 1:
            log_error("Cache size must be at least 1")
            return False
        
        return True
        
    except Exception as e:
        log_error(f"Error validating arguments: {e}")
        return False


def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    Apple Photos Management Tool v2.0.0                      ║
║                                                                              ║
║  🚀 Professional photo export and organization tool                         ║
║  📸 Supports HEIC, JPG, MOV, XMP, AAE and more                             ║
║  ⚡ Advanced performance optimization and monitoring                        ║
║  🏗️  Modular architecture following SOLID principles                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_configuration(args: argparse.Namespace):
    """Print configuration summary."""
    log_info("Configuration:")
    log_info(f"📁 Source: {args.source_dir}")
    log_info(f"📁 Target: {args.target_dir}")
    log_info(f"⚙️  Mode: {'DRY-RUN' if args.mode == 'dry' else 'EXECUTE'}")
    log_info(f"🔄 Duplicate Strategy: {args.duplicate_strategy}")
    log_info(f"👥 Workers: {args.workers}")
    log_info(f"📦 Batch Size: {args.batch_size}")
    log_info(f"📊 Log Level: {args.log_level}")
    log_info(f"💾 Cache Size: {args.cache_size}")
    log_info(f"🧠 Memory Optimization: {'Enabled' if args.memory_optimization else 'Disabled'}")
    log_info(f"📈 Performance Monitoring: {'Enabled' if args.performance_monitoring else 'Disabled'}")


def main() -> int:
    """Main application entry point."""
    try:
        # Parse command line arguments
        parser = create_parser()
        args = parser.parse_args()
        
        # Print banner
        print_banner()
        
        # Validate arguments
        if not validate_arguments(args):
            return 1
        
        # Setup initial logging (will be reconfigured with timestamp later)
        setup_logging(
            log_level=args.log_level,
            is_dry_run=(args.mode == 'dry'),
            log_dir=Path(args.target_dir)
        )
        
        # Print configuration
        print_configuration(args)
        
        # Initialize performance monitor
        if args.performance_monitoring:
            monitor = get_performance_monitor()
            monitor.enable_monitoring = True
            log_info("📈 Performance monitoring enabled")
        
        # Create photo exporter
        exporter = PhotoExporter(
            source_dir=args.source_dir,
            target_dir=args.target_dir,
            duplicate_strategy=args.duplicate_strategy,
            max_workers=args.workers,
            is_dry_run=(args.mode == 'dry')
        )
        
        # Run export
        log_info("🚀 Starting photo export process...")
        success = exporter.run_export()
        
        if success:
            log_info("✅ Photo export process completed successfully!")
            return 0
        else:
            log_error("❌ Photo export process failed!")
            return 1
            
    except KeyboardInterrupt:
        log_warning("⚠️  Process interrupted by user")
        return 130
    except Exception as e:
        log_error(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

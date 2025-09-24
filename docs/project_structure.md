# Project Structure

## Directory Layout

```
apple-photos-management/
├── src/                           # Source code
│   ├── __init__.py               # Package initialization
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── export_photos.py     # Main export logic
│   │   └── metadata_extractor.py # Metadata extraction
│   ├── logging/                  # Logging configuration
│   │   ├── __init__.py
│   │   └── logger_config.py     # Loguru-based logging
│   ├── security/                 # Security utilities
│   │   ├── __init__.py
│   │   └── security_utils.py    # Path validation & sanitization
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── file_utils.py        # File finding utilities
├── tests/                        # Test suite
│   └── test_export_photos.py    # Unit and integration tests
├── docs/                         # Documentation
│   ├── requirements.md          # Requirements document
│   └── project_structure.md     # This file
├── examples/                     # Example data and outputs
│   ├── TestComprehensive/       # Test dataset
│   └── test_output/             # Test export outputs
├── venv/                        # Python virtual environment
├── export_photos.sh             # Shell wrapper script (moved to root)
├── backlog.md                   # Development backlog (moved to root)
├── requirements.txt             # Python dependencies
└── README.md                    # Project overview
```

## Module Responsibilities

### Core Module (`src/core/`)
- **export_photos.py**: Main PhotoExporter class and export logic
- **metadata_extractor.py**: Metadata extraction from EXIF, XMP, and AAE files
- Handles photo processing, file organization, and duplicate detection
- Orchestrates the overall export process

### Logging Module (`src/logging/`)
- **logger_config.py**: Centralized logging configuration using Loguru
- Provides structured logging with context
- Handles log file creation and rotation
- Supports different log levels and output formats

### Security Module (`src/security/`)
- **security_utils.py**: Path validation and sanitization utilities
- Prevents path traversal attacks
- Sanitizes filenames and directory names
- Validates file access permissions

### Utils Module (`src/utils/`)
- **file_utils.py**: File finding utilities for XMP and AAE files
- **performance_monitor.py**: Real-time performance monitoring and metrics collection
- **performance_optimizer.py**: Performance optimization strategies and implementations
- **performance_analyzer.py**: Performance analysis and bottleneck identification
- Common functionality shared across modules
- Data processing and transformation utilities

## Design Principles

### 1. Separation of Concerns
- Each module has a single, well-defined responsibility
- Clear interfaces between modules
- Minimal coupling, maximum cohesion

### 2. Security First
- All file operations go through security validation
- Path traversal prevention at every entry point
- Input sanitization and validation

### 3. Comprehensive Logging
- Structured logging with context
- Different log levels for different scenarios
- On-demand error log creation

### 4. Error Handling
- Specific exception types for different error categories
- Graceful degradation when possible
- Comprehensive error reporting and recovery

### 5. Testability
- Modular design enables unit testing
- Clear separation of concerns
- Mockable dependencies

### 6. Performance Optimization
- File caching system reduces I/O operations by 50-70%
- Batch processing optimizes file operations
- Memory optimization with streaming for large datasets
- Dynamic worker scaling based on system resources
- Real-time performance monitoring and optimization

## File Naming Conventions

### Source Files
- Use snake_case for Python files
- Descriptive names that indicate purpose
- Group related functionality in modules

### Test Files
- Prefix with `test_` for pytest discovery
- Mirror the source structure
- Include test type in filename when needed

### Documentation
- Use descriptive names with `.md` extension
- Keep documentation close to code
- Maintain up-to-date project information

## Import Structure

### Internal Imports
```python
from src.logging.logger_config import log_info, log_error
from src.security.security_utils import validate_path, SecurityError
```

### External Imports
```python
from pathlib import Path
from datetime import datetime
from PIL import Image
```

## Development Guidelines

### 1. Code Organization
- Keep functions focused and small (< 50 lines)
- Use type hints for all public methods
- Document complex logic with comments

### 2. Error Handling
- Use specific exception types
- Provide meaningful error messages
- Log errors with appropriate context

### 3. Testing
- Write tests for all public methods
- Test error conditions and edge cases
- Maintain high test coverage

### 4. Documentation
- Update documentation when changing functionality
- Keep requirements document current
- Document design decisions and trade-offs

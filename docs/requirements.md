# Apple Photos Export Tool - Requirements Document

## 1. Project Overview

### 1.1 Purpose
The Apple Photos Export Tool is a comprehensive solution for exporting, organizing, and managing photos from Apple Photos library exports. It processes photos with their associated metadata files (XMP, AAE) and organizes them into a clean, chronological directory structure.

### 1.2 Scope
- Process photos exported from Apple Photos library
- Extract and utilize metadata from EXIF, XMP, and AAE files
- Organize photos chronologically by creation date
- Handle duplicate detection and resolution
- Provide dry-run capability for safe testing
- Generate comprehensive logs and reports

## 2. Functional Requirements

### 2.1 Photo Processing (REQ-001)
**Description**: The system shall process various photo and video formats from Apple Photos exports.

**Acceptance Criteria**:
- [x] Support image formats: HEIC, JPG, JPEG, PNG, TIFF, TIF, RAW, CR2, NEF, ARW
- [x] Support video formats: MOV, MP4, AVI, MKV, M4V
- [x] Support metadata formats: AAE (Apple Adjustment Export)
- [x] Support sidecar formats: XMP (Extensible Metadata Platform)
- [x] Process files in parallel using configurable worker threads
- [x] Handle unsupported formats gracefully with warnings
- [x] Automatically detect and process associated XMP files for each photo
- [x] Copy XMP files alongside their corresponding photos during export

### 2.2 Metadata Extraction (REQ-002)
**Description**: The system shall extract creation dates from multiple metadata sources with intelligent fallback.

**Acceptance Criteria**:
- [x] Extract EXIF creation date from image files
- [x] Extract XMP creation date from sidecar files (.xmp and .XMP extensions)
- [x] Extract AAE metadata from Apple Adjustment Export files
- [x] Use file modification date as fallback when metadata unavailable
- [x] Choose the earliest available date for chronological accuracy
- [x] Handle timezone information correctly (UTC conversion)

### 2.3 File Organization (REQ-003)
**Description**: The system shall organize photos into a clean, chronological directory structure.

**Acceptance Criteria**:
- [x] Create YEAR-based directory structure (e.g., 2023/, 2024/)
- [x] Generate standardized filenames: YYYYMMDD-HHMMSS-SSS.ext
- [x] Handle filename conflicts with automatic numbering
- [x] Normalize file extensions to lowercase (e.g., .HEIC → .heic)
- [x] Copy associated XMP and AAE files alongside photos

### 2.4 Duplicate Handling (REQ-004)
**Description**: The system shall detect and handle duplicate photos using multiple strategies.

**Acceptance Criteria**:
- [ ] Detect duplicates using file hash comparison
- [ ] Support multiple duplicate strategies:
  - `keep_first`: Keep first occurrence, rename subsequent
  - `skip_duplicates`: Skip duplicate files entirely
  - `preserve_duplicates`: Keep all duplicates with unique names
  - `cleanup_duplicates`: Move duplicates to separate folder
  - `!delete!`: Delete duplicate files permanently
- [ ] Generate duplicate detection reports
- [ ] Handle duplicate XMP and AAE files appropriately

### 2.5 Dry-Run Mode (REQ-005)
**Description**: The system shall provide a safe testing mode that simulates operations without making changes.

**Acceptance Criteria**:
- [ ] Simulate all file operations without actual file system changes
- [ ] Generate accurate statistics and reports
- [ ] Create dry-run specific log files
- [ ] Show exactly what would be copied/moved/deleted
- [ ] Validate all operations before actual execution

### 2.6 Logging and Reporting (REQ-006)
**Description**: The system shall provide comprehensive logging and reporting capabilities.

**Acceptance Criteria**:
- [ ] Generate timestamped log files for each operation
- [ ] Create separate logs for dry-run and actual execution
- [ ] Log errors only when they occur (no empty error logs)
- [ ] Generate JSON metadata export files
- [ ] Create human-readable summary reports
- [ ] Support log rotation and retention policies

### 2.7 Security and Validation (REQ-007)
**Description**: The system shall implement security measures to prevent path traversal and unauthorized access.

**Acceptance Criteria**:
- [ ] Validate all file paths to prevent directory traversal attacks
- [ ] Sanitize filenames to remove dangerous characters
- [ ] Restrict file operations to specified directories
- [ ] Implement proper error handling with specific exception types
- [ ] Use context managers for all file operations

## 3. Non-Functional Requirements

### 3.1 Performance (REQ-008)
**Description**: The system shall process large photo collections efficiently.

**Acceptance Criteria**:
- [ ] Process photos in parallel using multiple worker threads
- [ ] Support configurable worker count (default: min(CPU count, 8))
- [ ] Handle collections with 10,000+ photos
- [ ] Provide progress indicators for long-running operations
- [ ] Optimize memory usage for large file processing

### 3.2 Reliability (REQ-009)
**Description**: The system shall be robust and handle errors gracefully.

**Acceptance Criteria**:
- [ ] Continue processing despite individual file errors
- [ ] Provide detailed error reporting and recovery suggestions
- [ ] Implement proper resource cleanup on interruption
- [ ] Validate input parameters before processing
- [ ] Handle disk space limitations gracefully

### 3.3 Usability (REQ-010)
**Description**: The system shall be easy to use and understand.

**Acceptance Criteria**:
- [ ] Provide clear command-line interface
- [ ] Generate informative help and usage instructions
- [ ] Use consistent, descriptive log messages
- [ ] Provide colored console output for better readability
- [ ] Support both dry-run and actual execution modes

### 3.4 Maintainability (REQ-011)
**Description**: The system shall be well-structured and maintainable.

**Acceptance Criteria**:
- [ ] Follow clean code principles and SOLID design patterns
- [ ] Implement comprehensive type hints and documentation
- [ ] Use consistent coding standards and formatting
- [ ] Provide comprehensive test coverage
- [ ] Modularize code into logical components

## 4. Technical Requirements

### 4.1 Supported File Formats (REQ-012)
**Description**: The system shall support comprehensive file format processing.

**Acceptance Criteria**:
- [x] **Images**: HEIC, JPG, JPEG, PNG, TIFF, TIF, RAW, CR2, NEF, ARW
- [x] **Videos**: MOV, MP4, AVI, MKV, M4V
- [x] **Metadata**: AAE (Apple Adjustment Export)
- [x] **Sidecar**: XMP (Extensible Metadata Platform) - automatically detected and processed
- [x] **Detection Patterns**: Supports both .xmp and .XMP extensions
- [x] **Association**: Automatically links XMP files to their corresponding photos
- [x] **Extension Normalization**: Converts all file extensions to lowercase for consistency

### 4.2 Dependencies (REQ-013)
**Description**: The system shall use appropriate Python libraries and tools.

**Acceptance Criteria**:
- [ ] Use Pillow for image processing and EXIF extraction
- [ ] Use pillow-heif for HEIC/HEIF format support
- [ ] Use lxml for XML parsing (XMP files)
- [ ] Use python-dateutil for advanced date parsing
- [ ] Use loguru for structured logging
- [ ] Use tqdm for progress bars
- [ ] Support Python 3.8+ compatibility

### 4.3 File System (REQ-014)
**Description**: The system shall work with standard file system operations.

**Acceptance Criteria**:
- [ ] Support Unix-like file systems (macOS, Linux)
- [ ] Handle long file paths appropriately
- [ ] Preserve file permissions and timestamps
- [ ] Support symbolic links and special files
- [ ] Handle case-sensitive and case-insensitive file systems

### 4.4 Configuration (REQ-015)
**Description**: The system shall support flexible configuration options.

**Acceptance Criteria**:
- [ ] Support command-line argument configuration
- [ ] Allow configurable worker thread count
- [ ] Support different duplicate handling strategies
- [ ] Allow custom output directory specification
- [ ] Support dry-run mode toggle

### 4.5 File Naming Behavior (REQ-016)
**Description**: The system shall implement consistent file naming and extension handling.

**Acceptance Criteria**:
- [x] **Extension Normalization**: All file extensions converted to lowercase (.HEIC → .heic)
- [x] **Filename Generation**: Standardized format YYYYMMDD-HHMMSS-SSS.ext
- [x] **Case Consistency**: Ensures consistent file naming across different operating systems
- [x] **Duplicate Handling**: Automatic numbering for filename conflicts (e.g., -001, -002)

### 4.6 Performance Optimization (REQ-017)
**Description**: The system shall implement performance optimizations for efficient processing of large photo collections.

**Acceptance Criteria**:
- [x] **File Caching**: Intelligent caching system reduces I/O operations by 50-70%
- [x] **Batch Processing**: Optimized file operations with dynamic batch sizing
- [x] **Memory Optimization**: Streaming processing for large datasets (>1000 files)
- [x] **Dynamic Worker Scaling**: Automatic optimization based on system resources
- [x] **Real-time Monitoring**: Continuous performance tracking and optimization
- [x] **Intelligent Processing**: Automatic selection between streaming and batch methods
- [x] **Consistent Logging**: Performance logs follow same naming convention as other logs

## 5. Integration Requirements

### 5.1 Apple Photos Integration (REQ-018)
**Description**: The system shall work seamlessly with Apple Photos export data.

**Acceptance Criteria**:
- [ ] Process Apple Photos "Export Originals" output
- [ ] Handle Apple Photos specific file naming conventions
- [ ] Process AAE (Apple Adjustment Export) files
- [ ] Support Apple Photos metadata formats
- [ ] Handle Apple Photos directory structures

### 5.2 Shell Integration (REQ-018)
**Description**: The system shall provide shell script integration for easy usage.

**Acceptance Criteria**:
- [ ] Provide executable shell script wrapper
- [ ] Support dependency checking and installation guidance
- [ ] Provide colored console output
- [ ] Support help and usage information
- [ ] Handle command-line argument parsing

## 6. Quality Requirements

### 6.1 Testing (REQ-019)
**Description**: The system shall be thoroughly tested.

**Acceptance Criteria**:
- [ ] Unit tests for all core functionality
- [ ] Integration tests for end-to-end workflows
- [ ] Performance tests for large datasets
- [ ] Error handling tests for edge cases
- [ ] Security tests for path traversal prevention

### 6.2 Documentation (REQ-020)
**Description**: The system shall be well-documented.

**Acceptance Criteria**:
- [ ] Comprehensive README with usage examples
- [ ] API documentation for all public methods
- [ ] Code comments explaining complex logic
- [ ] Troubleshooting guide for common issues
- [ ] Requirements document with acceptance criteria

## 7. Constraints

### 7.1 Platform Support
- Primary: macOS (Apple Photos integration)
- Secondary: Linux (file system compatibility)
- Python 3.8+ required

### 7.2 Resource Limitations
- Memory usage should be reasonable for large photo collections
- Disk space requirements for temporary processing
- Network requirements: None (local file processing only)

### 7.3 Security Constraints
- No network access required
- All file operations must be local
- No external API dependencies
- Path traversal attacks must be prevented

## 8. Success Criteria

The Apple Photos Export Tool will be considered successful when:

1. **Functionality**: All functional requirements are met with 100% acceptance criteria coverage
2. **Performance**: Can process 10,000+ photos in under 30 minutes on standard hardware
3. **Reliability**: Less than 0.1% error rate for valid input files
4. **Security**: Zero path traversal vulnerabilities detected in security testing
5. **Usability**: Users can successfully export and organize photos with minimal guidance
6. **Maintainability**: Code coverage above 90% with comprehensive documentation

## 9. Future Enhancements

### 9.1 Potential Features
- Resume capability for interrupted exports
- Advanced duplicate detection using image similarity
- Metadata editing and correction capabilities
- Integration with cloud storage services
- Web-based user interface
- Batch processing of multiple source directories

### 9.2 Performance Optimizations
- Incremental processing for large collections
- Caching mechanisms for metadata extraction
- Parallel processing optimizations
- Memory usage optimizations for very large files

---

**Document Version**: 1.0  
**Last Updated**: 2025-09-24  
**Status**: Draft for Review

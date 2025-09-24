# Backlog

## 🚨 Critical Issues (Fix Immediately)

### Path Traversal Security Vulnerability
**Priority**: CRITICAL  
**Status**: ✅ FIXED  
**Description**: ~~No validation of file paths for security vulnerabilities - potential for path traversal attacks.~~

**✅ FIXED**: Implemented comprehensive path validation and sanitization.

**Files modified**:
- `src/security/security_utils.py` - New security utilities module
- `src/core/export_photos.py` - Updated to use security validation

**Impact**: All file operations now validated for security vulnerabilities.

---

### Exception Handling Anti-Patterns
**Priority**: CRITICAL  
**Status**: ✅ FIXED  
**Description**: ~~Multiple `except Exception:` blocks that silently swallow errors.~~

**✅ FIXED**: Replaced with specific exception types and proper error handling.

**Files modified**:
- `src/core/export_photos.py` - Added custom exception classes and specific error handling

**Impact**: Better error reporting and debugging capabilities.

---

### Resource Leak Potential
**Priority**: HIGH  
**Status**: ✅ FIXED  
**Description**: ~~File operations without proper context managers could lead to resource leaks.~~

**✅ FIXED**: All file operations already use proper context managers.

**Verification**: All `open()` calls use `with` statements.

**Impact**: No resource leaks in file operations.

---

## 🔥 High Priority (Fix Soon)

### Single Responsibility Principle Violations
**Priority**: HIGH  
**Status**: 🔄 IN PROGRESS  
**Description**: `PhotoExporter` class is doing too much (2000+ lines) - violates Single Responsibility Principle.

**Progress**:
- ✅ Created `src/utils/file_utils.py` - File finding utilities
- ✅ Created `src/core/metadata_extractor.py` - Metadata extraction
- 🔄 Need to extract duplicate handling logic
- 🔄 Need to extract file organization logic

**Solution**: Split into focused classes:
- `PhotoProcessor` - individual photo processing
- `DuplicateHandler` - duplicate detection and resolution
- `FileOrganizer` - directory structure and file organization
- `MetadataExtractor` - EXIF/XMP metadata extraction ✅
- `PhotoExporter` - orchestration only

---

### Code Duplication - File Finding Logic
**Priority**: HIGH  
**Status**: ✅ FIXED  
**Description**: ~~XMP and AAE file finding logic is repeated 4+ times throughout the codebase.~~

**✅ FIXED**: Extracted into utility methods in `src/utils/file_utils.py`.

**Files created**:
- `src/utils/file_utils.py` - Centralized file finding utilities

**Impact**: Single source of truth for file finding logic.

---

### Error Handling Inconsistency
**Priority**: HIGH  
**Status**: 🔄 IN PROGRESS  
**Description**: Inconsistent error handling patterns throughout codebase.

**Progress**:
- ✅ Added custom exception classes
- ✅ Improved exception handling in metadata extraction
- 🔄 Need to standardize return patterns across all methods

**Solution**: Standardize on exception-based error handling with proper error types and recovery strategies.

---

## ⚠️ Medium Priority (Fix When Possible)

### Configuration Management
**Priority**: MEDIUM  
**Status**: Open  
**Description**: Hardcoded values scattered throughout codebase make maintenance difficult.

**Examples**:
- File formats defined in multiple places
- Date formats hardcoded
- Buffer sizes and limits scattered
- Worker counts hardcoded

**Solution**: Create centralized `Config` class with all constants and configuration options.

---

### Method Length Violations
**Priority**: MEDIUM  
**Status**: Open  
**Description**: Several methods exceed recommended length (50+ lines).

**Problematic methods**:
- `run_export()` - 160+ lines
- `_process_photo_file()` - 100+ lines
- `_handle_duplicates()` - 80+ lines

**Solution**: Refactor long methods into smaller, focused methods.

---

### Type Hints & Documentation
**Priority**: MEDIUM  
**Status**: Open  
**Description**: Missing type hints and inconsistent documentation standards.

**Issues**:
- Many methods lack type hints
- Inconsistent docstring formats
- Missing parameter and return type documentation

**Solution**: Add comprehensive type annotations and standardize docstring format (Google style).

---

### Testing Coverage Gaps
**Priority**: MEDIUM  
**Status**: Open  
**Description**: Good test structure but missing critical edge cases and scenarios.

**Missing coverage**:
- Error scenarios and edge cases
- Performance tests for large datasets
- Integration tests for error recovery
- Memory usage tests
- Concurrent processing tests

**Solution**: Expand test suite with comprehensive edge case coverage and performance benchmarks.

---

## 📊 Low Priority (Nice to Have)

### Magic Numbers & Constants
**Priority**: LOW  
**Status**: Open  
**Description**: Hardcoded values throughout codebase reduce maintainability.

**Examples**:
- `1024.0` for byte conversion
- `1.1` for disk space buffer
- `8` for max workers
- Various timeout and retry values

**Solution**: Extract all magic numbers to named constants in configuration.

---

### String Formatting Inconsistency
**Priority**: LOW  
**Status**: Open  
**Description**: Mix of f-strings, `.format()`, and `%` formatting throughout codebase.

**Solution**: Standardize on f-strings for all string formatting.

---

### Metrics & Telemetry
**Priority**: LOW  
**Status**: Open  
**Description**: Lack of performance metrics and monitoring capabilities.

**Missing metrics**:
- Processing time per file type
- Memory usage tracking
- I/O performance metrics
- Error rates and patterns

**Solution**: Implement comprehensive metrics collection and monitoring dashboard.

---

### Progress Reporting & Resume
**Priority**: LOW  
**Status**: Open  
**Description**: Limited progress reporting and no resume capability for interrupted exports.

**Current limitations**:
- Basic progress bars only
- No ETA calculations
- No resume capability
- Limited progress granularity

**Solution**: Implement advanced progress reporting with ETA, resume capability, and detailed progress tracking.

---

## ✅ Completed Issues

### Log File Generation Logic Issue
**Priority**: High  
**Status**: ✅ FIXED  
**Description**: Dry-run mode incorrectly generated all three log files.

**✅ FIXED**: Now correctly generates only the appropriate log files for each mode.

### Inconsistent Logging Framework
**Priority**: High  
**Status**: ✅ FIXED  
**Description**: Mix of `colorlog` (old) and `loguru` (new) frameworks.

**✅ FIXED**: Standardized on `loguru` and removed all `colorlog` dependencies.

### Empty Error Log Files
**Priority**: Medium  
**Status**: ✅ FIXED  
**Description**: `*_errors.log` files were created even when there were no errors.

**✅ FIXED**: Error log files are now only created when actual errors occur.

### Project Structure Reorganization
**Priority**: Medium  
**Status**: ✅ FIXED  
**Description**: Reorganized project into clean, modular structure.

**✅ FIXED**: 
- Created `src/` directory with modular organization
- Moved core functionality to `src/core/`
- Moved logging to `src/logging/`
- Moved security to `src/security/`
- Moved utilities to `src/utils/`
- Moved tests to `tests/`
- Moved examples to `examples/`
- Moved documentation to `docs/`
- Moved single script back to root directory

---

## 📋 Next Steps

### Immediate (This Week)
1. Complete SRP refactoring - extract remaining classes
2. Standardize error handling patterns
3. Update main PhotoExporter to use new utility classes

### Short Term (Next 2 Weeks)
1. Implement configuration management
2. Add comprehensive type hints
3. Expand test coverage

### Long Term (Next Month)
1. Performance optimizations
2. Advanced features (resume, metrics)
3. Documentation improvements
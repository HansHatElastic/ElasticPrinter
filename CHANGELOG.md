# Changelog

All notable changes to ElasticPrinter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-06

### Added
- Initial release of ElasticPrinter
- Virtual printer integration with macOS CUPS
- Elasticsearch indexing with attachment pipeline
- Support for Elasticsearch Serverless clusters
- Multiple authentication methods (encoded API key, API key tuple, basic auth)
- Automatic content extraction from print jobs
- Comprehensive metadata capture (user, timestamp, title, hostname)
- YAML-based configuration system
- Logging to `/var/log/elasticprinter/app.log`
- Installation and uninstallation scripts
- PPD file for CUPS integration
- Python package structure with modular components:
  - `converter`: Content processing
  - `elastic`: Elasticsearch client
  - `utils`: Configuration and logging
- Automatic index and pipeline creation
- Support for DEBUG logging level
- Temporary file management

### Documentation
- Comprehensive README.md
- Detailed INSTALLATION.md guide
- CONTRIBUTING.md guidelines
- Configuration examples
- Architecture documentation
- Troubleshooting guide

### Technical Details
- Python 3.9+ support
- Elasticsearch 8.0+ compatibility
- CUPS backend integration
- Serverless-compatible client (uses `info()` instead of `ping()`)
- Proper error handling and logging
- Permission management for CUPS _lp user
- System-wide installation support

### Known Issues
- CUPS may occasionally fail to execute backend for queued jobs (manual backend execution works correctly)
- PDF conversion requires cupsfilter or PostScript handling capabilities

[1.0.0]: https://github.com/yourusername/elasticprinter/releases/tag/v1.0.0

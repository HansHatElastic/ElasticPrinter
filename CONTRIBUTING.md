# Contributing to ElasticPrinter

Thank you for your interest in contributing to ElasticPrinter! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

1. **Clear title** describing the problem
2. **Steps to reproduce** the issue
3. **Expected behavior** vs **actual behavior**
4. **Environment details**: macOS version, Python version, Elasticsearch version
5. **Logs** from `/var/log/elasticprinter/app.log` and `/var/log/cups/error_log`
6. **Error messages** (if any)

### Suggesting Features

For feature requests, please create an issue with:

1. **Use case**: What problem does this solve?
2. **Proposed solution**: How should it work?
3. **Alternatives considered**: What other approaches did you think about?

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**: Follow conventional commits format
6. **Push to your fork**
7. **Create a Pull Request**

## Development Setup

### Local Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/elasticprinter.git
cd elasticprinter

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Testing Changes

Before submitting a PR, test your changes:

```bash
# Install locally
sudo ./scripts/install_printer.sh

# Test backend
echo "Test" | sudo -u _lp /usr/libexec/cups/backend/elasticprinter 999 testuser "Test" 1 ""

# Check logs
tail -f /var/log/elasticprinter/app.log

# Uninstall after testing
sudo ./scripts/uninstall_printer.sh
```

## Code Style

### Python

- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Write **docstrings** for functions and classes
- Keep functions **focused and small**
- Use **meaningful variable names**

Example:

```python
def process_print_job(
    input_file: str,
    job_id: str,
    user: str,
    title: str = "Untitled",
    copies: int = 1
) -> bool:
    """Process a print job and index it in Elasticsearch.
    
    Args:
        input_file: Path to the print job file
        job_id: Unique job identifier
        user: Username who submitted the job
        title: Document title
        copies: Number of copies
        
    Returns:
        True if successful, False otherwise
    """
    # Implementation
```

### Commit Messages

Use conventional commits:

```
type(scope): description

Examples:
feat(backend): add support for PNG images
fix(elastic): handle serverless authentication
docs(readme): update installation instructions
refactor(converter): simplify PDF generation
test(elastic): add unit tests for client
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Project Structure

```
elasticprinter/
├── src/
│   ├── converter/         # Document processing
│   ├── elastic/           # Elasticsearch integration
│   ├── utils/             # Utilities (config, logging)
│   └── main.py            # Main orchestrator
├── printer/
│   ├── backend/           # CUPS backend script
│   └── elasticprinter.ppd # Printer definition
├── scripts/               # Installation/uninstall scripts
├── config/                # Configuration templates
├── docs/                  # Additional documentation
└── tests/                 # Unit tests
```

## Adding New Features

### Adding a New Converter

1. Create new file in `src/converter/`
2. Implement the converter class
3. Add unit tests
4. Update documentation

### Adding Elasticsearch Features

1. Modify `src/elastic/client.py`
2. Ensure backward compatibility
3. Add tests for new functionality
4. Update config.yaml.example if needed

### Modifying the Backend

1. Edit `printer/backend/elasticprinter`
2. Test thoroughly with CUPS
3. Ensure proper error handling
4. Update documentation

## Testing Guidelines

### Manual Testing Checklist

- [ ] Installation works from scratch
- [ ] Configuration file is properly read
- [ ] Elasticsearch connection succeeds
- [ ] Backend processes print jobs
- [ ] Content is extracted correctly
- [ ] Documents are indexed in Elasticsearch
- [ ] Logs are written properly
- [ ] Uninstallation removes all files

### Testing with Different Configurations

Test with:
- Different Elasticsearch versions (8.x, Serverless)
- Different authentication methods (API key, basic auth)
- Different document types (text, PDF, PostScript)
- Error conditions (network failures, auth errors, disk full)

## Pull Request Process

1. **Update README.md** if adding features
2. **Add tests** for new functionality
3. **Update CHANGELOG.md** with your changes
4. **Ensure all tests pass**
5. **Update documentation** as needed
6. **Request review** from maintainers

### PR Description Template

```markdown
## Description
[Describe what this PR does]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing Done
- [ ] Tested installation
- [ ] Tested core functionality
- [ ] Tested with different configurations
- [ ] Checked logs for errors

## Checklist
- [ ] Code follows style guidelines
- [ ] Added/updated tests
- [ ] Updated documentation
- [ ] No breaking changes (or documented if unavoidable)
```

## Release Process

Releases are handled by maintainers:

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag -a v1.0.0 -m "Release 1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub release with notes

## Getting Help

- **Questions**: Open a discussion on GitHub
- **Bugs**: Create an issue
- **Chat**: Join our community (if applicable)

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to ElasticPrinter!

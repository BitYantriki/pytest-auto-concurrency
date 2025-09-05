# Contributing to pytest-auto-concurrency

Thank you for your interest in contributing to pytest-auto-concurrency!

## Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/BitYantriki/pytest-auto-concurrency.git
cd pytest-auto-concurrency
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### 3. Install in Development Mode
```bash
# Install the package in editable mode with dependencies
pip install -e .

# Verify installation
pip list | grep pytest
```

### 4. Verify Plugin Registration
```bash
# Check if plugin options are available
pytest --help | grep -A 10 "auto-concurrency"
```

## Local Testing

### Basic Functionality Tests
```bash
# Test basic functionality
pytest tests/ --concurrency 2

# Test with debug output to see strategy selection
pytest tests/ --concurrency auto --auto-concurrency-debug

# Test different strategies
pytest tests/ --concurrency 4 --multithreading
pytest tests/ --concurrency 4 --multiprocessing --task-grouping
```

### Expected Output Examples

**Threading Strategy (≤2 cores or --multithreading):**
```
[AUTO-CONCURRENCY] Using 4 workers with threading strategy
```

**Multiprocessing Strategy (>2 cores or --multiprocessing):**
```
[AUTO-CONCURRENCY] Using 4 workers with multiprocessing strategy
[AUTO-CONCURRENCY] Task grouping enabled (--dist=loadfile)
```

### Testing with Real Projects
```bash
# Test with your own project
cd /path/to/your/project
pytest tests/ --concurrency auto --task-grouping
```

## Package Building and Publishing

### 1. Install Build Tools
```bash
pip install build twine
```

### 2. Build the Package
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build source distribution and wheel
python -m build
```

This creates:
- `dist/pytest-auto-concurrency-1.0.0.tar.gz` (source distribution)
- `dist/pytest_auto_concurrency-1.0.0-py3-none-any.whl` (wheel)

### 3. Test the Built Package
```bash
# Install from built wheel (in a new environment)
pip install dist/pytest_auto_concurrency-1.0.0-py3-none-any.whl

# Test functionality
pytest --help | grep concurrency
```

### 4. Upload to PyPI

#### Test PyPI (recommended first)
```bash
# Upload to test PyPI
twine upload --repository testpypi dist/*

# Install from test PyPI
pip install --index-url https://test.pypi.org/simple/ pytest-auto-concurrency
```

#### Production PyPI
```bash
# Upload to production PyPI
twine upload dist/*
```

## Development Workflow

### 1. Make Changes
- Edit code in `pytest_auto_concurrency/plugin.py`
- Update tests in `tests/`
- Update documentation in `README.md`

### 2. Test Changes
```bash
# Since installed with -e, changes are immediately available
pytest tests/ --concurrency 4 --auto-concurrency-debug
```

### 3. Run Full Test Suite
```bash
# Run all tests
pytest tests/

# Run tests with the plugin itself
pytest tests/ --concurrency 2
```

## PyPI Account Setup

### 1. Create PyPI Account
- Go to https://pypi.org/account/register/
- Create account and verify email

### 2. Create API Token
- Go to https://pypi.org/manage/account/token/
- Create token for this project
- Save token securely

### 3. Configure twine
```bash
# Option 1: Use token directly
twine upload -u __token__ -p pypi-YOUR_TOKEN_HERE dist/*

# Option 2: Create ~/.pypirc
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
EOF
```

## Project Structure

```
pytest-auto-concurrency/
├── pyproject.toml           # Package configuration
├── README.md               # User documentation  
├── CONTRIBUTING.md         # This file
├── LICENSE                 # MIT license
├── pytest_auto_concurrency/
│   ├── __init__.py        # Package initialization
│   └── plugin.py          # Main plugin code
├── tests/
│   ├── __init__.py        # Test package
│   ├── test_plugin.py     # Unit tests
│   └── test_basic.py      # Integration tests
└── examples/
    └── test_database.py   # Usage examples
```

## Version Management

Update version in `pyproject.toml`:
```toml
[project]
version = "1.0.1"  # Increment for releases
```

Use semantic versioning:
- `1.0.0` → `1.0.1` (bug fixes)
- `1.0.1` → `1.1.0` (new features)  
- `1.1.0` → `2.0.0` (breaking changes)

## Troubleshooting

### Plugin Not Found
```bash
# Check if properly installed
pip show pytest-auto-concurrency

# Reinstall if needed
pip uninstall pytest-auto-concurrency
pip install -e .
```

### Import Errors
```bash
# Check Python path
python -c "import pytest_auto_concurrency; print(pytest_auto_concurrency.__file__)"
```

### Hook Not Working
```bash
# Test with debug output
pytest tests/ --concurrency 2 --auto-concurrency-debug -v
```

## Getting Help

- Create issues at: https://github.com/BitYantriki/pytest-auto-concurrency/issues
- Check pytest plugin docs: https://docs.pytest.org/en/stable/how-to/writing_plugins.html
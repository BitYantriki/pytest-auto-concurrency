# pytest-auto-concurrency

[![PyPI version](https://badge.fury.io/py/pytest-auto-concurrency.svg)](https://badge.fury.io/py/pytest-auto-concurrency)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-auto-concurrency.svg)](https://pypi.org/project/pytest-auto-concurrency)
[![License](https://img.shields.io/pypi/l/pytest-auto-concurrency.svg)](https://github.com/BitYantriki/pytest-auto-concurrency/blob/main/LICENSE)

Intelligent pytest plugin that automatically selects the optimal concurrency strategy for your tests.

## Why pytest-auto-concurrency?

Different systems have different optimal concurrency strategies:

- **Single/Dual-core systems**: Threading works better (I/O-bound tests benefit from concurrency)
- **Multi-core systems**: Multiprocessing works better (true parallelism)

Instead of manually choosing between `pytest-xdist` and `pytest-parallel`, this plugin automatically selects the best strategy based on your system's capabilities.

## Installation

```bash
pip install pytest-auto-concurrency
```

## Usage

### Basic Usage

```bash
# Auto-detect optimal strategy and use all CPU cores
pytest --concurrency auto

# Use specific number of workers
pytest --concurrency 4

# Enable task grouping (preserves module-scoped fixtures)
pytest --concurrency 4 --task-grouping
```

### Manual Strategy Override

```bash
# Force threading (good for I/O-bound tests)
pytest --concurrency 4 --multithreading

# Force multiprocessing (good for CPU-bound tests) 
pytest --concurrency 4 --multiprocessing
```

## How It Works

1. **System Detection**: Analyzes CPU count to determine optimal strategy
2. **Automatic Selection**:
   - ≤2 cores → Threading (via custom implementation)
   - >2 cores → Multiprocessing (via pytest-xdist)
3. **Parameter Translation**: Converts `--concurrency` to appropriate backend parameters
4. **File Grouping**: Optional `--file-grouping` preserves module-scoped fixtures

## Strategies

### Threading Strategy
- **When**: ≤2 cores or `--multithreading` flag
- **Best for**: I/O-bound tests, database tests, API tests
- **Benefits**: Lower memory usage, shared fixtures work naturally

### Multiprocessing Strategy  
- **When**: >2 cores or `--multiprocess` flag
- **Best for**: CPU-bound tests, pure computation tests
- **Benefits**: True parallelism, complete test isolation

## Comparison with Other Tools

| Tool | Strategy | File Grouping | Auto-Detection |
|------|----------|---------------|----------------|
| pytest-xdist | Multiprocessing only | ✅ | ❌ |
| pytest-parallel | Threading only | ❌ | ❌ |
| **pytest-auto-concurrency** | **Both, auto-selected** | **✅** | **✅** |

## Examples

### Database Tests (Threading Recommended)
```bash
# Threading works better for I/O-bound database tests
pytest tests/test_database.py --concurrency 4 --multithreading --file-grouping
```

### CPU-Heavy Tests (Multiprocessing Recommended)  
```bash
# Multiprocessing works better for CPU-bound tests
pytest tests/test_calculations.py --concurrency auto --multiprocess
```

### Mixed Test Suite (Auto-Detection)
```bash
# Let the plugin choose the optimal strategy
pytest --concurrency auto --file-grouping
```

## Configuration

The plugin respects standard pytest configuration in `pytest.ini` or `pyproject.toml`:

```ini
[tool:pytest]
addopts = --concurrency auto --file-grouping
```

## Debug Mode

Enable debug output to see strategy selection:

```bash
pytest --concurrency 4 --auto-concurrency-debug
```

Output:
```
[AUTO-CONCURRENCY] 🚀 Processing command line: ['--concurrency', '4', 'tests/']
[AUTO-CONCURRENCY] 🧵 Threading strategy activated (4 threads)
[AUTO-CONCURRENCY] 📁 File-grouped threading distribution enabled
```

## Requirements

- Python 3.8+
- pytest ≥6.0.0
- pytest-xdist ≥2.0.0 (automatically installed)

## License

MIT License. See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
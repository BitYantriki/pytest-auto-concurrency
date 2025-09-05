"""
pytest-auto-concurrency: Intelligent test parallelization plugin.

Automatically selects between threading and multiprocessing strategies based on:
- System CPU count
- User preferences (--multithreading, --multiprocess)
- Test distribution requirements (--dist=loadfile)
"""

__version__ = "1.0.0"
__author__ = "Bit Yantriki Team"
__email__ = "dev@bityantriki.com"

from .plugin import pytest_cmdline_parse, pytest_addoption, pytest_configure

__all__ = [
    "pytest_cmdline_parse",
    "pytest_addoption", 
    "pytest_configure",
    "__version__",
]
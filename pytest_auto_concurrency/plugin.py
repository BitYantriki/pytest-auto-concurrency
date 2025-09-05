"""
Simple pytest plugin for intelligent concurrency strategy selection.

This plugin wraps pytest-xdist and provides a simple --concurrency parameter
that automatically selects the optimal strategy based on system capabilities.
"""

import multiprocessing
from collections import defaultdict
from typing import List

import pytest
from _pytest.nodes import Item


def pytest_addoption(parser):
    """Add command line options."""
    group = parser.getgroup('auto-concurrency', 'Auto-concurrency options')
    
    group.addoption(
        '--concurrency',
        action='store',
        metavar='N',
        help='Run tests with N workers (use "auto" for CPU count)'
    )
    
    group.addoption(
        '--task-grouping',
        action='store',
        default=None,
        choices=['file', 'package'],
        help='Group tests by file or package (equivalent to xdist\'s --dist=loadfile or --dist=loadgroup). Default: file'
    )
    
    group.addoption(
        '--multithreading',
        action='store_true',
        help='Force threading strategy (uses pytest-parallel)'
    )
    
    group.addoption(
        '--multiprocessing',
        action='store_true',
        help='Force multiprocessing strategy (uses pytest-xdist)'
    )


@pytest.hookimpl(wrapper=True)
def pytest_cmdline_parse(pluginmanager, args: List[str]):
    """
    Process args before other plugins see them.
    
    This wrapper ensures we execute before pytest-xdist processes arguments.
    """
    
    # Extract our parameters
    concurrency = None
    task_grouping = None
    force_multiprocessing = '--multiprocessing' in args
    force_multithreading = '--multithreading' in args
    
    # Find --concurrency and --task-grouping values
    for i, arg in enumerate(args):
        if arg == '--concurrency' and i + 1 < len(args):
            concurrency = args[i + 1]
        elif arg.startswith('--concurrency='):
            concurrency = arg.split('=', 1)[1]
        elif arg == '--task-grouping' and i + 1 < len(args):
            task_grouping = args[i + 1]
        elif arg.startswith('--task-grouping='):
            task_grouping = arg.split('=', 1)[1]
        elif arg == '--task-grouping':
            task_grouping = 'file'  # Default value when no parameter given
    
    # Remove our flags from args
    cleaned_args = []
    i = 0
    while i < len(args):
        arg = args[i]
        
        # Skip our flags
        if arg == '--concurrency':
            i += 2  # Skip flag and value
            continue
        elif arg.startswith('--concurrency='):
            i += 1  # Skip combined flag
            continue
        elif arg == '--task-grouping':
            # Check if next arg is a value or another flag
            if i + 1 < len(args) and not args[i + 1].startswith('-'):
                i += 2  # Skip flag and value
            else:
                i += 1  # Skip just the flag (bare --task-grouping)
            continue
        elif arg.startswith('--task-grouping='):
            i += 1  # Skip combined flag
            continue
        elif arg in ['--multithreading', '--multiprocessing']:
            i += 1  # Skip our flags
            continue
        
        cleaned_args.append(arg)
        i += 1
    
    # Process concurrency if specified
    if concurrency:
        # Convert 'auto' to CPU count
        if concurrency == 'auto':
            worker_count = multiprocessing.cpu_count()
        else:
            try:
                worker_count = int(concurrency)
            except ValueError:
                raise ValueError(f"Invalid --concurrency value: {concurrency}")
        
        # Determine strategy
        cpu_count = multiprocessing.cpu_count()
        
        if force_multithreading or (not force_multiprocessing and cpu_count <= 2):
            # Use threading strategy (pytest-parallel) 
            cleaned_args.extend(['--workers', str(worker_count)])
            strategy = "threading"
            
            # Task grouping for threading will be handled by our plugin class
            if task_grouping:
                print(f"[AUTO-CONCURRENCY] Task grouping ({task_grouping}) enabled for threading strategy")
        else:
            # Use multiprocessing strategy (pytest-xdist)
            cleaned_args.extend(['-n', str(worker_count)])
            strategy = "multiprocessing"
            
            if task_grouping:
                # Map our task-grouping values to pytest-xdist's --dist values
                if task_grouping == 'file':
                    dist_value = 'loadfile'
                elif task_grouping == 'package':
                    dist_value = 'loadgroup'
                else:
                    dist_value = 'loadfile'  # Default fallback
                cleaned_args.extend(['--dist', dist_value])
        
        print(f"[AUTO-CONCURRENCY] Using {worker_count} workers with {strategy} strategy")
        if task_grouping and strategy == "multiprocessing":
            dist_name = 'loadfile' if task_grouping == 'file' else 'loadgroup'
            print(f"[AUTO-CONCURRENCY] Task grouping enabled (--dist={dist_name})")
    
    # Update args in place
    args[:] = cleaned_args
    
    # Store configuration for the plugin instance
    if concurrency:
        # Store settings on the pluginmanager for pytest_configure to pick up
        setattr(pluginmanager, '_auto_concurrency_workers', worker_count)
        setattr(pluginmanager, '_auto_concurrency_strategy', strategy)
        setattr(pluginmanager, '_auto_concurrency_task_grouping', task_grouping)
    
    # Let other plugins run
    outcome = yield
    return outcome


class AutoConcurrencyPlugin:
    """Plugin class that handles threading-based file grouping scheduling."""
    
    def __init__(self, config):
        self.config = config
        self.workers = getattr(config.pluginmanager, '_auto_concurrency_workers', None)
        self.strategy = getattr(config.pluginmanager, '_auto_concurrency_strategy', None)
        self.task_grouping = getattr(config.pluginmanager, '_auto_concurrency_task_grouping', None)
    
    def _group_tests_by_file(self, items: List[Item]) -> List[Item]:
        """Group test items by their file path and return reordered list."""
        groups = defaultdict(list)
        
        for item in items:
            # Extract file path (everything before first '::')
            file_path = item.nodeid.split('::', 1)[0]
            groups[file_path].append(item)
        
        # Flatten groups back to list, keeping tests from same file together
        reordered_items = []
        for file_path, file_tests in groups.items():
            reordered_items.extend(file_tests)
        
        return reordered_items
    
    def _group_tests_by_package(self, items: List[Item]) -> List[Item]:
        """Group test items by their package/directory and return reordered list."""
        groups = defaultdict(list)
        
        for item in items:
            # Extract directory from file path
            file_path = item.nodeid.split('::', 1)[0]
            package_path = '/'.join(file_path.split('/')[:-1]) or '.'
            groups[package_path].append(item)
        
        # Flatten groups back to list, keeping tests from same package together
        reordered_items = []
        for package_path, package_tests in groups.items():
            reordered_items.extend(package_tests)
        
        return reordered_items
    
    def pytest_collection_modifyitems(self, config, items):
        """Modify test collection order to group tests before pytest-parallel sees them."""
        
        # Only handle threading strategy with task grouping
        if (self.strategy != "threading" or not self.task_grouping or not self.workers):
            return  # Don't modify items
        
        if len(items) <= 1:
            return  # No point in grouping single test
        
        # Count groups before reordering
        original_files = set()
        original_packages = set()
        for item in items:
            file_path = item.nodeid.split('::', 1)[0]
            original_files.add(file_path)
            package_path = '/'.join(file_path.split('/')[:-1]) or '.'
            original_packages.add(package_path)
        
        # Reorder tests based on task_grouping setting
        if self.task_grouping == 'file':
            grouped_items = self._group_tests_by_file(items)
            group_count = len(original_files)
            group_type = "file"
        else:  # package
            grouped_items = self._group_tests_by_package(items)
            group_count = len(original_packages)
            group_type = "package"
        
        # Replace the original items list with grouped version
        items[:] = grouped_items
        
        print(f"[AUTO-CONCURRENCY] Reordered {len(items)} tests into {group_count} {group_type} groups for threading strategy")
        print(f"[AUTO-CONCURRENCY] pytest-parallel will now schedule grouped tests across {self.workers} threads")


def pytest_configure(config):
    """Register the plugin if threading strategy with task grouping is enabled."""
    if (hasattr(config.pluginmanager, '_auto_concurrency_strategy') and
        getattr(config.pluginmanager, '_auto_concurrency_strategy') == "threading" and
        getattr(config.pluginmanager, '_auto_concurrency_task_grouping')):
        
        plugin = AutoConcurrencyPlugin(config)
        config.pluginmanager.register(plugin, 'auto_concurrency_threading')
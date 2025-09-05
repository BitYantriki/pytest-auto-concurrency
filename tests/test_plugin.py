"""Unit tests for pytest-auto-concurrency plugin."""

import pytest
from unittest.mock import patch, MagicMock
from pytest_auto_concurrency.plugin import pytest_addoption, pytest_cmdline_parse


class TestPytestAddOption:
    """Test pytest_addoption function."""
    
    def test_adds_concurrency_options(self):
        """Test that all expected options are added."""
        parser = MagicMock()
        group = MagicMock()
        parser.getgroup.return_value = group
        
        pytest_addoption(parser)
        
        # Verify group creation
        parser.getgroup.assert_called_once_with('auto-concurrency', 'Auto-concurrency options')
        
        # Verify all options are added
        expected_calls = [
            ('--concurrency',),
            ('--task-grouping',), 
            ('--multithreading',),
            ('--multiprocessing',)
        ]
        
        actual_calls = [call[0][0] for call in group.addoption.call_args_list]
        assert len(actual_calls) == 4
        for expected in [call[0] for call in expected_calls]:
            assert expected in actual_calls


class TestPytestCmdlineParse:
    """Test pytest_cmdline_parse function."""
    
    @patch('multiprocessing.cpu_count')
    def test_concurrency_auto_with_multiprocessing(self, mock_cpu_count):
        """Test concurrency=auto with >2 cores uses multiprocessing."""
        mock_cpu_count.return_value = 4
        pluginmanager = MagicMock()
        args = ['--concurrency', 'auto', 'tests/']
        
        # Create a mock outcome for the wrapper
        outcome = MagicMock()
        
        def mock_wrapper():
            yield outcome
            return outcome
        
        # Call the wrapper
        wrapper_gen = pytest_cmdline_parse(pluginmanager, args)
        result = next(wrapper_gen)
        
        # Check that xdist arguments were added
        assert '-n' in args
        assert '4' in args
        assert '--concurrency' not in args
        assert 'auto' not in args
    
    @patch('multiprocessing.cpu_count')  
    def test_concurrency_with_task_grouping(self, mock_cpu_count):
        """Test concurrency with task-grouping adds dist parameter."""
        mock_cpu_count.return_value = 4
        pluginmanager = MagicMock()
        args = ['--concurrency', '2', '--task-grouping=file', 'tests/']
        
        outcome = MagicMock()
        
        def mock_wrapper():
            yield outcome
            return outcome
        
        wrapper_gen = pytest_cmdline_parse(pluginmanager, args)
        result = next(wrapper_gen)
        
        # Check that both -n and --dist arguments were added
        assert '-n' in args
        assert '2' in args
        assert '--dist' in args
        assert 'loadfile' in args
        assert '--concurrency' not in args
        assert '--task-grouping=file' not in args
    
    @patch('multiprocessing.cpu_count')
    def test_concurrency_with_multithreading_flag(self, mock_cpu_count):
        """Test that --multithreading flag forces threading strategy."""
        mock_cpu_count.return_value = 8  # High CPU count
        pluginmanager = MagicMock()
        args = ['--concurrency', '4', '--multithreading', 'tests/']
        
        outcome = MagicMock()
        
        def mock_wrapper():
            yield outcome
            return outcome
        
        wrapper_gen = pytest_cmdline_parse(pluginmanager, args)
        result = next(wrapper_gen)
        
        # Should use --workers instead of -n due to multithreading flag
        assert '--workers' in args
        assert '4' in args
        assert '-n' not in args
        assert '--concurrency' not in args
        assert '--multithreading' not in args
    
    def test_no_concurrency_no_changes(self):
        """Test that args are unchanged when no --concurrency flag."""
        pluginmanager = MagicMock()
        original_args = ['tests/', '-v']
        args = original_args.copy()
        
        outcome = MagicMock()
        
        def mock_wrapper():
            yield outcome
            return outcome
        
        wrapper_gen = pytest_cmdline_parse(pluginmanager, args)
        result = next(wrapper_gen)
        
        # Args should be unchanged
        assert args == original_args
    
    @patch('multiprocessing.cpu_count')
    def test_task_grouping_package_maps_to_loadgroup(self, mock_cpu_count):
        """Test that --task-grouping=package maps to --dist=loadgroup."""
        mock_cpu_count.return_value = 4
        pluginmanager = MagicMock()
        args = ['--concurrency', '2', '--task-grouping=package', 'tests/']
        
        outcome = MagicMock()
        
        def mock_wrapper():
            yield outcome
            return outcome
        
        wrapper_gen = pytest_cmdline_parse(pluginmanager, args)
        result = next(wrapper_gen)
        
        # Check that loadgroup is used
        assert '--dist' in args
        assert 'loadgroup' in args
        assert 'loadfile' not in args
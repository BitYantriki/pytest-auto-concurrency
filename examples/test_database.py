"""
Example database tests that benefit from threading strategy.

I/O-bound tests like database operations work well with threading
because they spend time waiting for database responses.

Run with: pytest examples/test_database.py --concurrency 4 --multithreading --file-grouping
"""

import time
import pytest


@pytest.fixture(scope='module')
def database_connection():
    """Simulate database connection setup."""
    print("\n[DB] Setting up database connection...")
    time.sleep(0.1)  # Simulate connection time
    yield "db_connection_mock"
    print("\n[DB] Closing database connection...")


@pytest.fixture(scope='module')  
def test_data(database_connection):
    """Simulate loading test data."""
    print(f"\n[DB] Loading test data using {database_connection}...")
    time.sleep(0.1)  # Simulate data loading
    return {"users": ["alice", "bob", "charlie"]}


def test_user_creation(database_connection, test_data):
    """Test creating a user."""
    time.sleep(0.2)  # Simulate database operation
    assert "alice" in test_data["users"]
    print(f"✅ User creation test passed with {database_connection}")


def test_user_update(database_connection, test_data):
    """Test updating a user."""
    time.sleep(0.2)  # Simulate database operation
    assert "bob" in test_data["users"]
    print(f"✅ User update test passed with {database_connection}")


def test_user_deletion(database_connection, test_data):
    """Test deleting a user."""
    time.sleep(0.2)  # Simulate database operation
    assert "charlie" in test_data["users"]
    print(f"✅ User deletion test passed with {database_connection}")


def test_user_query(database_connection, test_data):
    """Test querying users."""
    time.sleep(0.2)  # Simulate database operation
    assert len(test_data["users"]) == 3
    print(f"✅ User query test passed with {database_connection}")


def test_user_authentication(database_connection, test_data):
    """Test user authentication."""
    time.sleep(0.2)  # Simulate database operation
    assert test_data["users"]  # Non-empty list
    print(f"✅ User auth test passed with {database_connection}")
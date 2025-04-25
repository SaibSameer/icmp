import pytest
from unittest.mock import MagicMock
from db import execute_query

def test_execute_query_success():
    # Mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value

    # Execute a simple query
    query = "SELECT 1"
    cursor = execute_query(mock_conn, query)

    # Verify the cursor is returned and execute is called
    assert cursor == mock_cursor
    mock_cursor.execute.assert_called_once_with(query, None)

def test_execute_query_failure():
    # Mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value

    # Simulate an exception during query execution
    mock_cursor.execute.side_effect = Exception("Query failed")

    # Verify that an exception is raised and rollback is called
    with pytest.raises(Exception, match="Query failed"):
        execute_query(mock_conn, "SELECT 1")

    mock_conn.rollback.assert_called_once()
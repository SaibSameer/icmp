"""
Tests for the agent stages variable provider.
"""

import unittest
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime
from backend.message_processing.variables.agent_stages import AgentStagesVariable

class TestAgentStagesVariable(unittest.TestCase):
    """Test cases for AgentStagesVariable."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_agent_id = str(uuid.uuid4())  # Generate a valid UUID
        self.mock_stages = [
            {
                "stage_id": str(uuid.uuid4()),
                "stage_name": "Test Stage 1",
                "stage_description": "First test stage",
                "stage_type": "conversation",
                "created_at": datetime(2023, 1, 1)
            },
            {
                "stage_id": str(uuid.uuid4()),
                "stage_name": "Test Stage 2",
                "stage_description": "Second test stage",
                "stage_type": "data_extraction",
                "created_at": datetime(2023, 1, 2)
            }
        ]
    
    def test_get_variable_name(self):
        """Test getting the variable name."""
        self.assertEqual(AgentStagesVariable.get_variable_name(), "agent_stages")
    
    def test_get_variable_description(self):
        """Test getting the variable description."""
        self.assertEqual(
            AgentStagesVariable.get_variable_description(),
            "Returns a list of stages associated with a specific agent"
        )
    
    def test_get_variable_parameters(self):
        """Test getting the variable parameters."""
        params = AgentStagesVariable.get_variable_parameters()
        self.assertIn("agent_id", params)
        self.assertTrue("Optional" in params["agent_id"])
    
    @patch('backend.message_processing.variables.agent_stages.get_db_connection')
    @patch('backend.message_processing.variables.agent_stages.release_db_connection')
    def test_provide_variable_with_agent_id_param(self, mock_release_conn, mock_get_conn):
        """Test providing stages with agent_id in parameters."""
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Create mock rows with proper datetime objects
        mock_rows = [
            (str(uuid.uuid4()), "Test Stage 1", "First test stage", "conversation", datetime(2023, 1, 1)),
            (str(uuid.uuid4()), "Test Stage 2", "Second test stage", "data_extraction", datetime(2023, 1, 2))
        ]
        mock_cursor.fetchall.return_value = mock_rows
        
        # Test the variable provider with agent_id in params
        result = AgentStagesVariable.provide_variable(
            {"agent_id": self.test_agent_id},
            context={"agent_id": str(uuid.uuid4())}  # Different UUID for context
        )
        
        # Verify the results
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["stage_name"], "Test Stage 1")
        self.assertEqual(result[1]["stage_name"], "Test Stage 2")
        
        # Verify the database query used the parameter agent_id
        mock_cursor.execute.assert_called_once()
        query, params = mock_cursor.execute.call_args[0]
        self.assertIn("WHERE s.agent_id = %s", query)
        self.assertEqual(params[0], self.test_agent_id)
        
        # Verify connection was released
        mock_release_conn.assert_called_once_with(mock_conn)
    
    @patch('backend.message_processing.variables.agent_stages.get_db_connection')
    @patch('backend.message_processing.variables.agent_stages.release_db_connection')
    def test_provide_variable_with_context_agent_id(self, mock_release_conn, mock_get_conn):
        """Test providing stages with agent_id from context."""
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Create mock row with proper datetime object
        mock_row = (str(uuid.uuid4()), "Test Stage 1", "First test stage", "conversation", datetime(2023, 1, 1))
        mock_cursor.fetchall.return_value = [mock_row]
        
        # Test the variable provider with agent_id from context
        result = AgentStagesVariable.provide_variable(
            {},  # No agent_id in params
            context={"agent_id": self.test_agent_id}
        )
        
        # Verify the results
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["stage_name"], "Test Stage 1")
        
        # Verify the database query used the context agent_id
        mock_cursor.execute.assert_called_once()
        query, params = mock_cursor.execute.call_args[0]
        self.assertIn("WHERE s.agent_id = %s", query)
        self.assertEqual(params[0], self.test_agent_id)
        
        # Verify connection was released
        mock_release_conn.assert_called_once_with(mock_conn)
    
    def test_provide_variable_missing_agent_id(self):
        """Test providing stages without agent_id in parameters or context."""
        result = AgentStagesVariable.provide_variable({}, context={})
        self.assertIsNone(result)
    
    @patch('backend.message_processing.variables.agent_stages.get_db_connection')
    @patch('backend.message_processing.variables.agent_stages.release_db_connection')
    def test_provide_variable_database_error(self, mock_release_conn, mock_get_conn):
        """Test handling database errors."""
        mock_get_conn.side_effect = Exception("Database error")
        
        result = AgentStagesVariable.provide_variable(
            {"agent_id": self.test_agent_id},
            context={"agent_id": str(uuid.uuid4())}
        )
        self.assertIsNone(result)
        
        # Verify connection was not released since it was never created
        mock_release_conn.assert_not_called()

    def test_provide_variable_real_db(self):
        """Integration test: fetch real stages for a real agent_id."""
        agent_id = "792c6318-79e2-49d9-8f7b-9b32aa78a272"
        result = AgentStagesVariable.provide_variable({"agent_id": agent_id}, context={})
        print("Result from real DB:", result)
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main() 
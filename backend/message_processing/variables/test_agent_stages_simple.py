#!/usr/bin/env python
import os
import sys
import argparse
import logging

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)

# Import after adding to path
from backend.message_processing.variables.agent_stages import AgentStagesVariable

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def test_agent_stages(agent_id):
    try:
        log.info(f"Testing with agent_id: {agent_id}")
        
        # Test with agent_id in parameters
        result = AgentStagesVariable.provide_variable(
            {"agent_id": agent_id},
            context={}
        )
        
        if result is None:
            log.error("Failed to get agent stages")
            return
            
        print("\nAgent Stages:")
        print("------------")
        for stage in result:
            print(f"Stage: {stage['stage_name']}")
            print(f"Description: {stage['stage_description']}")
            print(f"Type: {stage['stage_type']}")
            print("------------")
            
    except Exception as e:
        log.error(f"Error testing agent_stages: {str(e)}", exc_info=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the agent_stages variable provider.")
    parser.add_argument('--agent_id', type=str, help='Agent ID')
    args = parser.parse_args()

    agent_id = args.agent_id or input('Enter Agent ID: ')

    test_agent_stages(
        agent_id=agent_id
    ) 
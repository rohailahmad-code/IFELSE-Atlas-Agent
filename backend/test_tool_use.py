import os
import json
from dotenv import load_dotenv

load_dotenv()

# Ensure we can import from local directory
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.tool_use import tool_use_node
from state import AtlasState

def test_tool_use():
    print("Testing tool_use_node with a mock plan containing a tool_use step...")
    
    # Setup initial state with a pending tool_use step
    initial_state: AtlasState = {
        "goal": "Check if a customer's insurance claim for water damage is valid and estimate payout",
        "industry": "insurance",
        "plan": [
            {
                "step": "Retrieve customer policy details and claim documents.",
                "agent": "retriever",
                "status": "done"
            },
            {
                "step": "Utilize estimation software to estimate repair cost for minor water damage in living room.",
                "agent": "tool_use",
                "status": "pending"
            },
            {
                "step": "Calculate final payout and apply deductible.",
                "agent": "domain",
                "status": "pending"
            }
        ],
        "current_step_index": 1,  # Pointing to the second step (tool_use)
        "tool_results": [],
        "critic_feedback": None,
        "risk_level": "medium",
        "approved": None,
        "final_output": None,
        "trace": [
            {
                "agent": "planner",
                "action": "created_plan",
                "detail": "3 steps planned",
                "timestamp": "2026-06-26T10:00:00Z"
            }
        ]
    }
    
    print("\n--- Initial State ---")
    print(f"Current step index: {initial_state['current_step_index']}")
    print(f"Plan step 1 status: {initial_state['plan'][1]['status']}")
    
    try:
        updated_state = tool_use_node(initial_state)
        
        print("\n=== SUCCESS ===")
        print("Updated Tool Results:")
        print(json.dumps(updated_state["tool_results"], indent=2))
        
        print("\nUpdated Plan Statuses:")
        for idx, step in enumerate(updated_state["plan"]):
            print(f"Step {idx}: {step['step']} | Agent: {step['agent']} | Status: {step['status']}")
            
        print(f"\nNew Current Step Index: {updated_state['current_step_index']}")
        
        print("\nUpdated State Trace:")
        print(json.dumps(updated_state["trace"], indent=2))
        
    except Exception as e:
        print("\n=== TEST FAILED ===")
        print(f"Error executing tool use node: {str(e)}")

if __name__ == "__main__":
    test_tool_use()

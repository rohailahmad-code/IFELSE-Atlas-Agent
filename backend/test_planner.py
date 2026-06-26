import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure we can import from local directory
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.planner import planner_node
from state import AtlasState

def test_planner():
    print("Testing planner_node with sample insurance goal...")
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY is not set in backend/.env.")
        
    for i in range(1, 6):
        print(f"\n==========================================")
        print(f"RUN {i}/5")
        print(f"==========================================")
        
        sample_state: AtlasState = {
            "goal": "Check if a customer's insurance claim for water damage is valid and estimate payout",
            "industry": "insurance",
            "plan": [],
            "current_step_index": 0,
            "tool_results": [],
            "critic_feedback": None,
            "risk_level": "medium",
            "approved": None,
            "final_output": None,
            "trace": []
        }
        
        try:
            updated_state = planner_node(sample_state)
            print(f"\n=== RUN {i} SUCCESS ===")
            print("Generated Plan:")
            print(json.dumps(updated_state["plan"], indent=2))
        except Exception as e:
            print(f"\n=== RUN {i} FAILED ===")
            print(f"Error: {str(e)}")
            # Stop execution on failure so we can inspect
            break

if __name__ == "__main__":
    test_planner()

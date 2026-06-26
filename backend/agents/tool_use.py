import os
import json
import sys
from datetime import datetime

# Add root folder to sys.path so we can import tools and state
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state import AtlasState, ToolResult, TraceEntry
from tools.mock_tools import estimate_repair_cost

def tool_use_node(state: AtlasState) -> AtlasState:
    """
    Agent node that handles tool usage subtasks in the plan.
    Currently always routes to the estimate_repair_cost tool.
    """
    current_index = state.get("current_step_index", 0)
    plan = state.get("plan", [])
    
    if current_index >= len(plan):
        raise ValueError(f"current_step_index ({current_index}) is out of bounds for the plan (size: {len(plan)}).")
        
    current_step = plan[current_index]
    step_description = current_step.get("step", "")
    
    # Run the mock repair cost estimation tool
    tool_output = estimate_repair_cost(step_description)
    
    # Initialize list if not present
    if "tool_results" not in state or state["tool_results"] is None:
        state["tool_results"] = []
        
    # Append tool output to state
    tool_result_entry: ToolResult = {
        "step": step_description,
        "result": json.dumps(tool_output)
    }
    state["tool_results"].append(tool_result_entry)
    
    # Mark current step as done and increment step pointer
    current_step["status"] = "done"
    state["current_step_index"] = current_index + 1
    
    # Initialize trace if not present
    if "trace" not in state or state["trace"] is None:
        state["trace"] = []
        
    # Append trace entry
    trace_entry: TraceEntry = {
        "agent": "tool_use",
        "action": "called_tool",
        "detail": f"estimate_repair_cost -> Estimated Cost: ${tool_output['estimated_cost']} {tool_output['currency']} (Confidence: {tool_output['confidence']})",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    state["trace"].append(trace_entry)
    
    return state

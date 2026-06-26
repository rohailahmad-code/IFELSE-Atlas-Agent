import os
import json
from datetime import datetime
from typing import List
from google import genai
from google.genai import types
from state import AtlasState, PlanStep, TraceEntry

def planner_node(state: AtlasState) -> AtlasState:
    """
    Planner agent node that analyzes the goal and industry context,
    breaks it down into 2-5 concrete subtasks, and updates the state.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    if not api_key or api_key.startswith("your-api-key"):
        raise ValueError("GEMINI_API_KEY is not configured in environment variables.")

    # Construct the instruction prompt
    prompt = f"""
Analyze the following goal within the context of the specified industry.
Your task is to break down this goal into 2 to 5 concrete, sequential subtasks (steps) to achieve the goal.

Goal: "{state.get('goal', '')}"
Industry: "{state.get('industry', '')}"

For each subtask, assign the most appropriate agent type from these three options:
- "retriever": Looks up information in documents, files, knowledge bases, or static guidelines.
- "tool_use": Calls an external tool, calculator, database, or external API to perform computations or fetch live data.
- "domain": Applies industry-specific business logic, judgment, underwriting rules, or decision-making.

You must respond ONLY with a valid JSON array of objects. Do not include any preamble, introduction, markdown code fences, or explanations. 

The exact JSON schema of your response must be:
[
  {{
    "step": "Detailed description of the subtask",
    "agent": "retriever" | "tool_use" | "domain"
  }}
]
"""

    client = genai.Client(api_key=api_key)
    response_text = ""

    # Call Gemini with 503 fallback robustness
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        response_text = response.text or ""
    except Exception as api_err:
        err_str = str(api_err)
        # Attempt fallback if model is unavailable
        if "503" in err_str or "UNAVAILABLE" in err_str or "demand" in err_str:
            fallback_model = "gemini-1.5-flash" if model != "gemini-1.5-flash" else "gemini-1.5-pro"
            print(f"Primary model {model} unavailable (503). Trying fallback: {fallback_model}...")
            fallback_response = client.models.generate_content(
                model=fallback_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            response_text = fallback_response.text or ""
        else:
            raise api_err

    # Print raw response for debugging (requested for test_planner.py inspection)
    print("\n--- [DEBUG] Raw Unparsed Gemini Response ---")
    print(response_text)
    print("-------------------------------------------\n")

    import re
    cleaned_text = response_text.strip()
    
    # Locate the bounds of the JSON array
    start_idx = cleaned_text.find("[")
    end_idx = cleaned_text.rfind("]")
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = cleaned_text[start_idx:end_idx + 1]
    else:
        json_str = cleaned_text

    # Parse JSON with clean brackets fallback
    try:
        raw_plan = json.loads(json_str)
    except json.JSONDecodeError as parse_err:
        print("JSON parsing failed, attempting repair pass...")
        # Repair pass: search for a closing bracket or comma and look for a line starting with "step": without opening {
        # Pattern: (},\s*)("step"\s*:)
        repaired_str = re.sub(r'(},\s*)("step"\s*:)', r'\1{\2', json_str)
        try:
            raw_plan = json.loads(repaired_str)
            print("Repair pass successful!")
        except Exception as repair_err:
            raise ValueError(
                f"Failed to parse Gemini response as JSON list even after repair.\n"
                f"=== Raw Offending Text ===\n{response_text}\n"
                f"=== Segment Attempted ===\n{json_str}\n"
                f"=== Repaired Segment Attempted ===\n{repaired_str}\n"
                f"Original Parse Error: {str(parse_err)}\n"
                f"Repair Parse Error: {str(repair_err)}"
            )

    if not isinstance(raw_plan, list):
        raise ValueError(f"Parsed JSON is not a list. Segment: {json_str}")

    # Update state fields
    plan_steps: List[PlanStep] = []
    for step in raw_plan:
        plan_steps.append({
            "step": step.get("step", ""),
            "agent": step.get("agent", "domain"),  # Default to domain
            "status": "pending"
        })
        
    state["plan"] = plan_steps
    state["current_step_index"] = 0
    
    # Initialize trace list if not present
    if "trace" not in state or state["trace"] is None:
        state["trace"] = []
        
    # Append trace entry
    trace_entry: TraceEntry = {
        "agent": "planner",
        "action": "created_plan",
        "detail": f"{len(plan_steps)} steps planned",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    state["trace"].append(trace_entry)
    
    return state

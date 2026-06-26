from typing import TypedDict, Optional, Literal, List

class PlanStep(TypedDict):
    step: str
    agent: str
    status: str

class ToolResult(TypedDict):
    step: str
    result: str

class TraceEntry(TypedDict):
    agent: str
    action: str
    detail: str
    timestamp: str

class AtlasState(TypedDict):
    """
    State schema for the if/else Atlas Agent workflow.
    Designed for orchestration using LangGraph.
    """
    goal: str
    industry: str
    plan: List[PlanStep]
    current_step_index: int
    tool_results: List[ToolResult]
    critic_feedback: Optional[str]
    risk_level: Literal["low", "medium", "high"]
    approved: Optional[bool]
    final_output: Optional[str]
    trace: List[TraceEntry]

from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from tools import registry

load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY").strip(),
    model="gpt-4o-mini",
    temperature=0.3
)

class RCAState(TypedDict):
    error: str
    analysis: str
    hypothesis: str
    selected_tool: str
    tool_kwargs: Dict[str, Any]
    is_valid: bool
    fix: str
    attempts: int

def analyze_logs(state: RCAState):
    response = llm.invoke([
        SystemMessage(content="You are an expert SRE. Analyze the provided error log and identify what went wrong. Be concise and technical."),
        HumanMessage(content=f"Analyze this error:\n{state['error']}")
    ])
    return {**state, "analysis": response.content}

def generate_hypothesis(state: RCAState):
    response = llm.invoke([
        SystemMessage(content="You are an expert SRE. Based on the analysis, suggest ONE specific root cause hypothesis."),
        HumanMessage(content=f"Analysis:\n{state['analysis']}\n\nSuggest ONE root cause hypothesis.")
    ])
    return {**state, "hypothesis": response.content, "attempts": state["attempts"] + 1}

def choose_tool(state: RCAState):
    llm_with_tools = llm.bind_tools(registry.get_agent_schema())
    response = llm_with_tools.invoke([
        SystemMessage(content="You are an expert SRE. Choose the most appropriate diagnostic tool to verify the hypothesis."),
        HumanMessage(content=f"Hypothesis:\n{state['hypothesis']}\n\nWhich tool should verify this? Call it with correct arguments.")
    ])
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        return {**state, "selected_tool": tool_call["name"], "tool_kwargs": tool_call["args"]}
    return {**state, "selected_tool": "none", "tool_kwargs": {}}

def validate(state: RCAState):
    tool_name = state.get("selected_tool")
    tool_kwargs = state.get("tool_kwargs", {})
    if tool_name and tool_name != "none":
        try:
            result = registry.execute(tool_name, **tool_kwargs)
            return {**state, "is_valid": not result}
        except Exception as e:
            print(f"Tool execution failed: {e}")
            return {**state, "is_valid": False}
    return {**state, "is_valid": False}

def suggest_fix(state: RCAState):
    response = llm.invoke([
        SystemMessage(
            content=(
                "You are an RCA report generator. "
                "You MUST output ONLY the following report structure. "
                "Do NOT greet the user. Do NOT add tables. Do NOT add any text before 'RCA REPORT'. "
                "Do NOT add any sections other than the 8 listed below. "
                "Your entire response must follow this exact format:\n\n"
                "RCA REPORT [No Incident ID provided]\n\n"
                "## INCIDENT SUMMARY\n<content>\n\n"
                "## TIMELINE OF EVENTS\n<content>\n\n"
                "## ROOT CAUSE\n<content>\n\n"
                "## CONTRIBUTING FACTORS\n<content>\n\n"
                "## IMMEDIATE FIX\n<content>\n\n"
                "## PERMANENT FIX\n<content>\n\n"
                "## DETECTION GAPS\n<content>\n\n"
                "## PREVENTION\n<content>"
            )
        ),
        HumanMessage(content=(
            f"Error log: {state['error']}\n\n"
            f"Analysis: {state['analysis']}\n\n"
            f"Root cause hypothesis: {state['hypothesis']}\n\n"
            f"Validation tool used: {state['selected_tool']} with args {state['tool_kwargs']}\n\n"
            f"Hypothesis validated: {state['is_valid']}\n\n"
            "Generate the RCA report."
        ))
    ])
    return {**state, "fix": response.content}

def decide(state: RCAState):
    if state["is_valid"] or state["attempts"] >= 3:
        return "fix"
    return "retry"

builder = StateGraph(RCAState)
builder.add_node("analyze", analyze_logs)
builder.add_node("hypothesis", generate_hypothesis)
builder.add_node("choose_tool", choose_tool)
builder.add_node("validate", validate)
builder.add_node("fix", suggest_fix)

builder.set_entry_point("analyze")
builder.add_edge("analyze", "hypothesis")
builder.add_edge("hypothesis", "choose_tool")
builder.add_edge("choose_tool", "validate")
builder.add_conditional_edges("validate", decide, {"retry": "hypothesis", "fix": "fix"})
builder.add_edge("fix", END)

graph = builder.compile()

def run_rca(error_message: str) -> dict:
    return graph.invoke({
        "error": error_message,
        "analysis": "",
        "hypothesis": "",
        "selected_tool": "",
        "tool_kwargs": {},
        "is_valid": False,
        "fix": "",
        "attempts": 0
    })

"""CoursePilot Strands agent configuration."""
from __future__ import annotations
import os
from strands import Agent
from strands.models import BedrockModel
from .tools import calculate_grading_hours, check_assessment_plan, summarize_constraints

SYSTEM_PROMPT = """You are CoursePilot, an agentic course development and quality assurance assistant.
1. Treat explicit institutional/course constraints as hard constraints unless the instructor says otherwise.
2. Use tools for arithmetic, validation, and workload calculations.
3. Never claim a plan is valid before calling the relevant validation tools.
4. If hard constraints conflict, explain the conflict and ask for a human decision.
5. Distinguish facts from recommendations.
6. Keep the instructor as the final decision maker.
"""

def build_agent() -> Agent:
    model_id=os.getenv("COURSEPILOT_MODEL_ID","global.anthropic.claude-sonnet-4-6")
    region=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-west-2"
    model=BedrockModel(model_id=model_id, region_name=region, temperature=0.2)
    return Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=[summarize_constraints,check_assessment_plan,calculate_grading_hours])

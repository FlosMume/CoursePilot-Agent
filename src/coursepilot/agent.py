"""CoursePilot Strands/Bedrock planning agent.

The LLM is responsible for proposing and explaining a course plan.
Deterministic Python code remains authoritative for validation.
"""
from __future__ import annotations

import json
import os
from typing import Any

from pydantic import BaseModel, Field
from strands import Agent
from strands.models import BedrockModel

from .tools import (
    calculate_grading_hours,
    check_assessment_plan,
    summarize_constraints,
)


SYSTEM_PROMPT = """You are CoursePilot, an agentic course-development and
quality-assurance assistant.

Core rules:
1. Treat explicit institutional and instructor-defined constraints as hard
   constraints unless the instructor explicitly says otherwise.
2. Do not silently change instructor-defined assessment names, weights,
   scheduled weeks, or other explicit requirements.
3. Use the language model for planning, synthesis, and explanation.
4. Deterministic Python validation results are authoritative for rule checks.
5. Distinguish source facts, assumptions, and recommendations.
6. When constraints conflict, explain the conflict instead of hiding it.
7. Keep the instructor as the final decision maker.
"""


class AssessmentPlanItem(BaseModel):
    """One assessment appearing in the proposed course plan."""

    name: str = Field(description="Assessment name.")
    weight: float = Field(description="Assessment weight as a percentage.")
    week: int | None = Field(
        default=None,
        description="Scheduled course week, if explicitly known.",
    )
    purpose: str | None = Field(
        default=None,
        description="Brief pedagogical purpose of the assessment.",
    )


class WeeklyPlanItem(BaseModel):
    """One week in the proposed teaching plan."""

    week: int = Field(description="Course week number.")
    focus: str = Field(description="Main topic or instructional focus.")
    activities: list[str] = Field(
        default_factory=list,
        description="Suggested learning activities, labs, exercises, or milestones.",
    )


class CoursePlan(BaseModel):
    """Structured CoursePilot planning output."""

    course_code: str | None = None
    course_title: str | None = None
    weeks: int = Field(description="Number of course weeks.")
    summary: str = Field(description="Concise overview of the proposed course plan.")
    assessments: list[AssessmentPlanItem] = Field(
        default_factory=list,
        description="Assessment plan. Explicit source values must be preserved.",
    )
    weekly_plan: list[WeeklyPlanItem] = Field(
        default_factory=list,
        description="Week-by-week proposed teaching plan.",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions made because the source requirements were incomplete.",
    )


def get_model_settings() -> tuple[str, str]:
    """Return the configured Bedrock model ID and AWS region."""
    model_id = os.getenv(
        "COURSEPILOT_MODEL_ID",
        "global.amazon.nova-2-lite-v1:0",
    )
    region = (
        os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or "us-west-2"
    )
    return model_id, region


def build_agent(*, with_tools: bool = False) -> Agent:
    """Build a CoursePilot Strands agent backed by Amazon Bedrock."""
    model_id, region = get_model_settings()

    model = BedrockModel(
        model_id=model_id,
        region_name=region,
        temperature=0.2,
    )

    tools = []
    if with_tools:
        # Retained for compatibility and future interactive agent workflows.
        # The main MVP pipeline performs validation directly in Python.
        tools = [
            summarize_constraints,
            check_assessment_plan,
            calculate_grading_hours,
        ]

    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
    )


def generate_course_plan(course_data: dict[str, Any]) -> CoursePlan:
    """Generate a structured proposed course plan with Strands + Bedrock."""
    prompt = f"""Create a proposed course plan from the COURSE DATA below.

Important instructions:
- Preserve every explicitly supplied assessment name, weight, and scheduled week.
- Do NOT repair an invalid assessment total by changing instructor-defined weights.
- Do NOT hide contradictions in the source data.
- Build a week-by-week plan covering Weeks 1 through the stated course length.
- Use assumptions only where the source data is incomplete, and list those
  assumptions explicitly.
- Keep the proposal practical and concise.
- This is the PLANNING step only. Deterministic Python validators will run after
  this response, so do not claim that rule validation has already passed.

COURSE DATA:
{json.dumps(course_data, indent=2, ensure_ascii=False)}
"""

    result = build_agent()(prompt, structured_output_model=CoursePlan)
    plan = result.structured_output

    if plan is None:
        raise RuntimeError("CoursePilot did not return a structured CoursePlan.")

    return plan


def generate_instructor_review(
    course_data: dict[str, Any],
    course_plan: CoursePlan,
    validation: dict[str, Any],
) -> str:
    """Explain deterministic validation results for instructor review."""
    prompt = f"""Prepare a concise instructor review of the proposed CoursePilot plan.

The deterministic VALIDATION RESULTS below are authoritative.
Do not contradict them and do not silently fix instructor-defined values.

Your review should:
1. State whether the plan passed deterministic validation.
2. Clearly identify each failed check.
3. Explain why the issue matters.
4. Offer correction OPTIONS when useful, but do not apply a change that requires
   instructor approval.
5. End by clearly indicating whether instructor action is required.

SOURCE COURSE DATA:
{json.dumps(course_data, indent=2, ensure_ascii=False)}

PROPOSED COURSE PLAN:
{json.dumps(course_plan.model_dump(), indent=2, ensure_ascii=False)}

DETERMINISTIC VALIDATION RESULTS:
{json.dumps(validation, indent=2, ensure_ascii=False)}
"""

    return str(build_agent()(prompt))

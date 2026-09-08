"""Strands tools used by the CoursePilot agent."""
from __future__ import annotations
from typing import Any
from strands import tool
from .validators import estimate_grading_workload, validate_assessment_names, validate_assessment_weeks, validate_assessment_weights

@tool
def check_assessment_plan(assessments: list[dict[str, Any]], course_weeks: int = 13) -> dict[str, Any]:
    """Validate assessment weights, names, and scheduled weeks."""
    return {"weights": validate_assessment_weights(assessments), "names": validate_assessment_names(assessments), "weeks": validate_assessment_weeks(assessments, course_weeks)}

@tool
def calculate_grading_hours(enrollment:int, submissions_per_student:int, minutes_per_submission:float)->dict[str,Any]:
    """Estimate grading workload in hours."""
    return estimate_grading_workload(enrollment, submissions_per_student, minutes_per_submission)

@tool
def summarize_constraints(course_data: dict[str, Any]) -> dict[str, Any]:
    """Return a compact structured summary of course constraints for planning."""
    assessments=course_data.get("assessments",[])
    return {"course_code":course_data.get("course_code"),"course_title":course_data.get("course_title"),"weeks":course_data.get("weeks"),"enrollment":course_data.get("enrollment"),"assessment_count":len(assessments),"assessment_names":[a.get("name") for a in assessments],"constraints":course_data.get("constraints",[])}

"""Deterministic validation helpers for CoursePilot."""
from __future__ import annotations
from collections import Counter
from typing import Any

def validate_assessment_weights(assessments: list[dict[str, Any]]) -> dict[str, Any]:
    total = round(sum(float(item.get("weight", 0)) for item in assessments), 2)
    return {"valid": total == 100.0, "total_weight": total, "difference_from_100": round(total-100.0,2), "message": "Assessment weights total exactly 100%." if total == 100.0 else f"Assessment weights total {total}%, not 100%."}

def validate_assessment_names(assessments: list[dict[str, Any]]) -> dict[str, Any]:
    names=[str(item.get("name","")).strip() for item in assessments]
    duplicates=sorted(name for name,count in Counter(names).items() if name and count>1)
    return {"valid": not duplicates, "duplicates": duplicates, "message": "Assessment names are unique." if not duplicates else f"Duplicate assessment names: {', '.join(duplicates)}."}

def validate_assessment_weeks(assessments: list[dict[str, Any]], course_weeks: int) -> dict[str, Any]:
    invalid=[]
    for item in assessments:
        week=item.get("week")
        if week is None: continue
        try: week_num=int(week)
        except (TypeError,ValueError):
            invalid.append({"name":item.get("name"),"week":week}); continue
        if week_num<1 or week_num>course_weeks: invalid.append({"name":item.get("name"),"week":week_num})
    return {"valid": not invalid, "invalid_assessments": invalid, "message": "All assessment weeks are within the course." if not invalid else "One or more assessment weeks are outside the course."}

def estimate_grading_workload(enrollment:int, submissions_per_student:int, minutes_per_submission:float)->dict[str,Any]:
    total_submissions=enrollment*submissions_per_student
    total_minutes=total_submissions*minutes_per_submission
    return {"enrollment":enrollment,"submissions_per_student":submissions_per_student,"minutes_per_submission":minutes_per_submission,"total_submissions":total_submissions,"estimated_hours":round(total_minutes/60.0,2)}

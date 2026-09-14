"""Command-line entry point for the CoursePilot AWS-powered MVP."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .agent import generate_course_plan, generate_instructor_review, get_model_settings
from .validators import (
    estimate_grading_workload,
    validate_assessment_names,
    validate_assessment_weeks,
    validate_assessment_weights,
)


def _load_course_data(path: Path) -> dict[str, Any]:
    """Load and minimally verify a CoursePilot JSON input file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Input file is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise SystemExit("CoursePilot input must be a JSON object.")

    return data


def _validate_source_assessment_integrity(
    source_assessments: list[dict[str, Any]],
    planned_assessments: list[dict[str, Any]],
) -> dict[str, Any]:
    """Check that the LLM did not alter explicit instructor-defined values."""
    planned_by_name = {
        str(item.get("name", "")).strip(): item
        for item in planned_assessments
        if str(item.get("name", "")).strip()
    }

    issues: list[dict[str, Any]] = []

    for source in source_assessments:
        name = str(source.get("name", "")).strip()
        if not name:
            continue

        planned = planned_by_name.get(name)
        if planned is None:
            issues.append(
                {
                    "assessment": name,
                    "issue": "missing_from_generated_plan",
                }
            )
            continue

        if "weight" in source:
            try:
                source_weight = float(source["weight"])
                planned_weight = float(planned.get("weight"))
            except (TypeError, ValueError):
                issues.append(
                    {
                        "assessment": name,
                        "issue": "uncomparable_weight",
                        "source_weight": source.get("weight"),
                        "planned_weight": planned.get("weight"),
                    }
                )
            else:
                if source_weight != planned_weight:
                    issues.append(
                        {
                            "assessment": name,
                            "issue": "weight_changed",
                            "source_weight": source_weight,
                            "planned_weight": planned_weight,
                        }
                    )

        if source.get("week") is not None:
            try:
                source_week = int(source["week"])
                planned_week = int(planned.get("week"))
            except (TypeError, ValueError):
                issues.append(
                    {
                        "assessment": name,
                        "issue": "uncomparable_week",
                        "source_week": source.get("week"),
                        "planned_week": planned.get("week"),
                    }
                )
            else:
                if source_week != planned_week:
                    issues.append(
                        {
                            "assessment": name,
                            "issue": "week_changed",
                            "source_week": source_week,
                            "planned_week": planned_week,
                        }
                    )

    return {
        "valid": not issues,
        "issues": issues,
        "message": (
            "Instructor-defined assessment values were preserved."
            if not issues
            else "The generated plan changed or omitted instructor-defined assessment values."
        ),
    }


def _build_validation(
    course_data: dict[str, Any],
    planned_assessments: list[dict[str, Any]],
) -> dict[str, Any]:
    """Run deterministic validation after the LLM planning step."""
    try:
        course_weeks = int(course_data.get("weeks", 13))
    except (TypeError, ValueError):
        course_weeks = 13

    source_assessments = course_data.get("assessments", [])
    if not isinstance(source_assessments, list):
        source_assessments = []

    validation: dict[str, Any] = {
        "weights": validate_assessment_weights(planned_assessments),
        "names": validate_assessment_names(planned_assessments),
        "weeks": validate_assessment_weeks(planned_assessments, course_weeks),
        "source_assessment_integrity": _validate_source_assessment_integrity(
            source_assessments,
            planned_assessments,
        ),
    }

    grading = course_data.get("grading_workload")
    if isinstance(grading, dict):
        required = (
            course_data.get("enrollment"),
            grading.get("submissions_per_student"),
            grading.get("minutes_per_submission"),
        )

        if all(value is not None for value in required):
            try:
                validation["grading_workload"] = estimate_grading_workload(
                    enrollment=int(course_data["enrollment"]),
                    submissions_per_student=int(grading["submissions_per_student"]),
                    minutes_per_submission=float(grading["minutes_per_submission"]),
                )
            except (TypeError, ValueError):
                validation["grading_workload"] = {
                    "available": False,
                    "message": "Grading-workload inputs could not be converted to numbers.",
                }
        else:
            validation["grading_workload"] = {
                "available": False,
                "message": "Grading-workload data is incomplete.",
            }

    validation["overall_valid"] = all(
        validation[key].get("valid", False)
        for key in (
            "weights",
            "names",
            "weeks",
            "source_assessment_integrity",
        )
    )

    return validation


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: PYTHONPATH=src python -m coursepilot <course_requirements.json>"
        )

    input_path = Path(sys.argv[1])
    course_data = _load_course_data(input_path)

    # 1. Planning: Strands -> Amazon Bedrock -> Nova 2 Lite
    course_plan = generate_course_plan(course_data)

    # 2. Deterministic validation in Python
    planned_assessments = [
        item.model_dump()
        for item in course_plan.assessments
    ]
    validation = _build_validation(course_data, planned_assessments)

    # 3. Instructor-facing explanation/review
    instructor_review = generate_instructor_review(
        course_data,
        course_plan,
        validation,
    )

    model_id, region = get_model_settings()

    output = {
        "pipeline": [
            "course_input",
            "strands_bedrock_planning",
            "deterministic_validation",
            "instructor_review",
        ],
        "model": {
            "provider": "Amazon Bedrock",
            "model_id": model_id,
            "region": region,
        },
        "status": (
            "validated"
            if validation["overall_valid"]
            else "needs_instructor_review"
        ),
        "course_plan": course_plan.model_dump(),
        "validation": validation,
        "instructor_review": instructor_review,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

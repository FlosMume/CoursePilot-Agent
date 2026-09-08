"""Command-line entry point for CoursePilot v0.1."""
from __future__ import annotations
import json, sys
from pathlib import Path
from .agent import build_agent

def main()->None:
    if len(sys.argv)!=2: raise SystemExit("Usage: python -m coursepilot <course_requirements.json>")
    path=Path(sys.argv[1])
    data=json.loads(path.read_text(encoding="utf-8"))
    prompt=f"""Analyze the following course requirements. First summarize constraints, then validate the assessment plan using tools. If invalid, explain conflicts and propose correction options, but do not silently change instructor-defined weights. Also estimate grading hours if grading_workload is present.

COURSE DATA:
{json.dumps(data,indent=2)}"""
    print(build_agent()(prompt))

if __name__=="__main__": main()

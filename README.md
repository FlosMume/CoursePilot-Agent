# CoursePilot-Agent

An agentic course development and quality assurance assistant built with the **Strands Agents SDK** and **AWS**.

> **Hackathon status:** v0.1 scaffold. The MVP focuses on one end-to-end workflow: course requirements → planning → deterministic validation → instructor review.

## Why CoursePilot?
Course development is more than generating lecture content. Instructors must translate requirements into weekly schedules, assessments, labs, projects, grading plans, and teaching-assistant workloads while keeping dates, weights, policies, and workload constraints consistent.

CoursePilot is designed to automate repetitive coordination work while keeping the instructor as the final decision maker.

## MVP workflow
1. Read structured course requirements and instructor constraints.
2. Generate a proposed course and assessment plan.
3. Call deterministic Python validation tools.
4. Flag conflicts such as assessment weights that do not total 100%.
5. Revise the proposal or ask the instructor for a decision.
6. Return a validated plan and an explanation of remaining issues.

## Design principle
**Use the LLM for reasoning; use deterministic tools for rules.**

## Architecture
- **Strands Agents SDK** — agent loop and tool orchestration
- **Amazon Bedrock** — foundation-model reasoning
- **Amazon Bedrock AgentCore** — planned managed runtime / observability deployment
- **Amazon S3** — planned document and artifact storage

The v0.1 implementation runs locally with Strands and Amazon Bedrock. AgentCore and S3 integration come next.

## Quick start

### Prerequisites
- Python 3.10+
- AWS account with Amazon Bedrock access
- AWS credentials configured locally
- Permission for `bedrock:InvokeModel` and, when streaming, `bedrock:InvokeModelWithResponseStream`

### Create a virtual environment
```bash
python -m venv .venv
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Configure model settings
```bash
export AWS_REGION=us-west-2
export COURSEPILOT_MODEL_ID=global.anthropic.claude-sonnet-4-6
```

### Run CoursePilot
```bash
PYTHONPATH=src python -m coursepilot examples/sample_course_requirements.json
```

### Run tests
```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Current deterministic checks
- Assessment weights total 100%.
- Duplicate assessment names are flagged.
- Assessment week numbers fall inside the course length.
- Simple grading-workload hours can be estimated.

## Hackathon track
**Professional Agents**

## License
MIT License.

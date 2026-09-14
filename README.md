# CoursePilot-Agent

An agentic course-development and quality-assurance assistant built with the
**Strands Agents SDK** and **Amazon Bedrock**.

> **MVP status:** CoursePilot now runs an end-to-end local workflow in which
> structured course requirements are converted into a proposed course plan by
> Strands + Amazon Bedrock + Amazon Nova 2 Lite, checked by deterministic Python
> validators, and returned for instructor review.

## Why CoursePilot?

Course development is more than generating lecture content. Instructors must
translate requirements into weekly schedules, assessments, labs, projects,
grading plans, and teaching-assistant workloads while keeping dates, weights,
policies, and workload constraints consistent.

CoursePilot is designed to automate repetitive coordination work while keeping
the instructor as the final decision maker.

## MVP workflow

```text
CoursePilot JSON input
        |
        v
Strands Agents SDK
        |
        v
Amazon Bedrock / Nova 2 Lite
        |
        v
Structured proposed CoursePlan
        |
        v
Deterministic Python validators
        |
        v
Instructor review / final output
```

The key design principle is:

> **Use the LLM for planning and reasoning; use deterministic Python for rules.**

The current pipeline does **not** silently repair instructor-defined assessment
weights or dates. If the source data contains a conflict, CoursePilot preserves
the explicit values, reports the deterministic validation failure, and presents
the issue for instructor review.

## Architecture

- **Strands Agents SDK** — agent execution and structured output
- **Amazon Bedrock** — managed foundation-model access
- **Amazon Nova 2 Lite** — current planning/reasoning model
- **Deterministic Python validators** — rule checking for weights, assessment
  names, course weeks, and grading workload
- **Amazon Bedrock AgentCore** — planned managed runtime / observability layer
- **Amazon S3** — planned document and artifact storage

AgentCore and S3 are intentionally outside this integration step. The present
goal is to make the existing CoursePilot MVP work end to end before adding more
AWS infrastructure.

## Repository structure

```text
src/coursepilot/
├── __init__.py
├── __main__.py
├── agent.py
├── tools.py
└── validators.py
```

### Main responsibilities

- `agent.py`
  - configures Strands + Amazon Bedrock
  - defaults to Amazon Nova 2 Lite
  - defines the structured `CoursePlan`
  - generates the proposed plan
  - generates the instructor-facing review

- `__main__.py`
  - loads CoursePilot JSON input
  - calls the planning step
  - runs deterministic validators
  - checks that instructor-defined assessment values were not changed
  - produces a single JSON result

- `validators.py`
  - remains the deterministic rules layer
  - checks assessment weights, names, weeks, and grading workload

- `tools.py`
  - retains Strands tool wrappers for future interactive/agent workflows
  - is not required for the main deterministic-validation path

## Quick start

### Prerequisites

- Python 3.10+
- AWS account with Amazon Bedrock access
- AWS credentials configured locally
- permission to invoke the selected Bedrock model

### Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure the model

Linux / macOS / WSL:

```bash
export AWS_REGION=us-west-2
export COURSEPILOT_MODEL_ID=global.amazon.nova-2-lite-v1:0
```

PowerShell:

```powershell
$env:AWS_REGION="us-west-2"
$env:COURSEPILOT_MODEL_ID="global.amazon.nova-2-lite-v1:0"
```

### Run CoursePilot

```bash
PYTHONPATH=src python -m coursepilot examples/sample_course_requirements.json
```

The program now returns structured JSON containing:

```text
pipeline
model
status
course_plan
validation
instructor_review
```

If the proposed assessment weights do not total 100%, the deterministic
validator marks the plan invalid and the final status becomes:

```text
needs_instructor_review
```

CoursePilot should then explain the conflict and provide options without silently
changing instructor-defined values.

## Current deterministic checks

- assessment weights total exactly 100%
- assessment names are unique
- assessment week numbers fall inside the course length
- explicit instructor-defined assessment weights/weeks are preserved through
  the LLM planning step
- simple grading-workload hours can be estimated

## Tests

Existing deterministic tests can still be run with:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

No additional test files are required for this integration step.

## Next AWS phase

After the end-to-end MVP is stable, the next infrastructure steps can be:

1. package/deploy the CoursePilot agent with Amazon Bedrock AgentCore
2. add Amazon S3 for course inputs, generated plans, and review artifacts
3. add observability and run history
4. expand the instructor-review workflow

## Hackathon track

**Professional Agents**

## License

MIT License.

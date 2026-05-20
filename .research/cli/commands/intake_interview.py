#!/usr/bin/env python3
"""Conversational Intake Interviewer CLI command.

Generates intake.md through an interactive Q&A session rather than requiring
the user to fill out a static form.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


INTAKE_QUESTIONS = [
    {
        "id": "project_title",
        "question": "What is your project called? (A short title is fine)",
        "field": "Project title",
        "required": True,
    },
    {
        "id": "research_question",
        "question": "What is the main question you want to answer? Be as specific or vague as you like — we'll refine it.",
        "field": "Primary research question",
        "required": True,
    },
    {
        "id": "outcome_variable",
        "question": "What is the main outcome you care about? (e.g., 'house prices', 'test scores', 'survival rate')",
        "field": "Outcome variable",
        "required": True,
    },
    {
        "id": "key_predictors",
        "question": "What factors do you think might affect this outcome? (e.g., 'school quality', 'income', 'age')",
        "field": "Key predictors / independent variables",
        "required": False,
    },
    {
        "id": "data_description",
        "question": "Tell me about your data. What format is it in? How many rows/columns? Where did it come from?",
        "field": "Data overview",
        "required": True,
    },
    {
        "id": "domain",
        "question": "What field is this research in? (e.g., economics, psychology, biology, education, finance)",
        "field": "Domain",
        "required": False,
    },
    {
        "id": "constraints",
        "question": "Any constraints? (e.g., 'must use only public data', 'need to finish by Friday', 'no causal claims allowed')",
        "field": "Constraints",
        "required": False,
    },
    {
        "id": "audience",
        "question": "Who is the audience for this research? (e.g., 'science fair judges', 'academic journal', 'policy makers', 'myself')",
        "field": "Target audience",
        "required": False,
    },
    {
        "id": "controls",
        "question": "Are there any confounding variables you want to control for? (e.g., 'neighborhood income', 'age', 'gender')",
        "field": "Control variables",
        "required": False,
    },
    {
        "id": "hypothesis",
        "question": "Do you have a hypothesis? What do you expect to find?",
        "field": "Hypothesis",
        "required": False,
    },
]


def _detect_data_info() -> dict:
    """Scan inputs/data/raw/ for basic data info."""
    raw_dir = Path("inputs/data/raw")
    if not raw_dir.exists():
        return {"files": [], "total_size": 0}

    files = []
    total_size = 0
    for f in raw_dir.iterdir():
        if f.is_file() and not f.name.startswith("."):
            size = f.stat().st_size
            total_size += size
            files.append({
                "name": f.name,
                "size_mb": round(size / 1024 / 1024, 2),
                "extension": f.suffix,
            })

    return {"files": files, "total_size_mb": round(total_size / 1024 / 1024, 2)}


def _generate_intake_md(answers: dict) -> str:
    """Generate intake.md from collected answers."""
    data_info = _detect_data_info()

    lines = [
        "# Research Intake Form",
        f"\nGenerated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Method: Conversational Interview",
        "",
        "## Project Information",
        f"- **Project title**: {answers.get('project_title', '[NOT PROVIDED]')}",
        f"- **Primary research question**: {answers.get('research_question', '[NOT PROVIDED]')}",
        f"- **Domain**: {answers.get('domain', '[AUTO-DETECT]')}",
        f"- **Target audience**: {answers.get('audience', 'General')}",
        "",
        "## Research Design",
        f"- **Outcome variable**: {answers.get('outcome_variable', '[NOT PROVIDED]')}",
        f"- **Key predictors**: {answers.get('key_predictors', '[TO BE IDENTIFIED]')}",
        f"- **Control variables**: {answers.get('controls', '[TO BE IDENTIFIED]')}",
        f"- **Hypothesis**: {answers.get('hypothesis', '[TO BE FORMULATED]')}",
        "",
        "## Data Overview",
    ]

    if data_info["files"]:
        lines.append(f"- **Total data size**: {data_info['total_size_mb']} MB")
        lines.append("- **Files**:")
        for f in data_info["files"]:
            lines.append(f"  - `{f['name']}` ({f['size_mb']} MB, {f['extension']})")
    else:
        lines.append("- **No data files found in inputs/data/raw/**")
        lines.append(f"- **User description**: {answers.get('data_description', '[NOT PROVIDED]')}")

    lines.extend([
        "",
        "## Constraints",
        f"- {answers.get('constraints', 'None specified')}",
        "",
        "## Notes",
        f"- Data description from interview: {answers.get('data_description', '[NOT PROVIDED]')}",
        "",
        "---",
        "*This intake was generated via conversational interview. Review and edit as needed.*",
    ])

    return "\n".join(lines)


def run_intake_interview(start: bool = False, message: str = "") -> str:
    """Run the intake interview.

    Args:
        start: If True, start a new interview
        message: User's response to the current question

    Returns:
        Interview state or generated intake
    """
    session_file = Path(".research/cache/intake_session.json")

    if start or not session_file.exists():
        # Start new interview
        session = {
            "current_question": 0,
            "answers": {},
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        session_file.parent.mkdir(parents=True, exist_ok=True)

        q = INTAKE_QUESTIONS[0]
        session["answers"] = {}

        # Save session
        with open(session_file, "w") as f:
            json.dump(session, f, indent=2)

        return (
            f"🔬 **Research Intake Interview — Question 1/{len(INTAKE_QUESTIONS)}**\n\n"
            f"{q['question']}\n\n"
            f"(Reply with your answer, or type 'skip' to skip this question)"
        )

    # Load existing session
    with open(session_file) as f:
        session = json.load(f)

    current_idx = session["current_question"]

    if message and message.lower() != "skip":
        # Save the answer
        q = INTAKE_QUESTIONS[current_idx]
        session["answers"][q["id"]] = message

    # Move to next question
    current_idx += 1
    session["current_question"] = current_idx

    if current_idx >= len(INTAKE_QUESTIONS):
        # Interview complete — generate intake.md
        intake_path = Path("inputs/intake.md")
        intake_path.parent.mkdir(parents=True, exist_ok=True)
        intake_content = _generate_intake_md(session["answers"])
        intake_path.write_text(intake_content)

        # Clean up session
        session_file.unlink(missing_ok=True)

        return (
            f"✅ **Intake interview complete!**\n\n"
            f"Generated `inputs/intake.md` with your responses.\n\n"
            f"You can now run `research status` to see the next step, "
            f"or review and edit `inputs/intake.md` if needed."
        )

    # Save updated session
    with open(session_file, "w") as f:
        json.dump(session, f, indent=2)

    q = INTAKE_QUESTIONS[current_idx]
    return (
        f"**Question {current_idx + 1}/{len(INTAKE_QUESTIONS)}**\n\n"
        f"{q['question']}\n\n"
        f"(Reply with your answer, or type 'skip' to skip this question)"
    )

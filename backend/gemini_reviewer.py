import json
from google import genai
from config import GEMINI_MODEL, MAX_FILE_CHARS, MAX_FILES


# ──────────────────────────────────────────────
# SYSTEM PROMPT  (structured JSON output)
# ──────────────────────────────────────────────
def build_system_prompt(audit_type: str) -> str:
    focus_map = {
        "security":       "Focus ONLY on security vulnerabilities (injection, XSS, auth issues, secrets in code, etc.).",
        "performance":    "Focus ONLY on performance problems (inefficient loops, memory leaks, blocking calls, etc.).",
        "best practices": "Focus ONLY on code quality and best-practice violations (naming, structure, duplication, SOLID, etc.).",
        "everything":     "Check everything: security, performance, best practices, bugs, and code structure.",
    }
    focus_instruction = focus_map.get(audit_type.lower(), focus_map["everything"])

    return f"""
You are an expert AI code review assistant.

{focus_instruction}

Return ONLY a valid JSON object — no markdown, no explanation outside the JSON.

Schema:
{{
  "overall_status": "good" | "issues_found",
  "summary": "<one-sentence summary>",
  "files": [
    {{
      "file_name": "<filename>",
      "file_path": "<relative path>",
      "status": "good" | "issues_found",
      "issues": [
        {{
          "line": <line number or null>,
          "category": "<Bug | Security | Performance | Best Practice | Structure>",
          "issue": "<clear description of the problem>",
          "recommendation": "<concrete fix suggestion>"
        }}
      ]
    }}
  ]
}}

Rules:
- If a file has no issues set "status": "good" and "issues": [].
- Do not invent issues. Only report real problems.
- Line numbers must be integers or null if not applicable.
- Return ONLY the JSON object. No markdown code fences.
""".strip()


# ──────────────────────────────────────────────
# BUILD USER PROMPT
# ──────────────────────────────────────────────
def build_user_prompt(files_for_review: list) -> str:
    file_sections = []

    for file_data in files_for_review:
        content = file_data["content"]

        # Truncate very large files to stay within token limits
        if len(content) > MAX_FILE_CHARS:
            content = content[:MAX_FILE_CHARS] + "\n... [truncated]"

        file_sections.append(
            f"FILE: {file_data['file_name']}\n"
            f"PATH: {file_data['file_path']}\n"
            f"EXTENSION: {file_data['extension']}\n\n"
            f"SOURCE CODE:\n{content}"
        )

    separator = "\n\n" + "=" * 70 + "\n\n"
    files_block = separator.join(file_sections)

    return f"FILES TO REVIEW:\n\n{files_block}"


# ──────────────────────────────────────────────
# CALL GEMINI
# ──────────────────────────────────────────────
def review_all_files(processed_files: list, api_key: str, audit_type: str = "everything") -> dict:
    if not processed_files:
        raise ValueError("No processed files found for review.")

    # Limit files to avoid exceeding context window
    files_to_review = processed_files[:MAX_FILES]

    client = genai.Client(api_key=api_key)

    system_prompt = build_system_prompt(audit_type)
    user_prompt = build_user_prompt(files_to_review)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_prompt,
        config={
            "system_instruction": system_prompt,
            "temperature": 0.1,
        },
    )

    raw_text = response.text.strip()

    # Strip markdown code fences if model wrapped the JSON
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        raw_text = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        ).strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Gemini returned invalid JSON: {exc}\n\nRaw response:\n{raw_text}") from exc

    return result


# ──────────────────────────────────────────────
# SAVE RESULT TO DISK  (optional — kept for CLI use)
# ──────────────────────────────────────────────
def save_review_result(review_data: dict, output_path: str) -> dict:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=4, ensure_ascii=False)
    return review_data

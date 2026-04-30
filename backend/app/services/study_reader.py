import re
from pathlib import Path
from app.config import settings

SUBJECT_FILES = {
    "evolve": "evolveContent.js",
    "react": "reactContent.js",
    "python": "pythonContent.js",
}

SUBJECT_LABELS = {
    "evolve": "Evolve Interview Prep",
    "react": "React",
    "python": "Python",
}


def _read(subject: str) -> str:
    path = Path(settings.study_files_path) / SUBJECT_FILES[subject]
    return path.read_text(encoding="utf-8")


def get_subjects() -> list[dict]:
    return [{"id": k, "name": SUBJECT_LABELS[k]} for k in SUBJECT_FILES]


def get_categories(subject: str) -> list[dict]:
    if subject not in SUBJECT_FILES:
        return []
    content = _read(subject)
    matches = re.findall(
        r'sessionId:\s*["\`](\w+)["\`].{0,200}?categoryName:\s*["\`]([^"\`]+)["\`]',
        content,
        re.DOTALL,
    )
    return [{"id": sid, "name": name} for sid, name in matches]


def _get_session_block(content: str, session_id: str) -> str:
    start = re.search(rf'sessionId:\s*["\`]{re.escape(session_id)}["\`]', content)
    if not start:
        return ""
    after = content[start.start():]
    next_session = re.search(r'\n\s*\{\s*\n\s*sessionId:', after[20:])
    return after[: next_session.start() + 20] if next_session else after


def get_study_guide(subject: str, session_id: str) -> str:
    if subject not in SUBJECT_FILES:
        return ""
    content = _read(subject)

    cat_match = re.search(
        rf'sessionId:\s*["\`]{re.escape(session_id)}["\`].{{0,200}}?categoryName:\s*["\`]([^"\`]+)["\`]',
        content,
        re.DOTALL,
    )
    category_name = cat_match.group(1) if cat_match else session_id

    block = _get_session_block(content, session_id)
    if not block:
        return f"No content found for {subject}/{session_id}"

    col1_matches = list(re.finditer(r'col1:\s*["\`]([^"\`\n]+)["\`]', block))

    lines = [f"Category: {category_name}", "", "Topics and sub-topics:"]
    for i, match in enumerate(col1_matches):
        concept = match.group(1)
        start = match.end()
        end = col1_matches[i + 1].start() if i + 1 < len(col1_matches) else len(block)
        titles = re.findall(r'title:\s*["\`]([^"\`\n]+)["\`]', block[start:end])
        lines.append(f"\n{concept}")
        for t in titles:
            lines.append(f"  - {t}")

    return "\n".join(lines)

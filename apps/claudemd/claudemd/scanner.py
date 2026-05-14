"""Look at a directory and infer what kind of project it is.

We keep this lightweight on purpose: read a few well-known files, list
the top-level directory, and return a compact dict that the generator
hands to Claude as context.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

MAX_README_CHARS = 8_000
INTERESTING_FILES = [
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "Gemfile",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
    "Dockerfile",
    "docker-compose.yml",
    "Makefile",
    "tsconfig.json",
    "next.config.js",
    "next.config.ts",
    "vite.config.ts",
    "vite.config.js",
    "tailwind.config.js",
    ".eslintrc.json",
    ".prettierrc",
    "ruff.toml",
    "pytest.ini",
    "tox.ini",
    "README.md",
    "README",
    ".env.example",
    ".env.local.example",
]

LANG_EXT = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript (React)",
    ".js": "JavaScript",
    ".jsx": "JavaScript (React)",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".swift": "Swift",
    ".cpp": "C++",
    ".c": "C",
    ".sh": "Shell",
    ".sql": "SQL",
}

IGNORE_DIRS = {
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    "target",
    ".idea",
    ".vscode",
    "vendor",
    ".terraform",
}


def scan(root: Path) -> dict:
    root = root.resolve()

    found_files: dict[str, str] = {}
    for name in INTERESTING_FILES:
        p = root / name
        if p.exists() and p.is_file():
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                if name.startswith("README"):
                    content = content[:MAX_README_CHARS]
                else:
                    content = content[:4_000]
                found_files[name] = content
            except Exception:
                pass

    lang_counts: Counter = Counter()
    file_count = 0
    for path in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        file_count += 1
        if file_count > 5_000:
            break
        ext = path.suffix.lower()
        if ext in LANG_EXT:
            lang_counts[LANG_EXT[ext]] += 1

    languages = [
        {"language": lang, "files": count}
        for lang, count in lang_counts.most_common(8)
    ]

    top_level: list[str] = []
    try:
        for child in sorted(root.iterdir()):
            if child.name in IGNORE_DIRS or child.name.startswith("."):
                continue
            top_level.append(child.name + ("/" if child.is_dir() else ""))
    except Exception:
        pass

    project_name = root.name
    if "package.json" in found_files:
        try:
            pkg = json.loads(found_files["package.json"])
            project_name = pkg.get("name") or project_name
        except Exception:
            pass

    return {
        "project_name": project_name,
        "root_path": str(root),
        "top_level": top_level[:40],
        "languages": languages,
        "found_files": found_files,
        "total_files_scanned": file_count,
        "is_empty": file_count == 0 and not found_files,
    }

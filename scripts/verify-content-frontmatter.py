#!/usr/bin/env python3
"""
Проверка Markdown в content/: запрет ## title: и незакрытый YAML front matter (второй ---).
Запуск из корня репозитория: python3 scripts/verify-content-frontmatter.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

# Ошибка, из-за которой падал Hugo: markdown-заголовок вместо ключа YAML
BAD_TITLE_HEADING = re.compile(r"^\s*#+\s*title\s*:", re.MULTILINE)


def main() -> int:
    if not CONTENT.is_dir():
        print(f"ERROR: нет каталога {CONTENT}", file=sys.stderr)
        return 1

    errors: list[str] = []
    for path in sorted(CONTENT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)

        if BAD_TITLE_HEADING.search(text):
            errors.append(
                f"{rel}: найдено «## title:» или «# title:» — используйте в front matter только YAML-ключ title: без #"
            )

        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            continue

        end = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
        if end is None:
            errors.append(
                f"{rel}: front matter открыт «---», но нет закрывающего «---» (Hugo: EOF looking for end YAML front matter delimiter)"
            )

    if errors:
        print("Ошибки проверки front matter:\n", file=sys.stderr)
        for msg in errors:
            print(f"  - {msg}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

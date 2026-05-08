# Инструкция для агента (sergpo.tech)

Документ для ИИ-ассистента и людей: как правильно добавлять контент в Hugo и как убедиться, что деплой на GitHub Pages прошёл.

---

## 1. Заголовок Markdown-файла (YAML front matter)

### Правильный формат

Любая страница или пост в `content/` с метаданными **обязаны** начинаться так:

```yaml
---
title: "Заголовок страницы или поста"
date: 2026-05-08
draft: false
---
```

Дальше с новой строки идёт тело в Markdown/HTML.

Обязательно:

1. Первая строка файла — ровно `---` (открытие блока).
2. Поля — **YAML**, без префикса Markdown-заголовков: пишите `title:`, а не `## title:` и не `# title:`.
3. После полей — вторая строка `---` (закрытие блока). Без неё Hugo выдаст: `EOF looking for end YAML front matter delimiter`.
4. Тело документа — **после** второго `---`.

### Типичная ошибка (ломает CI)

Неправильно (так делать нельзя):

```yaml
---

## title: "я есть"
date: 2026-05-06
draft: false

Текст…
```

Здесь `## title:` воспринимается как Markdown, блок front matter не закрывается, сборка падает.

### Чеклист перед сохранением нового/изменённого `.md` в `content/`

1. Убедиться, что есть **два** разделителя `---` и между ними только YAML (ключ: значение), без `##` / `#` перед ключами.
2. Запустить проверку из корня репозитория:
  ```bash
   python3 scripts/verify-content-frontmatter.py
  ```
   Скрипт должен завершиться без вывода ошибок (exit code 0). Его же вызывает GitHub Actions перед `hugo build`.
3. Дополнительно (по желанию): `rg '^## title:' content/` — совпадений быть не должно.

---

## 2. Проверка деплоя после пуша в `main`

Пайплайн: **Deploy Hugo site to GitHub Pages** (файл `.github/workflows/hugo.yml`). После `git push origin main` не считать задачу выполненной, пока не подтверждён успешный прогон.

### Порядок действий для агента

1. Запомнить **полный SHA** последнего коммита после пуша, например `29e2b662883f27f9e96907185d654bd3fa23896e` (достаточно первых 7 символов для глаз, API отдаёт полный).
2. Подождать **30–90 секунд** (первый прогон обычно укладывается в эти рамки; при очереди раннера может быть дольше).
3. Запросить последние запуски workflow через GitHub API (публичный репозиторий, токен не обязателен, нужен заголовок `User-Agent`):
  ```text
   GET https://api.github.com/repos/shenwell/sergpo.tech/actions/runs?per_page=5
  ```
   Заголовок: `User-Agent: <любое осмысленное имя>` (без него API может отвечать 403).
4. В JSON взять первый элемент `workflow_runs[0]`, у которого:
  - `head_sha` совпадает с вашим коммитом (или с тем пушем, который проверяете);
  - `name` при желании сверить: `Deploy Hugo site to GitHub Pages`.
5. Интерпретация полей:
  - `status`: `queued` | `in_progress` | `completed`;
  - `conclusion`: пока `null`, пока не `completed`; при успехе — `success`, при ошибке — `failure` и т.д.
6. Если `status` ещё не `completed` — подождать **10–20 секунд** и повторить запрос того же `run` по URL из поля `workflow_runs[0].url` или снова списком `.../actions/runs?per_page=3`.
7. Сообщить пользователю итог: **успех** (`completed` + `conclusion: success`) или **провал** — дать ссылку `html_url` из объекта run на страницу логов в GitHub.

### Альтернатива: GitHub CLI

Если установлен `gh` и выполнен `gh auth login`:

```bash
gh run list --repo shenwell/sergpo.tech --workflow "Deploy Hugo site to GitHub Pages" --limit 3
gh run watch <RUN_ID> --repo shenwell/sergpo.tech --exit-status
```

### Ручная проверка

Открыть: [Actions репозитория](https://github.com/shenwell/sergpo.tech/actions).

---

## Кратко


| Шаг                     | Действие                                                             |
| ----------------------- | -------------------------------------------------------------------- |
| Перед коммитом контента | `python3 scripts/verify-content-frontmatter.py`                      |
| После пуша в `main`     | Подождать → API runs → `completed` + `success` по нужному `head_sha` |



# sergpo.tech

Статический сайт на [Hugo](https://gohugo.io/) и теме [hugo-blog-awesome](https://themes.gohugo.io/themes/hugo-blog-awesome/). Языки по умолчанию: русский (`/ru/…`), английский (`/en/…`).

## Локально

Требуется **Hugo Extended** той же версии, что в CI (**0.161.1**), и **Go** (для `hugo mod`).

```bash
hugo mod download
hugo server
```

Сборка:

```bash
hugo --gc --minify
```

Результат — каталог `public/`.

## GitHub Pages

1. Репозиторий → **Settings** → **Pages**: источник — **GitHub Actions**.
2. После первого деплоя при необходимости задайте **Custom domain**: `sergpo.tech`, включите **Enforce HTTPS**.
3. В DNS у регистратора для apex-домена следуйте [документации GitHub](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) (записи **A** для `185.199.108.0` … или **ALIAS/ANAME** у провайдера). Файл [`static/CNAME`](static/CNAME) уже содержит `sergpo.tech`.

## Структура контента

- `content/ru/` и `content/en/` — зеркальные пути: `write/`, `im.md`, `soul.md`, `memory.md`.
- Подписи в меню настраиваются в [`hugo.toml`](hugo.toml) (`[[languages.*.menu.main]]`).

## Модуль Hugo

Тема подключается как Go-модуль (`go.mod`). Обновление темы: изменить версию в `go.mod` и выполнить `hugo mod get` / `hugo mod tidy`.

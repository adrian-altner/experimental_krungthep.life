# Krung Thep Life

## Development

### Django
- Run server: `python manage.py runserver`
- Migrations: `python manage.py migrate`
- Tests: `python manage.py test`

### Frontend (Vite + Tailwind + htmx)
- Install deps: `pnpm install`
- Watch build (writes to `core/static/vite/`): `pnpm dev`
- Production build: `pnpm build`

Notes:
- New assets live in `frontend/src/` and are bundled to `core/static/vite/app.css` and `core/static/vite/app.js`.
- Existing static assets in `core/static/` remain unchanged.
- htmx is bundled via Vite; use `hx-*` attributes directly in templates.

## Linting

- djLint config lives in `.djlintrc.json`.

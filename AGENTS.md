# Repository Guidelines

## Project Structure & Module Organization
- `core/`: Django project config, settings, URLs, templates, and static assets.
- `home/`: Wagtail app with models, migrations, templates, static assets, and tests.
- `search/`: Search views and templates.
- `manage.py`: Django/Wagtail management entry point.
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Container build and runtime instructions.

## Build, Test, and Development Commands
- `python manage.py runserver`: Run the local development server on `http://127.0.0.1:8000/`.
- `python manage.py migrate`: Apply database migrations.
- `python manage.py makemigrations`: Create new migrations after model changes.
- `python manage.py test`: Run Django tests (currently located in `home/tests.py`).
- `python manage.py collectstatic`: Collect static assets into the configured static root.
- `docker build -t krungthep .` and `docker run -p 8000:8000 krungthep`: Build and run the containerized app.

## Coding Style & Naming Conventions
- Follow Django and Wagtail conventions for app layout and models.
- Use 4-space indentation in Python files.
- Keep template names descriptive and scoped (e.g., `home/templates/home/home_page.html`).
- No formatter or linter is configured in this repo; keep changes minimal and consistent with existing style.

## Testing Guidelines
- Tests are Django `TestCase` classes in `home/tests.py`.
- Prefer descriptive test method names (e.g., `test_homepage_renders`).
- Run tests with `python manage.py test` before submitting changes.

## Commit & Pull Request Guidelines
- No Git history is available in this workspace, so no commit message convention can be inferred.
- Use concise, imperative commit subjects (e.g., "Add welcome page CTA").
- PRs should describe the change, include steps to verify, and attach screenshots for template or CSS updates.

## Configuration Notes
- Environment-specific settings live in `core/settings/` (`base.py`, `dev.py`, `production.py`).
- The Docker image runs migrations and `gunicorn` at startup; use manual migrations in production deployments when possible.

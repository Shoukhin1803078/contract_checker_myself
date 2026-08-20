# Taste

## Tooling
- Uses uv as the Python package/dependency manager (`uv sync --frozen`, `uv run python manage.py ...`), with `pyproject.toml` + `uv.lock` rather than pip/poetry/requirements.txt. Confidence: 0.8
- Uses Docker Compose for local development, with a dev-specific compose file (`docker-compose.dev.yml`) and a thin `start.sh` wrapper that runs `docker compose ... up --build`. Confidence: 0.7
- Runs Django's dev server (`runserver 0.0.0.0:8000`) in Docker for local work. Confidence: 0.6

## Style / deliverables
- Prefers simple, minimal infra configs — explicitly asked for the Dockerfile, compose file, and start script to be written "simply" (no unnecessary services, env parsing, or layers). Confidence: 0.6

## Workflow
- Prefers to review and approve a written plan (plan mode) before files are created or edited. Confidence: 0.6

FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies from lockfile
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# Copy project source
COPY . .

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
# CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]


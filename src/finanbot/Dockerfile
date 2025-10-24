FROM python:3.13-slim

WORKDIR /usr/src/finanbot

# System build deps for packages like psycopg2
COPY pyproject.toml ./
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Generate requirements.txt from pyproject.toml using Python's tomllib (Python >= 3.11)
RUN python - << 'PY'
import pathlib, tomllib
p = pathlib.Path("pyproject.toml")
data = tomllib.loads(p.read_text(encoding="utf-8"))
deps = data.get("project", {}).get("dependencies", [])
# Write dependencies exactly as listed (preserves version specifiers)
with open("requirements.txt", "w", encoding="utf-8") as f:
    for dep in deps:
        f.write(dep.rstrip() + "\n")
print(f"Wrote requirements.txt ({len(deps)} entries)")
PY

# Install project dependencies with pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./src/finanbot ./src/finanbot
COPY ./ui ./ui
COPY ./src/finanbot/attachments ./attachments

ENV PYTHONUNBUFFERED=1

# Use package import path; ensure PYTHONPATH or installation matches how you run in dev/production
CMD ["uvicorn", "finanbot.main:app", "--host", "0.0.0.0", "--port", "8000"]

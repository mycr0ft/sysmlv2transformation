FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/workspace

WORKDIR /workspace

COPY pyproject.toml uv.lock /tmp/
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv \
    && uv export --directory /tmp --locked --no-dev --format requirements-txt \
         --output-file /tmp/requirements.txt \
    && uv pip install --system --no-cache -r /tmp/requirements.txt

COPY . /workspace

CMD ["python", "check_xmi_vehicle.py"]

FROM python:3.12-alpine AS base

RUN addgroup -g 1000 -S pygroup && adduser -u 1000 -S -G pygroup pyuser

RUN apk add --no-cache krb5

FROM base AS builder
WORKDIR /install

RUN apk add --no-cache gcc musl-dev krb5-dev curl

COPY pyproject.toml uv.lock ./
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN /root/.local/bin/uv sync --frozen --no-dev

FROM base
COPY --from=builder /install /usr/local
COPY demo /app
WORKDIR /app

USER pyuser:pygroup

ENV PATH="/usr/local/.venv/bin:${PATH}"
ENTRYPOINT ["python"]
CMD ["main.py"]

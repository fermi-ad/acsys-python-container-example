FROM python:3.12-alpine AS base

RUN apk add --no-cache krb5


FROM base AS builder
RUN mkdir /install
WORKDIR /install

RUN apk add --no-cache gcc musl-dev krb5-dev

COPY pyproject.toml pyproject.toml


FROM base
COPY --from=builder /install /usr/local
COPY demo /app
WORKDIR /app
ENV PYTHONPATH "/usr/local"
ENTRYPOINT ["python3"]
CMD ["/app/main.py"]

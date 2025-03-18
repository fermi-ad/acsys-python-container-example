FROM python:3.12-alpine AS base

RUN addgroup -g 1000 -S pygroup && adduser -u 1000 -S -G pygroup pyuser

RUN apk add --no-cache krb5


FROM base AS builder
RUN mkdir /install
WORKDIR /install

RUN apk add --no-cache gcc musl-dev krb5-dev

COPY pyproject.toml pyproject.toml
RUN pip install --no-cache-dir --target=/install .


FROM base
COPY --from=builder /install /usr/local
COPY demo /app
WORKDIR /app

USER pyuser:pygroup

ENTRYPOINT ["python3"]
CMD ["/app/main.py"]

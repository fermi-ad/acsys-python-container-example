FROM python:3.12-alpine as base

RUN apk add krb5-dev

FROM base as builder
RUN mkdir /install
WORKDIR /install

RUN apk add gcc musl-dev

COPY pyproject.toml pyproject.toml
RUN pip install --target=/install .

FROM base
COPY --from=builder /install /usr/local
COPY demo /app
WORKDIR /app
ENV PYTHONPATH "/usr/local"
CMD ["python3", "/app/main.py"]
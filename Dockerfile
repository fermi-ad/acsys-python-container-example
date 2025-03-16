FROM python:3.12-alpine AS builder

RUN apk add krb5-dev gcc musl-dev && mkdir -p /install

WORKDIR /install
COPY pyproject.toml pyproject.toml
RUN pip install --target=/install .

FROM builder
COPY --from=builder /install /usr/local
COPY demo /app
WORKDIR /app
ENV PYTHONPATH "/usr/local"
ENTRYPOINT ["python3"]
CMD ["/app/main.py"]

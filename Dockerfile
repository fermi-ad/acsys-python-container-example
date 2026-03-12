FROM registry.access.redhat.com/ubi9/python-312 AS base

USER root

RUN dnf install -y krb5-libs shadow-utils && dnf clean all
RUN groupadd -g 1000 pygroup && useradd -m -u 1000 -g pygroup pyuser

FROM base AS builder
WORKDIR /install

RUN dnf install -y gcc gcc-c++ make krb5-devel && dnf clean all

COPY pyproject.toml uv.lock ./
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN uv sync --frozen --no-dev

FROM base
COPY --from=builder /install /usr/local
COPY demo /app
WORKDIR /app

USER pyuser:pygroup

ENV PATH="/usr/local/.venv/bin:${PATH}"
ENTRYPOINT ["python"]
CMD ["main.py"]

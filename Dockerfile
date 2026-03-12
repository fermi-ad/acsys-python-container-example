FROM almalinux/9-base AS base

USER root

RUN dnf install -y \
      'dnf-command(config-manager)' \
 && dnf config-manager --set-enabled crb \
 && dnf install -y epel-release \
 && curl -L -o /etc/yum.repos.d/xpra.repo \
      https://raw.githubusercontent.com/Xpra-org/xpra/master/packaging/repos/almalinux/xpra.repo \
 && dnf makecache \
 && dnf install -y xpra \
 && dnf clean all

RUN dnf install -y krb5-libs shadow-utils python3.12 python3.12-devel && dnf clean all
RUN groupadd -g 1000 pygroup && useradd -m -u 1000 -g pygroup pyuser

FROM base AS builder
WORKDIR /install

RUN dnf install -y gcc gcc-c++ make krb5-devel && dnf clean all

COPY pyproject.toml uv.lock ./
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"
RUN uv sync --frozen --no-dev

FROM base
COPY --from=builder /install /usr/local
COPY demo /app
WORKDIR /app

USER pyuser:pygroup

ENV PATH="/usr/local/.venv/bin:${PATH}"
ENTRYPOINT ["python"]
CMD ["main.py"]

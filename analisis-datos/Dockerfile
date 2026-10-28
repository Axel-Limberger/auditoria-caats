FROM ghcr.io/astral-sh/uv:0.13.1-python3.12-trixie-slim

# el entorno virtual vive fuera de /work para que el volumen con los notebooks no lo oculte
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH=/opt/venv/bin:$PATH \
    HOME=/tmp

WORKDIR /work
COPY pyproject.toml uv.lock /work/
RUN uv sync --frozen --no-install-project

EXPOSE 8888
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", \
     "--IdentityProvider.token=", "--ServerApp.root_dir=/work"]

FROM archlinux:latest

# Update pacman keyring and system packages
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm \
    base-devel \
    python \
    python-pip \
    python-numpy \
    sqlite \
    nodejs \
    npm \
    tesseract \
    tesseract-data-eng \
    clang \
    git

# Install required Python packages for deep learning and verification
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    neo4j \
    pip-audit \
    requests \
    tesseract \
    pybind11

# Set workspace directory
WORKDIR /workspace
CMD ["tail", "-f", "/dev/null"]

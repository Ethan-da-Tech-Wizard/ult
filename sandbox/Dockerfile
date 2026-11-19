# How this file fits the app: defines the image "zeus-arch:latest" (built by setup/build_sandbox.sh or
# setup/install_all.py) in which chapter validators run. server/sandbox_manager.py starts one long-lived
# container from it, bind-mounting the player's files at /workspace and the validators at /sandbox.
# Rolling-release Arch Linux is used on purpose so toolchains (clang, tesseract, node) are current, at the
# price that rebuilds are not reproducible (no pinned versions and `:latest` base).
FROM archlinux:latest

# One RUN layer for update + install so the package cache is not baked into separate layers. Packages by
# purpose: base-devel/clang/git (compile native extensions for chapter 5), python/numpy/sqlite/nodejs
# (runtimes the chapters import), tesseract + English data (chapter 1 OCR).
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

# Python tools are installed in a virtual environment placed first on PATH, so `python` and `pip` inside
# the container refer to it.
# Install required Python packages for deep learning and verification.
# The venv does not see pacman's site-packages, so numpy must be installed
# here too — chapters 8, 9, 14, and 16 validators import it.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Libraries imported by the chapters: fastapi/uvicorn/pydantic (API chapters), numpy (chapters 8, 9, 14,
# 16), neo4j (graph chapter), pip-audit (dependency-audit chapter), requests, pytesseract (OCR) and
# pybind11 (C++ bridge chapter). --no-cache-dir keeps the image smaller.
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pydantic \
    numpy \
    neo4j \
    pip-audit \
    requests \
    pytesseract \
    pybind11

# /workspace is the mount point of save_data/relic_save; the idle `tail -f /dev/null` command keeps the
# container alive so `docker exec` can run validators quickly (sandbox_manager.py overrides nothing else).
# Set workspace directory
WORKDIR /workspace
CMD ["tail", "-f", "/dev/null"]

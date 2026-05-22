FROM python:3.10-slim

# Install system dependencies (LaTeX for PDF compilation, pandoc for markdown conversion)
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    pandoc \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install jupyterlab and package dependencies
RUN pip install --no-cache-dir jupyterlab && \
    pip install --no-cache-dir -e .[all]

# Default entry point for the OS CLI
ENTRYPOINT ["research-os"]
CMD ["--help"]

FROM python:3.10-slim

# Install system dependencies (LaTeX for PDF compilation, pandoc for markdown conversion, Node.js for mmdc)
RUN apt-get update && apt-get install -y \
    curl \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    pandoc \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and mermaid-cli for workflow diagram rendering
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @mermaid-js/mermaid-cli && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY pyproject.toml requirements.txt README.md ./
COPY src/ ./src/

# Install common research libraries and package dependencies
RUN pip install --no-cache-dir \
    numpy scipy pandas matplotlib seaborn scikit-learn jupyterlab && \
    pip install --no-cache-dir -e .[all]

# Default entry point for the OS CLI
ENTRYPOINT ["research-os"]
CMD ["--help"]

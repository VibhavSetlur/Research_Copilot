FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    texlive-latex-extra \
    texlive-pictures \
    texlive-science \
    && rm -rf /var/lib/apt/lists/*

# Install Research OS
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Research OS package
COPY . .
RUN pip install -e .

CMD ["python", "-m", "research_os.server"]

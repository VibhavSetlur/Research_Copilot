# Containerization & Air-Gapped Environments

Research-OS provides full Docker and Docker Compose support out of the box, allowing you to run the OS and a Jupyter workspace entirely within a reproducible container. This is especially useful for air-gapped environments or secure server deployments.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Running via Docker Compose

The simplest way to use Research-OS in an isolated environment is via `docker-compose`.

1. **Build the images:**
   ```bash
   docker-compose build
   ```

2. **Start the Jupyter Server:**
   ```bash
   docker-compose up -d jupyter
   ```
   Navigate to `http://localhost:8888` in your browser. You will have full access to your workspace, inputs, and synthesis outputs.

3. **Run the CLI commands:**
   You can run any Research-OS CLI command using the `research-os` service:
   ```bash
   docker-compose run --rm research-os init /app
   docker-compose run --rm research-os doctor
   docker-compose run --rm research-os env freeze 01_baseline
   docker-compose run --rm research-os env restore 01_baseline
   ```

## GPU Support

If your host machine has Nvidia GPUs and the NVIDIA Container Toolkit installed, you can enable GPU access. Open `docker-compose.yml` and uncomment the `deploy` sections under both services:

```yaml
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## Reproducible Step Environments

Research-OS supports freezing and restoring Python environments on a per-step basis. This is crucial for reproducibility.

- **Freeze**: Run `ros env freeze <step>` to save the current environment dependencies to `workspace/<step>/environment/requirements.txt`.
- **Restore**: Run `ros env restore <step>` to `pip install` those dependencies in your active environment.

When running via Docker, these environments will be bound to your volume, meaning you can easily share your experiment folder and allow others to recreate your exact container environment.

# Contributing to Agentic Research OS

Thank you for your interest in improving Agentic Research OS! This guide will help you get started with contributing.

## How to Contribute

1. **Fork the Repository**: Create a fork of this repository to your own GitHub account.
2. **Clone your Fork**: Clone the repository to your local machine.
3. **Create a Branch**: Create a new branch for your feature or bugfix (`git checkout -b feature/your-feature-name`).
4. **Make Changes**: Implement your changes. Ensure you adhere to the code style and formatting guidelines.
5. **Run Tests**: Ensure all existing and new tests pass by running `pytest`.
6. **Commit Changes**: Commit your changes with descriptive messages (`git commit -m "Add new feature"`).
7. **Push to Fork**: Push your branch to your forked repository (`git push origin feature/your-feature-name`).
8. **Submit a Pull Request**: Open a pull request from your fork's branch to the main repository.

## Development Setup

We recommend using `uv` or `poetry` for dependency management. To set up the environment:

```bash
pip install -e .[dev,all]
```

## Code Style and Formatting

We enforce strict code formatting using `ruff` and type checking using `mypy`.

Before committing, run:
```bash
ruff check .
ruff format .
mypy src/research_copilot/
```

## Writing Tests

We use `pytest` for testing. Place your tests in the `tests/` directory. If your code calls the LLM, use `pytest-mock` or `responses` to mock the API responses so tests run quickly and don't cost tokens.

## Bug Reports and Feature Requests

Please use the provided GitHub Issue templates to report bugs or request features. Ensure you provide as much detail as possible to help us understand and resolve the issue quickly.

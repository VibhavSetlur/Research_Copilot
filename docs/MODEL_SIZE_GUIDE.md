# Model Size Guide

Research OS can be run with various LLM models depending on your compute and context window constraints. The `researcher_config.yaml` file allows you to set a `model_profile` to optimize the workspace.

---

## Model Profiles

### `small`
- **Examples**: Claude 3.5 Haiku, GPT-4o-mini, Llama 3 (8B)
- **Token Budget**: Optimized for smaller context windows (<32k).
- **Protocols**: Always uses `light` variants in the `protocols/light/` directory. These have shorter instructions and fewer required checks.
- **Tools**: Limits responses using `sys.state.minimal_context` which truncates long logs to ~500 tokens.
- **Best For**: Quick, simple analytical tasks, rapid data extraction, or operating under strict API constraints.

### `medium`
- **Examples**: GPT-4o, Claude 3.5 Sonnet, Llama 3 (70B)
- **Token Budget**: Balanced (up to ~100k context window).
- **Protocols**: Uses full standard protocols by default.
- **Tools**: Standard logging and output verbosity.
- **Best For**: The default research setting. Excellent balance of cost, speed, and analytical rigor.

### `large`
- **Examples**: Claude 3 Opus, specialized enormous context models
- **Token Budget**: Large (>128k context window).
- **Protocols**: Uses full standard protocols and can handle multiple protocol contexts simultaneously.
- **Tools**: Capable of reading much larger file chunks (`sys.file.read` allows up to 50MB) and keeping entire detailed `analysis.md` histories in context without truncation.
- **Best For**: Massive systematic literature reviews, very deep codebase refactoring, and multi-disciplinary synthesis.

## Configuration

To switch profiles, modify `inputs/researcher_config.yaml`:

```yaml
# inputs/researcher_config.yaml
project_name: "My Project"
model_profile: "medium"  # 'small', 'medium', or 'large'
```

Alternatively, you can configure the IDE or MCP client to pass the desired profile through to the `sys.config.set` endpoint.

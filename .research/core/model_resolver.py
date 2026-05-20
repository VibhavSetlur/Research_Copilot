#!/usr/bin/env python3
"""Multi-Agent LLM Model Resolver with graceful degradation.

Reads models.yaml and resolves which model to use for each task based on
available API keys. If a required key is missing, falls back to the best
available model with a visible warning.

Usage:
    from model_resolver import resolve_model, get_available_models
    
    # Get the model config for a specific task
    model = resolve_model("literature_deep")
    
    # Check what models are available
    available = get_available_models()
"""

import os
import warnings
from pathlib import Path
from typing import Optional

from core.utils import load_yaml


_MODELS_YAML = Path(__file__).parent / "models.yaml"
_RESOLVED_CACHE = {}
_WARNINGS_SHOWN = set()


def _load_models_config() -> dict:
    """Load the models.yaml configuration."""
    if not _MODELS_YAML.exists():
        return {"models": {}, "fallback": {}}
    return load_yaml(_MODELS_YAML)


def _check_api_key(env_var: str) -> bool:
    """Check if an API key environment variable is set."""
    return bool(os.environ.get(env_var))


def resolve_model(task_name: str, config: Optional[dict] = None) -> dict:
    """Resolve which model to use for a given task.
    
    Args:
        task_name: The task/agent name (e.g., 'literature_deep', 'orchestrator')
        config: Optional pre-loaded models config
        
    Returns:
        Dict with resolved model configuration including actual provider/model to use.
    """
    if config is None:
        config = _load_models_config()
    
    cache_key = task_name
    if cache_key in _RESOLVED_CACHE:
        return _RESOLVED_CACHE[cache_key]
    
    models = config.get("models", {})
    fallback = config.get("fallback", {})
    
    task_config = models.get(task_name)
    if not task_config:
        # Task not in models.yaml, use fallback
        return _resolve_with_fallback(fallback, f"Task '{task_name}' not in models.yaml")
    
    api_key_env = task_config.get("api_key_env", "")
    if _check_api_key(api_key_env):
        # Primary model is available
        resolved = {**task_config, "_fallback_used": False, "_original_task": task_name}
        _RESOLVED_CACHE[cache_key] = resolved
        return resolved
    
    # Primary model unavailable — find best fallback
    warning_msg = (
        f"Model fallback: {task_name} requires {api_key_env} (not set). "
        f"Falling back from {task_config.get('provider')}/{task_config.get('model')}."
    )
    
    resolved = _resolve_with_fallback(fallback, warning_msg, task_config)
    _RESOLVED_CACHE[cache_key] = resolved
    return resolved


def _resolve_with_fallback(fallback: dict, warning_msg: str, original_config: Optional[dict] = None) -> dict:
    """Resolve to the best available fallback model."""
    if warning_msg not in _WARNINGS_SHOWN:
        warnings.warn(warning_msg, stacklevel=3)
        _WARNINGS_SHOWN.add(warning_msg)
    
    # Check if fallback itself is available
    fallback_key = fallback.get("api_key_env", "")
    if _check_api_key(fallback_key):
        return {
            **fallback,
            "_fallback_used": True,
            "_fallback_from": original_config.get("model", "unknown") if original_config else "unknown",
            "_warning": warning_msg,
        }
    
    # Try to find ANY available model
    available = _find_any_available_model()
    if available:
        return {
            **available,
            "_fallback_used": True,
            "_fallback_from": original_config.get("model", "unknown") if original_config else "unknown",
            "_warning": f"Multiple fallbacks: {warning_msg}",
        }
    
    # No models available
    return {
        **fallback,
        "_fallback_used": True,
        "_fallback_from": original_config.get("model", "unknown") if original_config else "unknown",
        "_warning": f"CRITICAL: No API keys available. {warning_msg}",
        "_no_keys_available": True,
    }


def _find_any_available_model() -> Optional[dict]:
    """Find any model whose API key is available, preferring high-context models."""
    config = _load_models_config()
    models = config.get("models", {})
    
    # Priority order: high context first
    priority = sorted(
        models.values(),
        key=lambda m: m.get("context_window", 0),
        reverse=True,
    )
    
    for model in priority:
        if _check_api_key(model.get("api_key_env", "")):
            return model
    
    # Check fallback
    fallback = config.get("fallback", {})
    if _check_api_key(fallback.get("api_key_env", "")):
        return fallback
    
    return None


def get_available_models(config: Optional[dict] = None) -> dict:
    """Get a summary of which models are available based on API keys.
    
    Returns:
        Dict with available/unavailable model lists and warnings.
    """
    if config is None:
        config = _load_models_config()
    
    models = config.get("models", {})
    fallback = config.get("fallback", {})
    
    available = []
    unavailable = []
    
    for name, model_config in models.items():
        key_env = model_config.get("api_key_env", "")
        if _check_api_key(key_env):
            available.append({
                "name": name,
                "provider": model_config.get("provider"),
                "model": model_config.get("model"),
                "context_window": model_config.get("context_window"),
            })
        else:
            unavailable.append({
                "name": name,
                "provider": model_config.get("provider"),
                "model": model_config.get("model"),
                "missing_key": key_env,
            })
    
    fallback_available = _check_api_key(fallback.get("api_key_env", ""))
    
    return {
        "available": available,
        "unavailable": unavailable,
        "fallback_available": fallback_available,
        "fallback_model": fallback.get("model"),
        "total_available": len(available),
        "total_unavailable": len(unavailable),
    }


def print_availability_report(config: Optional[dict] = None) -> str:
    """Generate a human-readable availability report."""
    report = get_available_models(config)
    
    lines = [
        "=" * 60,
        "LLM MODEL AVAILABILITY",
        "=" * 60,
        "",
        f"Available: {report['total_available']}",
        f"Unavailable: {report['total_unavailable']}",
        f"Fallback ({report['fallback_model']}): {'OK' if report['fallback_available'] else 'MISSING KEY'}",
        "",
    ]
    
    if report["available"]:
        lines.append("Available models:")
        for m in report["available"]:
            lines.append(f"  ✓ {m['name']}: {m['provider']}/{m['model']} (context: {m['context_window']:,})")
        lines.append("")
    
    if report["unavailable"]:
        lines.append("Unavailable (will use fallback):")
        for m in report["unavailable"]:
            lines.append(f"  ✗ {m['name']}: {m['provider']}/{m['model']} (missing: {m['missing_key']})")
        lines.append("")
    
    if not report["available"] and not report["fallback_available"]:
        lines.append("WARNING: No API keys detected. Set at least one of:")
        lines.append("  - OPENAI_API_KEY")
        lines.append("  - ANTHROPIC_API_KEY")
        lines.append("  - GOOGLE_API_KEY")
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    print(print_availability_report())

import json
import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger("research.schemas.validator")

T = TypeVar("T", bound=BaseModel)


def validate_with_retry(
    raw_json: str,
    schema: Type[T],
    call_llm: Callable[[str], str],
    base_prompt: str,
    max_retries: int = 3,
    node_id: Optional[str] = None,
) -> T:
    """Validate JSON string against a Pydantic schema, automatically retrying on failure.

    Args:
        raw_json: Initial JSON string to parse.
        schema: Pydantic model class.
        call_llm: Function taking a prompt string and returning a response string.
        base_prompt: The original prompt used to generate the output.
        max_retries: Number of correction attempts.
        node_id: Optional ID for logging context.

    Returns:
        An instance of the schema model.

    Raises:
        ValidationError: If validation fails after all retries.
    """
    prefix = f"[{node_id}] " if node_id else ""
    current_payload = raw_json

    for attempt in range(max_retries + 1):
        try:
            # Strip markdown code blocks if present
            cleaned = current_payload.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            instance = schema.model_validate(parsed)
            return instance

        except (json.JSONDecodeError, ValidationError) as e:
            if attempt == max_retries:
                logger.error(f"{prefix}Validation failed permanently after {max_retries} retries: {e}")
                raise e

            logger.warning(f"{prefix}Validation failed (attempt {attempt + 1}/{max_retries}): {e}. Triggering auto-recovery.")

            # Construct recovery prompt
            recovery_prompt = (
                f"{base_prompt}\n\n"
                "--------------------------------------------------\n"
                "SYSTEM RECOVERY INSTRUCTION:\n"
                "Your previous response failed schema validation.\n"
                f"Error details:\n{str(e)}\n\n"
                f"Previous output:\n{current_payload}\n\n"
                "Please correct the errors and output ONLY valid JSON matching the requested schema. "
                "Do not include markdown formatting or explanations."
            )

            try:
                current_payload = call_llm(recovery_prompt)
            except Exception as llm_err:
                logger.error(f"{prefix}LLM call failed during recovery: {llm_err}")
                raise llm_err

    # Fallback to satisfy typing, though the loop will raise or return before here
    raise ValidationError.from_exception_data(title="ValidationFailed", line_errors=[])

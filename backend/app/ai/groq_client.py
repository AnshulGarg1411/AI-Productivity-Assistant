import os
import json
import time
import logging

from groq import Groq


logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Groq Client
# ---------------------------------------------------------

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

TEXT_MAX_TOKENS = int(
    os.getenv(
        "GROQ_TEXT_MAX_TOKENS",
        "700"
    )
)

JSON_MAX_TOKENS = int(
    os.getenv(
        "GROQ_JSON_MAX_TOKENS",
        "500"
    )
)


# ---------------------------------------------------------
# Generate Normal Text
# ---------------------------------------------------------

def generate_text(
    prompt: str,
    system_instruction: str = "",
    temperature: float = 0.2
):
    """
    Generate a normal text response using Groq.
    """

    messages = []

    if system_instruction:
        messages.append({
            "role": "system",
            "content": system_instruction
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    for attempt in range(2):

        try:

            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=TEXT_MAX_TOKENS
            )

            content = response.choices[0].message.content

            if not content:
                logger.error(
                    "Groq returned empty text response"
                )
                return None

            return content

        except Exception as exc:

            logger.exception(
                "Groq generate_text failed: %s",
                exc
            )

            # Retry once for temporary failures
            if attempt == 0:
                time.sleep(2)
                continue

            return None

    return None


# ---------------------------------------------------------
# Generate JSON
# ---------------------------------------------------------

def generate_json(
    prompt: str,
    response_schema=None,
    system_instruction: str = "",
    temperature: float = 0.1
):
    """
    Generate a JSON response using Groq.

    response_schema is used as a prompt-level description
    instead of Groq strict JSON schema mode.

    This avoids strict-schema validation errors while
    keeping compatibility with the existing project.
    """

    messages = []

    # -----------------------------------------------------
    # System message
    # -----------------------------------------------------

    if system_instruction:

        messages.append({
            "role": "system",
            "content": system_instruction
        })

    # -----------------------------------------------------
    # Schema instruction
    # -----------------------------------------------------

    schema_instruction = ""

    if response_schema:

        try:

            schema_text = json.dumps(
                response_schema,
                indent=2
            )

        except Exception:

            schema_text = str(
                response_schema
            )

        schema_instruction = f"""

IMPORTANT:
Return ONLY valid JSON.

Do NOT return:
- Markdown
- ```json
- explanations
- comments
- text before the JSON
- text after the JSON

The expected JSON structure is:

{schema_text}

Make sure the response is valid JSON.
"""

    else:

        schema_instruction = """

IMPORTANT:
Return ONLY valid JSON.

Do NOT return:
- Markdown
- ```json
- explanations
- comments
- text before the JSON
- text after the JSON
"""

    # -----------------------------------------------------
    # User message
    # -----------------------------------------------------

    messages.append({
        "role": "user",
        "content": (
            prompt
            + "\n\n"
            + schema_instruction
        )
    })

    # -----------------------------------------------------
    # API request
    # -----------------------------------------------------

    for attempt in range(2):

        try:

            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=JSON_MAX_TOKENS,

                # IMPORTANT:
                # Use JSON OBJECT mode instead of strict
                # JSON schema mode.
                response_format={
                    "type": "json_object"
                }
            )

            content = (
                response
                .choices[0]
                .message
                .content
            )

            if not content:

                logger.error(
                    "Groq returned empty JSON response"
                )

                return None

            # -------------------------------------------------
            # Remove accidental markdown fences
            # -------------------------------------------------

            content = content.strip()

            if content.startswith("```json"):

                content = content[
                    len("```json"):
                ]

                if content.endswith("```"):
                    content = content[:-3]

                content = content.strip()

            elif content.startswith("```"):

                content = content[3:]

                if content.endswith("```"):
                    content = content[:-3]

                content = content.strip()

            # -------------------------------------------------
            # Parse JSON
            # -------------------------------------------------

            try:

                result = json.loads(
                    content
                )

                return result

            except json.JSONDecodeError as json_error:

                logger.error(
                    "Groq returned invalid JSON: %s",
                    json_error
                )

                logger.error(
                    "Raw response: %s",
                    content
                )

                # Retry once
                if attempt == 0:

                    time.sleep(2)

                    continue

                return None

        except Exception as exc:

            logger.exception(
                "Groq generate_json failed: %s",
                exc
            )

            # Retry once
            if attempt == 0:

                time.sleep(2)

                continue

            return None

    return None
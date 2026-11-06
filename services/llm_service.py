
import os
import requests

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


# ==========================================
# LLM CONFIGURATION
# ==========================================

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

# Local Ollama settings
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:3b"
)

# Cloud Groq settings
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


# ==========================================
# LOCAL OLLAMA RESPONSE
# ==========================================

def generate_ollama_answer(prompt, temperature=0.3):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        },
        timeout=180
    )

    response.raise_for_status()

    result = response.json()

    return result.get("response", "").strip()


# ==========================================
# CLOUD GROQ RESPONSE
# ==========================================

def generate_groq_answer(prompt, temperature=0.3):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    response = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_completion_tokens": 2048
        },
        timeout=120
    )

    response.raise_for_status()

    result = response.json()

    return result["choices"][0]["message"]["content"].strip()


# ==========================================
# MAIN ANSWER GENERATOR
# ==========================================

def generate_answer(prompt, temperature=0.3):

    if not isinstance(prompt, str) or not prompt.strip():
        return "Error: Prompt cannot be empty."

    try:

        if LLM_PROVIDER == "ollama":

            return generate_ollama_answer(
                prompt,
                temperature
            )

        elif LLM_PROVIDER == "groq":

            return generate_groq_answer(
                prompt,
                temperature
            )

        else:

            return f"Error: Unsupported LLM provider: {LLM_PROVIDER}"

    except requests.exceptions.Timeout:

        return "Error: AI response timed out."

    except requests.exceptions.ConnectionError:

        return "Error: Unable to connect to the AI service."

    except requests.exceptions.HTTPError as error:

        status_code = error.response.status_code

        if status_code == 401:
            return "Error: AI API authentication failed."

        elif status_code == 429:
            return "Error: AI rate limit reached. Please try again later."

        return f"Error: AI service returned status {status_code}."

    except ValueError as error:

        return f"Error: {str(error)}"

    except (KeyError, IndexError):

        return "Error: Invalid response received from AI service."

    except requests.exceptions.RequestException:

        return "Error: AI request failed."

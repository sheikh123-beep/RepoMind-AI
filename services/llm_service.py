import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"


def generate_answer(prompt, temperature=0.3):

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
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

    except requests.exceptions.ConnectionError:
        return "Error: Ollama server is not running."

    except requests.exceptions.Timeout:
        return "Error: AI response timed out."

    except requests.exceptions.RequestException as error:
        return f"Error generating AI response: {str(error)}"
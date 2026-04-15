import httpx
from openai import OpenAI

from api.app.core.config import settings


SYSTEM_PROMPT = (
    'You are a deal-closing assistant for service arbitrage. '
    'Write a concise, human message offering help with clear next steps and a price anchor.'
)


def generate_reply(lead_text: str) -> str:
    if settings.ai_provider.lower() == 'ollama':
        return _generate_ollama(lead_text)
    return _generate_openai(lead_text)


def _generate_openai(lead_text: str) -> str:
    if not settings.openai_api_key:
        raise RuntimeError('OPENAI_API_KEY is required when AI_PROVIDER=openai')

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': f'Lead: {lead_text}'},
        ],
    )
    return response.output_text.strip()


def _generate_ollama(lead_text: str) -> str:
    payload = {
        'model': settings.ollama_model,
        'prompt': f'{SYSTEM_PROMPT}\n\nLead: {lead_text}',
        'stream': False,
    }
    with httpx.Client(timeout=40.0) as client:
        r = client.post(f'{settings.ollama_url}/api/generate', json=payload)
        r.raise_for_status()
        data = r.json()
    return data.get('response', '').strip()

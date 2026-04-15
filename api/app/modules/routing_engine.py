import httpx

from api.app.core.config import settings


PLAYBOOKS: dict[str, dict] = {
    'quick_copywriting': {
        'trigger': ['copywriter', 'cold email', 'sales email'],
        'task_type': 'copywriting',
        'price_rule': 'quote = supplier_cost * 1.8',
        'supplier': 'upwork_saved_freelancer_copy_1',
        'execution_steps': [
            'Collect requirements',
            'Send to supplier template',
            'Deliver first draft in <6h',
        ],
        'kill_conditions': ['buyer no response >24h', 'scope expands >2 revisions'],
    },
    'quick_design': {
        'trigger': ['logo', 'thumbnail', 'one-pager'],
        'task_type': 'design',
        'price_rule': 'quote = supplier_cost * 2.0',
        'supplier': 'fiverr_saved_gig_designer_1',
        'execution_steps': ['Confirm style', 'Place order', 'QA before delivery'],
        'kill_conditions': ['buyer requests full branding package'],
    },
}


def choose_playbook(text: str) -> tuple[str, dict] | tuple[None, None]:
    lower = text.lower()
    for key, pb in PLAYBOOKS.items():
        if any(trigger in lower for trigger in pb['trigger']):
            return key, pb
    return None, None


def route_to_telegram(message: str) -> bool:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return False

    url = f'https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage'
    payload = {'chat_id': settings.telegram_chat_id, 'text': message}
    with httpx.Client(timeout=10.0) as client:
        response = client.post(url, json=payload)
        return response.status_code == 200

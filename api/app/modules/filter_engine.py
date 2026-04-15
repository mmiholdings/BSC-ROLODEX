from api.app.modules.signal_engine import RawSignal

KEYWORDS_SIMPLE = {
    'logo', 'landing page', 'fix bug', 'edit video', 'cold email', 'list building', 'scrape', 'automation',
}


def is_simple_task(text: str) -> bool:
    lower = text.lower()
    return any(k in lower for k in KEYWORDS_SIMPLE)


def qualifies(signal: RawSignal) -> bool:
    text = f'{signal.title} {signal.body}'.lower()
    if not signal.url or not signal.title:
        return False
    if 'unpaid' in text or 'volunteer' in text:
        return False
    return is_simple_task(text)

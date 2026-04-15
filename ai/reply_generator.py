from api.app.modules.response_engine import generate_reply


def build_reply(text: str) -> str:
    return generate_reply(text)

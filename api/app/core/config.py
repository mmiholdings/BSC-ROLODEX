from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_env: str = Field(default='dev', alias='APP_ENV')
    api_host: str = Field(default='0.0.0.0', alias='API_HOST')
    api_port: int = Field(default=8000, alias='API_PORT')

    database_url: str = Field(default='postgresql+psycopg2://moore:moore@localhost:5432/moore_money', alias='DATABASE_URL')
    redis_url: str = Field(default='redis://redis:6379/0', alias='REDIS_URL')

    openai_api_key: str | None = Field(default=None, alias='OPENAI_API_KEY')
    openai_model: str = Field(default='gpt-4.1-mini', alias='OPENAI_MODEL')
    ollama_url: str = Field(default='http://ollama:11434', alias='OLLAMA_URL')
    ollama_model: str = Field(default='llama3.1:8b', alias='OLLAMA_MODEL')
    ai_provider: str = Field(default='openai', alias='AI_PROVIDER')

    telegram_bot_token: str | None = Field(default=None, alias='TELEGRAM_BOT_TOKEN')
    telegram_chat_id: str | None = Field(default=None, alias='TELEGRAM_CHAT_ID')

    gmail_client_id: str | None = Field(default=None, alias='GMAIL_CLIENT_ID')
    gmail_client_secret: str | None = Field(default=None, alias='GMAIL_CLIENT_SECRET')
    gmail_refresh_token: str | None = Field(default=None, alias='GMAIL_REFRESH_TOKEN')

    min_score_threshold: float = Field(default=40.0, alias='MIN_SCORE_THRESHOLD')

    # Real public demand sources.
    rsshub_urls: str = Field(
        default='https://rsshub.app/reddit/r/forhire,https://rsshub.app/reddit/r/slavelabour',
        alias='RSSHUB_URLS',
    )
    hackernews_max_items_url: str = Field(
        default='https://hacker-news.firebaseio.com/v0/maxitem.json',
        alias='HN_MAX_ITEM_URL',
    )


settings = Settings()

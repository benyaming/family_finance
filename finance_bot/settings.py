from typing import List

from pydantic import BaseSettings, Field


class Env(BaseSettings):
    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'

    BOT_TOKEN: str = Field(..., env='BOT_TOKEN')
    DB_DSN: str = Field(..., env='DB_DSN')
    ADMITTED_USERS: List[int] = Field(..., env='ADMITTED_USERS')

    AMOUNT_PRECISION: int = Field(10_000, env='AMOUNT_PRECISION')
    CATEGORY_SUGGESTION_AMOUNT: int = Field(5, env='CATEGORY_SUGGESTION_AMOUNT')

    CURRENCY_CHAR: str = Field(..., env='CURRENCY_CHAR')

    IS_REMINDER_ENABLED: bool = Field(True, env='IS_REMINDER_ENABLED')
    REMINDER_HOUR: int = Field(21, env='REMINDER_HOUR', ge=0, lt=24)
    REMINDER_MINUTE: int = Field(0, env='REMINDER_MINUTE', ge=0, lt=60)


env = Env()

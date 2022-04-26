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


env = Env()

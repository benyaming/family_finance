from typing import List

from psycopg import AsyncCursor

from finance_bot.models import Transaction, Category
from finance_bot.misc import Misc


async def get_categories() -> List[Category]:
    resp = []
    async with Misc.db_conn.cursor() as acur:
        async for row in await acur.execute('SELECT * FROM category'):
            resp.append(Category(id=row[0], name=row[1]))
    return resp


async def get_category(category_id: int) -> Category:
    resp = None
    async with Misc.db_conn.cursor() as acur:
        async for row in await acur.execute('SELECT * FROM category WHERE id = %s', (category_id,)):
            resp = Category(id=row[0], name=row[1])
    return resp


async def save_transaction(transaction: Transaction):
    await Misc.db_conn.execute(
            'INSERT INTO transaction (amount, category_id, created_at) VALUES (%s, %s, %s)',
            (transaction.amount, transaction.category_id, transaction.created_at)
    )
    await Misc.db_conn.commit()

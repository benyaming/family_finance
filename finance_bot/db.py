from typing import List

from finance_bot.models import Transaction, Category, Subscription
from finance_bot.misc import Misc


async def get_categories() -> List[Category]:
    resp = []
    async with Misc.db_conn.cursor() as acur:
        async for row in await acur.execute('SELECT * FROM category ORDER BY id'):
            resp.append(Category(id=row[0], name=row[1]))
    return resp


async def get_category(category_id: int) -> Category:
    resp = None
    async with Misc.db_conn.cursor() as acur:
        async for row in await acur.execute('SELECT * FROM category WHERE id = %s', (category_id,)):
            resp = Category(id=row[0], name=row[1])
    return resp


async def save_category(category_name: str):
    await Misc.db_conn.execute('INSERT INTO category (name) VALUES (%s)', (category_name,))
    await Misc.db_conn.commit()


async def rename_category(category_id: int, new_name: str):
    await Misc.db_conn.execute('UPDATE category SET name = %s WHERE id = %s', (new_name, category_id))
    await Misc.db_conn.commit()


async def save_transaction(transaction: Transaction):
    await Misc.db_conn.execute(
            'INSERT INTO transaction (amount, category_id, created_at) VALUES (%s, %s, %s)',
            (transaction.amount, transaction.category_id, transaction.created_at)
    )
    await Misc.db_conn.commit()


async def get_transactions() -> List[Subscription]:
    resp = []
    async with Misc.db_conn.cursor() as acur:
        async for row in await acur.execute('SELECT * FROM subscription'):
            resp.append(Subscription(
                id=row[0],
                name=row[1],
                amount=row[2],
                day_of_month=row[3],
                category_id=row[4],
            ))
    return resp


async def save_subscription(subscription: Subscription):
    await Misc.db_conn.execute(
        'INSERT INTO subscription (name, amount, day_of_month, category_id) VALUES (%s, %s, %s, %s)',
        (subscription.name, subscription.amount, subscription.day_of_month, subscription.category_id)
    )
    await Misc.db_conn.commit()

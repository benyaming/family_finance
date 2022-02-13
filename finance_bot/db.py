from typing import List

import psycopg.errors

from finance_bot.misc import dp
from finance_bot.settings import env
from finance_bot.models import Transaction, Category, Subscription, CategoryGroup


async def get_all_categories() -> List[Category]:
    resp = []
    async with dp['db_conn'].cursor() as acur:
        async for row in await acur.execute('SELECT * FROM category ORDER BY id'):
            resp.append(Category(id=row[0], name=row[1], group_id=row[2]))
    return resp


async def get_top_categories(limit: int = env.CATEGORY_SUGGESTION_AMOUNT) -> List[Category]:
    query = '''
    SELECT ca.* from transaction t
    JOIN category ca ON t.category_id = ca.id
    GROUP BY ca.id
    ORDER BY COUNT(t.id) DESC
    LIMIT %s
    '''
    resp = []
    async with dp['db_conn'].cursor() as acur:
        async for row in await acur.execute(query, (limit,)):
            resp.append(Category(id=row[0], name=row[1], group_id=row[2]))
    return resp


async def get_categories_for_group(group_id: int) -> List[Category]:
    resp = []
    query = 'SELECT * FROM category WHERE group_id = %s ORDER BY id'
    async with dp['db_conn'].cursor() as acur:
        async for row in await acur.execute(query, (group_id,)):
            resp.append(Category(id=row[0], name=row[1], group_id=row[2]))
    return resp


async def get_category(category_id: int) -> Category:
    async with dp['db_conn'].cursor() as acur:
        await acur.execute('SELECT * FROM category WHERE id = %s', (category_id,))
        row = await acur.fetchone()
    resp = Category(id=row[0], name=row[1], group_id=row[2])
    return resp


async def save_category(category_name: str, group_id: int):
    query = 'INSERT INTO category (name, group_id) VALUES (%s, %s)'
    try:
        await dp['db_conn'].execute(query, (category_name, group_id))
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise


async def update_category(category: Category):
    query = '''
    UPDATE category
    SET name = %s, group_id = %s
    WHERE id = %s
    '''

    try:
        await dp['db_conn'].execute(query, (category.name, category.group_id, category.id))
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise


async def save_category_group(group_name: str):
    try:
        await dp['db_conn'].execute('INSERT INTO category_group (name) VALUES (%s)', (group_name,))
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise


async def get_category_groups(with_empty: bool = False) -> List[CategoryGroup]:
    resp = []
    if not with_empty:
        query = 'SELECT DISTINCT cg.* FROM category_group cg ' \
                'INNER JOIN category c ON c.group_id = cg.id ' \
                'ORDER BY cg.id'
    else:
        query = 'SELECT * FROM category_group ORDER BY id'
    async with dp['db_conn'].cursor() as acur:
        async for row in await acur.execute(query):
            resp.append(CategoryGroup(id=row[0], name=row[1]))
    return resp


async def get_category_group(group_id: int) -> CategoryGroup:
    async with dp['db_conn'].cursor() as acur:
        await acur.execute('SELECT * FROM category_group WHERE id = %s', (group_id,))
        row = await acur.fetchone()
    resp = CategoryGroup(id=row[0], name=row[1])
    return resp


async def rename_category_group(group_id: int, new_name: str):
    query = 'UPDATE category_group SET name = %s WHERE id = %s'
    try:
        await dp['db_conn'].execute(query, (new_name, group_id))
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise


async def remove_category_group(group_id: int):
    query = 'DELETE FROM category_group WHERE id = %s'
    try:
        await dp['db_conn'].execute(query, (group_id,))
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise


async def get_transactions() -> List[Subscription]:
    resp = []
    async with dp['db_conn'].cursor() as acur:
        async for row in await acur.execute('SELECT * FROM subscription'):
            resp.append(Subscription(
                id=row[0],
                name=row[1],
                amount=row[2],
                day_of_month=row[3],
                category_id=row[4],
            ))
    return resp


async def save_transaction(transaction: Transaction):
    query = 'INSERT INTO transaction (amount, category_id, created_at) VALUES (%s, %s, %s)'
    try:
        await dp['db_conn'].execute(query, (transaction.amount, transaction.category_id, transaction.created_at))
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise


async def save_subscription(subscription: Subscription):
    query = 'INSERT INTO subscription (name, amount, day_of_month, category_id) VALUES (%s, %s, %s, %s)'
    args = (subscription.name, subscription.amount, subscription.day_of_month, subscription.category_id)
    try:
        await dp['db_conn'].execute(query, args)
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise

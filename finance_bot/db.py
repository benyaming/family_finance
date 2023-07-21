import logging
from datetime import date
from typing import List, Tuple, Optional

import psycopg.errors

from finance_bot.misc import dp
from finance_bot.settings import env
from finance_bot.models import (
    Transaction,
    Category,
    Subscription,
    CategoryGroup,
    Limit
)


async def init_db():
    query = '''
    -- category_group table
    CREATE TABLE IF NOT EXISTS category_group
    (
        id    SERIAL CONSTRAINT category_group_pk PRIMARY KEY,
        name  TEXT NOT NULL,
        monthly_limit INTEGER
    );
    
    CREATE UNIQUE INDEX IF NOT EXISTS category_group_id_uindex ON category_group (id);
    CREATE UNIQUE INDEX IF NOT EXISTS category_group_name_uindex ON category_group (name);

    -- category table
    CREATE TABLE IF NOT EXISTS category
    (
        id       SERIAL CONSTRAINT category_pk PRIMARY KEY,
        name     TEXT              NOT NULL,
        group_id INTEGER DEFAULT 1 NOT NULL CONSTRAINT category_category_group_id_fk REFERENCES category_group
    );

    CREATE UNIQUE INDEX IF NOT EXISTS category_id_uindex ON category (id);
    CREATE UNIQUE INDEX IF NOT EXISTS category_name_uindex ON category (name);

    -- transaction table
    CREATE TABLE IF NOT EXISTS transaction
    (
        id          SERIAL  CONSTRAINT transaction_pk PRIMARY KEY,
        amount      INTEGER                 NOT NULL,
        category_id INTEGER                 NOT NULL CONSTRAINT transaction_category_id_fk REFERENCES category,
        created_at  TIMESTAMP DEFAULT now() NOT NULL 
    );

    CREATE UNIQUE INDEX IF NOT EXISTS transaction_id_uindex ON transaction (id);
    
    -- subscriptions table
    CREATE TABLE IF NOT EXISTS subscription
    (
        id           SERIAL   CONSTRAINT subscription_pk PRIMARY KEY,
        name         TEXT     NOT NULL,
        amount       INTEGER  NOT NULL,
        day_of_month SMALLINT NOT NULL,
        category_id  INTEGER  NOT NULL CONSTRAINT transaction_category_id_fk REFERENCES category,
        user_id      INTEGER  NOT NULL
    );
    
    CREATE UNIQUE INDEX IF NOT EXISTS subscription_id_uindex ON subscription(id);
    CREATE UNIQUE INDEX IF NOT EXISTS subscription_name_uindex ON subscription(name, category_id);
    
    
    -- Migration: add limits
    ALTER TABLE category_group ADD COLUMN IF NOT EXISTS monthly_limit INTEGER;
    '''
    try:
        await dp['db_conn'].execute(query)
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise


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


async def save_category_group(group_name: str, limit: int):
    query = 'INSERT INTO category_group (name, monthly_limit) VALUES (%s, %s)'
    try:
        await dp['db_conn'].execute(query, (group_name, limit))
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
            resp.append(CategoryGroup(id=row[0], name=row[1], limit=row[2]))
    return resp


async def get_category_group(group_id: int) -> CategoryGroup:
    async with dp['db_conn'].cursor() as acur:
        await acur.execute('SELECT * FROM category_group WHERE id = %s', (group_id,))
        row = await acur.fetchone()
    resp = CategoryGroup(id=row[0], name=row[1], limit=row[2])
    return resp


async def rename_category_group(group_id: int, new_name: str):
    query = 'UPDATE category_group SET name = %s WHERE id = %s'
    try:
        await dp['db_conn'].execute(query, (new_name, group_id))
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise


async def set_limit_for_category_group(group_id: int, new_limit: Optional[int]):
    query = 'UPDATE category_group SET monthly_limit = %s WHERE id = %s'
    try:
        await dp['db_conn'].execute(query, (new_limit, group_id))
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


async def save_transaction(transaction: Transaction):
    query = 'INSERT INTO transaction (amount, category_id, created_at) VALUES (%s, %s, %s)'
    try:
        await dp['db_conn'].execute(query, (transaction.amount, transaction.category_id, transaction.created_at))
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise


async def get_subscriptions() -> List[Subscription]:
    resp = []
    query = '''
    SELECT s.*, c.name, cg.name FROM subscription s
    JOIN category c on s.category_id = c.id
    JOIN category_group cg on c.group_id = cg.id
    ORDER BY s.id
    '''
    async with dp['db_conn'].cursor() as acur:
        async for row in await acur.execute(query):
            resp.append(Subscription(
                id=row[0],
                name=row[1],
                amount=row[2],
                day_of_month=row[3],
                category_id=row[4],
                user_id=row[5],
                category_name=row[6],
                group_name=row[7]
            ))
    return resp


async def get_subscription(subscription_id: int) -> Subscription:
    query = '''
        SELECT s.*, c.name, cg.name FROM subscription s
        JOIN category c on s.category_id = c.id
        JOIN category_group cg on c.group_id = cg.id
        WHERE s.id = %s 
        ORDER BY s.id
        '''
    async with dp['db_conn'].cursor() as acur:
        row = await (await acur.execute(query, (subscription_id,))).fetchone()

    if not row:
        raise ValueError('No subscription found!')

    resp = Subscription(
        id=row[0],
        name=row[1],
        amount=row[2],
        day_of_month=row[3],
        category_id=row[4],
        user_id=row[5],
        category_name=row[6],
        group_name=row[7]
    )
    return resp


async def save_subscription(subscription: Subscription):
    query = 'INSERT INTO subscription (' \
            '    name, amount, day_of_month, category_id, user_id' \
            ') VALUES (%s, %s, %s, %s, %s)'
    args = (
        subscription.name,
        subscription.amount,
        subscription.day_of_month,
        subscription.category_id,
        subscription.user_id
    )
    try:
        await dp['db_conn'].execute(query, args)
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise


async def update_subscription(subscription: Subscription):
    query = 'UPDATE subscription SET name = %s, amount = %s, day_of_month = %s, category_id = %s WHERE id = %s'
    args = (subscription.name, subscription.amount, subscription.day_of_month, subscription.category_id, subscription.id)
    try:
        await dp['db_conn'].execute(query, args)
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise


async def remove_subscription(subscription_id: int):
    query = 'DELETE FROM subscription WHERE id = %s'
    try:
        await dp['db_conn'].execute(query, (subscription_id,))
        await dp['db_conn'].commit()
    except psycopg.errors.DatabaseError:
        await dp['db_conn'].rollback()
        raise


async def get_subscriptions_for_today() -> list[Subscription]:
    day = date.today().day
    logging.info(f'getting subscriptions for day {day}')

    resp = []
    query = '''
        SELECT s.*, c.name, cg.name FROM subscription s
        JOIN category c on s.category_id = c.id
        JOIN category_group cg on c.group_id = cg.id
        WHERE s.day_of_month = %s
        ORDER BY s.id
        '''
    async with dp['db_conn'].cursor() as acur:
        async for row in await acur.execute(query, (day,)):
            resp.append(Subscription(
                id=row[0],
                name=row[1],
                amount=row[2],
                day_of_month=row[3],
                category_id=row[4],
                user_id=row[5],
                category_name=row[6],
                group_name=row[7]
            ))
    return resp


async def get_group_stats_for_month(month: int, year: int) -> Tuple[List[str], List[int], List[int]]:
    query = '''
    SELECT 
          cg.id,
          cg.name,
          (sum(amount) / 10000)::INT AS total
    FROM transaction t
    JOIN category c ON c.id = t.category_id
    JOIN category_group cg ON cg.id = c.group_id
    WHERE 
        date_part('month', t.created_at::TIMESTAMP) = %s AND
        date_part('year', t.created_at::TIMESTAMP) = %s
    GROUP BY cg.name, cg.id
    ORDER BY total DESC
    '''
    names = []
    amounts = []
    group_ids = []

    async with dp['db_conn'].cursor() as acur:
        async for row in await acur.execute(query, (month, year)):
            group_ids.append(row[0])
            names.append(row[1])
            amounts.append(row[2])
    return names, amounts, group_ids


async def get_category_stats_for_month(
        group_id: int,
        month: int,
        year: int
) -> Tuple[List[str], List[int]]:
    query = '''
    SELECT 
          c.name,
          (sum(amount) / 10000)::INT AS total
    FROM transaction t
    JOIN category c ON c.id = t.category_id
    JOIN category_group cg ON cg.id = c.group_id
    WHERE 
        cg.id = %s AND
        date_part('month', t.created_at::TIMESTAMP) = %s AND
        date_part('year', t.created_at::TIMESTAMP) = %s
    GROUP BY c.name
    ORDER BY total DESC
    '''
    names = []
    amounts = []

    async with dp['db_conn'].cursor() as acur:
        async for row in await acur.execute(query, (group_id, month, year)):
            names.append(row[0])
            amounts.append(row[1])
    return names, amounts


async def get_limits() -> list[Limit]:
    query = '''
    WITH data AS (
        SELECT cg.name,
               cg.monthly_limit,
               coalesce((sum(amount) / 10000)::INT, 0) AS total
        FROM transaction t
                 RIGHT JOIN category c ON c.id = t.category_id
                 RIGHT JOIN category_group cg ON cg.id = c.group_id
        WHERE
            (date_part('month', t.created_at::TIMESTAMP) = extract(MONTH FROM CURRENT_DATE) AND
            date_part('year', t.created_at::TIMESTAMP) = extract(YEAR FROM CURRENT_DATE) OR
            t.created_at IS NULL) -- for including categories without transactions
            AND cg.monthly_limit IS NOT NULL
        GROUP BY 1, 2
        ORDER BY total DESC)
    SELECT
        data.* ,
        data.monthly_limit - data.total AS rest,
        ((data.total::FLOAT / data.monthly_limit::FLOAT) * 100)::INT AS percentage
    FROM data
    '''

    limits = []

    async with dp['db_conn'].cursor() as acur:
        async for row in await acur.execute(query):
            limits.append(Limit(
                group_name=row[0],
                limit=row[1],
                spent=row[2],
                rest=row[3],
                usage_percentage=row[4],
            ))

    return limits


async def get_limit_for_group(group_id: int) -> Limit:
    query = '''
    WITH data AS (
        SELECT cg.name,
               cg.monthly_limit,
               (sum(amount) / 10000)::INT AS total
        FROM transaction t
                 JOIN category c ON c.id = t.category_id
                 JOIN category_group cg ON cg.id = c.group_id
        WHERE
            date_part('month', t.created_at::TIMESTAMP) = extract(MONTH FROM CURRENT_DATE) AND
            date_part('year', t.created_at::TIMESTAMP) = extract(YEAR FROM CURRENT_DATE) AND
            cg.id = %s
        GROUP BY 1, 2
        ORDER BY total DESC)
    SELECT
        data.* ,
        data.monthly_limit - data.total AS rest,
        ((data.total::FLOAT / data.monthly_limit::FLOAT) * 100)::INT AS percentage
    FROM data
    '''

    async with dp['db_conn'].cursor() as acur:
        row = await (await acur.execute(query, (group_id,))).fetchone()

    return Limit(
        group_name=row[0],
        limit=row[1],
        spent=row[2],
        rest=row[3],
        usage_percentage=row[4],
    )

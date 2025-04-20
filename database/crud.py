import aiohttp

import config
from database.connect import get_connection
from datetime import datetime

from database.connect import get_connection


async def get_bestchange_currency_id(slug):
    url = f'https://bestchange.app/v2/{config.API_KEY}/currencies/en'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"[ERROR] Failed to fetch currencies: status {response.status}")
                return None

            data = await response.json()

    # ✅ извлекаем список валют из словаря
    currencies = data.get("currencies", [])
    for currency in currencies:
        if currency["code"].lower() == slug.lower():
            return currency["id"]

    print(f"[WARN] Currency with code '{slug}' not found.")
    return None


async def get_all_bestchange_slugs():
    async with get_connection() as conn:
        # получаем и id, и slug
        async with conn.execute("SELECT id, bestchange_id, slug FROM exchange_coin") as cursor:
            rows = await cursor.fetchall()

        result_ids = []

        for coin_id, bestchange_id, slug in rows:
            if bestchange_id is not None:
                result_ids.append(bestchange_id)
            else:
                try:
                    fetched_id = int(await get_bestchange_currency_id(slug))
                    if fetched_id is not None:
                        async with get_connection() as conn:  # отдельный контекст для записи
                            await conn.execute(
                                "UPDATE exchange_coin SET bestchange_id = ? WHERE id = ?",
                                (fetched_id, coin_id)
                            )
                            await conn.commit()
                        print(f"[UPDATED] {slug} → bestchange_id = {fetched_id}")
                        result_ids.append(fetched_id)
                    else:
                        print(f"[SKIPPED] No match found for slug: {slug}")
                except Exception as e:
                    print(f"[ERROR] Failed to fetch or update slug {slug}: {e}")

        return result_ids


async def get_coin_id_by_slug(slug: int):
    async with get_connection() as conn:
        async with conn.execute("SELECT id FROM exchange_coin WHERE bestchange_id = ?", (slug,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def insert_exchange_rate(from_id: int, to_id: int, rate: float,
                               min_amount: float = 0.01, max_amount: float = 100.0):
    async with get_connection() as conn:
        await conn.execute(
            """
            INSERT OR REPLACE INTO exchange_exchangerate (
                current_rate, min_amount, max_amount, from_coin_id, to_coin_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (rate, min_amount, max_amount, from_id, to_id, datetime.utcnow())
        )
        await conn.commit()

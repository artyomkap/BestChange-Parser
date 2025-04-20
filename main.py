import asyncio
import config
import aiohttp
from database.crud import get_all_bestchange_slugs, get_coin_id_by_slug, insert_exchange_rate

BASE_URL = f"https://bestchange.app/v2/{config.API_KEY}/rates/"


def generate_all_slug_pairs(slugs: list[str]) -> list[str]:
    pairs = []
    for from_slug in slugs:
        for to_slug in slugs:
            if from_slug != to_slug:
                pairs.append(f"{from_slug}-{to_slug}")
    return pairs


def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


async def parse_all_pairs(pair_list_str: str):
    url = BASE_URL + pair_list_str
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"[ERROR] API responded with status {response.status}")
                return

            data = await response.json()

            for pair_key, offers in data.get("rates", {}).items():
                if not offers:
                    continue

                try:
                    from_slug, to_slug = pair_key.split("-")
                    from_id = await get_coin_id_by_slug(from_slug)
                    to_id = await get_coin_id_by_slug(to_slug)

                    top_offer = offers[0]
                    rate = round(float(top_offer["rate"]), 4)
                    inmin = float(top_offer["inmin"])
                    inmax = float(top_offer["inmax"])

                    await insert_exchange_rate(from_id, to_id, rate, inmin, inmax)
                    print(f"{from_slug} -> {to_slug} | rate: {rate} | min: {inmin} | max: {inmax}")
                except Exception as e:
                    print(f"[ERROR] Failed to process pair {pair_key}: {e}")


async def main():
    slugs = await get_all_bestchange_slugs()
    slug_pairs = generate_all_slug_pairs(slugs)
    chunks = list(chunk_list(slug_pairs, 500))

    for index, chunk in enumerate(chunks, start=1):
        pair_list_str = "+".join(chunk)
        print(f"\n[INFO] Sending chunk {index}/{len(chunks)} with {len(chunk)} pairs...")
        await parse_all_pairs(pair_list_str)


if __name__ == "__main__":
    async def loop_forever():
        while True:
            try:
                await main()
            except Exception as e:
                print(f"\n[!] Unexpected error in main loop: {e}")
            await asyncio.sleep(10)

    asyncio.run(loop_forever())

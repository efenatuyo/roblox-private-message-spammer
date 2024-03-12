from src import cookie, message, proxy

import asyncio, json, aiohttp

async def main(config):
    proxies = proxy.make(len(config["cookies"]))
    tasks = []
    tasks_region_unlock = []
    async with aiohttp.ClientSession() as session:
        for index, _proxy in enumerate(proxies):
            cc = cookie.RobloxCookie(config["cookies"][index])
            tasks.append(message.sender(cc, config["message"]["subject"], config["message"]["body"], config["user_ids"], _proxy).start())
            if config["unregion_lock_cookies"]:
                tasks_region_unlock.append(cc.region_unlock(session, _proxy.current))
        await asyncio.gather(*tasks_region_unlock)
        await session.close()
        await asyncio.gather(*tasks)
    
asyncio.run(main(json.loads(open("config.json", "r").read())))
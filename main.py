from src import cookie, message, proxy

import asyncio, json, aiohttp

async def sem_task(semaphore, coroutine, n=False):
    try:
        async with semaphore:
            if n:
                return await coroutine()
            else:
                return await coroutine
    except Exception as e:
        print(f"Error in coroutine: {e}")
        
async def limited_gather(max_concurrency, loop=False, total_cookies=0, *coroutines):
    semaphore = asyncio.Semaphore(max_concurrency)
    
    if not loop:
        semaphore = asyncio.Semaphore(max_concurrency)
        return await asyncio.gather(*[sem_task(semaphore, coro) for coro in coroutines])
    else:
        while True:
            semaphore = asyncio.Semaphore(max_concurrency)
            await asyncio.gather(*[sem_task(semaphore, coro, loop) for coro in coroutines])
            await asyncio.sleep(10 / total_cookies)

    
async def main(config):
    proxies = proxy.make(len(config["cookies"]))
    tasks = []
    tasks_region_unlock = []
    ccs = []
    async with aiohttp.ClientSession() as session:
        for index, _proxy in enumerate(proxies):
            cc = cookie.RobloxCookie(config["cookies"][index])
            ccs.append(cc)
            if config["unregion_lock_cookies"]:
                tasks_region_unlock.append(cc.region_unlock(session, _proxy.current))
        await limited_gather(config["total_threads"], False, 0, *tasks_region_unlock)
        await session.close()
        for index, _proxy in enumerate(proxies):
            if not ccs[index].cookie:
                continue
            tasks.append(message.sender(ccs[index], config["message"]["subject"], config["message"]["body"], config["user_ids"], _proxy).start)
        await limited_gather(config["total_threads"], True, len(config["cookies"]), *tasks)
    
asyncio.run(main(json.loads(open("config.json", "r").read())))

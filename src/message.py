import aiohttp, asyncio, random

class sender:
    def __init__(self, cookie: object, subject: str, body: str, user_ids: list, proxy: str):
        self.subject = subject
        self.body = body
        self.user_ids = user_ids
        self.cookie = cookie
        self.proxy = proxy
        
    async def send(self, session, user_id):
        response = await session.post("https://privatemessages.roblox.com/v1/messages/send",  data={"subject": self.subject, "body": self.body, "recipientId": user_id}, headers={"x-csrf-token": await self.cookie.x_token(session, self.proxy.current)}, cookies={".ROBLOSECURITY": self.cookie.cookie}, proxy=self.proxy.current)
        print(await response.text())
        self.proxy.next()
            
    async def start(self):
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    await self.send(session, random.choice(self.user_ids))
                except Exception as e:
                    print(e)
                finally:
                    await asyncio.sleep(10)
import requests, json, random, time, itertools

class spammer:
    class DotDict(dict):
        def __getattr__(self, attr):
            if attr in self:
                return self[attr]
            else:
                raise AttributeError(f"'DotDict' object has no attribute '{attr}'")
        
    def __init__(self):
        self.config = self._config

    @property
    def _config(self) -> dict:
        with open("config.json") as f: return json.load(f)
    
    def _get_xcsrf_token(self, cookie) -> str:
        response = requests.post("https://accountsettings.roblox.com/v1/email", cookies={".ROBLOSECURITY": cookie})
        xcsrf_token = response.headers.get("x-csrf-token")
        if xcsrf_token is None:
            raise Exception("An error occurred while getting the X-CSRF-TOKEN. "
                            "Could be due to an invalid Roblox Cookie")
        return xcsrf_token
    
    @property
    def _setup_xcsrf_token(self) -> dict:
        accounts = {}
        for cookie in self.config["cookies"]:
            accounts[cookie] = {"x-csrf-token": self._get_xcsrf_token(cookie)}
        return accounts
    
    def start(self):
        self.total_checks = 0
        self.receivers = itertools.cycle(self.config["receivers"])
        self.cookies = itertools.cycle(self.config["cookies"])
        self.accounts = self._setup_xcsrf_token
        request = self.DotDict({})
        request.status_code = "NaN"
        while True:
            try:
                currentCookie = next(self.cookies)
                currentReceiver = next(self.receivers)
                
                request = requests.post("https://privatemessages.roblox.com/v1/messages/send", data={"subject": self.config["message"]["subject"], "body": self.config["message"]["body"], "recipientId": currentReceiver}, headers={"x-csrf-token": self.accounts[currentCookie]["x-csrf-token"]}, cookies={".ROBLOSECURITY": currentCookie})
                if request.status_code == 403:
                    self.accounts[currentCookie]["x-csrf-token"] = self._get_xcsrf_token(currentCookie)
                    continue
                
                if request.status_code == 429:
                    print("Ratelimit hit waiting extra 10 seconds")
                    time.sleep(10)
                    continue
                    
                    
                json_request = request.json()
                if json_request["success"] is False and json_request["shortMessage"] == "VerifySenderEmail":
                    raise Exception("Email verification is required for the account.")
                
                if json_request["success"] is False and json_request["shortMessage"] == "SenderPrivacySettingsTooHigh":
                    raise Exception(f"You need to set EVERYONE for chatting on roblox. Error on cookie: {currentCookie}")
                
                if json_request["success"] is False and json_request["shortMessage"] == "RecipientPrivacySettingsTooHigh":
                    raise Exception(f"Receiver does not allow private messages. ID: {currentReceiver}.")
                
                if request.status_code == 200: 
                    self.total_checks += 1

            finally:
                print("Total Messages: ", self.total_checks, " Last status code: ", request.status_code)
                time.sleep(10 / len(self.config["cookies"]))
                

spammer().start()

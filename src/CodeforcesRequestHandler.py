import uuid
from typing import Dict, Any

import requests

class CodeforcesRequestHandler:

    def __init__(self,configs:Dict[str,Any]):
        self.codeforces_url = configs.get("codeforces").get("url")

        self.flaresolverr_url = configs.get("flaresolverr").get("url")
        self.flaresolverr_session = configs.get("flaresolverr").get("session",uuid.uuid4().__str__())



    def get(self,path:str,turnstile=False):
        headers = {"Content-Type": "application/json"}
        data = {
            "cmd": "request.get",
            "url": f"https://codeforces.com/{path}",
            "session": self.flaresolverr_session
        }
        if turnstile:
            data["tabs_till_verify"] = "1"
            data["waitInSeconds"] = "3"

        return requests.post(self.flaresolverr_url, headers=headers, json=data)

    def post(self,path:str,data:Dict[str,Any],turnstile=False):
        headers = {"Content-Type": "application/json"}
        data = {
            "cmd": "request.get",
            "url": f"https://codeforces.com/{path}",
            "session": self.flaresolverr_session
        }
        if turnstile:
            data["tabs_till_verify"] = "1"
            data["waitInSeconds"] = "3"

        return requests.post(self.flaresolverr_url, headers=headers, json=data)
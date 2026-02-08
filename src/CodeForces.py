from typing import Dict, Any

from src.CodeforcesRequestHandler import CodeforcesRequestHandler

class Codeforces:
    def __init__(self,configs:Dict[str,Any]):
        self.request_handler = CodeforcesRequestHandler(configs)

    def auth(self) -> bool:
        login_page = self.request_handler.get("enter",turnstile=True)

        # Redirect to the homepage if we are already logged in
        if login_page.status_code == 302:
            return True




        return False

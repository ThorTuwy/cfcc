from typing import Dict

import browser_cookie3
import httpx

DEFAULT_URL = "https://codeforces.com"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"

class CodeforcesRequester:
    def __init__(self,codeforces_requester_configs:Dict[str,str]):
        codeforces_url = codeforces_requester_configs.get("url", DEFAULT_URL)
        codeforces_domain = codeforces_url.split("://")[1].split("/")[0]

        user_agent = codeforces_requester_configs.get("user-agent", DEFAULT_USER_AGENT)
        for browser in browser_cookie3.all_browsers:
            try:
                cookies = browser(domain_name=codeforces_domain)
                if cookies.get("X-User"):
                    break
            except:
                continue

        if codeforces_url is None:
            codeforces_url = DEFAULT_URL
        if user_agent is None:
            user_agent = DEFAULT_USER_AGENT

        self._url = codeforces_url
        self._session = httpx.Client(
            cookies=cookies,
            headers={
                "User-Agent": user_agent
            }
        )

    def _get_contest_url(self,contest_id:str, is_gym=False):
        request_url = f"{self._url}/"
        if is_gym:
            request_url += "gym/"
        else:
            request_url += "contest/"
        request_url += f"{contest_id}"
        return request_url

    def get_problem(self,contest_id:str,problem_index:str, is_gym=False):
        request_url = f"{self._get_contest_url(contest_id,is_gym)}/problem/{problem_index}"
        return self._session.get(request_url)

    def get_contest(self,contest_id:str, is_gym=False):
        request_url = self._get_contest_url(contest_id,is_gym)
        return self._session.get(request_url)

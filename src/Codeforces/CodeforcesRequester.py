from typing import Any, AsyncGenerator

import browser_cookie3
import bs4
import httpx
from httpx_ws import aconnect_ws

from utils.program_configs import CodeforcesConfig

class CodeforcesRequester:
    def __init__(self,codeforces_config:CodeforcesConfig):
        codeforces_url = codeforces_config.url
        codeforces_domain = codeforces_url.split("://")[1].split("/")[0]

        browsers_to_check = browser_cookie3.all_browsers
        prefer_browser = None

        if codeforces_config.prefer_browser_cookies is not None:
            for browser in browsers_to_check:
                if browser.__name__.lower() == codeforces_config.prefer_browser_cookies.lower():
                    prefer_browser = browser
                    break

        if prefer_browser:
            browsers_to_check.remove(prefer_browser)
            browsers_to_check.insert(0, prefer_browser)

        user_agent = codeforces_config.user_agent
        cookies=None
        for browser in browsers_to_check:
            try:
                for cookie in browser(domain_name=codeforces_domain):
                    if cookie.name == "X-User":
                        cookies = browser(domain_name=codeforces_domain)
                        break
                if cookies is not None:
                    break
            except:
                continue

        if cookies is None:
            print("(!) No cookies found for Codeforces, you are not going to be able to access to some features (private gyms, submissions, etc).")

        self.url = codeforces_url
        self._session = httpx.Client(
            cookies=cookies,
            headers={
                "User-Agent": user_agent
            }
        )
        self._async_session = httpx.AsyncClient(
            cookies=cookies,
            headers={
                "User-Agent": user_agent
            }
        )

    def _get_contest_url(self,contest_id:str, is_gym=False):
        request_url = f"{self.url}/"
        if is_gym:
            request_url += "gym/"
        else:
            request_url += "contest/"
        request_url += f"{contest_id}"
        return request_url

    def get_problem(self,contest_id:str,problem_index:str, is_gym=False):
        for _ in range(3):
            request_url = f"{self._get_contest_url(contest_id,is_gym)}/problem/{problem_index}"
            request = self._session.get(request_url)
            if request.status_code != 200:
                continue
            return request
        raise Exception("Failed to get problem")

    def get_contest(self,contest_id:str, is_gym=False):
        request_url = self._get_contest_url(contest_id,is_gym)
        return self._session.get(request_url)

    def _get_csrf_token(self):
        request_url = f"{self.url}"
        main_page_response = self._session.get(request_url)
        main_page_soup = bs4.BeautifulSoup(main_page_response.content, "html.parser")
        return main_page_soup.find("span",class_="csrf-token").get("data-csrf")


    def submit_problem(self, contest_id:str, problem_index:str, problem_code:str, program_language_id:int, is_gym=False):
        request_url= f"{self._get_contest_url(contest_id,is_gym)}/submit"

        csrf_token = self._get_csrf_token()

        request_query = {
            "csrf_token" : csrf_token,
        }

        data_query = {
            "csrf_token" : csrf_token,
            "action" : "submitSolutionFormSubmitted",
            "turnstileToken" : "", # Intentionally empty
            "submittedProblemIndex" : problem_index,
            "programTypeId" : program_language_id,
            "source" : problem_code,
            "tabSize" : 4,
            "sourceFile":"", # Intentionally empty
        }

        request = self._session.post(request_url, data=data_query, params=request_query)

        return request.status_code != 200

    def get_my_submission(self,contest_id:str, is_gym=False):
        request_url = f"{self._get_contest_url(contest_id,is_gym)}/my"
        return self._session.get(request_url)

    async def stream_submission_messages_updates(self,contest_id:str, is_gym=False) -> AsyncGenerator[str, Any]:
        request_url = f"{self._get_contest_url(contest_id, is_gym)}/my"

        async with aconnect_ws(request_url, self._async_session) as ws:
            while True:
                message = await ws.receive_text()
                yield message

    def get_problem_data_by_id(self,contest_id:str, problem_internal_id:str):
        request_url = f"{self.url}/data/contests"
        data = {
            "action": "getProblemName",
            "mode": "CONTEST",
            "contestId": str(contest_id),
            "problemId": str(problem_internal_id),
            "communityCode": "",
            "csrf_token": self._get_csrf_token()
        }
        return self._session.post(request_url, data=data)
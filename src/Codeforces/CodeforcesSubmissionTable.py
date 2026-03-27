"""
This class handles the submission updates from Codeforces.
This is not included in CodeForces logic as the complexity would be too high.
"""
import json
from dataclasses import dataclass
from typing import Dict, AsyncGenerator

from bs4 import BeautifulSoup

from Codeforces.CodeforcesRequester import CodeforcesRequester

@dataclass
class CFSubmission:
    contest_id: str
    problem_index: str
    problem_name: str
    when:str
    verdict: str
    time_ms: int
    memory_kb: int
    passed_test: int = 0

class CodeforcesSubmissionTable:
    def __init__(self, requester: CodeforcesRequester, contest_id: str, is_gym=False):
        self.requester = requester
        self.contest_id:str = contest_id
        self.is_gym = is_gym
        self.submissions_data:Dict[str,CFSubmission] = {}
        self.pc = None
        self._fill_submissions()

    def _fill_submissions(self) -> None:
        """
        This method uses the submission table to fill the submission data.
        This is useful as messages only provided new information allowing us in this way to still get those submissions.
        And also because messages do not provide a problem name, so this is the only way to get it.
        :return:
        """
        submission_table_request = self.requester.get_my_submission(self.contest_id,self.is_gym)
        submission_table_soup = BeautifulSoup(submission_table_request.text, "html.parser")
        metas = submission_table_soup.find_all('meta')
        for meta in metas:
            if meta.get('name') == 'pc':
                self.pc = meta.get('content')

        submission_rows = submission_table_soup.find_all("tr", attrs={"data-submission-id": True})

        new_submission_data:Dict[str,CFSubmission] = {}

        for submission_row in submission_rows:
            submission_id = submission_row.find(attrs={"submissionid": True}).get("submissionid")

            problem_cell = submission_row.find(attrs={"data-problemid": True})
            problem_content = problem_cell.find("a")
            problem_index = problem_content.get("href").split("/")[4]
            problem_name = problem_content.text.split("-")[1].strip()

            when_element = submission_row.find(class_="format-time")
            when = when_element.text if when_element is not None else ""

            verdict_element = submission_row.find(attrs={"submissionverdict": True})
            verdict = verdict_element.get("submissionverdict") if verdict_element is not None else "TESTING"

            passed_test_element = submission_row.find(class_="verdict-format-judged")
            passed_test = int(passed_test_element.text) if passed_test_element is not None else 0

            time_element = submission_row.find(class_="time-consumed-cell")
            time_ms = int(time_element.text.split()[0]) if time_element is not None else 0

            memory_element = submission_row.find(class_="memory-consumed-cell")
            memory_kb = int(memory_element.text.split()[0]) if memory_element is not None else 0

            new_submission_data[submission_id] = CFSubmission(
                contest_id=self.contest_id,
                problem_index=problem_index,
                problem_name=problem_name,
                when=when,
                verdict=verdict,
                passed_test=passed_test,
                time_ms=time_ms,
                memory_kb=memory_kb
            )

        for submission_id in new_submission_data:
            if not submission_id in self.submissions_data:
                self.submissions_data[submission_id] = new_submission_data[submission_id]

    async def get_realtime_submission_table(self) -> AsyncGenerator[dict[str, CFSubmission]]:
        yield self.submissions_data
        async for message in self.requester.stream_submission_messages_updates(self.pc):
            payload = json.loads(message)['text']
            if payload is None:
                continue

            data = json.loads(payload).get("d", [])

            submission_id = str(data[1])

            submission = self.submissions_data.get(submission_id,None)
            if submission is None:
                self._fill_submissions()
            elif data[7]>submission.passed_test:
                print(f"New test passed on submission")
                print(data)
                submission.verdict = data[6]
                submission.passed_test = data[7]
                submission.time_ms = data[9]
                submission.memory_kb = data[10] // 1024 if data[10] is not None else 0
                self.submissions_data[submission_id] = submission
            else:
                continue

            yield self.submissions_data
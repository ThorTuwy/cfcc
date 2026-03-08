import json
from dataclasses import dataclass
from typing import AsyncGenerator

from bs4 import BeautifulSoup

from Codeforces.CodeforcesRequester import CodeforcesRequester
from Codeforces.CodeforcesSubmissionTable import CodeforcesSubmissionTable, CFSubmission
from Codeforces.CodeforcesTextParser import get_text_in_div
from utils.program_configs import CodeforcesConfig
from utils.language_to_program_id import language_to_program_id


@dataclass
class CFProblem:
    contest_id: str
    problem_index: str
    is_gym:bool
    title: str
    time_limit: float
    memory_limit: int
    statement_md: str
    input_md: str
    output_md: str
    samples: list[dict[str,str]]

@dataclass
class CFContest:
    id: str
    is_gym: bool
    title: str
    problems: list[str]

class Codeforces:
    def __init__(self, codeforces_config: CodeforcesConfig):
        self.requester = CodeforcesRequester(codeforces_config)
        self.program_language_id = language_to_program_id(codeforces_config.program_language)

    def get_contest(self, contest_id: str, is_gym=False) -> CFContest:
        contest_request = self.requester.get_contest(contest_id, is_gym)
        contest_soup = BeautifulSoup(contest_request.text, "html.parser")

        problem_list = []
        for problem_tag in contest_soup.find_all(class_='id'):
            problem_list.append(problem_tag.find('a')['href'].split('/')[4])

        return CFContest(
            id=contest_id,
            is_gym=is_gym,
            title=contest_soup.find("title").text.strip(),
            problems=problem_list
        )

    def get_problem(self, contest_id: str, problem_index: str, is_gym=False) -> CFProblem:
        problem_request = self.requester.get_problem(contest_id, problem_index, is_gym)

        problem_soup = BeautifulSoup(problem_request.text, "html.parser")

        problem_statement = problem_soup.find(class_='problem-statement')

        problem_header = problem_statement.find(class_='header')
        title = problem_header.find(class_='title').text
        time_limit = float(list(problem_header.find(class_='time-limit'))[1].text.split()[0])
        memory_limit = int(list(problem_header.find(class_='memory-limit'))[1].text.split()[0])

        problem_text_div = problem_header.find_next_sibling('div')
        problem_text = get_text_in_div(problem_text_div)

        input_text_div = problem_text_div.find_next_sibling('div')
        input_text = get_text_in_div(input_text_div)

        output_text_div = input_text_div.find_next_sibling('div')
        output_text = get_text_in_div(output_text_div)

        sample_div = output_text_div.find_next_sibling('div').find('div', class_='sample-test')
        inputs_divs = sample_div.find_all(class_='input')
        outputs_divs = sample_div.find_all(class_='output')

        problems_samples = []
        for i,o in zip(inputs_divs, outputs_divs):

            input_pre = i.find('pre')
            output_pre = o.find('pre')

            parsed_io = []

            for tag in [input_pre,output_pre]:
                parsed_text = ""
                for child in tag.children:
                    parsed_text += child.text.strip()+'\n'
                parsed_io.append(parsed_text)

            problems_samples.append({
                "input": parsed_io[0].strip(),
                "output": parsed_io[1].strip()
            })

        return CFProblem(
            contest_id=contest_id,
            problem_index=problem_index,
            is_gym=is_gym,
            title=title,
            time_limit=time_limit,
            memory_limit=memory_limit,
            statement_md=problem_text.markup,
            input_md=input_text.markup,
            output_md=output_text.markup,
            samples=problems_samples
        )

    def submit_problem(self, contest_id: str, problem_index: str, problem_code:str, is_gym=False):
        self.requester.submit_problem(contest_id, problem_index,problem_code, self.program_language_id, is_gym)

    def stream_submission_table(self, contest_id: str, is_gym=False) -> AsyncGenerator[dict[str, CFSubmission]]:
        cf_submission_table = CodeforcesSubmissionTable(self.requester, contest_id, is_gym)
        return cf_submission_table.get_realtime_submission_table()
import asyncio
from typing import AsyncGenerator, Dict, List

from rich import box
from rich.align import Align
from rich.console import Group,Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from Codeforces.CodeforcesSubmissionTable import CFSubmission

class SubmissionTable:
    def __init__(self,
                 title: str,
                 problem_letters: List[str]):
        self.title = title
        self.problem_letters = problem_letters

    def _get_title(self):
        return Text(self.title, style="bold magenta", justify="center")

    def _get_verdict_color(self, verdict: str):
        match verdict:
            case "OK":
                return "green"
            case "TESTING":
                return "yellow"
            case "UNTESTED":
                return "dim"
            case _:
                return "red"

    def _get_problem_panels(self,submissions: Dict[str, CFSubmission]):
        problems_verdict: Dict[str, str] = {pid: "UNTESTED" for pid in self.problem_letters}

        for sub in submissions.values():
            pid = sub.problem_index
            if problems_verdict[pid] != "OK":
                problems_verdict[pid] = sub.verdict

        panels = []
        for pid,problem_verdict in problems_verdict.items():

            verdict_color = self._get_verdict_color(problem_verdict)
            border_color, text_style = verdict_color, f"bold {verdict_color}"

            content = Text(f"{pid}", style=text_style, justify="center")
            panels.append(Panel(content, border_style=border_color, expand=False))

        grid = Table.grid(padding=(0, 1))
        grid.add_row(*panels)
        return Align.center(grid)

    def _get_submissions_tables(self, submissions: Dict[str, CFSubmission]) -> Align:
        def make_new_table(border_color: str) -> Table:
            COLUMN_SIZE_WHEN = 17
            COLUMN_SIZE_PROB = 30
            COLUMN_SIZE_VERD = 32
            COLUMN_SIZE_TIME = 12
            COLUMN_SIZE_MEM = 12
            table = Table(
                box=box.ROUNDED,
                show_header=False,
                expand=False,
                border_style=border_color,
                padding=(0, 1)
            )
            table.add_column(width=COLUMN_SIZE_WHEN, justify="center", no_wrap=True)
            table.add_column(width=COLUMN_SIZE_PROB, justify="left", no_wrap=True)
            table.add_column(width=COLUMN_SIZE_VERD, justify="left", no_wrap=True)
            table.add_column(width=COLUMN_SIZE_TIME, justify="right", no_wrap=True)
            table.add_column(width=COLUMN_SIZE_MEM, justify="right", no_wrap=True)
            return table

        tables_stack = []
        header_table_color = "cyan"
        header_table_style = f"bold {header_table_color}"
        header_table = make_new_table(header_table_color)
        header_table.add_row(
            Text("When", style=header_table_style),
            Text("Problem", style=header_table_style),
            Text("Verdict", style=header_table_style),
            Text("Time", style=header_table_style),
            Text("Memory", style=header_table_style)
        )
        tables_stack.append(header_table)

        for submission in reversed(list(submissions.values())):
            submission_color = self._get_verdict_color(submission.verdict)

            sub_table = make_new_table(submission_color)
            sub_table.add_row(
                submission.when,
                f"{submission.problem_index} - {submission.problem_name}",
                Text(f"{submission.verdict}", style=f"bold {submission_color}"),
                f"{submission.time_ms} ms",
                f"{submission.memory_kb} KB"
            )
            tables_stack.append(sub_table)

        return Align.center(Group(*tables_stack))

    def generate_submission_table(self, submissions: Dict[str, CFSubmission]):
        return Group(
            self._get_title(),
            Text("\n"),
            self._get_problem_panels(submissions),
            Text("\n"),
            self._get_submissions_tables(submissions)
        )

def display_submission_table(contest_name:str, contest_problems:list[str], console:Console,submissions_steam: AsyncGenerator[Dict[str, CFSubmission], None]):
    submission_table = SubmissionTable(contest_name, contest_problems)
    async def async_run_submission_table():
        async for submissions in submissions_steam:
            console.print(submission_table.generate_submission_table(submissions))

    asyncio.run(async_run_submission_table())

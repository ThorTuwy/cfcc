from pathlib import Path

import tomllib
from dacite import from_dict

from Codeforces.Codeforces import CFProblem, CFContest


def read_contest_file(contest_path:Path) -> CFContest:
    """Reads the contest.toml file in the given contest path and returns a CFContest object.
        This function also works if the path is a problem folder instead of the contest folder."""
    contest_toml = contest_path / "contest.toml"
    if not contest_toml.exists():
        contest_toml = contest_path.parent / "contest.toml"
        if not contest_toml.exists():
            raise Exception("No contest.toml found, you need to run this command in a contest/problem folder")

    with open(contest_toml, "rb") as f:
        contest_data = tomllib.load(f)
    cf_contest = from_dict(data_class=CFContest, data=contest_data)
    return cf_contest

def read_problem_file(problem_path:Path) -> CFProblem:
    problem_toml = problem_path / "problem.toml"
    if not problem_toml.exists():
        raise Exception("No problem.toml found, you need to run this command in a problem folder")
    with open(problem_toml, "rb") as f:
        problem_data = tomllib.load(f)
    cf_problem = from_dict(data_class=CFProblem, data=problem_data)
    return cf_problem
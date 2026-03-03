from pathlib import Path

import tomllib
from dacite import from_dict

from Codeforces.Codeforces import CFProblem

def read_problem_file(problem_path:Path) -> CFProblem:
    problem_toml = problem_path / "problem.toml"
    if not problem_toml.exists():
        raise Exception("No problem.toml found, you need to run this command in a problem folder")
    with open(problem_toml, "rb") as f:
        problem_data = tomllib.load(f)
    cf_problem = from_dict(data_class=CFProblem, data=problem_data)
    return cf_problem
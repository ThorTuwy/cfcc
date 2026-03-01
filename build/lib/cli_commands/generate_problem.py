"""
This file contains the command to generate a problem from a CFProblem object.
"""

import dataclasses
from pathlib import Path
import tomli_w
from Codeforces.Codeforces import CFProblem

def generate_problem(contest_path:Path, problem:CFProblem):
    problem_path = contest_path / problem.problem_index
    if problem_path.exists():
        return
    problem_path.mkdir()

    sample_number = 1

    for i in problem.samples:
        with open(problem_path / f"{sample_number}.in","w") as f:
            f.write(i['input'])
        with open(problem_path / f"{sample_number}.out","w") as f:
            f.write(i['output'])
        sample_number+=1

    with open(problem_path / f"problem.cpp", "w") as f:
        f.write("")

    with open(problem_path / f"problem.toml", "wb") as f:
        tomli_w.dump(dataclasses.asdict(problem), f)
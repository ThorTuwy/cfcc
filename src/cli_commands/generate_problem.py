"""
This file contains the command to generate a problem from a CFProblem object.
"""

import dataclasses
import os
import shutil
from pathlib import Path

import tomlkit

from Codeforces.Codeforces import CFProblem

def generate_problem(contest_path:Path, problem:CFProblem, code_template_file:Path|None=None):
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

    code_file_path = problem_path / f"{problem.problem_index}.cpp"

    if code_template_file:
        shutil.copy(code_template_file, problem_path /code_file_path)
        os.chmod(problem_path / code_file_path, 0o755)
    else:
        with open(problem_path / code_file_path, "w") as f:
            f.write("")

    with open(problem_path / f"problem.toml", "w") as f:
        tomlkit.dump(dataclasses.asdict(problem), f)
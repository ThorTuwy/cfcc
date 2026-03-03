from pathlib import Path
from typing import Any, Dict

import tomllib
import typer
from dacite import from_dict

from Codeforces.Codeforces import CFProblem

APP_NAME = "cfcc"

def load_general_config_file() -> Dict[str,Any]:
    config_file = Path(typer.get_app_dir(APP_NAME)) / "config.toml"

    config_file.parent.mkdir(parents=True,exist_ok=True)

    if not config_file.exists():
        open(config_file,"x")

    with config_file.open("rb") as f:
        config = tomllib.load(f)

    template_file = Path(typer.get_app_dir(APP_NAME)) / "template.cpp"
    if not template_file.exists():
        open(template_file,"x")

    if "code" not in config:
        config["code"] = {}
    config["code"]["template_file"] = str(template_file.resolve())
    return config

def read_problem_file(problem_path:Path) -> CFProblem:
    problem_toml = problem_path / "problem.toml"
    if not problem_toml.exists():
        raise Exception("No problem.toml found, you need to run this command in a problem folder")
    with open(problem_toml, "rb") as f:
        problem_data = tomllib.load(f)
    cf_problem = from_dict(data_class=CFProblem, data=problem_data)
    return cf_problem
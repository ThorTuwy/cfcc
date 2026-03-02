from pathlib import Path
from urllib.parse import urlsplit
from typing import Annotated, Any, Dict

import tomllib
import tomli_w
import typer
from dacite import from_dict
from rich.console import Console

from Codeforces.Codeforces import CFProblem,Codeforces

import cli_commands.problem_test
import cli_commands.generate_problem
import beautifier.problem


APP_NAME = "cfcc"
app = typer.Typer()
console = Console()

def load_config() -> Dict[str,Any]:
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

def read_problem_toml(problem_path:Path) -> CFProblem:
    problem_toml = problem_path / "problem.toml"
    if not problem_toml.exists():
        raise Exception("No problem.toml found, you need to run this command in a problem folder")
    with open(problem_toml, "rb") as f:
        problem_data = tomllib.load(f)
    cf_problem = from_dict(data_class=CFProblem, data=problem_data)
    return cf_problem

@app.command("problem")
def cli_get_problem(
    problem_url: Annotated[str, typer.Argument()] = "",
    problem_path_location: Annotated[
    Path,
    typer.Argument(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=True,
    ),
    ]=Path.cwd(),
):
    """Get a problem from Codeforces."""
    if not problem_url:
        print("No problem URL provided")
        return

    split_url=urlsplit(problem_url)
    if split_url is None:
        print("Invalid URL")
        return

    split_url_path=(split_url.path[1:]).split("/")
    if len(split_url_path) != 4:
        print("Incorrect URL")
        return

    is_gym = split_url_path[0] == "gym"
    contest_id=split_url_path[1]
    problem_index=split_url_path[3]

    config = load_config()
    codeforces_api = Codeforces(config.get("codeforces", {}))

    cf_problem = codeforces_api.get_problem(contest_id, problem_index, is_gym)

    template_file = config.get("code", {}).get("template_file", "")

    cli_commands.generate_problem.generate_problem(problem_path_location, cf_problem,template_file)

@app.command("contest")
def cli_get_contest(
    contest_url: Annotated[str, typer.Argument()] = "",
    contest_path_location: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ]=Path.cwd()
):
    """Get a contest from Codeforces."""
    if not contest_url:
        print("No contest URL provided")
        return

    split_url=urlsplit(contest_url)
    if split_url is None:
        print("Invalid URL")
        return

    split_url_path=(split_url.path[1:]).split("/")
    if len(split_url_path) != 2:
        print("Incorrect URL")
        return

    is_gym = split_url_path[0] == "gym"
    contest_id=split_url_path[1]

    config = load_config()
    codeforces_api = Codeforces(config.get("codeforces", {}))

    cf_contest = codeforces_api.get_contest(contest_id, is_gym)

    contest_folder = contest_path_location / contest_id
    contest_folder.mkdir()

    basic_contest_data = {
        "id": contest_id,
        "url": contest_url,
        "title": cf_contest.title,
        "problems": cf_contest.problems
    }

    with open(contest_folder / "contest.toml","wb") as f:
        tomli_w.dump(basic_contest_data,f)

    template_file = config.get("code", {}).get("template_file", "")

    for problem_index in cf_contest.problems:
        cf_problem = codeforces_api.get_problem(contest_id, problem_index, is_gym)
        cli_commands.generate_problem.generate_problem(contest_folder, cf_problem,template_file)

@app.command("read")
def read_problem():
    """
    Read the problem you are currently in.
    """
    current_path = Path.cwd()
    cf_problem = read_problem_toml(current_path)

    beautifier.problem.print_problem(console,cf_problem)

@app.command("test")
def test_problem():
    """
    Test the problem you are currently in.
    """
    current_path = Path.cwd()
    cf_problem = read_problem_toml(current_path)

    problem_code_file = current_path / f"{cf_problem.problem_index}.cpp"

    config = load_config()

    compilation_command = config.get("code", {}).get("compilation_command", None)

    cli_commands.problem_test.test_problem(console,current_path, problem_code_file, compilation_command)

if __name__ == "__main__":
    app()

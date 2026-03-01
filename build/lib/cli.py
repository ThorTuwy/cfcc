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
        return tomllib.load(f)

@app.command("problem")
def cli_get_problem(
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
    ],
    problem_url: Annotated[str, typer.Option("--url",help="URL of the problem", )] = "",
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

    cli_commands.generate_problem.generate_problem(problem_path_location, cf_problem)

@app.command("contest")
def cli_get_contest(
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
    ],
    contest_url: Annotated[str, typer.Option("--url",help="URL of the problem", )] = "",
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

    for problem_index in cf_contest.problems:
        cf_problem = codeforces_api.get_problem(contest_id, problem_index, is_gym)
        cli_commands.generate_problem.generate_problem(contest_folder, cf_problem)

@app.command("read")
def read_problem():
    current_path = Path.cwd()
    problem_toml = current_path / "problem.toml"
    if not problem_toml.exists():
        print("No problem.toml found, you need to run this command in a problem folder")
        return
    with open(problem_toml, "rb") as f:
        problem_data = tomllib.load(f)
    cf_problem = from_dict(data_class=CFProblem, data=problem_data)

    beautifier.problem.print_problem(console,cf_problem)

@app.command("test")
def test_problem():
    current_path = Path.cwd()
    problem_code_file = current_path / "problem.cpp"

    config = load_config()

    compilation_command = config.get("code", {}).get("compilation_command", "")

    cli_commands.problem_test.test_problem(console,current_path, problem_code_file, compilation_command)

if __name__ == "__main__":
    app()

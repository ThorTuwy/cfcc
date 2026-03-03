from pathlib import Path
from urllib.parse import urlsplit
from typing import Annotated

import tomli_w
import typer
from rich.console import Console
from rich.progress import track

from Codeforces.Codeforces import Codeforces

import cli_commands.problem_test
import cli_commands.generate_problem
import beautifier.problem

from utils.file_managment import load_general_config_file, read_problem_file

app = typer.Typer()
console = Console()

@app.command("problem")
def cli_get_problem(
    problem: Annotated[str, typer.Argument(help="ID or URL of the problem ( id format: contest_id-problem_index ej: 1337-A )")],
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
    is_gym: Annotated[bool|None, typer.Option("--gym",help="Is the contest a gym contest (Auto inferred if use the URL)", )] = None,
):
    """Get a problem from Codeforces."""
    if len(problem.split("-")) == 2:
        contest_id,problem_index=problem.split("-")
    elif problem.startswith("http"):
        problem_url=problem
        split_url = urlsplit(problem_url)
        if split_url is None:
            print("Invalid URL")
            return

        split_url_path = (split_url.path[1:]).split("/")
        if len(split_url_path) != 4:
            print("Incorrect URL")
            return
        if is_gym is None:
            is_gym = split_url_path[0] == "gym"
        contest_id = split_url_path[1]
        problem_index = split_url_path[3]
    else:
        print("Invalid problem id")
        return

    config = load_general_config_file()
    codeforces_api = Codeforces(config.get("codeforces", {}))

    cf_problem = codeforces_api.get_problem(contest_id, problem_index, is_gym)

    template_file = config.get("code", {}).get("template_file", "")

    cli_commands.generate_problem.generate_problem(problem_path_location, cf_problem,template_file)

@app.command("contest")
def cli_get_contest(
    contest: Annotated[str, typer.Argument(help="ID or URL of the contest")],
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
    ]=Path.cwd(),
    is_gym: Annotated[bool|None, typer.Option("--gym",help="Is the contest a gym contest (Auto inferred if use the URL)", )] = None,
):
    """Get a contest from Codeforces."""
    if contest.isnumeric():
        contest_id=contest
    elif contest.startswith("http"):
        contest_url=contest
        split_url=urlsplit(contest_url)
        if split_url is None:
            print("Invalid URL")
            return

        split_url_path=(split_url.path[1:]).split("/")
        if len(split_url_path) != 2:
            print("Incorrect URL")
            return
        if is_gym is None:
            is_gym = split_url_path[0] == "gym"
        contest_id = split_url_path[1]
    else:
        print("Invalid contest id")
        return

    config = load_general_config_file()
    codeforces_api = Codeforces(config.get("codeforces", {}))

    cf_contest = codeforces_api.get_contest(contest_id, is_gym)

    contest_folder = contest_path_location / contest_id
    contest_folder.mkdir()

    basic_contest_data = {
        "id": contest_id,
        "url": f"{codeforces_api.requester.url}/contest/{contest_id}",
        "title": cf_contest.title,
        "problems": cf_contest.problems
    }

    with open(contest_folder / "contest.toml","wb") as f:
        tomli_w.dump(basic_contest_data,f)

    template_file = config.get("code", {}).get("template_file", "")

    for problem_index in track(cf_contest.problems, description="Downloading problems..."):
        cf_problem = codeforces_api.get_problem(contest_id, problem_index, is_gym)
        cli_commands.generate_problem.generate_problem(contest_folder, cf_problem,template_file)

@app.command("read")
def read_problem():
    """
    Read the problem you are currently in.
    """
    current_path = Path.cwd()
    cf_problem = read_problem_file(current_path)

    beautifier.problem.print_problem(console,cf_problem)

@app.command("test")
def test_problem():
    """
    Test the problem you are currently in.
    """
    current_path = Path.cwd()
    cf_problem = read_problem_file(current_path)

    problem_code_file = current_path / f"{cf_problem.problem_index}.cpp"

    config = load_general_config_file()

    compilation_command = config.get("code", {}).get("compilation_command", None)

    cli_commands.problem_test.test_problem(console,current_path, problem_code_file, compilation_command)

if __name__ == "__main__":
    app()

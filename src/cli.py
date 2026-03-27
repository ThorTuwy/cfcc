import dataclasses
from pathlib import Path
from urllib.parse import urlsplit
from typing import Annotated

import tomlkit
import typer
from rich.console import Console
from yaspin import yaspin
from yaspin.spinners import Spinners

from Codeforces.Codeforces import Codeforces

import cli_commands.problem_test
import cli_commands.generate_problem
import beautifier.problem, beautifier.submission_table

from utils.file_managment import read_problem_file, read_contest_file
from utils.program_configs import ProgramConfigs

app = typer.Typer()
console = Console()

@app.command("regenerate_configs")
def force_regenerate_configs():
    """Forces the configs to regenerate by default"""
    regenerate_confirmation = typer.confirm("Are you sure you want to regenerate your configs? THIS WILL DELETE YOUR CURRENT CONFIGS")
    if not regenerate_confirmation:
        raise typer.Abort()
    ProgramConfigs.regenerate_config()
    print("Config regenerate successfully")

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
        if is_gym is None:
            is_gym = False
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

    problem_folder = problem_path_location / problem_index
    if problem_folder.exists():
        print(f"Folder {problem_folder} already exists")
        return

    config = ProgramConfigs.get_program_config()
    codeforces_api = Codeforces(config.codeforces_config)

    with yaspin(Spinners.earth, text="Fetching problem...") as sp:
        cf_problem = codeforces_api.get_problem(contest_id, problem_index, is_gym)
        sp.ok(f"> Problem {problem_index} downloaded successfully\n")

    template_file = config.code_config.template_file_path

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
        if is_gym is None:
            is_gym = False
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

    contest_folder = contest_path_location / contest_id
    if contest_folder.exists():
        print(f"Folder {contest_folder} already exists")
        return
    contest_folder.mkdir()

    config = ProgramConfigs.get_program_config()
    codeforces_api = Codeforces(config.codeforces_config)
    cf_contest = codeforces_api.get_contest(contest_id, is_gym)

    with open(contest_folder / "contest.toml","w") as f:
        tomlkit.dump(dataclasses.asdict(cf_contest),f)

    template_file = config.code_config.template_file_path

    with yaspin(Spinners.earth, text="Fetching problems...") as sp:
        for problem_index in cf_contest.problems:
            cf_problem = codeforces_api.get_problem(contest_id, problem_index, is_gym)
            cli_commands.generate_problem.generate_problem(contest_folder, cf_problem,template_file)
            sp.write(f"> Problem {problem_index} downloaded successfully")

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

    config = ProgramConfigs.get_program_config()

    compilation_command = config.code_config.compile_command

    cli_commands.problem_test.test_problem(console,current_path, problem_code_file, compilation_command)

@app.command("submit")
def submit_problem(
        yolo: Annotated[bool, typer.Option("--yolo",help="Send your program without trying your test and without confirmation.", )] = False,
        no_confirmation: Annotated[bool, typer.Option("--no-confirm",help="Disable confirmation.", )] = False,
        no_test: Annotated[bool, typer.Option("--no-test",help="Disable test.", )] = False,
    ):
    """
    Submit the problem (With included test and confirmation) you are currently in.
    """
    current_path = Path.cwd()
    cf_problem = read_problem_file(current_path)

    problem_code_file = current_path / f"{cf_problem.problem_index}.cpp"

    config = ProgramConfigs.get_program_config()

    if not yolo:
        if not no_test:
            compilation_command = config.code_config.compile_command
            cli_commands.problem_test.test_problem(console,current_path, problem_code_file, compilation_command)

        if not no_confirmation:
            submit_code_confirmation=typer.confirm("Are you sure you want to submit this problem?")
            if not submit_code_confirmation:
                raise typer.Abort()

    problem_code_text = problem_code_file.read_text()

    codeforces_api = Codeforces(config.codeforces_config)
    with yaspin(Spinners.earth, text="Submitting your problem...") as sp:
        codeforces_api.submit_problem(cf_problem.contest_id, cf_problem.problem_index, problem_code_text, cf_problem.is_gym)
        sp.ok(f"> Problem {cf_problem.problem_index} submitted successfully, good luck o7\n")

@app.command("submissions")
def get_submissions_table():
    """
    Get a live updating table with your submissions for your current contest.
    """
    current_path = Path.cwd()
    cf_contest = read_contest_file(current_path)

    config = ProgramConfigs.get_program_config()
    codeforces_api = Codeforces(config.codeforces_config)

    submissions_stream = codeforces_api.stream_submission_table(cf_contest.id, cf_contest.is_gym)
    beautifier.submission_table.display_submission_table(cf_contest.title, cf_contest.problems, console, submissions_stream)

if __name__ == "__main__":
    app()

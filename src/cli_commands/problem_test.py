import subprocess
from pathlib import Path

from rich.console import Console

import beautifier.errors
from beautifier.test_case import TestCaseVerdict
import beautifier.test_case

def _read_problem_testcases(problem_path:Path):
    testcases: list[tuple[str, str]] = []
    i = 1

    while True:
        in_path = problem_path / f"{i}.in"
        out_path = problem_path / f"{i}.out"

        if not in_path.exists() or not out_path.exists():
            break

        testcases.append((in_path.read_text(encoding="utf-8"),
                          out_path.read_text(encoding="utf-8")))
        i += 1

    if not testcases:
        raise ValueError("No test cases found")

    return testcases

def _compile_solution(console:Console,compilation_command: str, workdir: Path) -> Path:
    result = subprocess.run(
        compilation_command,
        shell=True,
        cwd=workdir,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        beautifier.errors.print_compilation_error(console,result.stdout, result.stderr)
        raise RuntimeError()

    problem_exe = workdir / "problem"
    if not problem_exe.exists():
        raise RuntimeError(f"Compilation succeeded but executable not found: {problem_exe}")
    return problem_exe

def _run_testcases(console:Console,problem_exe: Path, testcases: list[tuple[str, str]], time_limit: float=5):
    for idx, test_case in enumerate(testcases):

        case_input,expected_output = test_case

        run = subprocess.run(
            [str(problem_exe)],
            input=case_input,
            capture_output=True,
            text=True,
            timeout=time_limit
        )

        case_verdict = TestCaseVerdict.OK

        if run.returncode != 0:
            case_verdict = TestCaseVerdict.RUNTIME_ERROR
        elif run.stdout.strip() != expected_output.strip():
            case_verdict = TestCaseVerdict.WRONG_ANSWER

        beautifier.test_case.print_test_case(console,case_verdict, str(idx+1), case_input, expected_output, run.stdout, run.stderr)


DEFAULT_COMPILATION_COMMAND = "g++ -Wall -Wextra -Wshadow -Wfloat-equal -fsanitize=address -fsanitize=undefined -fno-sanitize-recover=undefined -std=c++23"

def test_problem(console:Console,problem_path:Path,problem_code_file:Path, user_compilation_command:str|None=None):

    if user_compilation_command is None:
        user_compilation_command = DEFAULT_COMPILATION_COMMAND

    testcases = _read_problem_testcases(problem_path)

    compilation_command = f"{user_compilation_command} {problem_code_file} -o problem"
    print(compilation_command)
    problem_exe=_compile_solution(console,compilation_command, problem_path)
    _run_testcases(console,problem_exe, testcases)






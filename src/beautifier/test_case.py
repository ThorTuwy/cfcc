from enum import Enum
from rich import box
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax


class TestCaseVerdict(Enum):
    OK = 1
    RUNTIME_ERROR = 2
    WRONG_ANSWER = 3

def print_test_case(console:Console,verdict:TestCaseVerdict, testcase_id:str, problem_input:str, expected_output:str, output:str, stderr:str):
    """
        Prints one "cool" table per test case.
        - OK  -> green table with 3 columns: Input | Expected output | Output
        - WA  -> red   table with the same 3 columns
        - RE  -> red   table that ONLY contains stderr
        """

    is_ok = verdict == TestCaseVerdict.OK
    is_wa = verdict == TestCaseVerdict.WRONG_ANSWER
    is_re = verdict == TestCaseVerdict.RUNTIME_ERROR

    border_style = "green" if is_ok else "red"
    title = f"[bold]Case {testcase_id}[/bold] • " + (
        "[bold green]OK[/bold green]" if is_ok else
        "[bold red]WA[/bold red]" if is_wa else
        "[bold red]RUNTIME ERROR[/bold red]"
    )

    if is_re:
        t = Table(
            title=title,
            box=box.ROUNDED,
            border_style=border_style,
            show_header=True,
            show_lines=True,
            expand=True,
        )
        t.add_column("stderr", style="red", overflow="fold")
        t.add_row(Syntax(stderr or "(no stderr)", "text", word_wrap=True))
        console.print(t)
        return

    # OK / WA (same structure, different color)
    t = Table(
        title=title,
        box=box.ROUNDED,
        border_style=border_style,
        show_header=True,
        show_lines=True,
        expand=True,
    )
    t.add_column("Input", style="cyan", overflow="fold", ratio=1)
    t.add_column("Expected output", style="green", overflow="fold", ratio=1)
    t.add_column("Output", style="yellow", overflow="fold", ratio=1)

    t.add_row(
        Syntax((problem_input or "").strip(), "text", word_wrap=True),
        Syntax((expected_output or "").strip(), "text", word_wrap=True),
        Syntax((output or "").strip(), "text", word_wrap=True),
    )

    console.print(t)

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

def print_compilation_error(console:Console,compiler_stdout:str,compiler_stderr:str):
    stdout_panel = Panel(
        Syntax(compiler_stdout or "", "text", word_wrap=True),
        title="[bold yellow]Compiler stdout[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
    )
    stderr_panel = Panel(
        Syntax(compiler_stderr or "", "text", word_wrap=True),
        title="[bold red]Compiler stderr[/bold red]",
        border_style="red",
        box=box.ROUNDED,
    )

    console.print(stdout_panel,stderr_panel)
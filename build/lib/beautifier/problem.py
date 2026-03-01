from rich import box
from rich.console import Group, Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich.align import Align
from rich.constrain import Constrain
from Codeforces.Codeforces import CFProblem

def print_problem(console:Console,problem: CFProblem):
    renderables = []

    #Problem header
    title_text = Text(problem.title, justify="center", style="bold bright_cyan")

    limits_table = Table(show_header=False, box=None, expand=True)
    limits_table.add_column(justify="right", ratio=1)
    limits_table.add_column(justify="center", width=3)
    limits_table.add_column(justify="left", ratio=1)
    limits_table.add_row(
        f"[bold yellow]Time Limit:[/bold yellow] {problem.time_limit}s",
        "|",
        f"[bold magenta]Memory Limit:[/bold magenta] {problem.memory_limit} MB"
    )
    header_group = Group(title_text, Rule(style="cyan"), limits_table)
    renderables.append(
        Panel(header_group, box=box.DOUBLE_EDGE, border_style="cyan", padding=(1, 2))
    )
    renderables.append(Text("\n"))

    # Main content
    renderables.append(
        Panel(problem.statement_md.strip(), title="[bold blue]Problem Statement[/bold blue]",
              title_align="left", border_style="blue", padding=(1, 2))
    )
    renderables.append(
        Panel(problem.input_md.strip(), title="[bold yellow]Input[/bold yellow]",
              title_align="left", border_style="yellow", padding=(1, 2))
    )
    renderables.append(
        Panel(problem.output_md.strip(), title="[bold green]Output[/bold green]",
              title_align="left", border_style="green", padding=(1, 2))
    )

    # Samples
    samples_table = Table(
        title="[bold magenta]Samples[/bold magenta]",
        title_justify="left",
        box=box.ROUNDED,
        expand=True,
        show_lines=True
    )
    samples_table.add_column("Input", style="cyan", ratio=1)
    samples_table.add_column("Output", style="green", ratio=1)

    for sample in problem.samples:
        samples_table.add_row(
            sample["input"],
            sample["output"]
        )

    renderables.append(samples_table)

    main_content = Group(*renderables)

    renderable = Align.center(Constrain(main_content, width=145))

    console.print(renderable)


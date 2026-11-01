import argparse
import sys

from . import __version__
from .modules import (
    INKS,
    FONTS,
    PAPERS,
    DEFAULT_FILENAME,
    DEFAULT_PDF_FILENAME,
    Assignment,
    AssignmentConfigOptions,
    resolve_ink,
    resolve_font,
    resolve_paper,
    read_text_file,
    available_fonts,
    available_papers,
)

try:
    from rich.console import Console
    from rich.markup import escape
    from rich.prompt import Prompt
    from rich.table import Table
except ImportError:
    Console = None


def _use_rich(as_text: bool) -> bool:
    return Console is not None and not as_text


def _say(paths: list, as_text: bool) -> None:
    for path in paths:
        if _use_rich(as_text):
            Console().print(f"[bold green]Saved:[/bold green] {escape(path)}")
        else:
            print(path)


def _fail(message: str) -> int:
    if Console is not None:
        Console(stderr=True).print(f"[bold red]Error:[/bold red] {escape(message)}")
    else:
        print(f"Error: {message}", file=sys.stderr)
    return 1


def _ask(label, default=None, validate=None, choices=None, as_text=False):
    """Ask a question until the answer is accepted. Raises EOFError if input ends."""
    while True:
        if _use_rich(as_text):
            options = {}
            if default is not None:
                options["default"] = default
            hint = f" ({'/'.join(choices)})" if choices else ""
            answer = Prompt.ask(f"{label}{hint}", **options)
        else:
            hint = f" [{'/'.join(choices)}]" if choices else ""
            shown = f" ({default})" if default is not None else ""
            answer = input(f"{label}{hint}{shown}: ")

        answer = answer.strip()
        if not answer:
            if default is None:
                continue
            answer = default
        if validate is None:
            return answer
        try:
            return validate(answer)
        except ValueError as error:
            _fail(str(error))


def _create(text, paper, font, ink, keep_line_breaks, save, as_text, pdf=False) -> int:
    try:
        config = AssignmentConfigOptions(
            Text=text,
            Paper=paper,
            Font=font,
            Ink=ink,
            KeepLineBreaks=keep_line_breaks,
        )
    except ValueError as error:
        return _fail(str(error))

    result = Assignment(config).create()
    if not result:
        return _fail("Could not create the assignment pages")

    if pdf:
        path = result.save_pdf(save)
        paths = [path] if path else None
    else:
        paths = result.save(save)
    if not paths:
        return _fail("Could not save the assignment pages")

    _say(paths, as_text)
    return 0


def _interactive(args) -> int:
    try:
        text = _ask("Text to write", as_text=args.as_text)
        paper = _ask(
            "Paper", args.paper, resolve_paper, available_papers(), args.as_text
        )
        font = _ask("Font", args.font, resolve_font, available_fonts(), args.as_text)
        ink = _ask("Ink", args.ink, resolve_ink, list(INKS), args.as_text)
        default_name = DEFAULT_PDF_FILENAME if args.pdf else DEFAULT_FILENAME
        save = _ask("Save as", args.save or default_name, as_text=args.as_text)
    except (EOFError, KeyboardInterrupt):
        print(file=sys.stderr)
        return 1
    return _create(
        text, paper, font, ink, args.keep_line_breaks, save, args.as_text, args.pdf
    )


def _list(argv) -> int:
    parser = argparse.ArgumentParser(
        prog="assignmentwriter list",
        description="Show the papers, fonts and inks that can be used.",
    )
    parser.add_argument(
        "--as-text",
        action="store_true",
        help="plain line-by-line output instead of tables",
    )
    args = parser.parse_args(argv)
    fonts = available_fonts()
    papers = available_papers()

    if _use_rich(args.as_text):
        console = Console()

        table = Table(title="Papers")
        table.add_column("Name", style="cyan")
        for name in papers:
            table.add_row(name)
        console.print(table)

        table = Table(title="Fonts")
        table.add_column("No.", justify="right")
        table.add_column("Name", style="cyan")
        for number, name in enumerate(FONTS, start=1):
            if name in fonts:
                table.add_row(str(number), name)
        console.print(table)

        table = Table(title="Inks")
        table.add_column("Name", style="cyan")
        table.add_column("RGB")
        for name, rgb in INKS.items():
            table.add_row(name, ", ".join(str(value) for value in rgb))
        console.print(table)
    else:
        for name in papers:
            print(f"paper\t{name}")
        for name in fonts:
            print(f"font\t{name}")
        for name in INKS:
            print(f"ink\t{name}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="assignmentwriter",
        description=(
            "Write an assignment on paper in your choice of handwriting and ink. "
            "Long text continues on more pages."
        ),
        epilog=(
            "Run with no arguments for an interactive prompt, or "
            "'assignmentwriter list' to see every paper, font and ink."
        ),
    )
    parser.add_argument("text", nargs="?", help="the text to write")
    parser.add_argument("--file", help="read the text from this UTF-8 text file")
    parser.add_argument(
        "--paper",
        default="a4",
        help=f"{', '.join(PAPERS)} (default: a4)",
    )
    parser.add_argument(
        "--font", default="caveat", help="font name or number (default: caveat)"
    )
    parser.add_argument(
        "--ink",
        default="blue",
        help=f"{', '.join(INKS)} or a hex colour (default: blue)",
    )
    parser.add_argument(
        "--save",
        help=(
            f"where to save (default: {DEFAULT_FILENAME}, or {DEFAULT_PDF_FILENAME} "
            "with --pdf). Long text goes on several pages: name_1.png, name_2.png, ..."
        ),
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="save all the pages together as one PDF instead of images",
    )
    parser.add_argument(
        "--keep-line-breaks",
        action="store_true",
        help="start a new line wherever the text has one",
    )
    parser.add_argument(
        "--as-text",
        action="store_true",
        help="plain output (just the saved path, no colors)",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)

    # "list" is a command only when it is the first word, to write the word
    # "list" on its own put it in a file and use --file
    if argv and argv[0] == "list":
        return _list(argv[1:])

    parser = _build_parser()
    args = parser.parse_args(argv)

    text = args.text
    if args.file is not None:
        if text is not None:
            parser.error("give the text directly or with --file, not both")
        try:
            text = read_text_file(args.file)
        except ValueError as error:
            return _fail(str(error))
    elif text is None:
        if sys.stdin is not None and not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            return _interactive(args)

    return _create(
        text,
        args.paper,
        args.font,
        args.ink,
        args.keep_line_breaks,
        args.save,
        args.as_text,
        args.pdf,
    )


if __name__ == "__main__":
    sys.exit(main())

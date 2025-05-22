import logging

from rich.console import Console


def setup_logging_with_rich(debug: bool = False):
    import sys

    from rich.logging import RichHandler

    level = logging.DEBUG if debug else logging.WARNING

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                markup=True,
                console=Console(file=sys.stderr),
            )
        ],
    )
    logging.getLogger("ctfdl").setLevel(level)

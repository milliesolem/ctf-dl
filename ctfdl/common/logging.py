import logging

from ctfdl.common.console import console


def setup_logging_with_rich(debug: bool = False):
    from rich.logging import RichHandler

    level = logging.DEBUG if debug else logging.ERROR

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True, console=console)],
    )
    logging.getLogger("ctfdl").setLevel(level)

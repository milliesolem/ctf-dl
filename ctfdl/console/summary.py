from rich.console import Console
from collections import Counter
from .decorators import verbosity_required
from .config import output_config

console = Console()

@verbosity_required(level=1)
def print_summary(challenges: list, duration: float):
    total = len(challenges)
    categories = Counter(c.category for c in challenges)

    console.print(f"\n📦 Found [bold]{total}[/] challenges in [cyan]{len(categories)}[/] categories")
    for cat, count in categories.items():
        console.print(f"  • [magenta]{cat}[/]: {count}")

    console.print(f"\n✅ Downloaded [bold green]{total}[/] challenges in {duration:.1f}s")
    output_config.log(f"Downloaded {total} challenges in {duration:.1f}s")

@verbosity_required(level=2)
def print_skipped_challenges(skipped: list[str]):
    if not skipped:
        return
    console.print(f"⏭ Skipped {len(skipped)} existing challenges:")
    for name in skipped:
        console.print(f"  • [dim]{name}[/]")

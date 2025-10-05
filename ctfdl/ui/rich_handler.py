import asyncio

from ctfbridge.models.challenge import Challenge, ProgressData
from rich.console import Console
from rich.live import Live
from rich.progress import Progress, ProgressColumn, SpinnerColumn, TextColumn
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

import ctfdl.ui.messages as console_utils
from ctfdl.core.events import EventEmitter


def handles(event_name: str):
    """Decorator to mark a method as an event handler for `event_name`."""

    def decorator(func):
        func._event_name = event_name
        return func

    return decorator


class AdaptiveTimeColumn(ProgressColumn):
    def render(self, task):
        elapsed = int(task.elapsed or 0)
        if elapsed < 60:
            text = f"{elapsed}s"
        else:
            minutes, seconds = divmod(elapsed, 60)
            text = f"{minutes}m {seconds:02d}s"
        return Text(text, style="yellow")


class RichConsoleHandler:
    def __init__(self, emitter: EventEmitter):
        self._console = Console()
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            TextColumn("[green]({task.completed} downloaded)"),
            AdaptiveTimeColumn(),
            console=self._console,
        )
        self._tree = Tree(self._progress)
        self._live = Live(
            self._tree,
            console=self._console,
            refresh_per_second=10,
            transient=True,
        )

        self._main_task_id = None
        self._category_nodes: dict[str, dict] = {}
        self._challenge_nodes: dict[str, dict] = {}
        self._attachment_nodes: dict[str, any] = {}
        self._lock = asyncio.Lock()

        self._stats = {"downloaded": 0, "updated": 0, "skipped": 0}

        # Register handles
        for attr_name in dir(self):
            fn = getattr(self, attr_name)
            if callable(fn) and hasattr(fn, "_event_name"):
                emitter.on(fn._event_name, fn)

    # ===== Connection =====

    @handles("connect_start")
    def on_connect_start(self, url: str):
        self._live.start()
        self._main_task_id = self._progress.add_task(
            description=f"Connecting to {url}...", total=None
        )

    @handles("connect_success")
    def on_connect_success(self):
        self._progress.update(self._main_task_id, description="Connection established")

    @handles("connect_fail")
    def on_connect_fail(self, reason: str):
        if self._live.is_started:
            self._live.stop()
        console_utils.connection_failed(reason, console=self._console)

    # ===== Download Lifecycle =====

    @handles("download_start")
    def on_download_start(self):
        self._progress.update(self._main_task_id, description="Downloading challenges")

    @handles("no_challenges_found")
    def on_no_challenges_found(self):
        if self._main_task_id:
            self._progress.update(self._main_task_id, description="No challenges found")
        console_utils.no_challenges_found(console=self._console)

    @handles("download_fail")
    def on_download_fail(self, msg: str):
        if self._live.is_started:
            self._live.stop()
        console_utils.error(msg)

    @handles("download_success")
    def on_download_success(self):
        if self._live.is_started:
            self._live.stop()

        downloaded = self._stats["downloaded"]
        updated = self._stats["updated"]
        skipped = self._stats["skipped"]
        total = downloaded + updated + skipped

        if updated == 0 and skipped == 0:
            console_utils.download_success_new(downloaded, console=self._console)
        elif skipped == total:
            console_utils.download_success_skipped_all(skipped, console=self._console)
        elif updated == total:
            console_utils.download_success_updated_all(updated, console=self._console)
        else:
            console_utils.download_success_summary(
                downloaded, updated, skipped, console=self._console
            )

    @handles("download_complete")
    def on_download_complete(self):
        if self._live.is_started:
            self._live.stop()

    # ===== Per-Challenge =====

    @handles("challenge_skipped")
    def on_challenge_skipped(self, challenge: Challenge):
        self._stats["skipped"] += 1

    @handles("challenge_start")
    async def on_challenge_start(self, challenge: Challenge):
        async with self._lock:
            if challenge.category not in self._category_nodes:
                node = self._tree.add(f"📁 [bold cyan]{challenge.category}[/bold cyan]")
                self._category_nodes[challenge.category] = {"node": node, "count": 0}
            category_info = self._category_nodes[challenge.category]
            parent_node = category_info["node"]
            category_info["count"] += 1
            challenge_node = parent_node.add(f"📂 [bold]{challenge.name}[/bold]")
            self._challenge_nodes[challenge.name] = {
                "node": challenge_node,
                "parent": parent_node,
            }

    @handles("challenge_fail")
    def on_challenge_fail(self, challenge: Challenge, reason: str):
        console_utils.failed_challenge(challenge.name, reason, console=self._console)

    @handles("challenge_complete")
    async def on_challenge_complete(self, challenge: Challenge):
        async with self._lock:
            if challenge.name in self._challenge_nodes:
                node_info = self._challenge_nodes.pop(challenge.name)
                challenge_node = node_info["node"]
                parent_node = node_info["parent"]
                if parent_node and challenge_node in parent_node.children:
                    parent_node.children.remove(challenge_node)

            if challenge.category in self._category_nodes:
                category_info = self._category_nodes[challenge.category]
                category_info["count"] -= 1
                if category_info["count"] == 0:
                    category_node_to_remove = category_info["node"]
                    if category_node_to_remove in self._tree.children:
                        self._tree.children.remove(category_node_to_remove)
                    del self._category_nodes[challenge.category]

            if self._main_task_id is not None:
                self._progress.update(self._main_task_id, advance=1)

    @handles("challenge_downloaded")
    def on_challenge_downloaded(self, challenge: Challenge, updated: bool = False):
        if updated:
            self._stats["updated"] += 1
        else:
            self._stats["downloaded"] += 1

    # ===== Attachments =====

    @handles("attachment_progress")
    async def on_attachment_progress(self, progress_data: ProgressData, challenge: Challenge):
        pd = progress_data
        async with self._lock:
            challenge_node_info = self._challenge_nodes.get(challenge.name)
            if not challenge_node_info:
                return
            challenge_node = challenge_node_info["node"]
            attachment_node = self._attachment_nodes.get(pd.attachment.url)

            progress_bar = ProgressBar(
                total=pd.total_bytes, completed=pd.downloaded_bytes, width=30
            )
            grid = Table.grid(expand=False)
            grid.add_row(
                f"📄 {pd.attachment.name} ",
                progress_bar,
                f" [yellow]{pd.percentage:.2f}%[/yellow]",
            )

            if attachment_node is None:
                new_node = challenge_node.add(grid)
                self._attachment_nodes[pd.attachment.url] = new_node
            else:
                attachment_node.label = grid

            if pd.downloaded_bytes == pd.total_bytes:
                if attachment_node and attachment_node in challenge_node.children:
                    challenge_node.children.remove(attachment_node)
                self._attachment_nodes.pop(pd.attachment.url, None)

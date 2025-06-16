import asyncio
from rich.console import Console
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.tree import Tree
import ctfdl.ui.messages as console_utils
from ctfdl.events import EventEmitter
from ctfbridge.models.challenge import Challenge, ProgressData


class RichConsoleHandler:
    def __init__(self, emitter: EventEmitter):
        self._console = Console()
        # FIX: The main description is now a generic spinner
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            TextColumn("[green]({task.completed} downloaded)"),
            TimeElapsedColumn(),
            console=self._console,
        )
        self._tree = Tree(self._progress)
        self._live = Live(
            self._tree,
            console=self._console,
            refresh_per_second=10,
            transient=True, # This ensures the display is cleared on exit
        )
        
        self._main_task_id = None
        self._category_nodes = {}
        self._challenge_nodes = {}
        self._attachment_nodes = {}
        self._lock = asyncio.Lock()
        self._register_listeners(emitter)

    def _register_listeners(self, emitter: EventEmitter):
        emitter.on("connect_start", self.on_connect_start)
        emitter.on("connect_success", self.on_connect_success)
        emitter.on("connect_fail", self.on_connect_fail)
        emitter.on("download_start", self.on_download_start)
        emitter.on("no_challenges_found", self.on_no_challenges_found)
        emitter.on("challenge_start", self.on_challenge_start)
        emitter.on("attachment_progress", self.on_attachment_progress)
        emitter.on("challenge_fail", self.on_challenge_fail)
        emitter.on("challenge_complete", self.on_challenge_complete)
        emitter.on("download_complete", self.on_download_complete)

    def on_connect_start(self, url: str):
        # FIX: Start the live display immediately and set the initial status
        self._live.start()
        self._main_task_id = self._progress.add_task(
            description=f"Connecting to {url}...", total=None
        )

    def on_connect_success(self):
        # FIX: Don't print. Update the progress description.
        self._progress.update(self._main_task_id, description="Connection established")
        # You can add a brief asyncio.sleep(0.5) here if you want the message to be visible for a moment

    def on_connect_fail(self, reason: str):
        # Stop the live display and then print the permanent error message
        if self._live.is_started:
            self._live.stop()
        console_utils.connection_failed(reason, console=self._console)

    def on_download_start(self):
        # FIX: Don't print. Just update the progress description to its main state.
        self._progress.update(self._main_task_id, description="Downloading Challenges")

    def on_no_challenges_found(self):
        # Update the description to reflect the status before stopping
        if self._main_task_id:
            self._progress.update(self._main_task_id, description="No challenges found")
        console_utils.no_challenges_found(console=self._console)
        
    def on_download_complete(self, count: int):
        if self._live.is_started:
            self._live.stop()
            
    # --- The rest of the methods are unchanged ---

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

    def on_challenge_fail(self, challenge: Challenge, reason: str):
        console_utils.failed_challenge(
            challenge.name, reason, console=self._console
        )

    async def on_challenge_complete(self, challenge: Challenge):
        async with self._lock:
            # --- FIX for 'list.remove(x): x not in list' ---
            # Correctly retrieve parent and remove child node
            if challenge.name in self._challenge_nodes:
                node_info = self._challenge_nodes.pop(challenge.name)
                challenge_node = node_info["node"]
                parent_node = node_info["parent"]
                # Add a protective check to ensure the child is still present before removing
                if parent_node and challenge_node in parent_node.children:
                    parent_node.children.remove(challenge_node)

            # --- FIX for "name 'category' is not defined" ---
            if challenge.category in self._category_nodes:
                category_info = self._category_nodes[challenge.category]
                category_info["count"] -= 1
                if category_info["count"] == 0:
                    category_node_to_remove = category_info["node"]
                    # Add a protective check here as well
                    if category_node_to_remove in self._tree.children:
                        self._tree.children.remove(category_node_to_remove)
                    # Corrected typo from 'category.category' to 'challenge.category'
                    del self._category_nodes[challenge.category]

            if self._main_task_id is not None:
                self._progress.update(self._main_task_id, advance=1)

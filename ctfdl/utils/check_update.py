from importlib.metadata import PackageNotFoundError, version

import httpx
from rich.console import Console

console = Console()


def check_updates():
    packages_to_check = ["ctf-dl", "ctfbridge"]
    outdated = []

    def get_latest_version(pkg):
        try:
            resp = httpx.get(f"https://pypi.org/pypi/{pkg}/json", timeout=5)
            resp.raise_for_status()
            return resp.json()["info"]["version"]
        except Exception as e:
            console.print(f"⚠️ Failed to fetch version for [yellow]{pkg}[/]: {e}")
            return None

    def compare_versions(pkg):
        try:
            installed = version(pkg)
        except PackageNotFoundError:
            console.print(f"❌ [red]{pkg}[/] is not installed.")
            return

        latest = get_latest_version(pkg)
        if not latest:
            return

        if installed != latest:
            console.print(
                f"📦 [yellow]{pkg}[/]: update available → [red]{installed}[/] → [green]{latest}[/]"
            )
            outdated.append(pkg)
        else:
            console.print(f"✅ {pkg} is up to date ([green]{installed}[/])")

    console.print("🔍 Checking for updates...\n")
    for pkg in packages_to_check:
        compare_versions(pkg)

    if outdated:
        upgrade_cmd = "pip install --upgrade " + " ".join(outdated)
        console.print(f"\n🚀 To upgrade, run:\n[bold]{upgrade_cmd}[/bold]")
    else:
        console.print("\n🎉 All packages are up to date.")

"""CLI command for listing profiles."""

from rich.console import Console
from rich.table import Table

from dspy_profiles.config import ProfileManager, find_profiles_path

console = Console()


def list_profiles():
    """Lists all available profiles and their core details."""
    config_path = find_profiles_path()
    manager = ProfileManager(config_path)
    all_profiles = manager.load()
    if not all_profiles:
        console.print("[yellow]No profiles found. Use 'dspy-profiles init' to create one.[/yellow]")
        return

    table = Table("Profile Name", "Language Model (LM)", "API Base", "API Key", "Extends")
    for name, profile_data in all_profiles.items():
        lm_section = profile_data.get("lm", {})
        model = lm_section.get("model", "[grey50]Not set[/grey50]")
        api_base_value = lm_section.get("api_base")
        api_base = str(api_base_value) if api_base_value else "[grey50]Not set[/grey50]"
        api_key = lm_section.get("api_key")
        if api_key:
            api_key_display = f"{api_key[:4]}...{api_key[-4:]}"
        else:
            api_key_display = "[grey50]Not set[/grey50]"
        extends = profile_data.get("extends", "[grey50]None[/grey50]")
        table.add_row(name, model, api_base, api_key_display, extends)

    console.print(table)

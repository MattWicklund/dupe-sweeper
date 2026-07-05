import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from dupe_sweeper.engine.actions import delete_files, trash_files
from dupe_sweeper.engine.cache import clear_cache, get_cache_stats
from dupe_sweeper.engine.matcher import find_duplicates
from dupe_sweeper.engine.scanner import scan_files

console = Console()

PHOTO_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "heic",
    "tif",
    "tiff",
    "webp",
    "raw",
    "cr2",
    "nef",
    "arw",
]


def format_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)

    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024

    return f"{size} B"


def build_summary_table(
    scanned_files: int,
    duplicate_groups: int,
    duplicate_files: int,
    recoverable_bytes: int,
    quick_hashes: int,
    full_hashes: int,
    cache_hits: int,
    cache_misses: int,
) -> Table:
    table = Table(title="Scan Summary")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Files scanned", str(scanned_files))
    table.add_row("Duplicate groups", str(duplicate_groups))
    table.add_row("Duplicate files", str(duplicate_files))
    table.add_row("Recoverable space", format_bytes(recoverable_bytes))
    table.add_row("Quick hashes", str(quick_hashes))
    table.add_row("Full hashes", str(full_hashes))
    table.add_row("Cache hits", str(cache_hits))
    table.add_row("Cache misses", str(cache_misses))

    return table


def print_duplicate_groups(duplicate_groups: list[list[Path]]) -> None:
    for index, group in enumerate(duplicate_groups, start=1):
        keep = group[0]
        duplicates = group[1:]

        console.print(f"\n[bold]Group {index}[/bold]")
        console.print(f"  [green]KEEP[/green] {keep}")

        for duplicate in duplicates:
            console.print(f"  [red]DUPE[/red] {duplicate}")


def run_scan(args: argparse.Namespace) -> None:
    if args.trash and args.delete:
        console.print("[red]Choose either --trash or --delete, not both.[/red]")
        raise SystemExit(1)

    directory = Path(args.directory).expanduser().resolve()

    if not directory.exists():
        console.print(f"[red]Directory does not exist:[/red] {directory}")
        raise SystemExit(1)

    if not directory.is_dir():
        console.print(f"[red]Path is not a directory:[/red] {directory}")
        raise SystemExit(1)

    console.print(
        Panel.fit(
            f"[bold]dupe-sweeper[/bold]\nScanning: {directory}",
            border_style="blue",
        )
    )

    extensions = PHOTO_EXTENSIONS if args.photos else args.ext

    files = list(
        scan_files(
            directory,
            recursive=args.recursive,
            extensions=extensions,
            include_hidden=args.include_hidden,
        )
    )

    result = find_duplicates(files, keep=args.keep, show_progress=True)
    duplicate_groups = result.groups

    duplicate_files = [duplicate for group in duplicate_groups for duplicate in group[1:]]

    recoverable_bytes = sum(file.stat().st_size for file in duplicate_files)

    console.print()
    console.print(
        build_summary_table(
            scanned_files=len(files),
            duplicate_groups=len(duplicate_groups),
            duplicate_files=len(duplicate_files),
            recoverable_bytes=recoverable_bytes,
            quick_hashes=result.quick_hashes,
            full_hashes=result.full_hashes,
            cache_hits=result.cache_hits,
            cache_misses=result.cache_misses,
        )
    )

    if duplicate_groups and args.verbose:
        print_duplicate_groups(duplicate_groups)

    if not duplicate_groups:
        console.print("\n[green]No duplicates found.[/green]")
        return

    if args.trash:
        trashed_count = trash_files(duplicate_files)
        console.print(f"\n[green]Moved {trashed_count} duplicate file(s) to Trash.[/green]")
    elif args.delete:
        deleted_count = delete_files(duplicate_files)
        console.print(f"\n[red]Permanently deleted {deleted_count} duplicate file(s).[/red]")
    else:
        console.print(
            "\n[yellow]Dry run only. "
            "Re-run with --trash or --delete to remove duplicates."
            "[/yellow]"
        )
        console.print("[dim]Use --verbose to show every duplicate group.[/dim]")


def run_cache_clear() -> None:
    clear_cache()
    console.print("[green]Cache cleared.[/green]")


def run_cache_stats() -> None:
    stats = get_cache_stats()

    table = Table(title="Cache Stats")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Cache path", stats["path"])
    table.add_row("Entries", str(stats["entries"]))
    table.add_row("Size", format_bytes(int(stats["size_bytes"])))

    console.print(table)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dupe-sweeper",
        description="Find duplicate files safely.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan a directory for duplicates")
    scan_parser.add_argument("directory", help="Directory to scan")
    scan_parser.add_argument("-r", "--recursive", action="store_true", help="Scan subdirectories")
    scan_parser.add_argument("--trash", action="store_true", help="Move duplicate files to Trash")
    scan_parser.add_argument(
        "--delete",
        action="store_true",
        help="Permanently delete duplicate files",
    )
    scan_parser.add_argument(
        "--keep",
        choices=["original", "oldest", "newest", "shortest-name"],
        default="original",
        help="Which file to keep from each duplicate group",
    )
    scan_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show every duplicate group",
    )
    scan_parser.add_argument(
        "--ext",
        nargs="+",
        help="Only scan files with these extensions, e.g. --ext jpg png pdf",
    )

    scan_parser.add_argument(
        "--photos",
        action="store_true",
        help="Only scan common photo/image file types",
    )
    scan_parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories",
    )

    cache_parser = subparsers.add_parser("cache", help="Manage the hash cache")
    cache_subparsers = cache_parser.add_subparsers(dest="cache_command", required=True)

    cache_subparsers.add_parser("clear", help="Clear cached file hashes")
    cache_subparsers.add_parser("stats", help="Show cache statistics")

    args = parser.parse_args()

    if args.command == "scan":
        run_scan(args)
    elif args.command == "cache":
        if args.cache_command == "clear":
            run_cache_clear()
        elif args.cache_command == "stats":
            run_cache_stats()


if __name__ == "__main__":
    main()

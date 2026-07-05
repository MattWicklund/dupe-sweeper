# dupe-sweeper

A safe, fast duplicate file finder for the command line.

`dupe-sweeper` scans directories, finds exact duplicate files, and lets you review them before moving duplicates to Trash or permanently deleting them.

## Features

- Exact duplicate detection using file hashes
- Fast candidate filtering by file size and quick hash
- Hash cache for faster repeated scans
- Dry-run by default
- Move duplicates to Trash
- Optional permanent delete
- Keep strategies:
  - `original`
  - `oldest`
  - `newest`
  - `shortest-name`
- Recursive scanning
- Photo-only scanning
- Extension filtering
- Hidden files skipped by default

## Install locally

```bash
pip install -e .
```

## Usage

Scan a directory:

```bash
dupe-sweeper scan ~/Downloads
```

Scan recursively:

```bash
dupe-sweeper scan ~/Pictures --recursive
```

Show detailed duplicate groups:

```bash
dupe-sweeper scan ~/Pictures --recursive --verbose
```

Move duplicates to Trash:

```bash
dupe-sweeper scan ~/Pictures --recursive --trash
```

Photo files only:

```bash
dupe-sweeper scan ~/Pictures --recursive --photos
```

Specific file extensions:

```bash
dupe-sweeper scan ~/Documents --recursive --ext pdf docx xlsx
```

Clear cache:

```bash
dupe-sweeper cache clear
```

Show cache stats:

```bash
dupe-sweeper cache stats
```

## Safety

By default, `dupe-sweeper` performs a dry run only. Files are only removed when you explicitly pass `--trash` or `--delete`.

Prefer `--trash` over `--delete`.

## Development

```bash
pip install -e ".[dev]"
pytest
```

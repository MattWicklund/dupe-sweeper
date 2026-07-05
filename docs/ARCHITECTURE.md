# dupe-sweeper Architecture

## Overview

**dupe-sweeper** is a safe, fast, and extensible duplicate file finder designed to scale from a simple command-line utility into a full-featured desktop application.

The project is built around a shared duplicate detection engine that can power multiple user interfaces, including:

* Command-Line Interface (CLI)
* Graphical User Interface (GUI)

By separating the engine from the presentation layer, improvements to duplicate detection automatically benefit every interface.

---

# Design Philosophy

The project is guided by five core principles.

## 1. Safety First

Protecting user data is the highest priority.

* Dry-run mode is the default.
* Destructive actions must always be explicit.
* Moving files to the Trash is preferred over permanent deletion.
* Users should always understand what the application intends to do before any files are removed.

---

## 2. Performance

The engine should minimize unnecessary work.

Current optimizations include:

* Group files by size before hashing.
* Use quick hashes to eliminate non-matching files.
* Compute full SHA-256 hashes only when necessary.
* Cache expensive hash calculations.

Future work will focus on:

* SQLite-backed caching
* Parallel hashing
* Incremental rescans
* Performance benchmarking

---

## 3. Separation of Concerns

The project is organized into independent layers.

The duplicate detection engine should never depend on:

* Rich
* argparse
* CLI formatting
* GUI code

Instead, user interfaces consume the engine as a reusable library.

---

## 4. User Experience

The application should be approachable for both technical and non-technical users.

Goals include:

* Clean console output
* Stable progress indicators
* Helpful error messages
* Sensible defaults
* Safe workflows
* Fast feedback

---

## 5. Maintainability

The codebase should remain easy to understand and extend.

Priorities include:

* Small, focused modules
* High test coverage
* Clear documentation
* Consistent coding style
* A contributor-friendly architecture

---

# Current Project Structure

```text
src/
└── dupe_sweeper/
    ├── cli/
    │   └── main.py
    │
    ├── engine/
    │   ├── actions.py
    │   ├── cache.py
    │   ├── hashing.py
    │   ├── matcher.py
    │   └── scanner.py
    │
    └── ui/
```

As the project grows, additional UI components and shared models will be introduced while preserving a clear separation between the engine and presentation layers.

---

# Duplicate Detection Pipeline

Current processing flow:

```text
Scan directory
        │
        ▼
Filter files
        │
        ▼
Group by file size
        │
        ▼
Quick hash candidate files
        │
        ▼
Full SHA-256 verification
        │
        ▼
Group exact duplicates
        │
        ▼
Apply keep strategy
        │
        ▼
Preview, Trash, or Delete
```

This staged pipeline minimizes expensive hashing operations while maintaining exact duplicate detection.

---

# Keep Strategies

The engine currently supports multiple strategies for determining which duplicate should be preserved.

| Strategy        | Description                                                         |
| --------------- | ------------------------------------------------------------------- |
| `original`      | Prefer the original filename without Finder-style numeric suffixes. |
| `oldest`        | Keep the file with the oldest modification timestamp.               |
| `newest`        | Keep the file with the newest modification timestamp.               |
| `shortest-name` | Keep the file with the shortest filename.                           |

Additional strategies may be added in future releases.

---

# Current Cache

The current implementation uses a JSON-based cache.

Each cached entry is keyed by a file fingerprint consisting of:

* Absolute path
* File size
* Modification timestamp

This allows unchanged files to skip expensive SHA-256 hashing during future scans.

The cache implementation is intentionally simple and will eventually be replaced by a SQLite-backed database.

---

# Roadmap

## Near Term

* Replace JSON cache with SQLite
* Multi-threaded hashing
* Benchmark command
* Ignore patterns
* Configuration file support
* Export results as JSON
* Export results as CSV

## Medium Term

* GitHub Actions CI
* Expanded test coverage
* Performance profiling
* Logging and diagnostics
* Plugin-friendly architecture

## Long Term

* Desktop GUI
* Thumbnail previews
* Perceptual image hashing
* Similar image detection
* Video duplicate detection
* Cross-platform installers

---

# Long-Term Vision

The goal is for **dupe-sweeper** to become more than a duplicate finder.

It should become a robust duplicate detection platform that provides a high-performance engine with multiple user interfaces while maintaining a strong focus on safety, usability, and clean software architecture.

---

# Architecture Decision Log

This section records significant architectural decisions made throughout the project's lifetime.

The purpose of this log is to capture **why** decisions were made, not just **what** was implemented. This provides historical context for future contributors and helps guide future design discussions.

---

## ADR-001 — Shared Engine Architecture

**Status:** Accepted

**Decision**

The duplicate detection engine will remain independent of all user interfaces.

The CLI and future GUI will consume the same engine rather than implementing duplicate detection separately.

**Rationale**

This separation allows:

* One implementation of duplicate detection
* Easier testing
* Easier maintenance
* Future GUI development without duplicating business logic

---

## ADR-002 — Safety Before Convenience

**Status:** Accepted

**Decision**

The application will never delete files by default.

Users must explicitly request destructive actions.

Moving files to the Trash is preferred over permanent deletion whenever possible.

**Rationale**

Accidental file deletion is significantly more costly than requiring an additional command-line option.

Safety is therefore prioritized over convenience.

---

## ADR-003 — Progressive Duplicate Detection

**Status:** Accepted

**Decision**

Duplicate detection is performed as a pipeline.

```text
Group by Size
      ↓
Quick Hash
      ↓
SHA-256 Verification
      ↓
Duplicate Groups
```

**Rationale**

Computing SHA-256 hashes for every file is unnecessarily expensive.

Reducing the candidate set at each stage dramatically improves overall performance.

---

## ADR-004 — Rich-Based Console Interface

**Status:** Accepted

**Decision**

The CLI uses the Rich library for console rendering.

**Rationale**

Rich provides:

* Stable progress bars
* Tables
* Panels
* Colors
* Better overall user experience

without coupling the duplicate detection engine to presentation code.

---

## ADR-005 — JSON Cache (Temporary)

**Status:** Accepted

**Decision**

The first cache implementation uses a JSON file stored in the user's home directory.

**Rationale**

JSON provides a simple implementation that is easy to debug while the application architecture stabilizes.

This decision is expected to change in a future release.

**Superseded By**

*(Pending)*

SQLite-backed cache.

---

## Future ADRs

Examples of future architectural decisions that should be documented here include:

* Migration from JSON to SQLite
* Multi-threaded hashing
* Plugin architecture
* Image similarity detection
* GUI framework selection
* Configuration system
* Cross-platform packaging strategy

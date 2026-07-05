from pathlib import Path

from dupe_sweeper.engine.matcher import find_duplicates


def write_file(path: Path, content: bytes) -> None:
    path.write_bytes(content)


def test_finds_exact_duplicates(tmp_path: Path) -> None:
    file_a = tmp_path / "photo.jpg"
    file_b = tmp_path / "photo 1.jpg"
    file_c = tmp_path / "different.jpg"

    write_file(file_a, b"same content")
    write_file(file_b, b"same content")
    write_file(file_c, b"different content")

    result = find_duplicates([file_a, file_b, file_c], show_progress=False)

    assert len(result.groups) == 1

    group = result.groups[0]

    assert group.keep.path == file_a
    assert [duplicate.path for duplicate in group.duplicates] == [file_b]


def test_keep_original_prefers_unsuffixed_file(tmp_path: Path) -> None:
    original = tmp_path / "ZF-9275.jpg"
    duplicate_1 = tmp_path / "ZF-9275 1.jpg"
    duplicate_2 = tmp_path / "ZF-9275 2.jpg"

    content = b"same content"

    write_file(duplicate_1, content)
    write_file(duplicate_2, content)
    write_file(original, content)

    result = find_duplicates(
        [duplicate_1, duplicate_2, original],
        keep="original",
        show_progress=False,
    )

    group = result.groups[0]

    assert group.keep.path == original
    assert [duplicate.path for duplicate in group.duplicates] == [
        duplicate_1,
        duplicate_2,
    ]

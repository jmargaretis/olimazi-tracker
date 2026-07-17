#!/usr/bin/env python3
"""Build the versioned Olimazi Tracker release archive."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
TOP_LEVEL = Path("olimazi-tracker")
INCLUDE_DIRS = ("engine", "skill", "docs")
INCLUDE_FILES = (
    "fixtures/make_fixture.py",
    "fixtures/check_fixture.py",
    "README.md",
    "LICENSE",
    "DISCLAIMER.md",
    "VERSION",
)


def excluded(path: Path) -> bool:
    return (
        "__pycache__" in path.parts
        or any(part.startswith(".git") for part in path.parts)
        or path.suffix in {".pyc", ".pyo"}
    )


def release_files() -> list[Path]:
    files = [ROOT / relative for relative in INCLUDE_FILES]
    for directory in INCLUDE_DIRS:
        files.extend(path for path in (ROOT / directory).rglob("*") if path.is_file())
    return sorted(
        (path for path in files if not excluded(path.relative_to(ROOT))),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def main() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not version:
        raise ValueError("VERSION must not be empty")

    destination = ROOT / "dist" / f"olimazi-tracker-v{version}.zip"
    destination.parent.mkdir(exist_ok=True)
    files = release_files()
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, (TOP_LEVEL / path.relative_to(ROOT)).as_posix())

    print(f"Created {destination.relative_to(ROOT).as_posix()}")
    print(f"Files: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path

import realtime_data_platform


def test_package_imports() -> None:
    assert realtime_data_platform.__version__ == "0.1.0"


def test_key_project_folders_exist() -> None:
    project_root = Path(__file__).resolve().parents[1]
    expected_folders = [
        "configs",
        "data/raw",
        "data/processed",
        "data/sample",
        "src/realtime_data_platform",
        "pipelines",
        "sql",
        "docs",
        "diagrams",
        "dashboard",
        "tests/fixtures",
        "scripts",
        ".github/workflows",
    ]

    missing = [folder for folder in expected_folders if not (project_root / folder).is_dir()]

    assert missing == []

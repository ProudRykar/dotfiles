
#!/usr/bin/env python3

import configparser
import json
import locale
import os
import shutil
import subprocess
from pathlib import Path


def get_application_directories() -> list[Path]:
    """Return directories containing desktop application entries."""
    home = Path.home()

    return [
        home / ".local/share/applications",
        Path("/usr/local/share/applications"),
        Path("/usr/share/applications"),
        home / ".local/share/flatpak/exports/share/applications",
        Path("/var/lib/flatpak/exports/share/applications"),
    ]


def get_application_name(entry: configparser.SectionProxy) -> str:
    """Return the application name in the user's preferred language."""
    language = locale.getlocale()[0] or os.environ.get("LANG", "en")
    language = language.split(".")[0].split("@")[0]

    candidates = [
        language,
        language.split("_")[0],
    ]

    for candidate in candidates:
        localized_name = entry.get(f"Name[{candidate}]")

        if localized_name:
            return localized_name

    return entry.get("Name", "")


def read_application(path: Path, root: Path) -> dict | None:
    """Read and validate a desktop application entry."""
    parser = configparser.ConfigParser(
        interpolation=None,
        strict=False,
    )
    parser.optionxform = str

    try:
        with path.open(encoding="utf-8", errors="replace") as file:
            parser.read_file(file)

        entry = parser["Desktop Entry"]

        if entry.get("Type") != "Application":
            return None

        if entry.getboolean("Hidden", fallback=False):
            return None

        if entry.getboolean("NoDisplay", fallback=False):
            return None

        name = get_application_name(entry)

        if not name:
            return None

        try_exec = entry.get("TryExec")

        if try_exec and not shutil.which(try_exec):
            return None

        desktop_id = path.relative_to(root).as_posix()
        desktop_id = desktop_id.replace("/", "-").removesuffix(".desktop")

        return {
            "name": name,
            "id": desktop_id,
        }

    except (OSError, ValueError, KeyError, configparser.Error):
        return None


def get_applications(search: str = "") -> list[dict]:
    """Discover installed desktop applications and remove duplicates."""
    applications = []
    seen = set()
    search = search.casefold().strip()

    for directory in get_application_directories():
        if not directory.is_dir():
            continue

        for current_directory, _, filenames in os.walk(
            directory,
            followlinks=False,
        ):
            for filename in filenames:
                if not filename.endswith(".desktop"):
                    continue

                path = Path(current_directory) / filename
                application = read_application(path, directory)

                if application is None:
                    continue

                desktop_id = application["id"]

                if desktop_id in seen:
                    continue

                seen.add(desktop_id)

                if search and search not in application["name"].casefold():
                    continue

                applications.append(application)

    return sorted(
        applications,
        key=lambda application: application["name"].casefold(),
    )


def get_search_query() -> str:
    """Return the current search query from Eww."""
    try:
        result = subprocess.run(
            ["eww", "get", "search"],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    except (OSError, subprocess.CalledProcessError):
        return ""


def main() -> None:
    """Print discovered applications as JSON."""
    search = get_search_query()
    print(json.dumps(get_applications(search), ensure_ascii=False))


if __name__ == "__main__":
    main()

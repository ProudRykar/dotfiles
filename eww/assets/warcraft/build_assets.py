#!/usr/bin/env python3
"""Сборка ассетов темы wofi «Scourge» (Warcraft III: нежить).

Источник — набор undead_wofi_assets_first (копируется в assets/source,
чтобы тема не зависела от ~/Downloads).

Запуск:  python3 ~/.config/wofi/assets/build_assets.py
"""

from pathlib import Path
import shutil

ASSETS_DIR = Path(__file__).resolve().parent
SOURCE_DIR = ASSETS_DIR / "source"

# Все элементы копируются без изменения размера, пропорций, цвета и alpha.
# Атлас оставляем только в source: Wofi использует отдельные вырезанные PNG.
ASSET_NAMES = (
    "01_main_window_frame",
    "02_search_bar",
    "03_entry_normal",
    "04_entry_selected",
    "05_scrollbar",
    "06_top_skull_ornament",
    "07_undead_banner",
    "08_necromantic_runes",
    "09_corner_ornament_left",
    "10_corner_ornament_right",
    "11_navigation_arrows",
    "12_skull_bone_cluster",
    "13_purple_gem",
    "14_metallic_separator",
    "15_frame_extension",
)


def main() -> None:
    """Copy the original PNG assets into the directory used by the Wofi theme."""
    if not SOURCE_DIR.is_dir():
        raise SystemExit(
            f"Не найдена папка с исходниками: {SOURCE_DIR}\n"
            "Помести оригинальные PNG в assets/source/."
        )

    missing = [name for name in ASSET_NAMES if not (SOURCE_DIR / f"{name}.png").is_file()]
    if missing:
        raise SystemExit("Не найдены исходные PNG: " + ", ".join(missing))

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for name in ASSET_NAMES:
        source = SOURCE_DIR / f"{name}.png"
        destination = ASSETS_DIR / source.name
        shutil.copy2(source, destination)

    # Удаляем только файлы, которые создавал прежний build_assets.py.
    # Оригинальные файлы в assets/source/ не затрагиваются.
    for legacy_name in ("frame.png", "panel.png", "separator.png", "entry_selected.png"):
        legacy_path = ASSETS_DIR / legacy_name
        if legacy_path.exists():
            legacy_path.unlink()

    legacy_src = ASSETS_DIR / "src"
    if legacy_src.is_dir():
        for legacy_name in (
            "02_search_bar.png",
            "03_entry_normal.png",
            "04_entry_selected.png",
            "15_frame_extension.png",
        ):
            legacy_path = legacy_src / legacy_name
            if legacy_path.exists():
                legacy_path.unlink()
        try:
            legacy_src.rmdir()
        except OSError:
            pass

    print("Оригинальные PNG скопированы без обработки:")
    for name in ASSET_NAMES:
        path = ASSETS_DIR / f"{name}.png"
        print(f"  {path.name}: {path.stat().st_size:,} bytes")
    print("Готово. panel.png и старые производные текстуры больше не используются.")


if __name__ == "__main__":
    main()

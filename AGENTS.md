# AGENTS.md

Guidance for coding agents working in this repository.

## Project Overview

AVBPowerTool is a Python 3.9+ tool for Android Verified Boot workflows. It wraps AOSP `avbtool.py` with interactive navigation, CLI commands, image-info extraction, signing, and config import/export management.

The entry point is `main.py`. Startup changes the process working directory to the project root, reads `GlobalConfig.cfg`, initializes logging, checks dependencies/folders, then either:

- runs CLI mode through `Core/CLIHandler.py` when a subcommand is supplied, or
- starts the interactive frontend through `Frontend/HomePageUI.py` and `Core/NavigationEngine.py`.

## Repository Layout

- `main.py`: application entry point and startup sequence.
- `Core/`: backend logic for CLI dispatch, config parsing/management, image metadata, signing, FEC, environment checks, logging, dynamic imports, and navigation.
- `Core/avbtool.py`: bundled AOSP AVB tool; treat as vendor code unless the task explicitly targets it.
- `Frontend/`: terminal UI classes. Most UI classes inherit from `Frontend/BaseUI.py`.
- `Navigator/`: JSON navigation map files used by `Core/NavigationEngine.py`.
- `GlobalConfig.cfg`: key/value global runtime configuration.
- `bin/`: bundled platform tools such as OpenSSL and FEC binaries.
- `Images/`, `Configs/`, `Keys/`, `Logs/`, `Core/currentConfigs/`, `Core/currentKeySet/`: runtime/user data locations. Avoid committing generated or private contents from these folders.
- `requirements.txt`: Python runtime dependencies (`numpy`, `reedsolo`).

## Development Commands

Use a virtual environment when installing dependencies.

```shell
pip install -r requirements.txt
python main.py about
python main.py --help
```

Useful CLI smoke checks:

```shell
python main.py get_all_config
python main.py read --images boot vbmeta
python main.py sign --images boot vbmeta
```

The `read` and `sign` commands depend on images/configs/keys in the runtime folders, so do not assume they are safe smoke tests in a clean checkout.

There is no formal test suite in the repository. `Core/test.py` is a hardcoded local script that references `F:\testImages`; do not treat it as a portable test.

## Coding Conventions

- Keep changes compatible with Python 3.9+.
- Follow the existing module style: standard-library imports first, then project imports; classes use PascalCase; many existing methods use snake_case.
- Preserve the project's explicit imports such as `import Core.SignImages as SignImages` unless refactoring is part of the task.
- Prefer structured file handling for JSON/config files. Navigator files are UTF-8 JSON.
- Keep terminal UI behavior consistent with `Frontend/BaseUI.py` and `Frontend/UIUtils.py`.
- Add concise comments only where they clarify non-obvious control flow or file/runtime side effects.

## Localization

User-facing strings should live in Android-style XML resources:

- default strings: `Resources/values/strings.xml`
- Chinese strings: `Resources/values-zh/strings.xml`
- additional languages: `Resources/values-<language>/strings.xml`

Use `from Core.Localization import t` and call `t("resource.key")`. Do not pass source-text defaults to `t()`; `strings.xml` is the source of truth. Format placeholders use Python `str.format`, for example `<string name="example">Hello {name}</string>` with `t("example", name="User")`.

The active language is configured in `GlobalConfig.cfg` with `language="en"` or `language="zh"`. Missing translations fall back to `Resources/values/strings.xml`; missing default keys render as the key name, which should be treated as a bug.

Navigator JSON must not use translated or display text for control flow. Each node should define:

- `Id`: stable unique identifier, for example `sign_images`
- `NameKey`: resource key for the display title
- `DescriptionKey`: resource key for the display description
- `Next`: target JSON filenames
- `Selection`: shortcut keys aligned with `Next`

Frontend custom actions should use stable action IDs such as `action:sign_selected_images` and localized labels from `t("...")`. `BaseUI.show_ui()` returns action IDs, not labels, so backend dispatch should compare against IDs only.

### Adding A New Language

When adding a new localization, use the existing Android-style resource layout:

1. Create `Resources/values-<language>/strings.xml`, for example `Resources/values-ja/strings.xml`.
2. Copy the XML structure from `Resources/values/strings.xml`.
3. Translate values only. Do not rename `name="..."` keys.
4. Preserve placeholders exactly, such as `{version}`, `{config}`, `{old}`, `{new}`, `{error}`, and `{config_key}`.
5. Set `language="<language>"` in `GlobalConfig.cfg` or through the Settings page.
6. Run `python main.py check_l10n` or the Settings page translation checker.
7. Add any missing entries reported by the checker to the selected language file.
8. Validate XML with:

```shell
python -c "import xml.etree.ElementTree as ET; ET.parse('Resources/values/strings.xml'); ET.parse('Resources/values-<language>/strings.xml')"
```

Do not duplicate source text in Python as fallback defaults. If a translated string is missing, the runtime should fall back to `Resources/values/strings.xml`, and `check_l10n` should report that missing key.

## Runtime State And Safety

This project manipulates Android image files, key material, config archives, and generated logs. Be careful with:

- `Images/*.img`
- `Keys/*`
- `Configs/*`
- `Core/currentConfigs/*`
- `Core/currentKeySet/*`
- `Logs/*`
- root-level `*.zip`

These paths are ignored by `.gitignore` because they are generated, private, or user-provided. Do not delete, overwrite, or normalize them unless the user explicitly asks.

The app may auto-install missing Python libraries depending on `GlobalConfig.cfg` (`install_missing_libs`, `check_missing_libs`). For deterministic agent runs, prefer installing dependencies explicitly with `pip install -r requirements.txt` in the active environment.

## Architecture Notes

- `Core/CLIHandler.py` defines argparse subcommands and dispatches to backend classes.
- `Core/ConfigManager.py` manages persistent config folders and import/export archives.
- `Core/ConfigParser.py` parses and writes image-info/config JSON used by signing workflows.
- `Core/ImageInfoUtils.py` reads AVB metadata from image files.
- `Core/SignImages.py` signs images based on the active/current config.
- `Core/NavigationEngine.py` reads `Navigator/*.json` files and controls page transitions.
- `Frontend/BaseUI.py` provides common interactive behavior and dynamically imports page UIs.
- `Core/LogUtils.py` provides singleton-style logging used throughout the project.

When adding a new interactive page, update both the relevant `Frontend/*.py` class and the matching `Navigator/*.json` map entries. Keep `Selection` and `Next` arrays aligned by index.

## Verification Guidance

For small backend or CLI changes, run:

```shell
python main.py about
python main.py --help
```

For navigation/frontend changes, at minimum run the app interactively:

```shell
python main.py
```

For config import/export, image reading, or signing changes, verify with disposable sample images/configs only. Avoid using private keys or user images unless the user has provided them for that purpose.

## Git Hygiene

Before editing, check the working tree:

```shell
git status --short
```

Do not revert unrelated local changes. In particular, runtime folders may contain user-specific keys, configs, images, and logs that should be left alone.

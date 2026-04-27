# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-04-27

### Added
- Added **Konsole** to the default terminals list.
- Added **Zed** to the default editors list.
- Improved application detection to search for multiple possible binary names (e.g., `warp-terminal` and `warp`).

### Changed
- Refactored application launching to use `start_new_session=True` for better process detachment, ensuring GUI apps stay open after the launcher exits.
- Updated launcher to use `cwd` parameter in `subprocess.Popen` for more reliable directory initialization.

### Fixed
- Fixed Warp terminal failing to open by removing invalid positional path argument (now relies on `cwd`).
- Fixed Konsole failing to open by using the correct `--workdir` flag instead of `--working-directory`.
- Fixed an issue where some GUI applications might close when the launcher script terminated.

## [1.0.1] - 2026-04-26

### Fixed
- Fixed an issue where Dolphin (KDE Plasma) would throw a "You are not authorized to execute this file" error by ensuring `.desktop` service menus are automatically marked as executable during installation.

## [1.0.0] - 2026-04-26

### Added
- Initial port from `macos-dev-launcher` to a standalone Linux project.
- Replaced macOS `osascript` AppleScript dialogs with native Linux `zenity` GUI dialogs.
- Cross-platform file manager installer (`install.sh`) added to support right-click "Open Dev Environment" actions.
- Support for Dolphin (KDE Plasma), Nautilus (GNOME), and Nemo (Cinnamon/Mint) context menus.
- Replaced `open -a` commands with native binary execution (e.g. `ghostty`, `kitty`, `warp-terminal`, `codium`).
- Built-in `--test` command to verify UI dependencies and system integrations.

### Changed
- Refactored project structure specifically for Linux filesystem hierarchies.
- Configuration is now stored in `~/.config/fedora-dev-launcher/config.json`.
- Logs are now correctly stored in `~/.local/state/fedora-dev-launcher/launcher.log` instead of macOS `Library/Logs`.

### Fixed
- Terminal launch commands accurately target the directory path locally based on Linux terminal specifications (e.g., `--working-directory` vs `--directory`).
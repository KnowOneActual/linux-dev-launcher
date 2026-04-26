# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
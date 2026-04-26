# Linux Dev Environment Launcher

![Language](https://img.shields.io/badge/Language-Python_3-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?logo=linux&logoColor=black)

A Linux GUI Quick Action that streamlines your workflow startup. 
Instead of manually opening a terminal, navigating to a project, and then launching your editor, this script lets you open any project folder and ask: **"Which terminal should we use today?"**

This is the direct counterpart to the `macos-dev-launcher`, built using Zenity for native Linux dialogs.

## Features

* **Interactive Picker:** Uses native Linux `zenity` dialogs to choose your terminal on the fly
* **Multi-Editor Support:** Configure multiple editors and pick the right one for each project
* **External Configuration:** JSON config file for easy customization without editing code
* **Memory System:** Remembers your terminal/editor choices per project
* **Context Aware:** Opens the terminal directly to the selected folder
* **Combined Dialog Mode:** One screen for terminal + editor
* **Lightweight & Fast:** Minimal dependencies

## Installation

### Dependencies
Ensure you have `zenity` installed.
* **Fedora/RHEL:** `sudo dnf install zenity`
* **Ubuntu/Debian:** `sudo apt install zenity`
* **Arch Linux:** `sudo pacman -S zenity`

### Shell Integration
Add this to `~/.bashrc` or `~/.zshrc`:

```bash
dev() {
    python3 "$HOME/github/linux-dev-launcher/open_dev_env.py" "${1:-.}"
}
```

Then reload:
```bash
source ~/.bashrc  # or ~/.zshrc
```

## Usage

* Open current directory:
  ```bash
  dev .
  ```
* Test installation:
  ```bash
  python3 open_dev_env.py --test
  ```

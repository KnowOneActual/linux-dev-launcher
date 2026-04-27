# Linux Dev Environment Launcher

![Language](https://img.shields.io/badge/Language-Python_3-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?logo=linux&logoColor=black)

A Linux GUI Quick Action that streamlines your workflow startup. 
Instead of manually opening a terminal, navigating to a project, and then launching your editor, this script lets you open any project folder and ask: **"Which terminal should we use today?"**

This is the direct counterpart to the `macos-dev-launcher`, built using Zenity for native Linux graphical dialogs.

## Features

* **Interactive File Manager Integration:** Right-click a folder in Dolphin, Nautilus, or Nemo to instantly launch your tools!
* **Native GUI Picker:** Uses Linux `zenity` dialogs to choose your terminal/editor on the fly.
* **Multi-Editor Support:** Pick the right tool for each project (VSCodium, Code, etc).
* **Smart Memory System:** Automatically remembers your terminal/editor choices per project!
* **Combined Dialog Mode:** One screen for terminal + editor choices.
* **Lightweight & Fast:** Minimal dependencies, rapid native launch.

---

## 1. Installation

### Dependencies
Ensure you have `zenity` installed to enable the graphical dialog prompts.
* **Fedora/RHEL:** `sudo dnf install zenity`
* **Ubuntu/Debian:** `sudo apt install zenity`
* **Arch Linux:** `sudo pacman -S zenity`

### Cloning the Repository
```bash
git clone https://github.com/KnowOneActual/linux-dev-launcher.git ~/github/linux-dev-launcher
cd ~/github/linux-dev-launcher
```

---

## 2. Right-Click Menu Integration (Recommended)

This project includes an installer that adds a convenient **"Open Dev Environment"** right-click context menu item to the most popular Linux file managers:
- **Dolphin** (KDE Plasma)
- **Nautilus** (GNOME)
- **Nemo** (Cinnamon / Linux Mint)

To install the right-click integration, run:
```bash
cd ~/github/linux-dev-launcher
./install.sh
```

**How to use:**
Open your file manager, navigate to any folder, **right-click**, and select `Open Dev Environment` (or `Actions` > `Open Dev Environment` in some KDE setups).

---

## 3. Terminal/CLI Integration (Optional)

If you also want to launch it from the command line, you can add an alias to your shell configuration file (`~/.bashrc` or `~/.zshrc`).

```bash
# Add this function to your .bashrc or .zshrc
dev() {
    python3 "$HOME/github/linux-dev-launcher/open_dev_env.py" "${1:-.}"
}
```

Reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

**How to use:**
```bash
dev .               # Open the current directory
dev ~/my-project    # Open a specific directory
```

---

## 4. Configuration

The first time you run it, a configuration file is created automatically at:
`~/.config/fedora-dev-launcher/config.json`

*(Note: The configuration directory defaults to fedora-dev-launcher but works on all Linux distributions).*

### Default Terminals & Editors
By default, it looks for:
- **Terminals:** Ghostty, Kitty, Warp, Gnome-Terminal, Alacritty, Konsole
  - *Note: Warp on Linux currently has a known issue where it defaults to the Home directory rather than the project directory. See [WARP_TROUBLESHOOTING.md](./WARP_TROUBLESHOOTING.md) for more details.*
- **Editors:** VSCodium, Code, Zed

### Changing Configuration
You can freely edit the `config.json` file to add custom command-line arguments to your tools, change your preferred terminals, or enable/disable project memory (`remember_choices`).

## Troubleshooting

**"You are not authorized to execute this file" (KDE Dolphin)**
If you see this error when right-clicking, ensure the context menu files are marked as executable by running:
`chmod +x ~/.local/share/kio/servicemenus/open-dev-env.desktop ~/.local/share/kservices5/ServiceMenus/open-dev-env.desktop`
*(Note: As of v1.0.1, the installer handles this automatically).*

**Testing Your Setup**
You can run the built-in test mode to verify your configuration and ensure Zenity is installed correctly:
```bash
cd ~/github/linux-dev-launcher
python3 open_dev_env.py --test
```

Logs are safely stored at `~/.local/state/fedora-dev-launcher/launcher.log` for any advanced debugging.

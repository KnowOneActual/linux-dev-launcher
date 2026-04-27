import sys
import os
import subprocess
import argparse
import shlex
import logging
import json
import shutil
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

# --- DEFAULT CONFIGURATION ---
DEFAULT_CONFIG = {
    "terminals": ["Ghostty", "Kitty", "Warp", "Gnome-Terminal", "Alacritty", "Konsole"],
    "editors": ["VSCodium", "Code", "Zed"],
    "app_args": {},
    "logging": {
        "enabled": True,
        "level": "INFO",
        "file": "~/.local/state/fedora-dev-launcher/launcher.log",
        "max_bytes": 1048576,
        "backup_count": 7
    },
    "behavior": {
        "auto_open_editor": True,
        "remember_choices": True,
        "combined_dialog": True
    }
}

# Config file location
CONFIG_DIR = Path.home() / ".config" / "fedora-dev-launcher"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"

# --- CONFIGURATION LOADING ---

def load_config(config_path=None, verbose=False):
    """Load configuration from JSON file with fallback to defaults."""
    config = DEFAULT_CONFIG.copy()
    
    if config_path is None:
        config_path = CONFIG_FILE
    else:
        config_path = Path(config_path).expanduser()
    
    if verbose:
        print(f"Looking for config at: {config_path}")
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            
            # Deep merge
            for key, value in user_config.items():
                if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                    config[key].update(value)
                else:
                    config[key] = value
            
            if verbose:
                print(f"✓ Loaded config from {config_path}")
            
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not load config from {config_path}: {e}", file=sys.stderr)
            print(f"Using default configuration", file=sys.stderr)
    else:
        if verbose:
            print(f"Config file not found, using defaults")
    
    return config

def create_example_config(verbose=False):
    """Create example configuration file at default location."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        
        if verbose:
            print(f"✓ Created config file at: {CONFIG_FILE}")
            print(f"Edit this file to customize your settings")
        
        return True
    except (OSError, PermissionError) as e:
        print(f"Error: Could not create config file: {e}", file=sys.stderr)
        return False

# Load configuration
config = load_config()

# Extract values
TERMINAL_APPS = config["terminals"]
EDITOR_APPS = config["editors"]
APP_ARGS = config.get("app_args", {})
LOGGING_ENABLED = config["logging"]["enabled"]
LOG_LEVEL = config["logging"]["level"]
LOG_FILE = Path(config["logging"]["file"]).expanduser()
LOG_DIR = LOG_FILE.parent
LOG_MAX_BYTES = config["logging"]["max_bytes"]
LOG_BACKUP_COUNT = config["logging"]["backup_count"]
AUTO_OPEN_EDITOR = config["behavior"]["auto_open_editor"]
REMEMBER_CHOICES = config["behavior"]["remember_choices"]
COMBINED_DIALOG = config["behavior"].get("combined_dialog", True)

# --- LOGGING SETUP ---

def setup_logging(enabled=True, verbose=False, level=None):
    """Configure logging with rotation."""
    logger = logging.getLogger('fedora-dev-launcher')
    
    if verbose:
        log_level = logging.DEBUG
    elif level:
        log_level = getattr(logging, level.upper(), logging.INFO)
    else:
        log_level = logging.INFO
    
    logger.setLevel(log_level)
    logger.handlers.clear()
    
    if enabled:
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=LOG_MAX_BYTES,
                backupCount=LOG_BACKUP_COUNT
            )
            file_handler.setLevel(logging.DEBUG)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not set up logging: {e}", file=sys.stderr)
    
    if verbose:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger

logger = logging.getLogger('fedora-dev-launcher')

# --- HISTORY/MEMORY FUNCTIONS ---

def load_history():
    """Load user's choice history."""
    if not HISTORY_FILE.exists():
        logger.debug(f"History file does not exist: {HISTORY_FILE}")
        return {}
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
        logger.debug(f"Loaded history with {len(history)} projects")
        return history
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Could not load history: {e}")
        return {}

def save_choice(project_path, terminal, editor):
    """Save user's choice for this project."""
    if not REMEMBER_CHOICES:
        logger.debug("remember_choices disabled, not saving")
        return
    
    try:
        history = load_history()
        
        path_key = str(project_path)
        history[path_key] = {
            "terminal": terminal,
            "editor": editor,
            "last_used": datetime.now().isoformat()
        }
        
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        
        logger.info(f"Saved choice: terminal={terminal}, editor={editor}")
        
    except (OSError, PermissionError, json.JSONDecodeError) as e:
        logger.warning(f"Could not save choice: {e}")

def get_last_choice(project_path):
    """Get last terminal/editor used for this project."""
    if not REMEMBER_CHOICES:
        return None, None
    
    history = load_history()
    path_key = str(project_path)
    
    if path_key in history:
        choice = history[path_key]
        terminal = choice.get("terminal")
        editor = choice.get("editor")
        logger.debug(f"Found history: terminal={terminal}, editor={editor}")
        return terminal, editor
    else:
        logger.debug(f"No history found")
        return None, None

# --- HELPER FUNCTIONS ---

def get_executable_name(app_name):
    """Resolve app name to executable name with existence check."""
    base_name = app_name.lower().replace(" ", "-")
    
    # Map of friendly names to possible executable names
    mapping = {
        "warp": ["warp-terminal", "warp"],
        "vscodium": ["codium", "vscodium"],
        "code": ["code", "visual-studio-code", "code-insiders"],
        "ghostty": ["ghostty"],
        "kitty": ["kitty"],
        "alacritty": ["alacritty"],
        "gnome-terminal": ["gnome-terminal"],
        "konsole": ["konsole"],
        "zed": ["zed", "zed-editor"]
    }
    
    if base_name in mapping:
        for cmd in mapping[base_name]:
            if shutil.which(cmd):
                return cmd
        return mapping[base_name][0] # Fallback to first in list
        
    return base_name

def app_exists(app_name):
    """Check if application exists in PATH."""
    if not app_name:
        return False
    cmd = get_executable_name(app_name)
    exists = shutil.which(cmd) is not None
    logger.debug(f"Checking {cmd}: {exists}")
    return exists

def sanitize_path(path_str, verbose=False):
    """Sanitize and validate a path."""
    logger.debug(f"Sanitizing path: {path_str}")
    
    try:
        path = Path(path_str).expanduser().resolve()
        
        if verbose:
            print(f"Sanitizing: {path_str}")
            print(f"  Resolved: {path}")
        
        if not path.exists():
            logger.warning(f"Path does not exist: {path}")
            if verbose:
                print(f"  ✗ Does not exist")
            return None
        
        if not path.is_dir():
            logger.warning(f"Not a directory: {path}")
            if verbose:
                print(f"  ✗ Not a directory")
            return None
        
        logger.info(f"Path validated: {path}")
        if verbose:
            print(f"  ✓ Valid")
        
        return path
        
    except (OSError, RuntimeError, ValueError) as e:
        logger.error(f"Path sanitization failed: {e}")
        if verbose:
            print(f"  ✗ Failed: {e}")
        return None

def get_available_terminals():
    """Get list of installed terminals."""
    available = [app for app in TERMINAL_APPS if app_exists(app)]
    logger.info(f"Available terminals: {available}")
    return available

def get_available_editors():
    """Get list of installed editors."""
    available = [app for app in EDITOR_APPS if app_exists(app)]
    logger.info(f"Available editors: {available}")
    return available

def show_error_dialog(title, message):
    """Display error dialog using zenity."""
    logger.error(f"Error: {title} - {message}")
    if shutil.which("zenity"):
        try:
            subprocess.run(['zenity', '--error', f'--title={title}', f'--text={message}'], check=True)
        except subprocess.CalledProcessError:
            print(f"ERROR: {title} - {message}", file=sys.stderr)
    else:
        print(f"ERROR: {title} - {message}", file=sys.stderr)

# --- DIALOG FUNCTIONS ---

def ask_combined_choice(project_path, project_name, verbose=False):
    """Single dialog for both terminal and editor using zenity forms."""
    logger.debug("Combined choice dialog")
    
    terminals = get_available_terminals()
    editors = get_available_editors()
    
    if verbose:
        print(f"Combined dialog mode")
        print(f"  Terminals: {terminals}")
        print(f"  Editors: {editors}")
    
    if not terminals:
        logger.error("No terminals installed")
        show_error_dialog("No Terminals", f"Please install one of: {', '.join(TERMINAL_APPS)}")
        return None, None
        
    if not shutil.which("zenity"):
        logger.error("Zenity is not installed. Please install zenity for UI dialogs.")
        print("Zenity is not installed. Falling back to default apps.", file=sys.stderr)
        return terminals[0], editors[0] if editors else None
    
    # Defaults
    term_opts = "|".join(terminals)
    ed_opts = "|".join(["None"] + editors)
    
    cmd = [
        'zenity', '--forms', 
        f'--title=🚀 Launch {project_name}',
        f'--text=Select environment for {project_name}:',
        '--add-combo=Terminal', f'--combo-values={term_opts}',
        '--add-combo=Editor', f'--combo-values={ed_opts}'
    ]
    
    try:
        result = subprocess.check_output(cmd, text=True).strip()
        parts = result.split("|")
        if len(parts) >= 1:
            terminal = parts[0]
            editor = parts[1] if len(parts) > 1 and parts[1] != "None" else None
            
            logger.info(f"Selected: terminal={terminal}, editor={editor}")
            if verbose:
                print(f"Selected: {terminal} + {editor or 'none'}")
            
            return terminal, editor
        return None, None
    except subprocess.CalledProcessError:
        logger.info("User cancelled")
        if verbose:
            print("User cancelled")
        return None, None

def ask_terminal_choice(project_path, verbose=False):
    """Show terminal picker dialog."""
    terminals = get_available_terminals()
    if not terminals:
        show_error_dialog("No Terminals", f"Install one of: {', '.join(TERMINAL_APPS)}")
        return None
    
    if not shutil.which("zenity"):
        return terminals[0]
        
    cmd = [
        'zenity', '--list',
        '--title=🚀 Open project in which terminal?',
        '--column=Terminal'
    ] + terminals
    
    try:
        result = subprocess.check_output(cmd, text=True).strip()
        return result if result else None
    except subprocess.CalledProcessError:
        return None

def ask_editor_choice(project_name, project_path, verbose=False):
    """Ask which editor to open."""
    if not AUTO_OPEN_EDITOR:
        return None
    
    editors = get_available_editors()
    if not editors:
        return None
        
    if not shutil.which("zenity"):
        return editors[0]
        
    options = ["None"] + editors
    cmd = [
        'zenity', '--list',
        f'--title=📝 Open {project_name} in which editor?',
        '--column=Editor'
    ] + options
    
    try:
        result = subprocess.check_output(cmd, text=True).strip()
        return None if result == "None" or not result else result
    except subprocess.CalledProcessError:
        return None

# --- APP LAUNCHING ---

def launch_app(app_name, path_str, is_terminal=False, verbose=False):
    cmd_name = get_executable_name(app_name)
    cmd = [cmd_name]
    
    if is_terminal:
        if cmd_name in ["gnome-terminal", "alacritty", "ghostty"]:
            cmd.append(f"--working-directory={path_str}")
        elif cmd_name == "konsole":
            cmd.append("--workdir")
            cmd.append(path_str)
        elif cmd_name == "kitty":
            cmd.append(f"--directory={path_str}")
        elif cmd_name in ["warp-terminal", "warp"]:
            # Warp on Linux doesn't reliably take a positional path arg for the GUI launch
            # and may try to interpret it as a URL. We rely on cwd=path_str in Popen.
            pass
        else:
            cmd.append(path_str)
    else:
        # Editors usually take path as positional arg
        cmd.append(path_str)
        
    if app_name in APP_ARGS:
        cmd.extend(APP_ARGS[app_name])
        
    logger.info(f"Launching command: {' '.join(cmd)} (cwd: {path_str})")
    if verbose:
        print(f"Launching {app_name} with command: {' '.join(cmd)}")
        
    try:
        # Use Popen to not block the script.
        # start_new_session=True ensures the app stays open after the script exits.
        # cwd=path_str ensures the app starts in the project directory.
        subprocess.Popen(
            cmd, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            cwd=path_str,
            start_new_session=True
        )
        return True
    except Exception as e:
        logger.error(f"Failed to launch {app_name}: {e}")
        show_error_dialog("Launch Failed", f"Could not launch {app_name}: {e}")
        return False

# --- MAIN FUNCTION ---

def open_project(path, verbose=False):
    """Open project in terminal and editor."""
    logger.info(f"Opening: {path}")
    
    sanitized_path = sanitize_path(str(path), verbose)
    
    if not sanitized_path:
        error_msg = f"Invalid path: {path}"
        logger.error(error_msg)
        show_error_dialog("Invalid Path", error_msg)
        return
    
    path_str = str(sanitized_path)
    project_name = sanitized_path.name
    
    if verbose:
        print(f"\nOpening: {project_name}")
        print(f"Path: {path_str}")
    
    if COMBINED_DIALOG:
        terminal_app, editor_app = ask_combined_choice(sanitized_path, project_name, verbose)
        if not terminal_app:
            logger.info("No terminal selected")
            return
    else:
        terminal_app = ask_terminal_choice(sanitized_path, verbose)
        if not terminal_app:
            logger.info("No terminal selected")
            return
        editor_app = ask_editor_choice(project_name, sanitized_path, verbose)
    
    # Launch terminal
    launch_app(terminal_app, path_str, is_terminal=True, verbose=verbose)
    
    # Launch editor
    if editor_app:
        launch_app(editor_app, path_str, is_terminal=False, verbose=verbose)
    
    # Save choices
    save_choice(sanitized_path, terminal_app, editor_app)
    
    logger.info(f"Finished: {project_name}")

# --- TEST MODE ---

def test_mode(verbose=False):
    """Test configuration."""
    logger.info("Test mode")
    
    print("=" * 60)
    print("Fedora Dev Launcher - Configuration Test")
    print("=" * 60)
    
    print("\nConfiguration:")
    print(f"  File: {CONFIG_FILE}")
    if CONFIG_FILE.exists():
        print(f"  ✓ Exists")
    else:
        print(f"  ✗ Not found (using defaults)")
        
    print(f"\nZenity (UI Dialogs):")
    if shutil.which("zenity"):
        print(f"  ✓ Installed")
    else:
        print(f"  ✗ NOT INSTALLED. Run: sudo dnf install zenity")
    
    print(f"\nTerminals: {', '.join(TERMINAL_APPS)}")
    available = get_available_terminals()
    if available:
        print(f"✓ Available: {', '.join(available)}")
    else:
        print(f"✗ None installed")
    
    print(f"\nEditors: {', '.join(EDITOR_APPS) if EDITOR_APPS else '(none)'}")
    if EDITOR_APPS:
        available_eds = get_available_editors()
        if available_eds:
            print(f"✓ Available: {', '.join(available_eds)}")
        else:
            print(f"✗ None installed")
    
    print("\n" + "=" * 60)
    if available:
        print("✓ Ready to use")
    else:
        print("✗ Install at least one terminal")
    print("=" * 60)

# --- MAIN ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Launch terminal and editor for Fedora')
    parser.add_argument('paths', nargs='*', help='Project paths')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-t', '--test', action='store_true', help='Test configuration')
    parser.add_argument('--no-log', action='store_true', help='Disable logging')
    parser.add_argument('--config', type=str, help='Custom config file')
    parser.add_argument('--create-config', action='store_true', help='Create config file')
    
    args = parser.parse_args()
    
    if args.create_config:
        if create_example_config(verbose=True):
            sys.exit(0)
        else:
            sys.exit(1)
    
    if args.config:
        config = load_config(args.config, args.verbose)
        TERMINAL_APPS = config["terminals"]
        EDITOR_APPS = config["editors"]
        APP_ARGS = config.get("app_args", {})
        LOGGING_ENABLED = config["logging"]["enabled"]
        LOG_LEVEL = config["logging"]["level"]
        REMEMBER_CHOICES = config["behavior"]["remember_choices"]
        COMBINED_DIALOG = config["behavior"].get("combined_dialog", True)
    
    logger = setup_logging(
        enabled=LOGGING_ENABLED and not args.no_log,
        verbose=args.verbose,
        level=LOG_LEVEL
    )
    
    try:
        if args.test:
            test_mode(args.verbose)
            sys.exit(0)
        
        if args.paths:
            for path in args.paths:
                open_project(path, args.verbose)
        else:
            print("No paths provided.")
            print("\nUsage:")
            print("  python3 fedora_dev_env.py ~/projects/my-app")
            print("  python3 fedora_dev_env.py --test")
            print("  python3 fedora_dev_env.py --create-config")
            sys.exit(1)
            
    except Exception as e:
        logger.exception(f"Error: {e}")
        raise

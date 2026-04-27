# Warp Terminal Troubleshooting (Linux)

## Current Status
Warp for Linux (v0.2026.04.22 and similar) currently has a known limitation where it does not reliably open in a specific directory when launched from an external script or file manager.

**The Issue:**
- Launching with a positional path (e.g., `warp-terminal /path/to/project`) results in an `error: invalid value ... for '[URLS]...': relative URL without a base`.
- Launching with `file://` URIs or environment variables like `WARP_CD` often still results in Warp defaulting to the Home directory (`~`).

## Roadmap & Potential Solutions

### 1. Future Native Support
The Warp team is actively working on better Linux integration. Track this issue on GitHub:
- [Warp GitHub Issue #6357](https://github.com/warpdotdev/Warp/issues/6357)

### 2. Community Workarounds to Investigate
- **`oz` CLI:** Warp is transitioning to the `oz` CLI tool. Future versions might support a command like `oz open --cwd <path>`.
- **Warp URI Handlers:** The `warp://action/new_tab?path=...` handler is intended for this purpose but currently lacks consistent implementation across all Linux window managers.

### 3. User Troubleshooting Steps
If you want Warp to open in your project directory:
1.  **Keep Warp Running:** If Warp is already running in the background, subsequent "Open in Terminal" requests are more likely to succeed.
2.  **Internal Warp Settings:**
    - Open Warp Settings (`Ctrl + ,`).
    - Go to **Features > Session**.
    - Set **Working directory for new sessions** to **Home directory**. This allows external signals to potentially override the path.

## Research Log
- **Positional Args:** Failed with "relative URL" error.
- **URI Schemes:** `file://` and `warp://` recognized but often ignored in favor of `~`.
- **`cwd` Parameter:** Passed to `subprocess.Popen`, but Warp's internal session management overrides it.
- **`WARP_CD` Env Var:** Used by some file manager plugins, but not natively supported by the binary yet.

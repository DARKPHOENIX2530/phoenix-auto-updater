# Phoenix Auto-Updater (Standalone)

**Download once, run forever.** This tool keeps your local Phoenix installation automatically updated from GitHub.

## How It Works

1. **Download this folder** (`phoenix-auto-updater`) to any location on your computer
2. **Run `run_updater.bat`** (or `python phoenix_auto_updater.py`)
3. **Enter your Phoenix installation path** when prompted (first run only)
4. **Leave it running** in the background

The updater will:
- Check for internet connectivity every 30 seconds
- Wait for **5 minutes of stable internet** before checking for updates
- Check the GitHub repo every **5 minutes** for new commits
- **Automatically download and apply updates** when available
- **Preserve your local config/files** (only updates code from the repo)
- Notify you when an update is applied — just restart Phoenix

## Requirements

- **Python 3.8+** (from [python.org](https://python.org))
- **Git** (usually installed with Python on Windows, or get from [git-scm.com](https://git-scm.com))
- **Internet connection**

## First Run

```
Starting Phoenix Auto-Updater...
Phoenix installation not found in common locations.
Enter full path to your Phoenix installation: C:\Users\You\phoenix
[Updater] Found Phoenix at: C:\Users\You\phoenix
[Updater] Monitoring https://github.com/DARKPHOENIX2530/phoenix-assistant.git (main)
[Updater] Current version: a1b2c3d4
[Updater] Running in background... (Ctrl+C to stop)
```

## What Gets Updated

- All `.py` files from the repo
- `webgui/` folder
- `tests/` folder
- Any new files added to the repo

## What's Preserved (Never Overwritten)

- Your config files (if not in repo)
- Local data, logs, databases
- Any files you added yourself
- The updater itself (it's separate from Phoenix)

## Stopping the Updater

Press **Ctrl+C** in the console window.

## Running at Startup (Optional)

1. Press `Win+R`, type `shell:startup`
2. Create a shortcut to `run_updater.bat` in that folder
3. It will auto-start when you log in

## Manual Update Check

If you want to force an immediate check, just restart the updater (Ctrl+C, then run again).

---

**Repository:** https://github.com/DARKPHOENIX2530/phoenix-assistant  
**Updater Source:** This folder (not part of Phoenix repo — avoids conflicts)
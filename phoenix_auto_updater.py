"""
Phoenix Auto-Updater (Standalone)
==================================
A separate tool users download ONCE. It monitors the GitHub repo and
auto-updates their local Phoenix installation when new commits are pushed.

NOT part of the Phoenix repo - avoids downgrading local development.
"""
import asyncio
import subprocess
import sys
import os
import json
import time
import shutil
from pathlib import Path
from datetime import datetime

# ============ CONFIGURATION ============
REPO_URL = "https://github.com/DARKPHOENIX2530/phoenix-assistant.git"
BRANCH = "main"
CHECK_INTERVAL = 300  # 5 minutes
STABLE_INTERNET_WINDOW = 300  # 5 minutes stable connection before updating
# =======================================

class InternetMonitor:
    """Monitors internet connectivity stability."""
    
    def __init__(self, stable_window=STABLE_INTERNET_WINDOW):
        self.stable_window = stable_window
        self.connected_since = None
        
    async def check_connectivity(self) -> bool:
        """Quick connectivity check using multiple endpoints."""
        test_hosts = [
            ("8.8.8.8", 53),      # Google DNS
            ("1.1.1.1", 53),      # Cloudflare DNS
            ("github.com", 443),  # GitHub HTTPS
        ]
        
        for host, port in test_hosts:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port), timeout=3
                )
                writer.close()
                await writer.wait_closed()
                return True
            except Exception:
                continue
        return False
    
    async def update_status(self) -> bool:
        """Update connection status and return True if stable for required window."""
        now = time.time()
        connected = await self.check_connectivity()
        
        if connected:
            if self.connected_since is None:
                self.connected_since = now
            return (now - self.connected_since) >= self.stable_window
        else:
            self.connected_since = None
            return False


class PhoenixUpdater:
    """Manages a local Phoenix installation, updating from GitHub."""
    
    def __init__(self, install_dir: Path):
        self.install_dir = install_dir
        self.repo_dir = install_dir / ".phoenix_repo"  # Bare mirror repo
        self.current_commit = self._get_installed_commit()
        
    def _get_installed_commit(self) -> str:
        """Get commit hash of currently installed Phoenix."""
        commit_file = self.install_dir / ".phoenix_commit"
        if commit_file.exists():
            return commit_file.read_text().strip()
        return ""
    
    def _save_installed_commit(self, commit: str):
        """Record the installed commit hash."""
        (self.install_dir / ".phoenix_commit").write_text(commit)
    
    def _init_mirror_repo(self):
        """Initialize or update a bare mirror repository."""
        if self.repo_dir.exists():
            # Update existing mirror
            subprocess.run(
                ["git", "fetch", "origin", BRANCH],
                cwd=self.repo_dir, capture_output=True, timeout=20
            )
        else:
            # Clone as bare mirror (no working tree, minimal space)
            self.repo_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["git", "clone", "--bare", "--mirror", REPO_URL, str(self.repo_dir)],
                capture_output=True, timeout=30
            )
    
    def _get_remote_commit(self) -> str:
        """Get latest commit from mirror repo."""
        try:
            self._init_mirror_repo()
            result = subprocess.run(
                ["git", "rev-parse", f"origin/{BRANCH}"],
                cwd=self.repo_dir, capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception:
            return ""
    
    def _install_commit(self, commit: str) -> bool:
        """Check out a specific commit to the install directory."""
        try:
            # Create a temporary worktree for the commit
            worktree_dir = self.install_dir / ".phoenix_temp"
            if worktree_dir.exists():
                shutil.rmtree(worktree_dir)
            
            subprocess.run(
                ["git", "worktree", "add", str(worktree_dir), commit],
                cwd=self.repo_dir, capture_output=True, timeout=20
            )
            
            # Copy files to install directory (exclude .git and updater files)
            exclude = {'.git', '.phoenix_repo', '.phoenix_temp', '.phoenix_commit', 'auto_updater.py', 'run_auto_updater.bat'}
            for item in worktree_dir.iterdir():
                if item.name not in exclude:
                    dest = self.install_dir / item.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    if item.is_dir():
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)
            
            # Cleanup
            shutil.rmtree(worktree_dir)
            subprocess.run(
                ["git", "worktree", "prune"],
                cwd=self.repo_dir, capture_output=True
            )
            
            self._save_installed_commit(commit)
            return True
            
        except Exception as e:
            print(f"[Updater] Install failed: {e}")
            return False
    
    async def check_and_update(self) -> bool:
        """Check for updates and apply if available."""
        remote_commit = self._get_remote_commit()
        if not remote_commit:
            print("[Updater] Could not fetch remote commit")
            return False
            
        if remote_commit == self.current_commit:
            return False  # Already up to date
            
        print(f"[Updater] Update available: {self.current_commit[:8] if self.current_commit else 'none'} -> {remote_commit[:8]}")
        
        if self._install_commit(remote_commit):
            self.current_commit = remote_commit
            print("[Updater] Phoenix updated successfully")
            return True
        return False


def find_phoenix_install() -> Path:
    """Find the user's Phoenix installation directory."""
    # Check common locations
    candidates = [
        Path.home() / "phoenix",
        Path.home() / "Phoenix",
        Path.home() / "Documents" / "Phoenix",
        Path("C:/Phoenix"),
        Path("C:/Program Files/Phoenix"),
        Path.cwd(),  # Current directory if run from there
    ]
    
    for c in candidates:
        if (c / "main.py").exists() or (c / "assistant.py").exists():
            return c
    
    # Ask user
    print("Phoenix installation not found in common locations.")
    path = input("Enter full path to your Phoenix installation: ").strip()
    p = Path(path)
    if (p / "main.py").exists() or (p / "assistant.py").exists():
        return p
    raise ValueError("Invalid Phoenix installation path")


async def main():
    print("=" * 50)
    print("Phoenix Auto-Updater (Standalone)")
    print("=" * 50)
    
    try:
        install_dir = find_phoenix_install()
        print(f"[Updater] Found Phoenix at: {install_dir}")
    except Exception as e:
        print(f"[Updater] Error: {e}")
        return
    
    monitor = InternetMonitor()
    updater = PhoenixUpdater(install_dir)
    
    print(f"[Updater] Monitoring {REPO_URL} ({BRANCH})")
    print(f"[Updater] Check interval: {CHECK_INTERVAL}s")
    print(f"[Updater] Requires {STABLE_INTERNET_WINDOW}s stable internet before updating")
    print(f"[Updater] Current version: {updater.current_commit[:8] if updater.current_commit else 'unknown'}")
    print("[Updater] Running in background... (Ctrl+C to stop)")
    print()
    
    while True:
        try:
            stable = await monitor.update_status()
            
            if stable:
                updated = await updater.check_and_update()
                if updated:
                    print("[Updater] Phoenix updated! Restart Phoenix to use new version.")
            else:
                await asyncio.sleep(30)
                continue
                
        except KeyboardInterrupt:
            print("\n[Updater] Stopped by user")
            break
        except Exception as e:
            print(f"[Updater] Error: {e}")
            
        await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
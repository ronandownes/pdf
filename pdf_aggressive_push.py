# pdf_aggressive_push.py
# Aggressive Windows-safe Git pusher for your PDF repo.
#
# - Uses the folder containing THIS script as the repo root (no cd hassle).
# - Keeps scripts in repo (good for reproducing workflow on laptop).
# - Optionally runs pdf_builder.py before committing (toggle below).
#
# Remote:
#   https://github.com/ronandownes/PDF.git
#
# Usage:
#   python pdf_aggressive_push.py

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

REMOTE_URL = "https://github.com/ronandownes/PDF.git"
REMOTE_NAME = "origin"
BRANCH = "main"

# Toggle: build the index.html before push
RUN_BUILDER = True
BUILDER_SCRIPT = "pdf_builder.py"  # expected in repo root

# Default identity to avoid first-commit failures
DEFAULT_USER_NAME = "Ronan Downes"
DEFAULT_USER_EMAIL = "ronandownes@users.noreply.github.com"


def run(cmd: list[str], check: bool = True) -> int:
    print("\n>> " + " ".join(cmd))
    p = subprocess.run(cmd, check=False)
    if check and p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, cmd)
    return p.returncode


def capture(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return (p.stdout or "").strip()


def git_available() -> bool:
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True, text=True)
        return True
    except Exception:
        return False


def ensure_repo():
    if not Path(".git").is_dir():
        run(["git", "init"])
    # make sure branch is called main
    run(["git", "branch", "-M", BRANCH], check=False)


def ensure_remote():
    remotes = capture(["git", "remote"]).splitlines()
    if REMOTE_NAME not in remotes:
        run(["git", "remote", "add", REMOTE_NAME, REMOTE_URL])
    else:
        # enforce the correct URL in case it was different
        run(["git", "remote", "set-url", REMOTE_NAME, REMOTE_URL])


def ensure_identity():
    name = capture(["git", "config", "user.name"])
    email = capture(["git", "config", "user.email"])
    if not name:
        run(["git", "config", "user.name", DEFAULT_USER_NAME], check=False)
    if not email:
        run(["git", "config", "user.email", DEFAULT_USER_EMAIL], check=False)


def maybe_pull_rebase():
    # If remote has main, pull --rebase to reduce push errors
    run(["git", "fetch", REMOTE_NAME], check=False)
    heads = capture(["git", "ls-remote", "--heads", REMOTE_NAME, BRANCH])
    if heads:
        run(["git", "pull", "--rebase", REMOTE_NAME, BRANCH], check=False)


def working_tree_dirty() -> bool:
    return bool(capture(["git", "status", "--porcelain"]).strip())


def prompt_commit_message() -> str:
    # Simple terminal prompt (fast, reliable)
    msg = input("\nCommit message (blank = update): ").strip()
    return msg or "update"


def run_builder_if_enabled(repo_root: Path):
    if not RUN_BUILDER:
        return
    builder = repo_root / BUILDER_SCRIPT
    if not builder.is_file():
        print(f"\n[!] RUN_BUILDER is True but '{BUILDER_SCRIPT}' was not found in:\n    {repo_root}")
        return

    # Use the same Python that is running this script
    print(f"\n>> Running builder: {BUILDER_SCRIPT}")
    p = subprocess.run([sys.executable, str(builder)], check=False)
    if p.returncode != 0:
        print(f"\n[!] Builder returned non-zero exit code ({p.returncode}). Continuing to git anyway.")


def main():
    if not git_available():
        print("ERROR: Git not found on PATH. Install Git for Windows and restart VS Code/terminal.")
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent
    os.chdir(repo_root)
    print("Repo root:", repo_root)

    ensure_repo()
    ensure_remote()
    ensure_identity()
    maybe_pull_rebase()

    # Optional: rebuild index.html before commit
    run_builder_if_enabled(repo_root)

    # Stage everything
    run(["git", "add", "-A"], check=True)

    if working_tree_dirty():
        msg = prompt_commit_message()
        # Use list args (no quoting issues on Windows)
        run(["git", "commit", "-m", msg], check=False)
    else:
        print("\nNothing to commit (working tree clean).")

    # If no commits exist yet, push will fail. Detect and handle nicely.
    head = capture(["git", "rev-parse", "--verify", "HEAD"])
    if not head:
        print("\nERROR: No commits exist yet. Add a file (or change something), then run again.")
        sys.exit(1)

    run(["git", "push", "-u", REMOTE_NAME, BRANCH], check=True)
    input("\nDone. Press Enter to close...")


if __name__ == "__main__":
    main()

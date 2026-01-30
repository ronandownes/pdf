# pdf_aggressive_push.py
# Location: E:/pdfhub/pdf/
# Run:      python pdf_aggressive_push.py
#
# Does:
# - Prompts for commit message EVERY run
# - Runs pdf_builder.py to regenerate index.html
# - git add -A, commit if needed, push to GitHub

import os
import sys
import subprocess
from pathlib import Path

REMOTE_URL = "https://github.com/ronandownes/PDF.git"
REMOTE_NAME = "origin"
BRANCH = "main"
BUILDER = "pdf_builder.py"

DEFAULT_USER_NAME = "Ronan Downes"
DEFAULT_USER_EMAIL = "ronandownes@users.noreply.github.com"

def run(cmd: list[str], check: bool = False) -> int:
    print("\n>> " + " ".join(cmd))
    p = subprocess.run(cmd, check=False)
    if check and p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, cmd)
    return p.returncode

def capture(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return (p.stdout or "").strip()

def ensure_git():
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True, text=True)
    except Exception:
        print("ERROR: Git not found on PATH. Install Git for Windows and restart VS Code/terminal.")
        raise SystemExit(1)

def ensure_repo():
    if not Path(".git").is_dir():
        run(["git", "init"], check=True)
    run(["git", "branch", "-M", BRANCH])

def ensure_remote():
    remotes = capture(["git", "remote"]).splitlines()
    if REMOTE_NAME not in remotes:
        run(["git", "remote", "add", REMOTE_NAME, REMOTE_URL], check=True)
    else:
        run(["git", "remote", "set-url", REMOTE_NAME, REMOTE_URL], check=True)

def ensure_identity():
    if not capture(["git", "config", "user.name"]):
        run(["git", "config", "user.name", DEFAULT_USER_NAME])
    if not capture(["git", "config", "user.email"]):
        run(["git", "config", "user.email", DEFAULT_USER_EMAIL])

def maybe_pull_rebase():
    run(["git", "fetch", REMOTE_NAME])
    heads = capture(["git", "ls-remote", "--heads", REMOTE_NAME, BRANCH])
    if heads:
        run(["git", "pull", "--rebase", REMOTE_NAME, BRANCH])

def main():
    repo_root = Path(__file__).resolve().parent
    os.chdir(repo_root)
    print("Repo root:", repo_root)

    ensure_git()
    ensure_repo()
    ensure_remote()
    ensure_identity()
    maybe_pull_rebase()

    msg = input("\nCommit message (every run): ").strip() or "update"

    # rebuild index
    builder_path = repo_root / BUILDER
    if builder_path.is_file():
        run([sys.executable, str(builder_path)], check=True)
    else:
        print(f"WARNING: {BUILDER} not found; skipping build.")

    run(["git", "add", "-A"], check=True)

    if capture(["git", "status", "--porcelain"]):
        run(["git", "commit", "-m", msg])
    else:
        print("\nNo changes to commit.")

    # ensure at least one commit exists before push
    head = capture(["git", "rev-parse", "--verify", "HEAD"])
    if not head:
        print("\nERROR: No commits exist yet. Make a change/add a file, then run again.")
        raise SystemExit(1)

    run(["git", "push", "-u", REMOTE_NAME, BRANCH], check=True)
    input("\nDone. Press Enter to close...")

if __name__ == "__main__":
    main()

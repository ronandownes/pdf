# pdf_you_pick_mover.py
# Location: E:/pdfhub/pdf/
# Run:      python pdf_you_pick_mover.py
#
# CUT/PASTE mover (YOU pick):
# - Source folder: parent of this script (E:/pdfhub/)
# - Destination:   this script folder (E:/pdfhub/pdf/)   [repo root]
# - Shows PDFs not already present in destination
# - "Show selection" lets you review exactly what will move
# - MOVE = shutil.move (no copies)

import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox

DEST_DIR = os.path.dirname(os.path.abspath(__file__))            # E:/pdfhub/pdf
SRC_DIR = os.path.abspath(os.path.join(DEST_DIR, os.pardir))     # E:/pdfhub

def list_candidates():
    # destination filenames (case-insensitive)
    existing = {
        f.lower() for f in os.listdir(DEST_DIR)
        if os.path.isfile(os.path.join(DEST_DIR, f))
    }

    out = []
    for f in os.listdir(SRC_DIR):
        full = os.path.join(SRC_DIR, f)
        if not os.path.isfile(full):
            continue

        lf = f.lower()
        if not lf.endswith(".pdf"):
            continue

        # skip if already in destination (same name)
        if lf in existing:
            continue

        out.append(f)

    return sorted(out, key=lambda x: x.lower())

def safe_move(src_path: str, dest_dir: str) -> str:
    """
    Move src_path into dest_dir.
    If name collision occurs, append (1), (2), ... before extension.
    Returns destination path used.
    """
    base = os.path.basename(src_path)
    name, ext = os.path.splitext(base)

    target = os.path.join(dest_dir, base)
    i = 1
    while os.path.exists(target):
        target = os.path.join(dest_dir, f"{name} ({i}){ext}")
        i += 1

    shutil.move(src_path, target)
    return target

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("You-pick PDF Mover → repo folder (MOVE / cut-paste)")
        self.geometry("820x640")
        self.minsize(620, 460)

        top = ttk.Frame(self, padding=(12, 10))
        top.pack(fill="x")
        ttk.Label(top, text=f"Source (staging): {SRC_DIR}").pack(anchor="w")
        ttk.Label(top, text=f"Destination (repo): {DEST_DIR}").pack(anchor="w")
        ttk.Label(top, text="Only PDFs. Anything moved is removed from staging (cut/paste).").pack(anchor="w")

        btns = ttk.Frame(self, padding=(12, 0))
        btns.pack(fill="x")
        ttk.Button(btns, text="Select All", command=self.select_all).pack(side="left")
        ttk.Button(btns, text="Clear", command=self.clear_all).pack(side="left", padx=(8, 0))
        ttk.Button(btns, text="Refresh", command=self.refresh).pack(side="left", padx=(8, 0))

        ttk.Button(btns, text="Show selection", command=self.show_selection).pack(side="right", padx=(8, 0))
        ttk.Button(btns, text="MOVE selected", command=self.move_selected).pack(side="right")

        ttk.Separator(self).pack(fill="x", padx=12, pady=10)

        container = ttk.Frame(self, padding=(12, 0))
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.scroll = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_wheel)

        status = ttk.Frame(self, padding=(12, 8))
        status.pack(fill="x")
        self.status_var = tk.StringVar(value="")
        ttk.Label(status, textvariable=self.status_var).pack(anchor="w")

        self.vars = []  # list of (BooleanVar, filename)
        self.refresh()

    def _on_wheel(self, e):
        self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def refresh(self):
        for w in self.inner.winfo_children():
            w.destroy()
        self.vars.clear()

        files = list_candidates()
        if not files:
            ttk.Label(self.inner, text="No PDFs found to move (or all already in destination).").pack(anchor="w", pady=6)
            self.status_var.set("0 files listed.")
            return

        for f in files:
            v = tk.BooleanVar(value=False)
            row = ttk.Frame(self.inner, padding=(0, 2))
            row.pack(fill="x", anchor="w")
            ttk.Checkbutton(row, variable=v).pack(side="left")
            ttk.Label(row, text=f).pack(side="left", fill="x", expand=True)
            self.vars.append((v, f))

        self.status_var.set(f"{len(files)} file(s) available in staging.")

    def select_all(self):
        for v, _ in self.vars:
            v.set(True)

    def clear_all(self):
        for v, _ in self.vars:
            v.set(False)

    def _selected_files(self):
        return [f for v, f in self.vars if v.get()]

    def show_selection(self):
        selected = self._selected_files()
        if not selected:
            messagebox.showinfo("Selection", "Nothing selected.")
            return

        preview = "\n".join(selected[:60])
        if len(selected) > 60:
            preview += f"\n...and {len(selected) - 60} more."

        messagebox.showinfo(
            "These will MOVE (cut/paste)",
            f"Count: {len(selected)}\n\n{preview}"
        )

    def move_selected(self):
        selected = self._selected_files()
        if not selected:
            messagebox.showinfo("Nothing selected", "Tick at least one PDF to move.")
            return

        preview = "\n".join(selected[:30])
        if len(selected) > 30:
            preview += f"\n...and {len(selected) - 30} more."

        ok = messagebox.askyesno(
            "Confirm MOVE (cut/paste)",
            f"This will MOVE (remove from staging) {len(selected)} PDF(s) into:\n\n{DEST_DIR}\n\nFirst few:\n{preview}\n\nContinue?"
        )
        if not ok:
            return

        moved = 0
        errors = []

        for f in selected:
            src_path = os.path.join(SRC_DIR, f)
            try:
                if not os.path.exists(src_path):
                    continue
                safe_move(src_path, DEST_DIR)
                moved += 1
            except Exception as e:
                errors.append(f"{f}: {e}")

        msg = f"Moved: {moved}\nDestination: {DEST_DIR}"
        if errors:
            msg += "\n\nErrors:\n" + "\n".join(errors[:20])
            if len(errors) > 20:
                msg += f"\n...and {len(errors) - 20} more."

        messagebox.showinfo("Done", msg)
        self.refresh()

if __name__ == "__main__":
    App().mainloop()

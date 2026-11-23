#!/usr/bin/env python3
"""The whole UI: a list of files in exes/. Double-click or Enter to run."""
import os, subprocess, threading, tkinter as tk

EXE_DIR = os.environ.get("EXE_DIR", os.path.join(os.getcwd(), "exes"))
EXTS = (".exe", ".msi", ".bat")
BG, FG, ACC = "#111418", "#e6e6e6", "#3b82f6"
running = 0
lock = threading.Lock()

def scan():
    out = []
    base = EXE_DIR.rstrip("/")
    for d, dirs, files in os.walk(base):
        if d[len(base):].count(os.sep) >= 3:
            dirs[:] = []
        for f in files:
            if f.lower().endswith(EXTS):
                out.append(os.path.relpath(os.path.join(d, f), base))
    return sorted(out, key=str.lower)

root = tk.Tk()
root.title("EXE Runner")
root.configure(bg=BG)
root.geometry("640x460+60+40")

status = tk.StringVar(value="")
tk.Label(root, text="EXE Runner", bg=BG, fg=FG, font=("sans", 16, "bold")).pack(pady=(14, 6))
lb = tk.Listbox(root, bg="#1a1f26", fg=FG, selectbackground=ACC, activestyle="none",
                font=("monospace", 12), bd=0, highlightthickness=0)
lb.pack(fill="both", expand=True, padx=14, pady=6)
tk.Label(root, textvariable=status, bg=BG, fg="#9aa4b2").pack(pady=(0, 4))

def command_for(rel):
    path = os.path.join(EXE_DIR, rel)
    low = rel.lower()
    if low.endswith(".msi"):
        return ["wine", "msiexec", "/i", path], os.path.dirname(path)
    if low.endswith(".bat"):
        return ["wine", "cmd", "/c", path], os.path.dirname(path)
    return ["wine", path], os.path.dirname(path)

def restore():
    root.deiconify(); root.lift(); root.focus_force()

def worker(cmd, cwd, name):
    global running
    try:
        p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        code = p.wait()
        subprocess.run(["wineserver", "-w"])
        msg = f"{name} exited" + (f" with code {code}" if code else "")
    except FileNotFoundError:
        msg = "wine is not installed (rerun setup)"
    with lock:
        running -= 1
        left = running
    def done():
        status.set(msg)
        if left == 0:
            restore()
    root.after(0, done)

def run(_=None):
    global running
    sel = lb.curselection()
    if not sel:
        return
    rel = lb.get(sel[0])
    cmd, cwd = command_for(rel)
    with lock:
        running += 1
    status.set(f"Running {rel}…  (F12 brings this window back)")
    threading.Thread(target=worker, args=(cmd, cwd, rel), daemon=True).start()
    root.after(400, root.iconify)

def stop_all():
    subprocess.Popen(["wineserver", "-k"])
    status.set("Stopped everything")

bar = tk.Frame(root, bg=BG); bar.pack(pady=(0, 14))
for text, fn in (("Run", run), ("Stop all", stop_all)):
    tk.Button(bar, text=text, command=fn, bg="#222831", fg=FG, bd=0, padx=18, pady=6,
              activebackground=ACC, activeforeground="white").pack(side="left", padx=6)
lb.bind("<Double-Button-1>", run)
root.bind("<Return>", run)

current = []
def refresh():
    global current
    new = scan()
    if new != current:
        sel = lb.get(lb.curselection()[0]) if lb.curselection() else None
        lb.delete(0, "end")
        for item in new:
            lb.insert("end", item)
        if sel in new:
            lb.selection_set(new.index(sel))
        elif new:
            lb.selection_set(0)
        current = new
        if not new:
            status.set("Upload .exe files into the exes/ folder in the Explorer sidebar")
    root.after(1500, refresh)

refresh()
root.mainloop()

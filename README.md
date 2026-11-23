# EXE Runner (Codespaces)

1. Push this folder to a GitHub repo, then **Code → Codespaces → Create codespace**.
2. Wait for setup to finish (first time only, a few minutes). Port 6080 opens in a new tab.
3. Drag your `.exe` / `.msi` / `.bat` files into the `exes/` folder in the Explorer sidebar.
4. In the tab, double-click one to run it. F12 brings the launcher back; "Stop all" kills everything.

Tuning: edit `RES` in `.devcontainer/start.sh` (960x540 = fastest, 1920x1080 = sharpest).
Restart the display with `bash .devcontainer/start.sh`. Logs are in `/tmp/exe-runner/`.
Files in `exes/` are git-ignored so big uploads don't get committed by accident.

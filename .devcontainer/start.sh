#!/usr/bin/env bash
# Runs on every start. Idempotent.
cd "$(dirname "$0")/.."
export EXE_DIR="$PWD/exes"; mkdir -p "$EXE_DIR" /tmp/exe-runner
RES="${RES:-1280x720}"            # change to 1920x1080 if you want sharper, 960x540 if you want faster
export DISPLAY=:1
export WINEDEBUG=-all             # biggest free speed-up for Wine
export WINEDLLOVERRIDES="mscoree,mshtml=;winemenubuilder.exe=d"
export LP_NUM_THREADS="$(nproc)"  # software GL uses every core

pkill -f "Xvnc :1" 2>/dev/null; pkill -f websockify 2>/dev/null; pkill -f launcher.py 2>/dev/null
sleep 0.5

setsid nohup Xvnc :1 -geometry "$RES" -depth 24 -rfbport 5901 -localhost yes \
  -SecurityTypes None -AlwaysShared >/tmp/exe-runner/xvnc.log 2>&1 &
for i in $(seq 1 50); do [ -S /tmp/.X11-unix/X1 ] && break; sleep 0.1; done

xsetroot -solid black
setsid nohup openbox >/tmp/exe-runner/openbox.log 2>&1 &
setsid nohup bash -c 'while true; do python3 .devcontainer/launcher.py; sleep 1; done' \
  >/tmp/exe-runner/launcher.log 2>&1 &
setsid nohup websockify --web /usr/share/novnc 6080 localhost:5901 \
  >/tmp/exe-runner/websockify.log 2>&1 &
echo "EXE Runner ready on port 6080"

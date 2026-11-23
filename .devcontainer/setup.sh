#!/usr/bin/env bash
# One-time setup: minimal X + VNC + noVNC + openbox + Wine. Nothing else.
set -e
sudo dpkg --add-architecture i386
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  tigervnc-standalone-server novnc websockify openbox wmctrl x11-xserver-utils python3-tk \
  wine wine64 wine32:i386 libwine libwine:i386 fonts-wine \
  libgl1-mesa-dri libgl1-mesa-dri:i386 libglx-mesa0 libglx-mesa0:i386 libgl1:i386

# noVNC landing page: auto-connect, scale to window, reconnect on drop.
echo '<meta http-equiv="refresh" content="0;url=vnc.html?autoconnect=true&resize=scale&reconnect=true&show_dot=true&quality=5&compression=1">' \
  | sudo tee /usr/share/novnc/index.html >/dev/null

# Openbox: default config, minus the right-click desktop menu, plus F12 = bring launcher back.
mkdir -p ~/.config/openbox
cp /etc/xdg/openbox/rc.xml ~/.config/openbox/rc.xml
python3 - <<'PY'
import re, os
p = os.path.expanduser("~/.config/openbox/rc.xml")
s = open(p).read()
s = re.sub(r'<context name="Root">.*?</context>', '', s, flags=re.S)
key = '<keybind key="F12"><action name="Execute"><command>wmctrl -a "EXE Runner"</command></action></keybind>'
s = s.replace("<keyboard>", "<keyboard>\n    " + key, 1)
open(p, "w").write(s)
PY

# Create the Wine prefix headless so the first launch is instant.
WINEDEBUG=-all WINEDLLOVERRIDES="mscoree,mshtml=" DISPLAY= wineboot -u >/dev/null 2>&1 || true
echo "setup done"

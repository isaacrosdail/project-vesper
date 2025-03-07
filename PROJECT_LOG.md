## Use this file for tracking progress / steps / challenges per session/day worked

## Mittwoch 26.02.25
1) Installed RaspberryPi OS on Raspberry Pi 4 Model B
2) Installed node.js & got MagicMirror software running
3) Set up remote control to use web app to tweak MagicMirror layout/config using MMM-Remote-Control, installed dependencies using npm install within ~/modules/MMM-Remote-Control
4) Whitelisted all local IPs to enable access from laptop/etc on same local network

To use MMM-Remote-Control:
1) Start with npm run start on Pi (or npm run server to access through browsers alone)
2) On other computer on same network, go to http://<Rasp Pi's IP address>:8080/remote.html


Commands:
To run (cd MagicMirror):
- npm run start
- npm run start:dev (to start with Dev Tools enabled)
ALT+F4 to escape fullscreen?
ALT to access toolbar menu when in mirror mode
CTRL+SHIFT+I to toggle (web) developer tools from mirror mode

To exit:
CTRL+ALT+T to open new terminal
```killall node```

## [Sonntag 02.03.25] Pomodoro Timer Prototype

Goal(s): Build a Pomodoro timer that:
1. Runs locally on desktop (first test version)
2. Has a start, stop, & reset function
3. Tracks work vs break sessions
4. Later, can be ported to Magic Mirror on Raspberry Pi

What I did this session:
- Added SSH key for new PC && cloned Vesper repo to Desktop/Projects
- Installed Python 3.13 to C:\Program Files\Python313
- Added basic file structure & files
- Implemented basic pomodoro prototype with pomodoro.py as logic for timer and cli.py for start/stop/print/etc for now
-     As part of above, added basic multithreading for timer logic

What to do next time!:
1. Fix user input to enable typing "stop" during the countdown to stop

## [Friday 07.03.25] 

What I did this session:
- Made desktop shortcut on Pi to initiate MagicMirror
- Added hotkey (CTRL+Q) using xbindkeys to killall node to exit MagicMirror
-     Added line to bottom of ~/.xbindkeysrc
- Made a scripts folder on Pi 4B
-     Then used crontab -e (Nano as editor) to add this to start xbindkeys on startup: @reboot /home/pi/scripts/start_xbindkeys.sh


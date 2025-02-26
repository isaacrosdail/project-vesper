## Use this file for tracking progress / steps / challenges per session/day worked

## Mittwoch 26.02.25
1) Installed RaspberryPi OS on Raspberry Pi 4 Model B
2) Installed node.js & got MagicMirror software running
3) Set up remote control to use web app to tweak MagicMirror layout/config using MMM-Remote-Control, installed dependencies using npm install within ~/modules/MMM-Remote-Control

To use MMM-Remote-Control:
1) Start with npm run start on Pi
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

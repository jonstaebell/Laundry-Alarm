# Laundry-Alarm

Detects when your washer or dryer finishes based on audible beeps, then alerts you via Chromecast speakers and Discord.
Deisgned for LG Washer and Dryer: https://youtu.be/5Y7rj98trow
Can be adapted for other appliances

## 📦 Features

- Real-time audio monitoring using PyAudio
- Frequency detection using FFT (Fast Fourier Transform)
- Alerts via:
  - Chromecast speaker playback
  - Discord webhook notifications
- Optional support for multiple Chromecast devices
- Sensitivity, alarm tone, and timing fully configurable

## 🚀 Requirements

- Python 3 (e.g. Python 3.7+)
- Raspberry Pi OS or any Linux-based system
- `pyaudio`, `numpy`, `scipy`, `pychromecast`, `discord_webhook`, etc.

## 🔧 Configuration

Discord Webhook:
The optional Discord webhook is set as environmental variable DISCORD.
If DISCORD variable is "", no webhook is invoked.

Example laundry.sh file:

    export DISCORD="https://discord.com/api/webhooks/..."
    python laundry.py


Update these values in the Python script (laundry.py):
    Chromecast Devices:

device_friendly_name = "Living Room speaker"
device_friendly_name2 = "Library speaker"

    Alarm Frequency:

TONE = 2200  # Frequency to detect
BANDWIDTH = 300
SENSITIVITY = 0.1

audio "LG.WAV" is cast to Chromecast devices when an alarm occurs

## 🛠️ Usage

    Run manually:

./laundry.sh

Or install as a systemd service:
Example laundry_alarm.service:

    [Unit]
    Description=Laundry Alarm Monitor
    After=network.target

    [Service]
    ExecStart=/home/pi/Laundry-Alarm/laundry.sh
    WorkingDirectory=/home/pi/Laundry-Alarmm
    StandardOutput=append:/home/pi/Laundry-Alarm/laundry.log
    StandardError=append:/home/pi/Laundry-Alarm/laundry.log
    Restart=on-failure
    User=pi

    [Install]
    WantedBy=multi-user.target

Then enable the service:

    sudo systemctl daemon-reload
    sudo systemctl enable laundry_alarm.service
    sudo systemctl start laundry_alarm.service

## 🔍 Debugging

Audio from LG Washer and Dryer available here: https://youtu.be/5Y7rj98trow
    View logs:

    tail -f /home/pi/Laundry-Alarm/laundry.log

Check systemd status:

    sudo systemctl status laundry_alarm.service

    See full logs via journalctl:

    journalctl -u laundry_alarm.service

## Acknowledgements

Code for alarm detection taken from https://github.com/benjaminchodroff/alarmBeepDetect/blob/master/alarmBeepDetect.py
Chatgpt used to rewrite my code

## Contact

Project by Jon Staebell, jonstaebell@gmail.com
Feel free to fork, improve, and make it work with other appliances!

## 🛡️ License

This project is open source and available under the MIT License.



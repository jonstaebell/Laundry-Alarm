#!/usr/bin/env python3
"""
Refactored Laundry Alarm - Supports Discord Webhooks & Optional Chromecast Playback
Original: Jon Staebell | Refactored: ChatGPT (2025-06-06)
"""

import time
import pychromecast
import pyaudio
import numpy as np
import os
import sys
from datetime import datetime
from numpy.fft import fft
from discord_webhook import DiscordWebhook

# -----------------------------
# Configuration
# -----------------------------
CONFIG = {
    "alarm_volume": 0.4,
    "tone_frequency": 2200,
    "bandwidth": 300,
    "sensitivity": 0.1,
    "alarm_length": 7,
    "alarm_delay": 60,
    "max_blip_interval": 2,
    "sample_rate": 44100,
    "num_samples": 2048,
    "device_names": ["Living Room speaker", "Library speaker"],
    "audio_url": "http://127.0.0.1/home/pi/Laundry-Alarm/LG.wav",
    "debug": True,
    "frequency_output": False,
    "min_log_freq": 800,
    "max_log_freq": 3000
}

CONFIG["discord_webhook"]= os.getenv('DISCORD', '')

# -----------------------------
# Discord Logging
# -----------------------------
def send_discord_message(message: str): 
    program_name, _ = os.path.splitext(os.path.basename(sys.argv[0])) # remove path and extension from current program name
    print (program_name + ": " + message,flush=True)
    if CONFIG["discord_webhook"] != '':
        webhook = DiscordWebhook(url=CONFIG["discord_webhook"], content=program_name + ": " + message)
        try:
            webhook.execute()
        except Exception as e:
            print(f"Discord webhook error: {e}",flush=True)

# -----------------------------
# Logging Helper
# -----------------------------
def log_event(event, param=''):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [now, event, param]
    if CONFIG["debug"]:
        print(row,flush=True)
 
# -----------------------------
# Chromecast Setup
# -----------------------------
def find_chromecasts(device_names):
    casts = {}
    chromecasts = pychromecast.get_chromecasts()
    for name in device_names:
        cast = next((cc for cc in chromecasts if cc.device.friendly_name == name), None)
        if cast:
            cast.wait()
            casts[name] = cast
        else:
            msg = f"{name} not found, skipping..."
            print(msg,flush=True)
            send_discord_message(msg)
    return casts


# -----------------------------
# Alarm Trigger
# -----------------------------
def trigger_alarm(casts):
    send_discord_message("Alarm! " + datetime.now().strftime("%I:%M%p on %B %d, %Y"))
    for name, cast in casts.items():
        mc = cast.media_controller
        try:
            old_volume = cast.status.volume_level
            cast.set_volume(CONFIG["alarm_volume"])
            mc.play_media(CONFIG["audio_url"], content_type="audio/wav")
            time.sleep(10)
            cast.set_volume(old_volume)
        except Exception as e:
            print(f"Error with {name}: {e}",flush=True)

# -----------------------------
# Audio Input Setup
# -----------------------------
def setup_audio_stream():
    pa = pyaudio.PyAudio()
    return pa.open(format=pyaudio.paInt16,
                   channels=1,
                   rate=CONFIG["sample_rate"],
                   input=True,
                   frames_per_buffer=CONFIG["num_samples"])

# -----------------------------
# Frequency Detection
# -----------------------------
def detect_beep(data):
    normalized = data / 32768.0
    intensity = np.abs(fft(normalized))[:CONFIG["num_samples"] // 2]
    frequencies = np.linspace(0.0, CONFIG["sample_rate"] / 2, CONFIG["num_samples"] // 2)

    if CONFIG["frequency_output"]:
        peak = intensity[1:].argmax() + 1
        if peak != len(intensity) - 1:
            y0, y1, y2 = np.log(intensity[peak-1:peak+2])
            x1 = 0.5 * (y2 - y0) / (2*y1 - y2 - y0)
            thefreq = (peak + x1) * CONFIG["sample_rate"] / CONFIG["num_samples"]
        else:
            thefreq = peak * CONFIG["sample_rate"] / CONFIG["num_samples"]
        if CONFIG["min_log_freq"] < thefreq < CONFIG["max_log_freq"]:
            log_event("freq", thefreq)

    tone_range = (frequencies > CONFIG["tone_frequency"] - CONFIG["bandwidth"]) & \
                 (frequencies < CONFIG["tone_frequency"] + CONFIG["bandwidth"])
    noise_range = (frequencies > CONFIG["tone_frequency"] - 2000) & \
                  (frequencies < CONFIG["tone_frequency"] - 1000)
    
    return intensity[tone_range].max() > intensity[noise_range].max() + CONFIG["sensitivity"]

# -----------------------------
# Main Loop
# -----------------------------
def main():
    send_discord_message("Laundry alarm started " + datetime.now().strftime("%I:%M%p on %B %d, %Y")) 
    stream = setup_audio_stream()
    casts = find_chromecasts(CONFIG["device_names"])
    
    blip_count = 0
    last_blip = datetime.now()
    last_alarm = datetime(2000, 1, 1)

    print(datetime.now(), "Alarm detector working. Press CTRL-C to quit.",flush=True)
    log_event("Start " + datetime.now().strftime("%I:%M%p on %B %d, %Y")) 

    try:
        while True:
            if stream.get_read_available() < CONFIG["num_samples"]:
                time.sleep(0.01)
                continue

            audio_data = np.frombuffer(stream.read(CONFIG["num_samples"]), dtype=np.int16)
            if detect_beep(audio_data):
                now = datetime.now()
                if (now - last_blip).seconds > CONFIG["max_blip_interval"]:
                    blip_count = 0
                    if CONFIG["debug"]:
                        print("Blip count reset",flush=True)

                blip_count += 1
                last_blip = now
                log_event("Blip", blip_count)

                if blip_count >= CONFIG["alarm_length"] and (now - last_alarm).seconds > CONFIG["alarm_delay"]:
                    trigger_alarm(casts)
                    last_alarm = now
                    blip_count = 0
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Interrupted. Exiting.",flush=True)
        send_discord_message("Laundry alarm stopped " + datetime.now().strftime("%I:%M%p on %B %d, %Y")) 

# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    main()

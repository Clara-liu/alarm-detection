# Alarm detection
This script can be used to detect audio alarms and alert you via a telegram text.
## Requirements
- A USB microphone
- A device such as a raspberry pi for compute
- Internet connection
- Python 3.x and pip on the device (tested with python 3.9.2 and pip 22.3)
## Installation
On the device (e.g. ssh into rasp pi), do:
1. Install PyAudio with `sudo apt install python3-pyaudio`. See [here](https://pypi.org/project/PyAudio/) for alternative methods.
2. Install dependencies with `pip install -r requirements.txt`.
3. Create a yaml file like below. For instructions on how to obtain a bot token and chat ID with Telegram, see [here](https://medium.com/codex/using-python-to-send-telegram-messages-in-3-simple-steps-419a8b5e5e2).
   ```yaml
   token: <YOUR BOT TOKEN>
   chat_id: <A CHAT ID>
   ```
## Usage
Run `python detection.py --help` for manual:
```
usage: detector.py [-h] --alarm-freq ALARM_FREQ [--band-width BAND_WIDTH] [--volume-gate VOLUME_GATE] [--alert-win ALERT_WIN] --mic-id MIC_ID [--test-mode]
                   [--verbose] --telegram-file TELEGRAM_FILE

Audio alarm detection

optional arguments:
  -h, --help            show this help message and exit
  --alarm-freq ALARM_FREQ
                        Frequency of the alarm to detect
  --band-width BAND_WIDTH
                        Error margin is equal to the alarm freq plus and minus band width
  --volume-gate VOLUME_GATE
                        Alarm is detected when the loudest frequency is louder than this threshold.
  --alert-win ALERT_WIN
                        How many beeps before alerting.
  --mic-id MIC_ID       The device ID of the USB microphone.
  --test-mode           whether to use testing mode.
  --verbose             Whether to log each detection.
  --telegram-file TELEGRAM_FILE
                        Path to file containing info on telegram bot.
```
### Arguments
Only three are *not* optional: `--alarm-freq`, `--mic-id` and `--telegram-file`.

- **--alarm-freq**: The frequency of your alarm tone. In the UK it is usually 3000 Hz. You can visualise the spectrogram of your alarm signal with software like Audacity ot Praat.
- **--band-width**: The error margin for alarm detection.
- **--volume-gate**: The threshold of loudest for detection trigger. The default is 0.1. You can play with this parameter to adjust the sensitivity of the detector.
- **--alert-win**: Alert is sent when the detector detects the presence of an alarm consecutively for this amount of times. You can play with this parameter to adjust the sensitivity of the detector.
- **--mic-id**: The ID of your USB microphone according to Pyaudio. You can run `python utils/get_devices.py` to list all the devices available.
- **--test-mode**: Whether to enter test mode.
- **--verbose**: Whether to log details of each detection.
- **--telegram-file**: Path to a yaml file containing information on your telegram bot and chat ID. This should either be an absolute path or relative to this folder.
## System Service
For ease of installation, a systemd service file is available: [systemd/alarm-detection.service](./systemd/alarm-detection.service).

This service file assumes that the path to your detection repo is `/opt/alarm-detection`, modify `WorkingDirectory` if this isn't the case.

Modify the `ExecStart` with the arguments you want to use.

Copy the systemd service file to `/etc/systemd/system` and start the service
```bash
sudo systemctl start alarm-detection
```
and enable automatically start on boot
```bash
sudo systemctl enable alarm-detection
```
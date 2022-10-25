# Alarm detection
This script can be used to detect audio alarms and alert you via text.
## Requirements
- A USB microphone
- A device such as a raspberry pi for compute
- Internet connection
- Python 3.x and pip3 on the device
## Installation
On the device (e.g. ssh into rasp pi), do:
1. Install PyAudio with `sudo apt install python3-pyaudio`. See [here](https://pypi.org/project/PyAudio/) for alternative methods.
2. Install dependencies with `pip install -r requirements.txt`.
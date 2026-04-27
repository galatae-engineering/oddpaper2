INSTALL:

cd ~/git/oddpaper2
python3 -m venv venv
source venv/bin/activate
pip install pyserial
pip install opencv-python
pip install RPi.GPIO

LAUNCH:
cd ~/git/oddpaper2 && source venv/bin/activate && sudo python main.py

pinctrl set 5 op dl
pinctrl set 5 op dh

vcgencmd measure_temp
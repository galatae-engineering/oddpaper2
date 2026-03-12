INSTALL:

cd ~/git/oddpaper2
python3 -m venv venv
source venv/bin/activate
pip install pyserial

LAUNCH:
cd ~/git/oddpaper2 && source venv/bin/activate && sudo python main.py

pinctrl set 4 op dl
pinctrl set 4 op dh
#!/usr/bin/env python3
import subprocess
import time
import sys

app = "gnome-sudoku"
subprocess.Popen([app])

t = 0
while t < 20:
    try:
        # wait for the application's pid
        pid = subprocess.check_output(["pgrep", "-f", app]).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        pass
    else:
        try:
            # read the window list
            w_data = subprocess.check_output(["wmctrl", "-lp"]).decode("utf-8").splitlines()
            # find the window of the found pid
            window = [w.split()[0] for w in w_data if pid in w][0]
            # raise it and terminate the script
            subprocess.Popen(["wmctrl", "-ia", window])
            break
        except IndexError:
            pass
    time.sleep(0.5)
    t = t + 1

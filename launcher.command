#!/bin/bash
defaults write com.apple.Terminal NSQuitAlwaysKeepsWindows -bool false
echo HBS_Tools opening ...
cd /Users/olivier/Documents/Doc_2020/Q9_25_Memoire/Master-thesis-repo/
python3 -Wignore main.py > log.txt
killall Terminal
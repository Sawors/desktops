#!/bin/bash
detectService="desktops-detect.service"
applyService="desktops-apply.service"

sudo ln -s $(pwd)/$detectService /etc/systemd/system
#sudo ln -s $(pwd)/$applyService /etc/systemd/user

sudo systemctl enable $detectService
#systemctl --user enable $applyService

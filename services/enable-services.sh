#!/bin/bash
detectService="desktops-detect.service"
applyService="desktops-apply.service"

desktops_root=/etc/desktops

sudo ln -s $desktops_root/$detectService /etc/systemd/system
sudo ln -s $desktops_root/$applyService /etc/systemd/user

sudo systemctl enable $detectService
systemctl --user enable $applyService

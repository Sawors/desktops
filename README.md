# desktops
Desktops is a lightweight tool designed to allow you to use a single operating system on different hardware. Its primary usage is to allow operating systems installed on bootable external hard drives to be used on different machines seamlessly.

## Usage
Desktops is meant to be launched at startup, during the boot process. It acts in 2 phases :
1. Initial detection of the hardware and triggering of root launch scripts
2. Triggering of user launch scripts

## Hardware Configs
Desktops is based on a **hardware config** system. Each combinaison of hardware you want to detect is defined in a `yaml` file named `components.yml`. These files will be loaded during the early detection of the hardware, and can be located in two places : `/etc/desktops/computers/` and `/usr/share/desktops/computers`.

These 


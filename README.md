# desktops
*Desktops* is a lightweight tool designed to allow you to use a single operating system on different hardware. Its primary usage is to allow operating systems installed on bootable external hard drives to be used seamlessly on different machines.

## Usage
*Desktops* is launched at startup during the boot process. It acts in 2 phases :
1. Initial detection of the hardware and triggering of root launch scripts
2. Triggering of user launch scripts

## Hardware Configs
Desktops is based on a **hardware config** system. Each combination of hardware you want to detect is defined in a `yaml` file named `components.yml`. These files will be loaded during the early detection of the hardware. 

The default location for hardware configs is `/usr/share/desktops/hardware/`, but other configs located in `<script directory>/hardware/` may be loaded if present.

### File structure
Each config consists of a directory containing a hardware description, and a few startup scripts.
```
hardware/
  ├─ <config-name>/
  │   │
  │   ├─ components.yml
  │   ├─ user-launch.sh
  │   └─ root-launch.sh
  │
  ├─ <other-hardware-config>/
  │   │
  │   └...
  │
  └...
```

The name of the directory the components are stored in is used as the name of the config.
When the hardware detection is first run, it will attempt to read each `components.yml` file to determine the closest match of hardware (this description follows a specific structure, TODO : ADD WIKI LINK).

>Note : if you need to match only exactly corresponding hardware, a config option should be added soon to restrict the matching process

### Startup scripts
When the initial detection is done and the config is found, the `root-launch.sh` script is immediately run as root. Please ensure that the permissions of this file are properly set to avoid the execution of unknown code with root privileges.

Once the inital detection and root startup has been executed, scripts are no more automatically executed and user scripts should be started manually.  


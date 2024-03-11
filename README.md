# desktops
*desktops* is a lightweight tool designed to allow you to use a single operating system on different hardware. Its primary usage is to allow operating systems installed on bootable external hard drives to be used seamlessly on different machines.

## Usage
*desktops* is launched at startup during the boot process. It acts in 2 phases :
1. Initial detection of the hardware and triggering of root launch scripts
2. Triggering of user launch scripts

The main commands of *desktops* are :
```bash
# Detects the currently used config, and write the found config to disk.
desktops detect
```
```bash
# Executes startup scripts for the current config
desktops apply
```

>For more commands, run `desktops --help`

## Hardware Configs
Desktops is based on a **hardware config** system. Each combination of hardware you want to detect is defined in a `yaml` file named `components.yml`. These files will be loaded during the early detection of the hardware. 

The default location for hardware configs is `/etc/desktops/hardware/`.

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

## Startup scripts
### Root script
When the initial detection is done and the config is found, the `root-launch.sh` script is immediately run as root. Please ensure that the permissions of this file are properly set to avoid the execution of unknown code with root privileges.

### User scripts
Once the inital detection and root startup has been executed, scripts are no more automatically executed and user scripts should be started manually.

To start user scripts, use `desktops apply` while logged in to start them. User scripts can be in two locations :
- `/etc/desktops/hardware/<config_name>/user-launch.sh`
- `~/.config/desktops/hardware/<config_name>/user-launch.sh`

Using two different locations allows you to create a general user script, which will be executed for all users when they log in, and user-specific scripts.

In order of execution, the general script located in `/etc/.../<config_name>` will be executed **before** the script in the user's home directory.

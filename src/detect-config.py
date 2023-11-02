#!/bin/env python3
from os import system
from os import path
import os
from sys import argv
from time import time
#from plyer import notification
import subprocess
import glob
import yaml

root = "/etc/desktops"
computers = "hardware"
hardwareLocations = [f"/usr/share/desktops/{computers}", f"{root}/{computers}"]
currentUsedConfig = f"{root}/current"
configFormat = "components.yml"
displayIdentifier = "Display"
memoryIdentifier = "memory"
cpuIdentifier = "cpu"
launchScriptIdentifier = "launch-script"
userConfigLocation = f".config/desktops/{computers}"
EXACT_MATCH=False


# TODO 
#   - [ ] add program config support
#   - [ ] change language (to a compiled/packaged one, java/rust/dart)
#   - [ ] create README
#   - [ ] add to git
#   - [ ] split code into dedicated classes and interfaces
#


# takes raw data, and attempts to make it standardized.
# Data should be split with one component per key (and monitor amount pre-computed)
# this methods DOES NO ALTER THE BASE COLLECTION, but it does clone it, thus increasing memory footprint
# NOTE : this method works for fast fetch only
# TODO : move this to the fastfetch implementation
def standardizeData(rawData: dict) -> dict:
    data = rawData.copy()
    for rawKey in rawData.keys():
        value = str(rawData[rawKey])
        key = rawKey.lower()

        if key == memoryIdentifier and "/" in value and "(" in value:
            value = value[value.find("/")+2:value.find("(")-1]
        elif key == cpuIdentifier and "@" in value:
            value = value[0:value.find("@")-1]
            
        data[key] = value
    return data


# TODO : move this to the fastfetch implementation
def loadComponents() -> dict:
    output = ""
    try:
        output = subprocess.check_output("fastfetch --pipe -s Board:CPU:GPU:Memory:Display --multithreading", shell=True).decode("UTF-8")
    except subprocess.CalledProcessError :
        print("an error occured when fetching the data !")
        print("no config found")
        with open(currentUsedConfig,"w") as current:
            current.write("unknown")

    fetched = output.strip().splitlines()

    dataMap = {}
    monitorAmount = 0

    for entry in fetched :
        if entry.startswith(displayIdentifier):
            # do not count monitors with a height smaller than 1080 pixels (to avoid detecting fake monitors)
            if(int(entry.split("x")[1][0:4]) < 1080):
                continue
            monitorAmount+=1
        else:
            duo = entry.split(":")
            key = str(duo[0])
            data = duo[1].strip()
                
            dataMap[str(duo[0]).lower()] = data
    
    dataMap["monitors"] = monitorAmount

    return standardizeData(dataMap)


# returns the number of matching fields (so that a general config may be applied if all other fail and exact match is set to false)
def matchConfig(config: str, dataMap: dict, exactMatch=False) -> int:
    if (not path.isfile(config)) or dataMap == None or len(dataMap) == 0: return 0
    matching = 0
    try:
        with open(config) as configRawData :
            data = standardizeData(yaml.safe_load(configRawData))

            if exactMatch and data == dataMap: return len(dataMap)

            # if exactMatch is not specified, it will attempt to find the closest config it can find
            for field in data.keys() :
                if field in dataMap and data[field].lower() == dataMap[field].lower(): 
                    matching += 1
    except e as PermissionError:
        print(f"Config {config} could not be loaded due to unsufficient permissions")

    return matching


# returns a dict containing the paths to the configs found. It loads the configs found in the users home directory
# and the ones defines in TODO config.yml
def loadConfigs() -> set:
    userConfigs = set()
    homeDir = "/home"
    if not path.isdir(homeDir): return userConfigs
    for user in glob.glob(root_dir=homeDir,recursive=False,pathname="*/"):
        configRoot = f"{homeDir}/{user}{userConfigLocation}"
        if not (path.isdir(configRoot)) : continue
        for configName in glob.glob(root_dir=configRoot, pathname=f"*/{configFormat}", recursive=True):
            userConfigs.add(f"{configRoot}/{configName}")

    for rootpath in hardwareLocations :
        for config in glob.glob(root_dir=rootpath, recursive=True, pathname=f"*/{configFormat}"):
                userConfigs.add(f"{rootpath}/{config}")
    
    return userConfigs


def trimConfigName(configPath:str) -> str:
    trimmed = str(configPath)
    if f"/{configFormat}" in trimmed.lower():
        trimmed = trimmed[0:trimmed.rfind(f"/{configFormat}")]
    if "/" in trimmed:
        trimmed = trimmed[trimmed.rfind("/")+1:len(trimmed)]

    return trimmed

def detect():
    startTime = time()
    dataMap = loadComponents()
    fetchTime = round((time()-startTime)*1000)
    print(f"fetching took {fetchTime}ms")
    dataSize = len(dataMap)
    print(f"hardware: {dataMap}")

    foundConfigs = loadConfigs()
    print(f"found {len(foundConfigs)} hardware configs")
    matchMap = {}

    for configPath in foundConfigs:
        matchMap[configPath] = matchConfig(config=configPath, dataMap=dataMap, exactMatch=EXACT_MATCH)
    
    config = None
    configPath = ""

    sortedMatches = sorted(matchMap.items(), key=lambda k:k[1], reverse=True)

    if not (len(sortedMatches) == 0 or (EXACT_MATCH and sortedMatches[0][1] != dataSize)):
        bestMatch = sortedMatches[0]
        configPath = path.dirname(bestMatch[0])
        config = trimConfigName(configPath)
        if bestMatch[1] == dataSize:
            print(f"config [{config}] exactly matched !")
        elif not EXACT_MATCH:
            print(f"using config [{config}] with {bestMatch[1]}/{dataSize} matches")


    if config != None:
        with open(currentUsedConfig,"w") as current:
            current.write(f"{config}\n{configPath}\n")

    else:
        print("no config found")
        with open(currentUsedConfig,"w") as current:
            current.write("unknown")
    totalTime = round((time()-startTime)*1000)
    print(f"config matching done in {totalTime-fetchTime}ms")
    print(f"complete config detection done in {totalTime}ms")

def apply(args: list):
    # the config will be applied as the current user. For any operation requiring root privileges please edit /etc/sddm/Xsetup.
    passedArgument = ""
    for index, otherArg in enumerate(args):
        if (otherArg == "--type" or otherArg == "-t") and len(args) > index+1:
            passedArgument = args[index+1]
            break
        
    config = None
    scripts = [None]*2

    isRoot = "--root" in args or "-r" in args

    def checkSure():
        sure = input("Are you sure this is what you want to do ? (y/N): ").lower() in ["y","yes"]
        if not sure:
            print("User cancelation, aborting sequence.")
            exit()

    if isRoot and os.geteuid() != 0:
        print("Applying root config as a non-root user, this is not an intended usage.")
        checkSure()
    elif (not isRoot) and os.geteuid() == 0:
        print("Root user detected, automatically switching to root mode (--root)")
        isRoot = True

    if isRoot:
        print("Applying root startup scripts...")
    else:
        print(f"Applying user startup scripts for user [{os.getlogin()}]...")

    # general config launch script
    with open(currentUsedConfig, "r") as current:
        lines = current.readlines()
        config = lines[0].strip()
        configPath = lines[1].strip()
        generalFile = f"{configPath}/{'root-launch' if isRoot else 'user-launch'}.sh"
        if path.isfile(generalFile):
            scripts[0] = generalFile
        elif path.isfile():
            print(f"ERROR: config path not found, did the config detection execute well? (path: {configPath})")
    
    if config == None or len(config) == 0:
            print("No config found!")
            exit(1)

    # user-specific launch script
    if not isRoot:
        userConfig = path.expanduser(f"~/.config/desktops/{computers}/{config}/user-launch.sh")
        if path.isfile(userConfig): scripts[1] = userConfig

    successfulScripts = 0

    for s in scripts:
        try:
            if not s == None and not len(s) == 0: 
                #system(f"{s} {passedArgument}")
                successfulScripts += 1
        except:
            print(f"Permissions to run {s} denied !")
            if isRoot:
                print("Please run this program with root privileges when using --root or -r !")

    if not isRoot:
        try:
            system(f"notify-send \"Desktops\" \"Config [{config}] {'applied' if successfulScripts > 0 else 'FAILED TO BE APPLIED'} !\"")
        except:
            print("notification could not be sent! THIS IS NOT AN ERROR BUT A BAD IMPLEMENTATION")
    

#
#   End of definitions, beginning of script flow
#

try:
    hardwareLocations.append(f"{path.dirname(argv[0])}/{computers}")
except:
    print("Current directory not usable for hardware detection")

if len(argv) < 2:
    print("""
    Please specify an action.

    Possible actions are :
        detect
        apply
        create""")
    exit()

argument = argv[1]
match argument:
    case "detect":
        print("Detecting hardware configuration...")
        detect()
        
    case "apply":
        apply(argv)

    case "create":
        print("not patched yet! Aborting creation")
        exit()

exit()

for argument in argv:
    if(argument.startswith("create")):
        name = argument[len("--create")+1:len(argument)]
        dataMap = loadComponents()
        dataMap[launchScriptIdentifier] = f"{root}/{computers}/{name}/user-launch.sh"
        
        # write config yaml
        with open(f"{root}/{computers}/{name}/config.yml", "w") as targetFile:
            yaml.safe_dump(data=dataMap,stream=targetFile)
        # write empty root script (if possible)
        try :
            scriptPath = f"{root}/{computers}/{name}/root-launch.sh"
            if(path.isfile(scriptPath)): break
            with open(scriptPath, "w") as targetRootScript :
                targetRootScript.write("# instructions put here will be executed as root, be careful !")
        except PermissionError as e:
            print("could not create the template root script : permission denied")        
        try :
            scriptPath = f"{root}/{computers}/{name}/user-launch.sh"
            if(path.isfile(scriptPath)): break
            with open(scriptPath, "w") as targetScript :
                targetRootScript.write(""" # instructions put here are executed as the current logged user
                
                do_delayed_operation() {
                    # since this script is part of the booting process, it must by design not
                    # slow down the system. Instruction put here are executed ASYNCHRONOUSLY from the
                    # main thread in a SINGLE NEW THREAD (by default). It means that you cann still
                    # put operations in a sequential execution order even if we are out of the main thread

                    # > delayed operations here <
                    # these operations usually are queries taking some delay to finish,
                    # like for instance getting a list of available networks and doing operations
                    # on this list.

                }

                # executing the async block 
                do_delayed_operations &

                if [[ $1 == "boot" ]];
                then
                    # put here instructions which should be executed only at boot
                    # (at boot the string "boot" should be passed to this script)
                    #
                    # usually this is useful to start commonly used softwares
                fi
                """)
        except PermissionError as e:
            print("could not create the template root script : permission denied")        

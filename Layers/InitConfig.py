import common
from Layers.command import setLayer
from Layers.keyEvents import hook
import os
import json
try:
    import keyboard
except ImportError:
    keyboard = None

try:
    import evdev
except ImportError:
    evdev = None

from threading import Event, Thread
import re
from customFuncs import *
from Layers.runTimeConfig import parseKeyConfig, getAppCmds

def updateConfig():
    
    getAppCmds.cache_clear()

    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hotkeysJson", "config.json"), "r") as file:
        conf = json.load(file)

        common.doRemapping = conf.get("doRemapping", common.doRemapping )
        common.layout = conf.get("layout", common.layout)
        common.drawGUI = conf.get("drawGUI", common.drawGUI)
        common.updateBGInterval = conf.get("updateBGInterval", common.updateBGInterval)
        common.disabledApps = conf.get("DisableGUIIn", common.disabledApps)

        common.toggleKey = conf["toggleKey"].lower()
        common.toRemap = [key["remap"].lower() for key in conf["keys"]]
        common.untoggled = {key["remap"].lower():parseKeyConfig(key["baseLayer"]) for key in conf["keys"]}
        
        common.toggleActions = {
                                "tap"   : parseKeyConfig(conf["ToggleActions"]["tap"]),
                                "longPress" : parseKeyConfig(conf["ToggleActions"]["longPress"]),
                                }

        for val in conf["Funcs"]:
            prefix = val["prefix"]
            cmd = val["function"]
            common.prefixToFunc[prefix] = globals()[cmd]

    for fileName in os.listdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hotkeysJson")):
        if fileName.endswith(".json") and fileName != "config.json":
            fullFileName = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hotkeysJson", fileName)
            with open(fullFileName, "r") as file:
                conf = json.load(file)

                keys = {}
                appName = conf["appName"]
                common.titleMatchToConfigFile[appName] = fullFileName

                if "regex" in conf:
                    if "priority" in conf:
                        priority = conf["priority"]
                    else:
                        priority = 0

                    regex = conf["regex"]
                    common.regexToAppName[re.compile(regex)] = (appName, int(priority))
    

    common.keyReleaseEvents[common.toggleKey] = Event()
    if keyboard:
        keyboard.unhook_all()

        keyboard.hook_key(common.toggleKey, hook, suppress=True)

        if common.doRemapping:
            for key in common.toRemap:
                keyboard.hook_key(key, hook, suppress=True)
    elif evdev:
        def keyHooks():
            device = evdev.InputDevice("/dev/input/event25")
            device.grab()

            for event in device.read_loop():
                hook(event)

        
        t = Thread(target=keyHooks)
        t.start()
import common
from Layers.command import command, setLayer
from Layers.keyEvents import hook
import os
import json
import keyboard
from typing import Callable, Union, List, Dict
from threading import Event
import re
from customFuncs import *

def parseKeyConfig(conf : Union[Dict[str, str], List[Dict[str, str]]]) -> Union[command, List[command], None]:
    if type(conf) is dict:
        if "press" in conf or "rel" in conf:
            return command(conf.get("press", ""), common.prefixToFunc, conf.get("rel", ""), imgPath=conf.get("icon path", None), description = conf.get("description", None))
        else:
            return None
    elif type(conf) is list:
        retVal = []
        for c in conf:
            retVal.append( parseKeyConfig(c))

        if retVal:
            return retVal
        else:
            return None

    else:
        return None

def updateConfig():

    

    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hotkeysJson", "config.json"), "r") as file:
        conf = json.load(file)

        common.doRemapping = conf.get("layout", True)
        common.layout = conf.get("layout", None)

        common.toggleKey = conf["toggleKey"].lower()

        common.toRemap = [key["remap"].lower() for key in conf["keys"]]
        common.appToKeys["Untoggled"] = [key["baseLayer"] for key in conf["keys"]]

        for val in conf["actions"]:
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

                for key, target in enumerate(conf["hks"]):
                    keys[common.toRemap[key]] = parseKeyConfig(target)

                common.appToKeys[appName] = keys

                if "regex" in conf:
                    if "priority" in conf:
                        priority = conf["priority"]
                    else:
                        priority = 0

                    regex = conf["regex"]
                    common.regexToAppName[re.compile(regex)] = (appName, int(priority))
    
    keyboard.unhook_all()

    keyboard.hook_key(common.toggleKey, hook, suppress=True)
    common.keyReleaseEvents[common.toggleKey] = Event()

    for key in common.toRemap:
        keyboard.hook_key(key, hook, suppress=True)
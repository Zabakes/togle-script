
from typing import Callable, Union, List, Dict
from Layers.command import command, setLayer
import common
import json
from functools import lru_cache

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

@lru_cache(3)
def getAppCmds(titleMatch):
    with open(common.titleMatchToConfigFile[titleMatch], "r") as file:
        conf = json.load(file)

        keys = {}

        for key, target in enumerate(conf["hks"]):
            keys[common.toRemap[key]] = parseKeyConfig(target)

        return keys

def getCmd(key, titleMatch = None):

    if titleMatch is None:
        titleMatch = common.getTitleMatch()
    
    toSend = getAppCmds(titleMatch)
    if not(cmd := toSend.get(key, None)):
        cmd = getAppCmds("Default").get(key)

    if type(cmd) is list:
        l = min(len(cmd)-1, common.getLayer())
        cmd = cmd[l]
        if cmd is None:
            cmd = getAppCmds("Default").get(key)

    return cmd
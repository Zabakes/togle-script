import re
import common
try:
    import keyboard
except ImportError:
    keyboard = None

try:
    from evdev import UInput, ecodes
except ImportError:
    evdev = None
from time import sleep
import json
from collections.abc import Iterable
from customFuncs import *

def setLayer(s=None, *args, **kwargs):
    
    if common.isEditing:
        return

    if not kwargs:
        kwargs = json.loads(s)

    if kwargs["type"] == "inc":
        common.layer += 1
        if "max" in kwargs and common.layer > kwargs["max"]:
            common.layer = kwargs["max"]
    elif kwargs["type"] == "dec":
        common.layer -= 1
        common.layer = max(common.layer, 0) 
    elif kwargs["type"] == "set":
        common.layer = kwargs["val"]

    common.redrawGui = True

def wrapFunc(f, callback=None, *args, **kwargs):
    def func():
        f(*args, **kwargs)
        if callback:
            callback()
    return func

class command():
    
    fmtString = re.compile(r"(?<!\\){(?P<cmd>.*?)((?P<down> down)|(?P<up> up))?(?<!\\)}|(?P<str>[^\{]+)")
    ui = UInput()
    
    def __init__(self, press, prefixToFunc={}, release="", description = None, imgPath = None) -> None:
        self.description = description
        self.imgPath = imgPath
        self.pressS = str(press)
        self.releaseS = str(release)
        self.waitForRel =  False
        self.hideGUIBeforeRun = False
        self.runFuncs = self.getFuncsList(press, prefixToFunc)
        self.releaseFuncs = self.getFuncsList(release, prefixToFunc)

        if self.description is None:
            self.description = self.__str__()

    def __str__(self) -> str:
        return f"{{\"press\" : \"{self.pressS}\", \"rel\" : \"{self.releaseS}\"}}"

    def __repr__(self) -> str:
        return self.__str__()

    def getFuncsList(self, config, prefixToFunc={}):
        funcs = []
        if type(config) is str:
            for match in re.finditer(self.fmtString, config):
                if sendStr := match.group("str"):
                    self.hideGUIBeforeRun = True
                    funcs.append(self.sendStrFactory(sendStr))
                elif cmd := match.group("cmd"):
                    cmd = re.sub(r"\\+({|})", r"\g<1>", cmd)
                    if cmd[0] in prefixToFunc.keys():
                        if prefixToFunc[cmd[0]] != setLayer:
                            self.hideGUIBeforeRun = True

                        funcs.append((lambda : prefixToFunc[cmd[0]](cmd[1:]),  f"{prefixToFunc[cmd[0]].__name__}({cmd[1:]})"))
                    else:
                        self.hideGUIBeforeRun = True
                        if match.group("down"):
                            if keyboard:
                                funcs.append((wrapFunc(keyboard.press, cmd), f"down {cmd}"))
                            else:
                                if key := ecodes.ecodes.get(f'KEY_{cmd}', None):
                                    funcs.append((wrapFunc(self.ui.write, self.ui.syn, ecodes.EV_KEY, key, 1), f"down {cmd}"))
                        elif match.group("up"):
                            if keyboard:
                                funcs.append((wrapFunc(keyboard.release, cmd), f"up {cmd}"))
                            else:
                                if key := ecodes.ecodes.get(f'KEY_{cmd}', None):
                                    funcs.append((wrapFunc(self.ui.write, self.ui.syn, ecodes.EV_KEY, key, 0), f"down {cmd}"))
                        else:
                            funcs.append(self.sendStrFactory(cmd))
        elif type(config) is dict:
            if "function" in config.keys():
                try:
                    funcs.append((wrapFunc(globals()[config["function"]], **config.get("args", {})), f"""{config["function"]}({config.get("args", {})})"""))
                except KeyError as e:
                    print("Error could not find function:", e, "\n\n\n The globals are :", globals())
        elif isinstance(config, Iterable):
            for conf in config:
                funcs += self.getFuncsList(conf, prefixToFunc)
        elif type(config) is int:
            self.hideGUIBeforeRun = True
            funcs.append(self.sendStrFactory(config))

        return funcs


    def sendStrFactory(self, sendStr):
        if keyboard:
            try:
                keyboard.parse_hotkey(sendStr)
                return (lambda : keyboard.send(sendStr), f"send {sendStr}")
            except ValueError:
                return (lambda : keyboard.write(sendStr), f"write {sendStr}")
        else:
            def f():

                print(sendStr)
                if(type(sendStr) is int):
                    key = sendStr
                else:
                    key = ecodes.ecodes.get(f'KEY_{sendStr.upper()}', None)

                if key:
                    self.ui.write(ecodes.EV_KEY, key, 1)  # KEY_A down

                    self.ui.write(ecodes.EV_KEY, key, 0)  # KEY_A up
                    self.ui.syn()


            return (f, f"write {sendStr}")

    def press(self):
        for f in self.runFuncs:
            print(f[1], f[0])
            f[0]()
            sleep(.005)

    def release(self):
        for f in self.releaseFuncs:
            print(f[1], f[0])
            f[0]()
            sleep(.005)

    def getDescription(self):
        return self.description

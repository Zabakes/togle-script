from platform import release, system
from threading import Event, Lock, Thread
import os
from time import sleep, time
import keyboard
import re
from customFuncs import *

appToKeys = {}
regexToAppName = {}
keyReleaseEvents = {}
toggle = False

class command():
    
    fmtString = re.compile(r"{(?P<cmd>.*?)((?P<down> down)|(?P<up> up))?}|(?P<str>[^\{]+)")
    
    def __init__(self, press, prefixToFunc={}, release="") -> None:

        
        self.runFuncs = self.getFuncsListFromString(press, prefixToFunc)
        self.releaseFuncs = self.getFuncsListFromString(release, prefixToFunc)

    def getFuncsListFromString(self, s, prefixToFunc={}):
        funcs = []
        for match in re.finditer(self.fmtString, s):
            if sendStr := match.group("str"):
                funcs.append(self.sendStrFactory(sendStr))
            elif cmd := match.group("cmd"):
                cmd[0]
                if cmd[0] in prefixToFunc.keys():
                    print(f"{prefixToFunc[cmd[0]].__name__}({cmd[1:]})")
                    funcs.append((lambda : prefixToFunc[cmd[0]](cmd[1:]),  f"{prefixToFunc[cmd[0]].__name__}({cmd[1:]})"))
                else:
                    if match.group("down"):

                        def down():
                            keyboard.press(cmd)

                        funcs.append((down, f"down {cmd}"))
                    elif match.group("up"):
                        
                        def up():
                            keyboard.release(cmd)

                        funcs.append((up, f"up {cmd}"))

                    else:
                        funcs.append(self.sendStrFactory(cmd))
        return funcs

    @staticmethod
    def sendStrFactory(sendStr):
        try:
            keyboard.parse_hotkey(sendStr)
            return (lambda : keyboard.send(sendStr), f"send {sendStr}")
        except ValueError:
            return (lambda : keyboard.write(sendStr), f"write {sendStr}")

    def press(self):
        for f in self.runFuncs:
            f[0]()
            sleep(.1)

    def release(self):
        for f in self.releaseFuncs:
            f[0]()
            sleep(.1)

if system() == 'Windows':
    import win32gui

    def getWindowName() -> str:
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())
elif system() == 'Linux':
    def getWindowName() -> str:
        print("TODO IMPLEMENT LINUX")

def updateConfig():

    global regexToAppName, appToKeys, toggleKey, toRemap

    toRemap = []
    prefixToFunc = {}
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Hotkeys", "config.ini"), "r") as file:
        lines = [l.strip() for l in file.readlines()]
        appName = lines[0]

        toggleKey = lines[6].lower()
        cmds = lines[8]

        toRemap = [l.strip("\" ").lower() for l in lines[2].split(",")]

        for val in cmds.split(","):
            prefix, cmd = val.split(":")
            prefixToFunc[prefix] = globals()[cmd]

    for fileName in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Hotkeys")):
        if fileName.endswith(".ini") and fileName != "config.ini":
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Hotkeys", fileName), "r") as file:
                lines = [l.strip() for l in file.readlines()]

                appName = lines[0].strip("")
                
                release = {}

                if len(lines) > 4 and lines[4]:
                    for key in lines[4].split(","):
                        key, toSend = key.split(":")
                        release[toRemap[int(key)-1]] = toSend

                keys = {key : command(target.strip("\" "), prefixToFunc, release.get(key, "")) for key, target in zip(toRemap, lines[2].split(","))}

                if len(lines) > 6 and lines[6]:
                    regexToAppName[re.compile(lines[6])] = appName

            appToKeys[appName] = keys
    
    keyboard.unhook_all()

    keyboard.hook_key(toggleKey, hook, suppress=True)
    for key in toRemap:
        keyboard.hook_key(key, hook, suppress=True)

def MsgBox(s):
    print(s)

toggleThread = Lock()
def toggleFunc(key):
    global hotKeyUsed, toggleThread, toggle
    if not toggleThread.acquire(blocking=False):
        return

    keyReleaseEvents[key] = Event()

    hotKeyUsed = False
    
    waitStart = time()
    if keyReleaseEvents[key].wait(timeout=.045):
        keyboard.send(".")
        toggleThread.release()
        return
    else:
        toggle = True

    keyReleaseEvents[key].wait()

    toggle = False
    toggleThread.release()

    if not hotKeyUsed:
        run("C:\\Users\\zeusa\\OneDrive\\Documents\\Code\\AHK Scripts\\togle-script\\tilingManagerTest.exe")


winTitleSplitter =  re.compile(u'[\u2014\-\*]')

def keyPress(key):
    global regexToAppName, hotKeyUsed, toggle, keyReleaseEvents

    if key in keyReleaseEvents:
        return

    keyReleaseEvents[key] = Event()

    if toggle:
        winName = getWindowName()
        hotKeyUsed = True

        appName = re.split(winTitleSplitter, winName).pop().strip()

        if not (toSend := appToKeys.get(appName, None)):
            for ptrn, title in regexToAppName.items():
                if re.search(ptrn, winName):
                    toSend = appToKeys.get(title, None)

        if toSend is None or key not in toSend:
            toSend = appToKeys["Default"]

    else:
        toSend = appToKeys["Untoggled"]

    processCmd(toSend.get(key, None), keyReleaseEvents.get(key, None))

    keyReleaseEvents.pop(key)

def triggerKeyReleaseEvent(key):

    if event := keyReleaseEvents.get(key, None):
        event.set()

def processCmd(c : command, event=None):
    if c is not None:
        c.press()
        if event is not None:
            event.wait()
            c.release()


def on_press(key):
    if key == toggleKey:
        t = Thread(target=toggleFunc, args=[key])
    elif key in toRemap:
        t = Thread(target=keyPress, args=[key])
    else:
        return

    t.start()

def on_release(key):
    if key == toggleKey or key in toRemap:
        t = Thread(target=triggerKeyReleaseEvent, args=[key])
        t.start()

def hook(event):
    
    key = event.name

    if keyboard.is_pressed(key):
        on_press(key)
    else:
        on_release(key)
    
    return False

updateConfig()

import pystray

from PIL import Image

# In order for the icon to be displayed, you must provide an icon
menu = pystray.Menu(pystray.MenuItem("Quit", lambda : icon.stop()), pystray.MenuItem("Refresh hotkeys", lambda : updateConfig()))

icon = pystray.Icon(
    'ToggleScript',
    icon=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "toggleScript.ico")),
    menu=menu)

# To finally show you icon, call run
icon.run()

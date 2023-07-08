from platform import release, system
from threading import Event, Lock, Thread
import os
from time import sleep, time
import keyboard
import re
from customFuncs import *
import json
import tkinter as tk
from typing import Callable, Union, List, Dict
from PIL import Image, ImageTk

appToKeys = {}
regexToAppName = {}
keyReleaseEvents = {}
titleMatchToConfigFile = {}
toggle = False

class command():
    
    fmtString = re.compile(r"(?<!\\){(?P<cmd>.*?)((?P<down> down)|(?P<up> up))?(?<!\\)}|(?P<str>[^\{]+)")
    
    def __init__(self, press, prefixToFunc={}, release="", description = None, imgPath = None) -> None:
        self.description = description
        self.imgPath = imgPath
        self.pressS = press
        self.releaseS = release
        self.waitForRel =  False
        self.hideGUIBeforeRun = False
        self.runFuncs = self.getFuncsListFromString(press, prefixToFunc)
        self.releaseFuncs = self.getFuncsListFromString(release, prefixToFunc)


        if self.description is None:
            self.description = self.__str__()

    def __str__(self) -> str:
        return f"{{\"press\" : \"{self.pressS}\", \"rel\" : \"{self.releaseS}\"}}"

    def __repr__(self) -> str:
        return self.__str__()

    def getFuncsListFromString(self, s, prefixToFunc={}):
        funcs = []
        for match in re.finditer(self.fmtString, s):
            if sendStr := match.group("str"):
                self.hideGUIBeforeRun = True
                funcs.append(self.sendStrFactory(sendStr))
            elif cmd := match.group("cmd"):
                cmd = re.sub(r"\\+({|})", r"\g<1>", cmd)
                if cmd[0] in prefixToFunc.keys():
                    #print(f"{prefixToFunc[cmd[0]].__name__}({cmd[1:]})")
                    if prefixToFunc[cmd[0]] != setLayer:
                        self.hideGUIBeforeRun = True

                    funcs.append((lambda : prefixToFunc[cmd[0]](cmd[1:]),  f"{prefixToFunc[cmd[0]].__name__}({cmd[1:]})"))
                else:
                    self.hideGUIBeforeRun = True
                    if match.group("down"):
                        funcs.append((wrapFunc(keyboard.press, cmd), f"down {cmd}"))

                    elif match.group("up"):
                        funcs.append((wrapFunc(keyboard.release, cmd), f"up {cmd}"))

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
            print(f[1], f[0])
            f[0]()
            sleep(.001)

    def release(self):
        for f in self.releaseFuncs:
            print(f[1])
            f[0]()
            sleep(.001)

    def getDescription(self):
        return self.description

def wrapFunc(f, *args, **kwargs):
    def func():
        print(locals())
        f(*args, **kwargs)
    return func

windowTitle = ""
if system() == 'Windows':
    import win32gui
    def getWindowName() -> str:
        #print(win32gui.GetWindowText(win32gui.GetForegroundWindow()))
        global windowTitle
        if showGUI.isSet():
            return windowTitle
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())
elif system() == 'Linux':
    def getWindowName() -> str:
        print("TODO IMPLEMENT LINUX")

def parseKeyConfig(conf : Union[Dict[str, str], List[Dict[str, str]]]) -> Union[command, List[command], None]:
    if type(conf) is dict:
        if "press" in conf or "rel" in conf:
            return command(conf.get("press", ""), prefixToFunc, conf.get("rel", ""), imgPath=conf.get("icon path", None), description = conf.get("description", None))
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

prefixToFunc = {}
def updateConfig():

    global regexToAppName, appToKeys, toggleKey, toRemap, prefixToFunc, doRemapping, layout

    toRemap = []

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hotkeysJson", "config.json"), "r") as file:
        conf = json.load(file)

        doRemapping = conf.get("layout", True)
        layout = conf.get("layout", None)

        toggleKey = conf["toggleKey"].lower()

        toRemap = [key["remap"].lower() for key in conf["keys"]]
        appToKeys["Untoggled"] = [key["baseLayer"] for key in conf["keys"]]

        for val in conf["actions"]:
            prefix = val["prefix"]
            cmd = val["function"]
            prefixToFunc[prefix] = globals()[cmd]

    for fileName in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hotkeysJson")):
        if fileName.endswith(".json") and fileName != "config.json":
            fullFileName = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hotkeysJson", fileName)
            with open(fullFileName, "r") as file:
                conf = json.load(file)

                keys = {}
                appName = conf["appName"]
                titleMatchToConfigFile[appName] = fullFileName

                for key, target in enumerate(conf["hks"]):
                    keys[toRemap[key]] = parseKeyConfig(target)

                appToKeys[appName] = keys

                if "regex" in conf:
                    if "priority" in conf:
                        priority = conf["priority"]
                    else:
                        priority = 0

                    regex = conf["regex"]
                    regexToAppName[re.compile(regex)] = (appName, int(priority))
    keyboard.unhook_all()

    keyboard.hook_key(toggleKey, hook, suppress=True)
    keyReleaseEvents[toggleKey] = Event()

    for key in toRemap:
        keyboard.hook_key(key, hook, suppress=True)

def MsgBox(s):
    print(s)

layer = 0
def setLayer(s):
    global layer, redrawGui, stickyLayer
    if isEditing:
        return

    kwargs = json.loads(s)
    print(kwargs)
    if kwargs["type"] == "inc":
        layer += 1
        if "max" in kwargs and layer > kwargs["max"]:
            layer = kwargs["max"]
    elif kwargs["type"] == "dec":
        layer -= 1
        layer = max(layer, 0) 
    elif kwargs["type"] == "set":
        layer = kwargs["val"]

    redrawGui = True

from tkinterweb import HtmlFrame #import the HtmlFrame widget
import tkinter as tk
import pyautogui
from tktooltip import ToolTip as ToolTip_base

kill = False
isEditing = False

class ToolTip(ToolTip_base):

    liveToolTips = set()
    
    def __init__(self, widget, msg = None, delay = 0, follow = True, refresh = 1, x_offset=+10, y_offset=+10, parent_kwargs = {"bg": "black", "padx": 1, "pady": 1}, **message_kwargs):
        super().__init__(widget, msg, delay, follow, refresh, x_offset, y_offset, parent_kwargs, **message_kwargs)
        self.wm_attributes('-topmost', 1)

    def _show(self) -> None:
        self.liveToolTips.add(self)
        return super()._show()

    def on_leave(self, discard=True):
        if discard:
            self.liveToolTips.discard(self)
        return super().on_leave()

def hideGUI():
    if not isEditing:
        showGUI.clear()

class keyBox(tk.Frame):
    allBeingEdited = set()
    bgimg = None
    
    def __init__(self, 
                 master = None,
                 index = None,
                 *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        
        self.htmlFrame = HtmlFrame(self, messages_enabled = False) #create HTML browser
        self.img = None
        self.textBox = tk.Text(self, height=WIDGET_HEIGHT//4, width=WIDGET_WIDTH//3, wrap=tk.WORD)
        
        self.index = index
        if self.index is not None:
            print(self.index)
            self.keyIndexLabel = tk.Label(self, text=self.index+1, justify=tk.CENTER)
            self.keyIndexLabel.grid(row=0, column=0, sticky="nsew")
            self.rowconfigure(0, minsize=WIDGET_HEIGHT//30, weight=1)
        
        
        self.imgFrame = tk.Label(self)
        self.textBox.grid(row=1, column=0, sticky="nsew")
        self.htmlFrame.grid(row=1, column=0, sticky="nsew")
        self.imgFrame.grid(row=1, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1) 
        self.rowconfigure(1, weight=1)

        self.textBox.bind("<Control-Return>", self.saveConfig)
        self.textBox.bind("<Control-s>", self.saveConfig)
        self.textBox.bind("<Escape>", self.discardConfig)

        self.toolTip = ToolTip(self.imgFrame)

        self.key = self.titleMatch = self.newWindow = None

    def showText(self):
        self.textBox.tkraise()

    def showDescription(self):
        if self.img:
            self.imgFrame.tkraise()
        else:
            self.htmlFrame.tkraise()

    def updateConfigFile(self, event):
        global isEditing
        isEditing = True

        self.allBeingEdited.add(self)

        fname = titleMatchToConfigFile[self.titleMatch]
        with open(fname, "r") as f:
            self.conf = json.load(f)
            rawConfData = self.conf["hks"][self.index]
        
        self.textBox.config(state=tk.NORMAL)
        self.textBox.delete("1.0",tk.END)
        self.textBox.insert("1.0",json.dumps(rawConfData, indent=4))
        self.showText()
        #print(json.dumps(rawConfData))

    def makeNewFile(self, pfix, fileNameEntry, winTitle, input):
        fileName = fileNameEntry.get()
        self.titleMatch = winTitle

        self.conf = {
            "appName" : winTitle,
            "hks" : [dict()]*len(toRemap)
        }
        fname = os.path.join(pfix, fileName)
        with open(fname, "w") as f:
                f.write(json.dumps(self.conf, indent=4))

        appToKeys[self.titleMatch] = {key:None for key in toRemap}

        titleMatchToConfigFile[self.titleMatch] = fname
        self.saveConfig(None, fname, input)

    def saveConfig(self, e, fname = None, input = None):
        global isEditing

        if fname is None:
            fname = titleMatchToConfigFile[self.titleMatch]

            pfix, fnameTail = os.path.split(fname)
            if fnameTail == "Default.json":
                self.newWindow = tk.Toplevel(self)
                eFileName = tk.Entry(self.newWindow)
                WinTitle = re.split(winTitleSplitter, getWindowName()).pop().strip()
                eFileName.insert(0, f"""{WinTitle.replace(" ", "_")}.json""")
                bYes = tk.Button(self.newWindow, text="Make New File", command=lambda : self.makeNewFile(pfix, eFileName, WinTitle, input))
                bNo = tk.Button(self.newWindow, text="Modify default", command=lambda : self.saveConfig(e, fname))
                
                eFileName.grid(row=0, column=0, columnspan=2, sticky="ew")
                bYes.grid(row=2, column=0, sticky="ew")
                bNo.grid(row=2, column=1, sticky="ew")
                return
        
        
        if input is None:
            input = self.textBox.get("1.0",tk.END)

        try:
            self.conf["hks"][self.index] = json.loads(input)
            target = json.loads(input)

            appToKeys[self.titleMatch][self.key] = parseKeyConfig(target)

            with open(fname, "w") as f:
                f.write(json.dumps(self.conf, indent=4))

        except json.JSONDecodeError:
            pass

        if self.newWindow:
            self.newWindow.destroy()
            self.newWindow = None
        
        self.allBeingEdited.discard(self)
        
        if self.allBeingEdited:
            other = self.allBeingEdited.pop()
            with open(fname, "r") as f:
                other.conf = json.load(f)
            other.saveConfig(e)
        
        isEditing = False
        hideGUI()

    def discardConfig(self, e):
        global isEditing
        self.allBeingEdited = set()
        isEditing = False
        hideGUI()

    def updateKeyBox(self, cmd) -> None:
        if cmd.imgPath:
            try:
                i = Image.open(cmd.imgPath)
                self.img = ImageTk.PhotoImage(i)
                self.imgFrame.configure(image=self.img)
                self.imgFrame.tkraise()
                self.toolTip.msg = cmd.getDescription()
            except FileNotFoundError:
                self.img = None
                pass
        else:
            self.htmlFrame.tkraise()

        self.htmlFrame.load_html(f"""<p>{cmd.getDescription()}</p>""")


WIDGET_WIDTH = 400
WIDGET_HEIGHT = 750

def findWidgetAndUpdateConf(event):
    global isEditing
    isEditing = True
    w = event.widget
    
    while type(w) != keyBox:
        w = w.master
        if type(w) == tk.Tk:
            return
    
    w.updateConfigFile(event)

def makeWidget():
    global isEditing, redrawGui
    root = tk.Tk(className="ZMAC_OVERLAY", baseName="ZMAC_POP_UP")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    WIDGET_HEIGHT = int(screen_height//2.75)
    WIDGET_WIDTH = int(WIDGET_HEIGHT/1.75)
    root.call('wm', 'attributes', '.', '-topmost', '1')
    root.overrideredirect(True)
    abs_coord_x, abs_coord_y = pyautogui.position()
    root.geometry(f"{WIDGET_WIDTH}x{WIDGET_HEIGHT}+{abs_coord_x}+{abs_coord_y}")
    
    buttonElements = []

    for i, button in enumerate(toRemap):
        tk.Grid.rowconfigure(root,i//3,weight=1)
        tk.Grid.columnconfigure(root,i%3,weight=1)
        keyFrame = keyBox(master=root, index=i) #create HTML browser


        keyFrame.grid(row = i//3, column = i%3, sticky="NSEW", padx=(5, 5), pady=(5, 5)) #attach the HtmlFrame widget to the parent window
        buttonElements.append(keyFrame)

    root.bind("<Button-3>", findWidgetAndUpdateConf)
        
    while True:
        abs_coord_x, abs_coord_y = pyautogui.position()

        if(WIDGET_WIDTH+abs_coord_x > screen_width):
            abs_coord_x = screen_width-WIDGET_WIDTH
        
        if(WIDGET_HEIGHT+abs_coord_y > screen_height):
            abs_coord_y = screen_height-WIDGET_HEIGHT

        root.geometry(f"{WIDGET_WIDTH}x{WIDGET_HEIGHT}+{abs_coord_x}+{abs_coord_y}")
        
        redrawGui = True
        titleMatch = getTitleMatch()

        while showGUI.isSet():
            if redrawGui:
                for i, (key, element) in enumerate(zip(toRemap, buttonElements)):
                    cmd = getCmd(key, titleMatch)
                    element.key = key
                    element.titleMatch = titleMatch
                    element.updateKeyBox(cmd)
                    redrawGui = False
            #root.lift()
            for tt in ToolTip.liveToolTips:
                #print("raise tt", ToolTip.liveToolTips)
                tt.lift()
            root.update_idletasks()
            root.update()
            sleep(.05)

        for tt in ToolTip.liveToolTips:
            tt.on_leave(discard=False)
        ToolTip.liveToolTips = set()

        root.withdraw()

        for element in buttonElements:
            element.showDescription()

        showGUI.wait()
        
        if kill:
            root.destroy()
            return
        isEditing = False

        sleep(.125)
        if showGUI.isSet():
            root.deiconify()


toggleThread = Lock()

showGUI = Event()
def toggleFunc(key):
    global hotKeyUsed, toggleThread, toggle, showGUI, windowTitle, layer
    if not toggleThread.acquire(blocking=False):
        return
    
    windowTitle = getWindowName()
    showGUI.set()
    keyReleaseEvents[key].clear()

    hotKeyUsed = False
    toggle = True

    if keyReleaseEvents[key].wait(timeout=.15):
        if not hotKeyUsed:
            toggle = False
            keyboard.send(".")
            toggleThread.release()
            hideGUI()
            return

    keyReleaseEvents[key].wait()

    hideGUI()

    toggle = False
    layer = 0
    
    toggleThread.release()

    if (not hotKeyUsed) and (not isEditing):
        run("C:\\Users\\zeusa\\OneDrive\\Documents\\Code\\AHK Scripts\\togle-script\\tilingManagerTest.exe")

winTitleSplitter =  re.compile(u'[\u2014\-\*]')
def getTitleMatch():
    winName = getWindowName()

    print(winName)
    titleMatch = None
    appName = re.split(winTitleSplitter, winName).pop().strip()
    print(appName)
    if not appName in appToKeys:
        p = None
        for ptrn, (title, pr) in regexToAppName.items():
            if re.search(ptrn, winName) and (p is None or p < pr):
                #print("This", winName, ptrn, title, pr, p)
                titleMatch = title
                p = pr
    else:
        titleMatch = appName

    if titleMatch is None:
            titleMatch = "Default"

    return titleMatch

layerApp = ""
layer = 0
def getLayer(titleMatch = None):
    if titleMatch is None:
        titleMatch = getTitleMatch()

    global layer, layerApp
    
    if titleMatch != layerApp:
        layer = 0
        layerApp = titleMatch

    return layer

def getCmd(key, titleMatch = None):

    if titleMatch is None:
        titleMatch = getTitleMatch()
    
    toSend = appToKeys.get(titleMatch, None)
    if not(cmd := toSend.get(key, None)):
        cmd = appToKeys["Default"].get(key)

    if type(cmd) is list:
        l = min(len(cmd)-1, getLayer())
        cmd = cmd[l]
        if cmd is None:
            cmd = appToKeys["Default"].get(key)

    return cmd


def keyPress(key):
    global regexToAppName, hotKeyUsed, toggle, keyReleaseEvents, isEditing, layer, redrawGui

    if key in keyReleaseEvents:
        return

    resetLayer = layer != 0

    keyRelEvent = Event()
    keyReleaseEvents[key] = keyRelEvent

    if toggle and not isEditing:

        hotKeyUsed = True
        c = getCmd(key)

    else:
        c = getCmd(key, "Untoggled")

    if c.hideGUIBeforeRun:
        hideGUI()

    processCmd(c, keyRelEvent)

    keyReleaseEvents.pop(key)
    
    if resetLayer:
        layer = 0
        redrawGui = True

    if toggleThread.locked():
        showGUI.set()

def triggerKeyReleaseEvent(key):
    if event := keyReleaseEvents.get(key, None):
        event.set()

def processCmd(c : command, event=None):
    if c is not None:
        c.press()
        if c.releaseFuncs or c.waitForRel:
            event.wait()
            c.release()


def on_press(key):
    global doRemapping
    if not doRemapping:
        return
    elif key == toggleKey:
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
t = Thread(target=makeWidget)
t.start()

import pystray

from PIL import Image

kill = False
def quit():
    global kill
    kill = True
    showGUI.set()
    icon.stop()

# In order for the icon to be displayed, you must provide an icon
menu = pystray.Menu(pystray.MenuItem("Quit", quit), pystray.MenuItem("Refresh hotkeys", lambda : updateConfig()))

icon = pystray.Icon(
    'ToggleScript',
    icon=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "toggleScript.ico")),
    menu=menu)

# To finally show you icon, call run
icon.run()
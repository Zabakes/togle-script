from platform import release, system
from threading import Event, Lock, Thread
import os
from time import sleep, time
import keyboard
import re
from customFuncs import *
import json
import tkinter as tk

appToKeys = {}
regexToAppName = {}
keyReleaseEvents = {}
titleMatchToConfigFile = {}
toggle = False

class command():
    
    fmtString = re.compile(r"(?<!\\){(?P<cmd>.*?)((?P<down> down)|(?P<up> up))?(?<!\\)}|(?P<str>[^\{]+)")
    
    def __init__(self, press, prefixToFunc={}, release="", description = None) -> None:
        self.description = description
        self.pressS = press
        self.releaseS = release
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
                funcs.append(self.sendStrFactory(sendStr))
            elif cmd := match.group("cmd"):
                cmd = re.sub(r"\\+({|})", r"\g<1>", cmd)
                if cmd[0] in prefixToFunc.keys():
                    #print(f"{prefixToFunc[cmd[0]].__name__}({cmd[1:]})")
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
            #print(f[1])
            f[0]()
            sleep(.1)

    def release(self):
        for f in self.releaseFuncs:
            #print(f[1])
            f[0]()
            sleep(.1)

    def getDescription(self):
        return self.description

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

prefixToFunc = {}
def updateConfig():

    global regexToAppName, appToKeys, toggleKey, toRemap, prefixToFunc

    toRemap = []

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Hotkeys", "config.ini"), "r") as file:
        lines = [l.strip() for l in file.readlines()]
        appName = lines[0]

        toggleKey = lines[6].lower()
        cmds = lines[8]

        toRemap = [l.strip("\" ").lower() for l in lines[2].split(",")]

        for val in cmds.split(","):
            prefix, cmd = val.split(":")
            prefixToFunc[prefix] = globals()[cmd]

    for fileName in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hotkeysJson")):
        if fileName.endswith(".json") and fileName != "config.ini":
            fullFileName = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hotkeysJson", fileName)
            with open(fullFileName, "r") as file:
                conf = json.load(file)

                keys = {}
                appName = conf["appName"]
                titleMatchToConfigFile[appName] = fullFileName

                for key, target in enumerate(conf["hks"]):
                    if "press" in target or "rel" in target:
                        keys[toRemap[key]] = command(target.get("press", ""), prefixToFunc, target.get("rel", ""), description = target.get("description", None))
                    else:
                        keys[toRemap[key]] = None
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

from tkinterweb import HtmlFrame #import the HtmlFrame widget
import tkinter as tk
import pyautogui
kill = False
isEditing = False

def hideGUI():
    if not isEditing:
        showGUI.clear()

class htmlFrameWithTextBox(tk.Frame):
    
    allBeingEdited = set()
    
    def __init__(self, 
                 master = None, 
                 *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        self.htmlFrame = HtmlFrame(self, messages_enabled = False) #create HTML browser
        self.textBox = tk.Text(self, height=WIDGET_HEIGHT//4, width=WIDGET_WIDTH//3, wrap=tk.WORD)
        
        self.textBox.grid(row=0, column=0, sticky="nsew")
        self.htmlFrame.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1) 
        self.rowconfigure(0, weight=1)

        self.textBox.bind("<Control-Return>", self.saveConfig)
        self.textBox.bind("<Control-s>", self.saveConfig)
        self.textBox.bind("<Escape>", self.discardConfig)
        
        self.key = self.titleMatch = self.keyIndex = self.newWindow = None
        
    def showText(self):
        self.textBox.tkraise()

    def showHTML(self):
        self.htmlFrame.tkraise()
        
    def updateConfigFile(self, event):
        global isEditing
        isEditing = True

        self.allBeingEdited.add(self)

        fname = titleMatchToConfigFile[self.titleMatch]
        with open(fname, "r") as f:
            self.conf = json.load(f)
            rawConfData = self.conf["hks"][self.keyIndex]
        
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
            self.conf["hks"][self.keyIndex] = json.loads(input)
            target = json.loads(input)
            appToKeys[self.titleMatch][self.key] = command(target["press"], prefixToFunc, target.get("rel", ""), description = target.get("description", None))
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

WIDGET_WIDTH = 400
WIDGET_HEIGHT = 750

def findWidgetAndUpdateConf(event):
    global isEditing
    isEditing = True
    w = event.widget
    
    while type(w) != htmlFrameWithTextBox:
        w = w.master
        if type(w) == tk.Tk:
            return
    
    w.updateConfigFile(event)

def makeWidget():
    global isEditing
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    WIDGET_HEIGHT = int(screen_height//2.5)
    WIDGET_WIDTH = int(WIDGET_HEIGHT/1.5)
        
    root.call('wm', 'attributes', '.', '-topmost', '1')
    root.overrideredirect(True)
    abs_coord_x, abs_coord_y = pyautogui.position()
    root.config(bg="black")
    root.geometry(f"{WIDGET_WIDTH}x{WIDGET_HEIGHT}+{abs_coord_x}+{abs_coord_y}")
    
    buttonElements = []
    for i, button in enumerate(toRemap):
        tk.Grid.rowconfigure(root,i//3,weight=1)
        tk.Grid.columnconfigure(root,i%3,weight=1)
        myhtmlframe = htmlFrameWithTextBox(root) #create HTML browser
        myhtmlframe.keyIndex = i
        myhtmlframe.grid(row = i//3, column = i%3, sticky="NSEW", padx=(5, 5), pady=(5, 5)) #attach the HtmlFrame widget to the parent window
        buttonElements.append(myhtmlframe)
    cont = 0
    root.bind("<Button-3>", findWidgetAndUpdateConf)

    while True:
        abs_coord_x, abs_coord_y = pyautogui.position()

        if(WIDGET_WIDTH+abs_coord_x > screen_width):
            abs_coord_x = screen_width-WIDGET_WIDTH
        
        if(WIDGET_HEIGHT+abs_coord_y > screen_height):
            abs_coord_y = screen_height-WIDGET_HEIGHT

        root.geometry(f"{WIDGET_WIDTH}x{WIDGET_HEIGHT}+{abs_coord_x}+{abs_coord_y}")
        
        titleMatch = getToSend()
        toSend = appToKeys.get(titleMatch, None)
        for i, (key, element) in enumerate(zip(toRemap, buttonElements)):
            element.key = key
            element.titleMatch = titleMatch
            if not toSend.get(key, None):
                element.htmlFrame.load_html(f"""<h3>{i+1}</h3><br><p>{appToKeys["Default"].get(key).getDescription()}</p>""")
            else:
                element.htmlFrame.load_html(f"""<h3>{i+1}</h3><br><p>{toSend.get(key).getDescription()}</p>""")

        while showGUI.isSet():
            root.lift()
            root.update_idletasks()
            root.update()


        root.withdraw()
        showGUI.wait()
        if kill:
            root.destroy()
            return
        root.deiconify()
        for element in buttonElements:
            element.showHTML()
        isEditing = False
        cont += 1
        
    


toggleThread = Lock()

showGUI = Event()
def toggleFunc(key):
    global hotKeyUsed, toggleThread, toggle, showGUI, windowTitle
    if not toggleThread.acquire(blocking=False):
        return
    
    windowTitle = getWindowName()
    showGUI.set()
    keyReleaseEvents[key].clear()

    hotKeyUsed = False
    toggle = True

    waitStart = time()
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
    
    toggleThread.release()

    if (not hotKeyUsed) and (not isEditing):
        run("C:\\Users\\zeusa\\OneDrive\\Documents\\Code\\AHK Scripts\\togle-script\\tilingManagerTest.exe")


def getToSend():
    winName = getWindowName()
    #print(winName)
    toSend = None
    appName = re.split(winTitleSplitter, winName).pop().strip()
    if not appName in appToKeys:
        p = None
        for ptrn, (title, pr) in regexToAppName.items():
            if re.search(ptrn, winName) and (p is None or p < pr):
                #print("This", winName, ptrn, title, pr, p)
                toSend = title
                p = pr
    else:
        toSend = appName

    if toSend is None:
            toSend = "Default"

    return toSend

winTitleSplitter =  re.compile(u'[\u2014\-\*]')

def keyPress(key):
    global regexToAppName, hotKeyUsed, toggle, keyReleaseEvents, isEditing

    if key in keyReleaseEvents:
        return

    hideGUI()

    keyReleaseEvents[key] = Event()

    if toggle and not isEditing:

        hotKeyUsed = True
        toSend = appToKeys.get(getToSend(), None)

        if key not in toSend:
            toSend = appToKeys["Default"]

    else:
        toSend = appToKeys["Untoggled"]


    processCmd(toSend.get(key, None), keyReleaseEvents.get(key, None))

    keyReleaseEvents.pop(key)
    if toggleThread.locked():
        showGUI.set()

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

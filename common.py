from platform import system
from threading import Event, Lock, Thread
import re

appToKeys = {}
regexToAppName = {}
keyReleaseEvents = {}
titleMatchToConfigFile = {}
prefixToFunc = {}
toggle = False
layer = 0
toggleThread = Lock()
showGUI = Event()
winTitleSplitter =  re.compile(u'[\u2014\-\*]')
layerApp = ""
kill = False
isEditing = False
toggleKey = None
toRemap = []
WIDGET_HEIGHT = 0
WIDGET_WIDTH = 0
doRemapping = True
redrawGui = False

windowTitle = ""
if system() == 'Windows':
    import win32gui
    def getWindowName() -> str:
        if showGUI.isSet():
            return windowTitle
        return win32gui.GetWindowText(win32gui.GetForegroundWindow())
elif system() == 'Linux':
    def getWindowName() -> str:
        print("TODO IMPLEMENT LINUX")

def getTitleMatch():
    winName = getWindowName()

    titleMatch = None
    appName = re.split(winTitleSplitter, winName).pop().strip()
    
    if not appName in appToKeys:
        p = None
        for ptrn, (title, pr) in regexToAppName.items():
            if re.search(ptrn, winName) and (p is None or p < pr):
                print("This", winName, ptrn, title, pr, p)
                titleMatch = title
                p = pr
    else:
        titleMatch = appName

    if titleMatch is None:
            titleMatch = "Default"

    return titleMatch


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

def getLayer(titleMatch = None):
    global layer, layerApp
    if titleMatch is None:
        titleMatch = getTitleMatch()

    if titleMatch != layerApp:
        layer = 0
        layerApp = titleMatch

    return layer
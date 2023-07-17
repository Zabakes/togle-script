from platform import system
from threading import Event, Lock, Thread
import json
import re

toggleActions = {}
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
disableGUI = False
updateBGInterval = 0
layout = None

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
    
    if not appName in titleMatchToConfigFile:
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

def getLayer(titleMatch = None):
    global layer, layerApp
    if titleMatch is None:
        titleMatch = getTitleMatch()

    if titleMatch != layerApp:
        layer = 0
        layerApp = titleMatch

    return layer
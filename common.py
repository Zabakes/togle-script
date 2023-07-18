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
drawGUI = True

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

def getAppName():
    winName = getWindowName()
    win32gui.GetDesktopWindow
    return re.split(winTitleSplitter, winName).pop().strip()

def getTitleMatch():
    winName = getWindowName()

    titleMatch = None
    appName = re.split(winTitleSplitter, winName).pop().strip()
    
    if not appName in titleMatchToConfigFile:
        maxPriority = None
        for ptrn, (title, priority) in regexToAppName.items():
            if re.search(ptrn, winName) and (maxPriority is None or maxPriority < priority):
                titleMatch = title
                maxPriority = priority
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
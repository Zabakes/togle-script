import common
from GUI.guiVisibility import hideGUI, showGUI
from customFuncs import *
import keyboard
from threading import Event, Thread
from time import sleep
from Layers.runTimeConfig import getCmd


def toggleFunc(key):
    global hotKeyUsed
    
    if not common.toggleThread.acquire(blocking=False):
        return
    
    common.windowTitle = common.getWindowName()
    showGUI()
    common.keyReleaseEvents[key].clear()

    hotKeyUsed = False
    common.toggle = True

    if common.keyReleaseEvents[key].wait(timeout=.15):
        if not hotKeyUsed:
            common.toggle = False
            processCmd(common.toggleActions.get("tap", None))
            common.toggleThread.release()
            hideGUI()
            return

    common.keyReleaseEvents[key].wait()

    hideGUI()

    common.toggle = False
    common.layer = 0
    
    common.toggleThread.release()

    if (not hotKeyUsed) and (not common.isEditing):
        processCmd(common.toggleActions.get("longPress", None))

    return

def keyPress(key):
    global hotKeyUsed

    print(key)
    if key in common.keyReleaseEvents:
        return

    resetLayer = common.layer != 0

    keyRelEvent = Event()
    common.keyReleaseEvents[key] = keyRelEvent

    if common.toggle and not common.isEditing:
        hotKeyUsed = True
        c = getCmd(key)

    else:
        c = common.untoggled.get(key, None)
        print(common.untoggled)

    if c is not None and c.hideGUIBeforeRun:
        hideGUI()

    processCmd(c, keyRelEvent)

    common.keyReleaseEvents.pop(key)
    
    if resetLayer:
        common.layer = 0
        common.redrawGui = True

    if common.toggleThread.locked():
        sleep(.01)
        showGUI()

def triggerKeyReleaseEvent(key):
    if event := common.keyReleaseEvents.get(key, None):
        event.set()

def processCmd(c, event=None):
    if c is not None:
        c.press()
        if c.releaseFuncs or c.waitForRel:
            event.wait()
            c.release()

def on_press(key):

    if key == common.toggleKey:
        t = Thread(target=toggleFunc, args=[key])
    elif key in common.toRemap:
        t = Thread(target=keyPress, args=[key])
    else:
        return

    t.start()

def on_release(key):
    if key == common.toggleKey or key in common.toRemap:
        t = Thread(target=triggerKeyReleaseEvent, args=[key])
        t.start()

def hook(event):
    
    key = event.name

    if keyboard.is_pressed(key):
        on_press(key)
    else:
        on_release(key)
    
    return False
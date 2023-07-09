import common
from GUI.hideGUI import hideGUI
from customFuncs import *
import keyboard
from threading import Event, Thread


def toggleFunc(key):
    global hotKeyUsed
    
    if not common.toggleThread.acquire(blocking=False):
        return
    
    common.windowTitle = common.getWindowName()
    common.showGUI.set()
    common.keyReleaseEvents[key].clear()

    hotKeyUsed = False
    common.toggle = True

    if common.keyReleaseEvents[key].wait(timeout=.15):
        if not hotKeyUsed:
            common.toggle = False
            keyboard.send(".")
            common.toggleThread.release()
            hideGUI()
            return

    common.keyReleaseEvents[key].wait()

    hideGUI()

    common.toggle = False
    common.layer = 0
    
    common.toggleThread.release()

    if (not hotKeyUsed) and (not common.isEditing):
        run("C:\\Users\\zeusa\\OneDrive\\Documents\\Code\\AHK Scripts\\togle-script\\tilingManagerTest.exe")

    return

def keyPress(key):
    global hotKeyUsed

    if key in common.keyReleaseEvents:
        return

    resetLayer = common.layer != 0

    keyRelEvent = Event()
    common.keyReleaseEvents[key] = keyRelEvent

    if common.toggle and not common.isEditing:
        hotKeyUsed = True
        c = common.getCmd(key)

    else:
        c = common.getCmd(key, "Untoggled")

    if c.hideGUIBeforeRun:
        hideGUI()

    processCmd(c, keyRelEvent)

    common.keyReleaseEvents.pop(key)
    
    if resetLayer:
        common.layer = 0
        common.redrawGui = True

    if common.toggleThread.locked():
        common.showGUI.set()

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
    
    if not common.doRemapping:
        return
    elif key == common.toggleKey:
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
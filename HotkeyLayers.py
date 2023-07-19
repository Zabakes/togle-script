from threading import Thread
import os
from PIL import Image
from Layers.InitConfig import updateConfig
import common
from GUI.createGUI import makeWidget
from GUI.guiVisibility import showGUI, hideGUI

import pystray

def quit():
    common.kill = True
    showGUI()
    icon.stop()

def refreshConfigs():
    global t
    updateConfig()
    common.kill = True
    if t:
        showGUI()
        t.join(timeout=.5)
        hideGUI()
    common.kill = False
    if common.drawGUI:
        t = Thread(target=makeWidget,
            args=[common.layout])
        t.start()

# In order for the icon to be displayed, you must provide an icon
menu = pystray.Menu(pystray.MenuItem("Quit", quit),
                    pystray.MenuItem("Refresh configs", refreshConfigs), 
                    )

icon = pystray.Icon(
    'ToggleScript',
    icon=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "toggleScript.ico")),
    menu=menu)

t : Thread = None
refreshConfigs()

# To finally show you icon, call run
icon.run()
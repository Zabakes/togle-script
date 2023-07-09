from threading import Thread
import os
from PIL import Image
from Layers.configure import updateConfig
import common
from GUI.createGUI import makeWidget

updateConfig()
t = Thread(target=makeWidget)
t.start()

import pystray

from PIL import Image

def quit():
    
    common.kill = True
    common.showGUI.set()
    icon.stop()

# In order for the icon to be displayed, you must provide an icon
menu = pystray.Menu(pystray.MenuItem("Quit", quit), pystray.MenuItem("Refresh hotkeys", lambda : updateConfig()))

icon = pystray.Icon(
    'ToggleScript',
    icon=Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "toggleScript.ico")),
    menu=menu)

# To finally show you icon, call run
icon.run()
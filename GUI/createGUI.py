import common
import tkinter as tk
from GUI.keybox import keyBox
from GUI.tootlip import ToolTip
import pyautogui
from time import sleep

def findWidgetAndUpdateConf(event):
    
    common.isEditing = True
    w = event.widget
    
    while type(w) != keyBox:
        w = w.master
        if type(w) == tk.Tk:
            return
    
    w.updateConfigFile(event)

def makeWidget():
    
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

    for i, button in enumerate(common.toRemap):
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
        
        common.redrawGui = True
        titleMatch = common.getTitleMatch()

        while common.showGUI.isSet() and not common.kill:
            if common.redrawGui:
                for i, (key, element) in enumerate(zip(common.toRemap, buttonElements)):
                    cmd = common.getCmd(key, titleMatch)
                    element.key = key
                    element.titleMatch = titleMatch
                    element.updateKeyBox(cmd)
                    common.redrawGui = False
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

        common.showGUI.wait()
        
        if common.kill:
            root.destroy()
            return
        common.isEditing = False

        sleep(.125)
        if common.showGUI.isSet():
            root.deiconify()
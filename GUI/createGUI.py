import common
import tkinter as tk
import json
from GUI.keybox import keyBox
import pyautogui
from time import sleep
from PIL import ImageTk, ImageGrab, ImageFilter, ImageEnhance
from math import floor
from Layers.runTimeConfig import getCmd

class layerPreview(tk.Canvas):
    
    def __init__(self, 
                 master= None,
                 layoutFile = None, 
                 *args, **kwargs) -> None:

        super().__init__(master,
                        *args,
                        **kwargs)

        if layoutFile is None:
            layoutFile = "Layouts\keyboard-layout-4.json"
            
        with open(layoutFile, 'r') as layout:
            layoutInfo = json.load(layout)
        
        layoutInfo = self.combineLegendAndData(layoutInfo)
        
        collCount = 0
        rowCount = 0
        
        
        rNum = 0
        for row in layoutInfo:
            cNum = 0
            for key in row:
                collSpan = key.get("w", 1)
                rowSpan = key.get("h", 1)
                
                collOffset = key.get("x", 0)
                rowOffset = key.get("y", 0)

                collCount = max(collCount, cNum+collOffset+collSpan)

                cNum += collOffset+collSpan
                rNum += rowOffset

            rowCount = max(rowCount, (rNum+rowOffset)+rowSpan)
            rNum += 1

        common.WIDGET_WIDTH = int(common.WIDGET_HEIGHT*collCount/rowCount)
        
        collSize = (common.WIDGET_WIDTH-10)//collCount
        rowSize = (common.WIDGET_HEIGHT-50)//rowCount
        
        self.keysToGUI = []
        
        rNum = 0
        for row in layoutInfo:
            cNum = 0
            for key in row:
                collSpan = key.get("w", 1)
                rowSpan = key.get("h", 1)
                
                collOffset = key.get("x", 0)
                rowOffset = key.get("y", 0)

                # This being a map means that duplicate legends leads to hidden keys TODO fix that
                self.keysToGUI.append((key["legend"], keyBox(   x=floor((cNum+collOffset)*collSize)+5,
                                                                y=floor((rNum+rowOffset)*rowSize)+50,
                                                                master=self, 
                                                                key=key["legend"], 
                                                                width=floor(collSpan*collSize), 
                                                                height=floor(rowSpan*rowSize))))
                cNum += collOffset+collSpan
                rNum += rowOffset
            rNum += 1

    def getKeyboxByPosition(self, x, y):
        for idx, key in self.keysToGUI:
            if x >= key.x and y >= key.y and x <= key.x+key.width and y <= key.y+key.height:
                return key

    def combineLegendAndData(self, layoutInfo):
        newInfo = []
    
        for row in layoutInfo:
            lastKey = None
            newInfo.append([])
            for key in row:
                if type(key) is str:
                    d = {"legend" : key}
                    if lastKey is not None:
                        d.update(lastKey)
                        lastKey = None
                    newInfo[-1].append(d)
                    lastKey = None
                elif type(key) is dict:
                    lastKey = key
        return newInfo
    
    def findWidgetAndUpdateConf(self, event):
        w = self.getKeyboxByPosition(event.x, event.y)
        if w is None:
            return

        common.isEditing = True
        w.updateConfigFile(event)

def updateBG(imgHandle, abs_coord_x, abs_coord_y, pview, root):
    global img
    if not common.showGUI.isSet():
        return

    #root.withdraw()
    img = ImageGrab.grab([abs_coord_x, abs_coord_y, abs_coord_x+common.WIDGET_WIDTH, abs_coord_y+common.WIDGET_HEIGHT])
    #root.deiconify()
    
    img = img.filter(ImageFilter.GaussianBlur(radius=10))
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.5)
    img = ImageTk.PhotoImage(img)
    pview.itemconfig(imgHandle, image=img)
    pview.tag_lower(imgHandle)
    #if common.updateBGInterval > 0:
        #pview.after(int(common.updateBGInterval*1000), lambda : updateBG(imgHandle, abs_coord_x, abs_coord_y, pview, root))
HWND = 0
import win32gui
def winEnumHandler( hwndT, ctx ):
    global HWND
    if win32gui.GetWindowText( hwndT ) == "zMAC_OVERLAY":
        HWND = hwndT

def makeWidget(layoutFile):
    global img, HWND
    root = tk.Tk(className="ZMAC_OVERLAY", baseName="ZMAC_POP_UP")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    common.WIDGET_HEIGHT = screen_height//3
    common.WIDGET_WIDTH = int(common.WIDGET_HEIGHT/1.75)
    root.call('wm', 'attributes', '.', '-topmost', '1')
    root.overrideredirect(True)
    abs_coord_x, abs_coord_y = pyautogui.position()
    root.geometry(f"{common.WIDGET_WIDTH}x{common.WIDGET_HEIGHT}+{abs_coord_x}+{abs_coord_y}")
    #root.update()
    #win32gui.EnumWindows( winEnumHandler, None )
    #print(HWND, root.winfo_id())
    #GlobalBlur(HWND, Dark=True, hexColor="ffffff00")
    #root.withdraw()

    pview = layerPreview(root, layoutFile=layoutFile, background="black", highlightthickness=0)
    pview.grid(row = 0, column = 0, sticky="NSEW")
    
    winTitleText = pview.create_text(common.WIDGET_WIDTH//2,
                      20,
                      text="", 
                      fill="White", 
                      font=('Helvetica 10 bold'),
                      anchor=tk.N,
                      justify='center',
                      tags="elements")
 
    tk.Grid.rowconfigure(root,0,weight=1)
    tk.Grid.columnconfigure(root,0,weight=1)

    root.bind("<Button-3>", pview.findWidgetAndUpdateConf)
    
    img = ImageGrab.grab([abs_coord_x, abs_coord_y, abs_coord_x+common.WIDGET_WIDTH, abs_coord_y+common.WIDGET_HEIGHT])
    img = img.filter(ImageFilter.GaussianBlur(radius=10))
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.75)
    img = ImageTk.PhotoImage(img)
    imgHandle = pview.create_image(0,0, image=img, anchor=tk.NW)
    while True:

        common.showGUI.wait()

        abs_coord_x, abs_coord_y = pyautogui.position()
        if(common.WIDGET_WIDTH+abs_coord_x > screen_width):
            abs_coord_x = screen_width-common.WIDGET_WIDTH
        
        if(common.WIDGET_HEIGHT+abs_coord_y > screen_height):
            abs_coord_y = screen_height-common.WIDGET_HEIGHT

        updateBG(imgHandle, abs_coord_x, abs_coord_y, pview, root)

        root.deiconify()
        root.geometry(f"{common.WIDGET_WIDTH}x{common.WIDGET_HEIGHT}+{abs_coord_x}+{abs_coord_y}")

        common.redrawGui = True

        titleMatch = common.getTitleMatch()

        while common.showGUI.isSet() and not common.kill:
            if common.redrawGui:
                pview.tag_raise(imgHandle)
                for i, (key, element) in enumerate(pview.keysToGUI):
                    pview.itemconfig(winTitleText, text=common.getAppName())
                    cmd = getCmd(key, titleMatch)
                    element.key = key
                    element.titleMatch = titleMatch
                    element.updateKeyBox(cmd)
                    pview.tag_raise(winTitleText)
                    pview.tag_raise(element.rectangleTag)
                    pview.tag_raise(element.keyIndexLabel)
                    common.redrawGui = False
            #root.lift()
            #for tt in ToolTip.liveToolTips:
                #print("raise tt", ToolTip.liveToolTips)
                #tt.lift()
            root.update_idletasks()
            root.update()
            sleep(.005)

        #for tt in ToolTip.liveToolTips:
        #    tt.on_leave(discard=False)

        #ToolTip.liveToolTips = set()

        root.withdraw()

        if common.kill:
            root.destroy()
            return

        common.isEditing = False
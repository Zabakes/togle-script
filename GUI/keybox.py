import tkinter as tk
from tkinterweb import HtmlFrame
import common
import json
import os
from GUI.tootlip import ToolTip
from Layers.runTimeConfig import parseKeyConfig, getAppCmds

from GUI.guiVisibility import hideGUI
from PIL import Image, ImageTk, ImageOps
import re


class keyBox():
    allBeingEdited = set()
    bgimg = None


    def __init__(self, 
                 x,
                 y,
                 width,
                 height,
                 key,
                 master : tk.Canvas,
                 *args, **kwargs) -> None:

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.key = key

        self.img = None
        self.index = None
        
        self.textBox = tk.Text(master.master, width=width, wrap=tk.WORD)

        self.textBox.place_forget()

        self.master = master
        self.textWidg = master.create_text( x+self.width/2, 
                                            y+30,
                                            width=width-20,
                                            fill="White", 
                                            font=('Helvetica 10 bold'),
                                            anchor=tk.N,
                                            justify='center',
                                            tags="elements") #create HTML browser
        
        self.rectangleTag = master.create_rectangle(x, y, x+width, y+height, outline="white")

        for i , key in enumerate(common.toRemap):
            if key == self.key:
                self.index = i

        self.keyIndexLabel = master.create_text(self.x+self.width/2, 
                                                self.y+20,
                                                text=self.key, 
                                                fill="White", 
                                                font=('Helvetica 10 bold'),
                                                anchor=tk.CENTER,
                                                justify='center',
                                                tags="elements")

        self.imgFrame = self.master.create_image(self.x+self.width/2, self.y+self.height/2, image=self.img, anchor=tk.CENTER)

        self.textBox.bind("<Control-Return>", self.saveConfig)
        self.textBox.bind("<Control-s>", self.saveConfig)
        self.textBox.bind("<Escape>", self.discardConfig)
        self.key = self.titleMatch = self.newWindow = None
        self.master.tk.call('raise', self.master._w)


    def showText(self):
        self.textBox.place(x = self.x,
            y =  self.y, 
            width=self.width,
            height=self.height)
        self.textBox.tkraise()

    def showDescription(self):
        self.textBox.place_forget()
        self.master.tk.call('raise', self.master._w)
        if self.img:
            self.master.tag_raise(self.imgHandle)
        else:
            self.master.tag_raise(self.htmlFrame)

    def updateConfigFile(self, event):
        if self.index is None:
            common.isEditing = False
            return
        
        common.isEditing = True

        self.allBeingEdited.add(self)

        fname = common.titleMatchToConfigFile[self.titleMatch]
        
        with open(fname, "r") as f:
            self.conf = json.load(f)
            rawConfData = self.conf["hks"][self.index]
        
        self.textBox.config(state=tk.NORMAL)
        self.textBox.delete("1.0",tk.END)
        self.textBox.insert("1.0",json.dumps(rawConfData, indent=4))
        self.showText()

    def makeNewFile(self, pfix, fileNameEntry, winTitle, input):
        fileName = fileNameEntry.get()
        self.titleMatch = winTitle

        self.conf = {
            "appName" : winTitle,
            "hks" : [dict()]*len(common.toRemap)
        }
        fname = os.path.join(pfix, fileName)
        with open(fname, "w") as f:
                f.write(json.dumps(self.conf, indent=4))

        common.appToKeys[self.titleMatch] = {key:None for key in common.toRemap}

        common.titleMatchToConfigFile[self.titleMatch] = fname
        self.saveConfig(None, fname, input)

    def saveConfig(self, e, fname = None, input = None):

        if self.newWindow:
            self.newWindow.destroy()
            self.newWindow = None

        if fname is None:
            fname = common.titleMatchToConfigFile[self.titleMatch]
            pfix, fnameTail = os.path.split(fname)
            WinTitle = re.split(common.winTitleSplitter, common.getWindowName()).pop().strip()
            if fnameTail == "Default.json" and WinTitle:
                self.newWindow = tk.Toplevel(self.master)
                self.newWindow.attributes('-topmost', True)
                self.newWindow.update()
                title = tk.Label(self.newWindow, text="Would you like to make a new file or save onto the default mapping? To make a new file enter it's name into the text box.")
                eFileName = tk.Entry(self.newWindow)
                eFileName.insert(0, f"""{WinTitle.replace(" ", "_")}.json""")
                bYes = tk.Button(self.newWindow, text="Make New File", command=lambda : self.makeNewFile(pfix, eFileName, WinTitle, input))
                bNo = tk.Button(self.newWindow, text="Modify default", command=lambda : self.saveConfig(e, fname))
                
                eFileName.grid(row=0, column=0, columnspan=2, sticky="ew")
                bYes.grid(row=2, column=0, sticky="ew")
                bNo.grid(row=2, column=1, sticky="ew")
                return False

        if input is None:
            input = self.textBox.get("1.0",tk.END)

        try:
            self.conf["hks"][self.index] = json.loads(input)
            target = json.loads(input)

            getAppCmds.cache_clear()

            with open(fname, "w") as f:
                f.write(json.dumps(self.conf, indent=4))

        except json.JSONDecodeError:
            self.textBox.configure(bg="red")
            self.textBox.after(1000, lambda : self.textBox.configure(bg="white"))
            return False

        self.allBeingEdited.discard(self)
        
        if self.allBeingEdited:
            other = self.allBeingEdited.pop()
            with open(fname, "r") as f:
                other.conf = json.load(f)
            if not other.saveConfig(e, fname=fname):
                self.allBeingEdited.add(other)
                return False
        
        self.master.tk.call('raise', self.master._w)
        common.isEditing = False
        hideGUI()
        return True

    def discardConfig(self, e):
        if self.newWindow:
            self.newWindow.destroy()
            self.newWindow = None
        self.allBeingEdited = set()
        
        self.master.tk.call('raise', self.master._w)
        common.isEditing = False
        hideGUI()

    def updateKeyBox(self, cmd) -> None:
        if cmd is None:
            return

        if cmd.imgPath:
            try:
                i = Image.open(cmd.imgPath)
                ImageOps.contain(i, (self.width, self.height))
                self.img = ImageTk.PhotoImage(i)
                self.master.itemconfig(self.imgFrame, image=self.img)
                self.master.tag_raise(self.imgFrame)
            except FileNotFoundError:
                self.img = None
                pass
        else:
            self.master.tag_raise(self.textWidg)

        self.master.itemconfig(self.textWidg, text=cmd.getDescription())

import tkinter as tk
from tkinterweb import HtmlFrame
import common
import json
import os
from GUI.tootlip import ToolTip
from Layers.configure import parseKeyConfig
from GUI.hideGUI import hideGUI
from PIL import Image, ImageTk
import re


class keyBox(tk.Frame):
    allBeingEdited = set()
    bgimg = None
    
    def __init__(self, 
                 master = None,
                 index = None,
                 *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)
        
        self.htmlFrame = HtmlFrame(self, messages_enabled = False) #create HTML browser
        self.img = None
        self.textBox = tk.Text(self, height=common.WIDGET_HEIGHT//4, width=common.WIDGET_WIDTH//3, wrap=tk.WORD)
        
        self.index = index
        if self.index is not None:
            print(self.index)
            self.keyIndexLabel = tk.Label(self, text=self.index+1, justify=tk.CENTER)
            self.keyIndexLabel.grid(row=0, column=0, sticky="nsew")
            self.rowconfigure(0, minsize=common.WIDGET_HEIGHT//30, weight=1)
        
        
        self.imgFrame = tk.Label(self)
        self.textBox.grid(row=1, column=0, sticky="nsew")
        self.htmlFrame.grid(row=1, column=0, sticky="nsew")
        self.imgFrame.grid(row=1, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1) 
        self.rowconfigure(1, weight=1)

        self.textBox.bind("<Control-Return>", self.saveConfig)
        self.textBox.bind("<Control-s>", self.saveConfig)
        self.textBox.bind("<Escape>", self.discardConfig)

        self.toolTip = ToolTip(self.imgFrame)

        self.key = self.titleMatch = self.newWindow = None

    def showText(self):
        self.textBox.tkraise()

    def showDescription(self):
        if self.img:
            self.imgFrame.tkraise()
        else:
            self.htmlFrame.tkraise()

    def updateConfigFile(self, event):
        
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
        #print(json.dumps(rawConfData))

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
        

        if fname is None:
            fname = common.titleMatchToConfigFile[self.titleMatch]

            pfix, fnameTail = os.path.split(fname)
            if fnameTail == "Default.json":
                self.newWindow = tk.Toplevel(self)
                eFileName = tk.Entry(self.newWindow)
                WinTitle = re.split(common.winTitleSplitter, common.getWindowName()).pop().strip()
                eFileName.insert(0, f"""{WinTitle.replace(" ", "_")}.json""")
                bYes = tk.Button(self.newWindow, text="Make New File", command=lambda : self.makeNewFile(pfix, eFileName, WinTitle, input))
                bNo = tk.Button(self.newWindow, text="Modify default", command=lambda : self.saveConfig(e, fname))
                
                eFileName.grid(row=0, column=0, columnspan=2, sticky="ew")
                bYes.grid(row=2, column=0, sticky="ew")
                bNo.grid(row=2, column=1, sticky="ew")
                return
        
        
        if input is None:
            input = self.textBox.get("1.0",tk.END)

        try:
            self.conf["hks"][self.index] = json.loads(input)
            target = json.loads(input)

            common.appToKeys[self.titleMatch][self.key] = parseKeyConfig(target)

            with open(fname, "w") as f:
                f.write(json.dumps(self.conf, indent=4))

        except json.JSONDecodeError:
            pass

        if self.newWindow:
            self.newWindow.destroy()
            self.newWindow = None
        
        self.allBeingEdited.discard(self)
        
        if self.allBeingEdited:
            other = self.allBeingEdited.pop()
            with open(fname, "r") as f:
                other.conf = json.load(f)
            other.saveConfig(e)
        
        common.isEditing = False
        hideGUI()

    def discardConfig(self, e):
        
        self.allBeingEdited = set()
        common.isEditing = False
        hideGUI()

    def updateKeyBox(self, cmd) -> None:
        if cmd.imgPath:
            try:
                i = Image.open(cmd.imgPath)
                self.img = ImageTk.PhotoImage(i)
                self.imgFrame.configure(image=self.img)
                self.imgFrame.tkraise()
                self.toolTip.msg = cmd.getDescription()
            except FileNotFoundError:
                self.img = None
                pass
        else:
            self.htmlFrame.tkraise()

        self.htmlFrame.load_html(f"""<p>{cmd.getDescription()}</p>""")

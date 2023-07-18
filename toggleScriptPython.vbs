Dim wshShell, fso, loc, cmd

'~ cmd = "%ComSpec% /k C:\Languages\Python\python.exe " + loc + "\test.py"
cmd = "cmd /k C:/Users/zeusa/Anaconda3/Scripts/activate & conda activate toggleScript & python ""c:\Users\zeusa\OneDrive\Documents\Code\AHK Scripts\togle-script\HotkeyLayers.py"""

Set wshShell = CreateObject("WScript.Shell")
wshShell.Run cmd, 0, False
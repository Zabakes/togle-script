#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#SingleInstance, force
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

vertCells := 2
horCells := 3

CoordMode, Mouse, Screen

mode = 1

toResize := getWinTitle()

mon := GetMonitorMouse()

SysGet, mon, MonitorWorkArea, %mon%

monSizeX := monRight - monLeft
monSizeY := monBottom - monTop

cellSizeX := floor(monSizeX/horCells)
cellSizeY := floor(monSizeY/vertCells)

Gui Color, Blue
Gui, +LastFound
Gui, +AlwaysOnTop
WinSet, Transparent, 100
Gui, -Caption
Gui Show, w%monSizeX% h%monSizeY% X%monLeft% Y%monTop%
WinSet, Region, 0-0 W0 H0

MouseGetPos, initX, initY

while getkeystate("LButton", "P") == 0{

    MouseGetPos, x, y

    boxX := x-initX
    boxY := y-initY

    startCellX := (floor(boxX/(monSizeX/20)))
    startCellY := (floor(boxY/(monSizeY/10)))

    startCellX := max(startCellX, 0)
    startCellY := max(startCellY, 0)

    startCellX := min(startCellX, horCells-1)
    startCellY := min(startCellY, vertCells-1)

    ToolTip, %startCellX% %startCellY% , 10, 10

    winStartX := startCellX*cellSizeX
    winStartY := startCellY*cellSizeY

    WinSet, Region, %winStartX%-%winStartY% W%cellSizeX% H%cellSizeY%
    
    Sleep, 100
}

KeyWait, LButton, D

MouseGetPos, initX, initY

while getkeystate("LButton", "P") == 1{

    MouseGetPos, x, y

    boxX := x-initX
    boxY := y-initY

    cellsX := (floor(boxX/(monSizeX/20))+1)
    cellsY := (floor(boxY/(monSizeY/10))+1)

    cellsX := max(cellsX, 1)
    cellsY := max(cellsY, 1)

    cellsX := min(cellsX, horCells)
    cellsY := min(cellsY, vertCells)

    ToolTip, %cellsX% %cellsY% , 10, 10

    winRegionX := cellsX*cellSizeX
    winRegionY := cellsY*cellSizeY

    WinSet, Region, %winStartX%-%winStartY% W%winRegionX% H%winRegionY%

    Sleep, 100
}
winStartX += monLeft
winStartY += monTop
WinMove, %toResize%,, %winStartX%, %winStartY%, %winRegionX%, %winRegionY%
WinActivate, %toResize%

mode = 0
Gui, Destroy
ToolTip

ExitApp

GetMonitorMouse()
{
    MouseGetPos, x, y

    SysGet, numOfMonitors, 80

    i:= 1
    
    while i <= numOfMonitors{
        SysGet, mon, MonitorWorkArea, %i%
        if (x < monRight && x > monLeft && y < monBottom && y > monTop){
            Return %i%
        }
        i++
    }
    Return -1
}

getWinTitle(){
	;get the active window
    WinGet, id, ID, A
	;get the title from the active window
    WinGetTitle, windowTitle, ahk_id %id%
	;break up the window title  - is the delimiter drop spaces
    return windowTitle
}

#If mode ; All hotkeys below this line will only work if mode is TRUE
    LButton::Return
#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#SingleInstance, force
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

vertCells := 2
horCells := 6

CoordMode, Mouse, Screen

mode = 1

toResize := getWinTitle()

mon := GetMonitorMouse()

SysGet, mon, MonitorWorkArea, %mon%

monSizeX := monRight - monLeft
monSizeY := monBottom - monTop

cellSizeX := floor(monSizeX/horCells)
cellSizeY := floor(monSizeY/vertCells)

Gui Color, Black
Gui, +LastFound
Gui, +AlwaysOnTop
WinSet, Transparent, 100
Gui, -Caption
Gui Show, w%monSizeX% h%monSizeY% X%monLeft% Y%monTop%
WinSet, Region, 0-0 W0 H0

while getkeystate("LButton", "P") == 0{
	MouseGetPos, x, y

    

	downXcell := x // cellSizeX
	downYcell := y // cellSizeY

	ToolTip, %downXcell% %downYcell% , 10, 10

	winStartX := downXcell*cellSizeX
	winStartY := downYcell*cellSizeY

	WinSet, Region, %winStartX%-%winStartY% W%cellSizeX% H%cellSizeY%

 	Sleep, 100
}

KeyWait, LButton, D

while getkeystate("LButton", "P") == 1{
	MouseGetPos, x, y

    x -= monLeft
    y -= monTop

	upXcell := x // cellSizeX
	upYcell := y // cellSizeY

	startXcell := Min(downXcell, upXcell)
	startYcell := Min(downYcell, upYcell)

	spanX := Abs(downXcell - upXcell) + 1
	spanY := Abs(downYcell - upYcell) + 1

	winStartX := startXcell*cellSizeX
	winStartY := startYcell*cellSizeY

	ToolTip, %spanX% %spanY% , 10, 10

	winRegionX := spanX*cellSizeX
	winRegionY := spanY*cellSizeY

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

	i := 1

	while i <= numOfMonitors
		{
		SysGet, mon, MonitorWorkArea, %i%
		if (x < monRight && x > monLeft && y < monBottom && y > monTop)
			{
			Return %i%
			}
		i++
		}
	Return -1
	}

getWinTitle()
	{
	;get the active window
	WinGet, id, ID, A
	;get the title from the active window
	WinGetTitle, windowTitle, ahk_id %id%
	;break up the window title  - is the delimiter drop spaces
	return windowTitle
	}

$Escape:: 
	mode = 0
	Gui, Destroy
	ToolTip
	ExitApp
Return

#If mode ; All hotkeys below this line will only work if mode is TRUE
	LButton::Return
#If
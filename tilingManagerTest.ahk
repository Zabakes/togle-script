#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#SingleInstance, force
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

Menu, Tray, Icon, toggleScriptRed.ico



vertCells := 2
horCells := 6

CoordMode, Mouse, Screen

mode = 1

toResize := getWinTitle()
Done := 0
GoSub, start
ExitApp

start:

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

	    x -= monLeft
	    y -= monTop

		downXcell := x // cellSizeX
		downYcell := y // cellSizeY

		ToolTip, %downXcell% %downYcell% , 10, 10

		winStartX := downXcell*cellSizeX
		winStartY := downYcell*cellSizeY

		if (mon != GetMonitorMouse()){
			Goto, start
		}

		WinSet, Region, %winStartX%-%winStartY% W%cellSizeX% H%cellSizeY%
	}

	KeyWait, LButton, D
	if (mode != 1){
		goSub, $Escape
	}

	Menu, Tray, Icon, toggleScriptGreen.ico

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
	}
	winStartX += monLeft
	winStartY += monTop
	WinRestore, %toResize%
	WinMove, %toResize%,, %winStartX%, %winStartY%, %winRegionX%, %winRegionY%
	WinActivate, %toResize%

	mode = 0
	Gui, Destroy
	ToolTip

	return

GetMonitorMouse(){
	MouseGetPos, x, y

	SysGet, numOfMonitors, 80

	i := 1

	while (i <= numOfMonitors){
		SysGet, mon, MonitorWorkArea, %i%
		if (x <= monRight && x >= monLeft && y <= monBottom && y >= monTop)
			{
			Return %i%
			}
		i++
		}
	MsgBox,16,,Your mouse isn't on a monitor???????? quiting, 2
	ExitApp
	}

getWinTitle(){
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
	LButton:: 
	if (mode == 1){
		Return
	}
	if (mode > 1){
		ExitApp
	}
	return
#If

$RButton::
	mode := 2
	if (Done == 0){
		Menu, Windows, Add
		Menu, Windows, deleteAll
		WinGet windows, List
		Menu, Windows, Add, Done, $Escape
		Menu, Windows, Default, Done

		Loop %windows%
		{
			id := windows%A_Index%
			WinGetTitle title, ahk_id %id%
			If (title = "")
				continue
			WinGetClass class, ahk_id %id%	
			If (class = "ApplicationFrameWindow") 
			{
				WinGetText, text, ahk_id %id%
				If (text = "")
					continue
			} 
			WinGet, style, style, ahk_id %id%
			if !(style & 0xC00000) ; if the window doesn't have a title bar
			{
				; If title not contains ...  ; add exceptions
					continue
			}
			WinGet, Path, ProcessPath, ahk_id %id%
			Menu, Windows, Add, %title%, Activate_Window
			Try 
				Menu, Windows, Icon, %title%, %Path%,, 0
			Catch 
				Menu, Windows, Icon, %title%, %A_WinDir%\System32\SHELL32.dll, 3, 0
		}
		Done := 1
	}Else{
		Menu, Windows, Disable, %Done%
	}

	Menu, Windows, Show
return

Activate_Window:
	mode := 1
	SetTitleMatchMode, 3
	toResize := A_ThisMenuItem
	Done := A_ThisMenuItem
	GoSub, start
	GoSub, $RButton
return

$MButton::
	WinMinimizeAll
	return

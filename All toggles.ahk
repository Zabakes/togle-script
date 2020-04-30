/*
	This script uses the F4 key to toggle between numbers and hotkeys for use on a MM0 mouse.
    each set of toggled keys is stored in an array in order. the keypresses on the mouse are mapped to the inicies of the array with the "keysToIndecies" linked list.
    a hotkey is set up for each key in the linked list when the hotkey is setup. when the hotkey is pressed the script checks what window is active.
    if there is a set of hotkey array for the active app the script uses that array to define the toggles.

	Thanks /u/GroggyOtter for making it clean

	To make a hotkey set run Hotkey setter the top box in on press the bottom is on release

*/

#SingleInstance, force

;initalize the app names as keys in appkeysDown
appkeysDown := []
appkeysUp := []
keysToIndices := {}

; Default toggle state
toggle := 0
keypress := False 

goSub, updateConfig

; End Auto-Execute Section
return

; Label to run when any key is pressed
ToggleSend:
		; Remove the $* hotkey prefixes using regex
    	; This leaves the key that was pressed
        hk  := RegExReplace(A_ThisHotkey, "^\$\*", "")

        ; If toggle is turned on...
        if (toggle = 1){

			keyPress := True

			;get the window title and split up it's name
			MouseGetPos, , , id, control
			WinGetTitle, winTitle, ahk_id %id%
			WinActivate, %winTitle%
    		chopped := StrSplit(winTitle, "-" , " ")
			

			if (InStr(chopped[1], ".ipynb")){
				hotkeysToUse := appkeysDown["JupyterLab"]
				hotkeysUp := appkeysUp["JupyterLab"]
			}else{
				;use the hotkeys based on the tab within a browser
				;this is at the begining of the window title so check that first
				hotkeysToUse := appkeysDown[("" chopped[1] "")]
				hotkeysUp := appkeysUp[("" chopped[1] "")]
			}


			; if hotkeys to use is still empty (No meaningful tabs have have control)
			if (hotkeysToUse.MaxIndex() <= 1){
				;use the hotkey based on the application
				;the application name is usually at the end of the window title so get the last word(s) in the window title
				hotkeysToUse := appkeysDown[("" chopped[chopped.MaxIndex()] "")]
				hotkeysUp := appkeysUp[("" chopped[chopped.MaxIndex()] "")]
				;MsgBox % appkeysDown[("" chopped[chopped.MaxIndex()] "")].MaxIndex()
				;MsgBox % chopped[chopped.MaxIndex()]
				;MsgBox % hotkeysToUse.MaxIndex()
			}

			; if hotkeys to use is still empty
			if (hotkeysToUse.MaxIndex() <= 1){
				;Use default hotkeys
				hotkeysToUse := appkeysDown["Default"]
				hotkeysUp := appkeysUp["Default"]
				;MsgBox using Defaults
			}
        
        ; If toggle is turned off...
        }Else{

            ; ...send default of the key you pressed
			hotkeysToUse := appkeysUp["Config"]
			hotkeysUp := []
		}

			; ...use hka s an index to get it's associated key from the array
			
		    SendInput, % hotkeysToUse[keysToIndices[("" hk "")]]

			if (hotkeysUp.MaxIndex() >= 1){

				KeyWait, %hk%, U

				SendInput, % hotkeysUp[keysToIndices[("" hk "")]]
			}

return

; toggles alt sending
ToggleKey:
	ToggleKey  := RegExReplace(A_ThisHotkey, "^\$\*", "")
	keyPress := False
	;run this first so a single press is instant
	toggle := 1
	KeyWait, %ToggleKey%, T0.15
    if (ErrorLevel = 0 && keyPress = False){
        sendInput, . ;tap the toggle key to send a period
	}else{
		KeyWait, %ToggleKey%, U
		if (getWinTitle() != "" ){
			if (keyPress = False){
				run, tilingManagerTest.exe ;press hold and release without pressing a hotkey to run the tiling manager
				toggle := 0
				return
			}
		}
	}
	KeyWait, %ToggleKey%
	toggle := 0
	return



$*F3::
	Suspend Permit ;don't suspend this
	if (togglekeyPresses > 0){ ; SetTimer already started, so we log the keypress instead.
		togglekeyPresses += 1
    	return
	}
	; Otherwise, this is the first press of a new series. Set count to 1 and start
	; the timer:
	togglekeyPresses := 1


	SetTimer, Multipressf3, -600 ; Wait for more presses within a 600 millisecond window then run multipress
	return

Multipressf3:

	if (togglekeyPresses = 1){
		sendInput, {F3}
	}else if (togglekeyPresses = 2){ ; The key was pressed twice.
		printHotkeyState() ; tell the user if hotkeys are enabled
	}else if (togglekeyPresses = 3){
    	Suspend, Toggle ; enable or disable hotkeys
		printHotkeyState() ; tell the user
	}else if (togglekeyPresses >= 4){
		MsgBox % getWinTitle()
		goSub, updateConfig
	}
	; Regardless of which action above was triggered, reset the count to
	; prepare for the next series of presses:
	togglekeyPresses := 0
	return

printHotkeyState(){
	if(A_IsSuspended){
		MsgBox Hotkeys Suspended
	}else{
		MsgBox Hotkeys Enabled
	}
}

getWinTitle(){
	;get the active window
    WinGet, id, ID, A
	;get the title from the active window
    WinGetTitle, windowTitle, ahk_id %id%
	;break up the window title  - is the delimiter drop spaces
    return windowTitle
}

updateConfig:

	Loop, Files, %A_ScriptDir%\Hotkeys\*.*, FR
	{

		FileReadLine, AppName, %A_LoopFilePath%, 1
		FileReadLine, keysDown, %A_LoopFilePath%, 3

		if (AppName == "Config"){
			FileReadLine, toggleKey, %A_LoopFilePath%, 7
		}

		appkeysDown[("" AppName "")] := StrSplit(keysDown, ",", """")

		FileReadLine, keysUp, %A_LoopFilePath%, 5
		if (ErrorLevel = 0)
		{
			if (AppName != "Config"){
				keysUpArray := []
				if (InStr(keysUp, ",")){
					AllKeys := StrSplit(keysUp, ",")
						for index, value in AllKeys{
							indexKeytoSend := StrSplit(value, ":")
							keysUpArray[indexKeytoSend[1]] := indexKeytoSend[2]
						}
				}else{
					indexKeytoSend := StrSplit(keysUp, ":")
					keysUpArray[indexKeytoSend[1]] := indexKeytoSend[2]
				}
			appkeysUp[("" AppName "")] := keysUpArray
			}else{
				appkeysUp[("" AppName "")] := StrSplit(keysUp, ",", """")
			}

		}else{
			keysUpArray := []
		}
	}

		for index, value in appkeysDown["Config"]{
			keysToIndices[("" value "")] := index
		}

		; For loop to loop through key
		for index, value in keysToIndices{
			; Create hotkeys using the index from the loop
			Hotkey, % "$*" index, ToggleSend, On
		}

		Hotkey, % "$*" toggleKey, ToggleKey, On

	return



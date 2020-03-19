/*
	This script uses the F4 key to toggle bettween numbers and hotkeys for use on a MM0 mouse.
    each set of toggled keys is stored in an array in order. the keypresses on the mouse are mapped to the inicies of the array with the "keysToIndecies" linked list.
    a hotkey is set up for each key in the linked list when the hotkey is setup. when the hotkey is pressed the script checks what window is active.
    if there is a set of hotkey array for the active app the script usses that array to define the toggles.

	Thanks /u/GroggyOtter for making it clean

	To make a hotkey set run Hotkey setter the top box in on press the bottom is on realease

*/

#SingleInstance, force
;Divvy path
EnvGet, LCLAPPDATA, LOCALAPPDATA
; Associative array for mapping the keys to indiceis
keysToIndecies := {"1":1 ,"2":2 ,"3":3 ,"4":4 ,"5":5 ,"6":6 ,"7":7 ,"8":8 ,"9":9 ,"0":10 ,"-":11 ,"BS":12}

;initalize the app names as keys in appkeysDownappkeysDown
appkeysDown := []
appkeysUp := []

Loop, Files, %A_ScriptDir%\Hotkeys\*.*, FR
{
	FileReadLine, AppName, %A_LoopFilePath%, 1
	FileReadLine, keysDown, %A_LoopFilePath%, 3

	appkeysDown[("" AppName "")] := StrSplit(keysDown, ",", """")

	FileReadLine, keysUp, %A_LoopFilePath%, 5
	if (ErrorLevel = 0)
	{
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
		keysUpArray := []
	}

}


; Default toggle state
toggle := 0
keypress := False 

; For loop to loop through keyA
for index, value in keysToIndecies
    ; Create hotkeys using the index from the loop
    Hotkey, % "$" index, ToggleSend, On
; End Auto-Execute Section
return


; Label to run when any key is pressed
ToggleSend:
   
		keypress := True

		; Remove the $* hotkey prefixes using regex
    	; This leaves the key that was pressed
        hk  := RegExReplace(A_ThisHotkey, "^\$", "")

        ; If toggle is turned on...
        if (toggle = 1){

			;get the window title and split up it's name
			MouseGetPos, , , id, control
			WinGetTitle, winTitle, ahk_id %id%
			WinActivate, %winTitle%
    		chopped := StrSplit(winTitle, "-" , " ")
			;MsgBox, %chopped% 

			;use the hotkeys based on the tab within a browser
			;this is at the begining of the window title so check that first
			hotkeysToUse := appkeysDown[("" chopped[1] "")]
			hotkeysUp := appkeysUp[("" chopped[1] "")]

			; if hotkeys to use is still empty (No meaningfull tabs have have control)
			if (hotkeysToUse.MaxIndex() <= 1){
				;use the hotkey based on the aplication
				;the aplication name is usualy at the end of the window title so get the last word(s) in the window title
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



			; ...use hka s an index to get it's associated key from the array
       		;MsgBox % hotkeysToUse[keysToIndecies[("" hk "")]]
       		SendInput, % hotkeysToUse[keysToIndecies[("" hk "")]]

			KeyWait, %hk%

			SendInput, % hotkeysUp[keysToIndecies[("" hk "")]]
          
        ; If toggle is turned off...
        }Else{
            ; ...send the key you just pressed
            Send, % "{" hk "}"
		}


return

; F4 toggles alt sending
$*F4::
	keypress := False
	;run this first so a single press is instant
	toggle := 1
	KeyWait, F4, T0.15
    if (ErrorLevel = 0 && keypress = False){
        sendInput, . ;tap the toggle key to send a period
	}else{
		if (FileExist(LCLAPPDATA "\Mizage LLC\Divvy\divvy.exe")){
			KeyWait, F4, T0.15
			if (ErrorLevel = 1 && keypress = False)
				run, divvy.exe, %LCLAPPDATA%\\Mizage LLC\Divvy ;tap the toggle key to send a period
		}
	}
	KeyWait, f4
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



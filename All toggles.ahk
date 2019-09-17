/*
	This script uses the F4 key to toggle bettween numbers and hotkeys for use on a MM0 mouse.
    each set of toggled keys is stored in an array in order. the keypresses on the mouse are mapped to the inicies of the array with the "keysToIndecies" linked list.
    a hotkey is set up for each key in the linked list when the hotkey is setup. when the hotkey is pressed the script checks what window is active.
    if there is a set of hotkey array for the active app the script usses that array to define the toggles.

    to add aditional apps create another array keep in mind the order of the array matters as that's how the script knows what to bind to your toggles.
    next add to the if else tree on line 94. check for when wintitle equals the name of the aplication you want to have toggles for then set "ToggleKeysToUse" to your array.
    if you don't know the name of the aplication uncomment "MsgBox %windowTitle%" on line 93 then hit any key that becomes toggled with the app you want to use as your active application.
    a messegw box will pop up with the name of your aplication copy this name exatly into the if else tree.

Thanks /u/GroggyOtter for making it clean
*/


; Associative array for mapping the keys to the array
keysToIndecies := {"1":1 ,"2":2 ,"3":3 ,"4":4 ,"5":5 ,"6":6 ,"7":7 ,"8":8 ,"9":9 ,"0":10 ,"-":11 ,"Delete":12}


/*
	Fusion 360
		1 -> Extrude		2 -> Line						3 -> Dimension
		4 -> Circle			5 -> Rectangle					6 -> Camera controls
		7 -> Project		8 -> Inspect/mesure				9 -> normal/construction line toggle
		10 -> Joint			11 -> visibility toggle			12 -> Enter
*/
Fusion  :=  ["e"					;1
,"l"								;2
,"d"								;3
,"c"								;4
,"r"								;5
,"{Shift down}{MButton down}"		;6
,"p"								;7
,"i"								;8
,"x"								;9
,"j"								;10
,"v"								;11
,"{Enter}"]							;12

/*
	Maya TODO
		1 -> Extrude		2 -> Line						3 -> Dimension
		4 -> Circle			5 -> Rectangle					6 -> Camera controls
		7 -> Project		8 -> Inspect/mesure				9 -> normal/construction line toggle
		10 -> Joint			11 -> visibility toggle			12 -> Enter
*/
Maya :=  ["e"					;1
,"l"							;2
,"d"							;3
,"c"							;4
,"r"							;5
,"{Alt down}{LButton down}"		;6
,"{}}"							;7
,"8"							;8
,"{{}"							;9
,"j"							;10
,"v"							;11
,"{Enter}"]						;12



/*
	  Firefox
		1 -> Back 								2 -> Refresh 					3 -> Forward
		4 -> Next tab 							5 -> New tab 					6 -> Previous tab
		7 -> Open google drive in new tab 		8 -> Open gmail in new tab 		9 -> Open pitt in new tab
		10 -> Search 							11 -> Print 					12 -> Enter
*/
firefoxToggles := ["{XButton1}"								;1
, "{f5}"													;2
,"{XButton2}"												;3
, "{Control down}{PgUp}{Control up}"						;4
, "{Control down}{t}{Control up}"							;5
, "{Control down}{PgDn}{Control up}"						;6
, "{Control down}{t}{Control up}drive.google.com {enter}"	;7
, "{Control down}{t}{Control up}gmail.com {enter}"			;8
, "{Control down}{t}{Control up}my.pitt.edu {enter}"		;9
, "{Control down}{f}{Control up}"							;10
, "{Control down}{p}{Control up}"							;11
, "{Enter}"]												;12


/*
	  Chrome
		1 -> Back 								2 -> Refresh 					3 -> Forward
		4 -> Next tab 							5 -> New tab 					6 -> Previous tab
		7 -> Open google drive in new tab 		8 -> Open gmail in new tab 		9 -> Open pitt in new tab
		10 -> Search 							11 -> Print 					12 -> Enter
*/
chromeToggles := ["{XButton1}"									;1
, "{f5}"														;2
,"{XButton2}"													;3
, "{Control down}{Shift down}{Tab}{Shift up}{Control up}"		;4
, "{Control down}{t}{Control up}"								;5
, "{Control down}{Tab}{Control up}"								;6
, "{Control down}{t}{Control up}drive.google.com{enter}"		;7
, "{Control down}{t}{Control up}gmail.com{enter}"				;8
, "{Control down}{t}{Control up}my.pitt.edu{enter}"				;9
, "{Control down}{f}{Control up}"								;10
, "{Control down}{p}{Control up}"								;11
, "{Enter}"]													;12

/*
	   VScode
		1 -> Column (box) select 	2 -> Save 				3 -> Commands
		4 -> Select previous 		5 -> select lines 		6 -> Select next
		7 -> move line down 		8 -> Toggle comment 	9 -> move line up
		10 -> Search 				11 -> Print 			12 -> Enter
*/
VSCode := ["{Shift down}{Alt down}{LButton down}"	;1
, "{Control down}{s}{Control up}"					;2
,"{f1}"												;3
, "{Shift down}{left}{Shift up}"					;4
, "{Control down}{l}{Control up}"					;5
, "{Shift down}{right}{Shift up}"					;6
, "{Alt down}{down}{Alt up}"						;7
, "{Shift down}{Alt down}{a}{Shift up}{Alt up}"		;8
, "{Alt down}{up}{Alt up}"							;9
, "{Control down}{f}{Control up}"					;10
, "{Control down}{p}{Control up}"					;11
, "{Enter}"]										;12


/*
	   Jupyter lab
		1 -> New cell	2 -> Save		3 -> ()
		4 -> = 			5 -> + 			6 -> *
		7 -> split cell	8 -> /			9 -> ^
		10 -> Search 	11 -> Sqrt()	12 -> Run
*/
Math :=  ["{Escape}b"										;1
, "{Control down}{s}{Control up}"							;2
, "{(}"														;3
, "="														;4
, "{+}"														;5
, "{*}"														;6
, "{Control down}{Shift down}{-}{Shift up}{Control up}" 	;7
, "{/}"														;8
, "{^}"														;9
, "{Control down}{f}{Control up}"							;10
, "sqrt(){Left}"											;11
,"{Control down}{Enter}{Control up}"]						;12


/*
	   Default
		1 -> change window		2 -> Save			3 -> play pause
		4 -> volume down		5 -> mute			6 -> voulume up
		7 -> Minimzie window	8 -> Start menu		9 -> Maximzie window
		10 -> Search			11 -> print			12 -> Enter
*/
Other :=    ["^!{Tab}"					;1
, "{Control down}{s}{Control up}"		;2
, "{Media_Play_Pause}"					;3
, "{Volume_Down}"						;4
, "{Volume_Mute}"						;5
, "{Volume_Up}"							;6
, "{LWin down}{down}{LWin up}"			;7
, "{LWin}"								;8
, "{LWin down}{up}{LWin up}"			;9
, "{Control down}{f}{Control up}"		;10
, "{Control down}{p}{Control up}"		;11
,"{Enter}"]								;12


; Default toggle state
toggle := 0 




; For loop to loop through keyA
for index, value in keysToIndecies
    ; Create hotkeys using the index from the loop
    Hotkey, % "$" index, ToggleSend, On
; End Auto-Execute Section
return


; Label to run when any key is pressed
ToggleSend:
    ; Remove the $* hotkey prefixes using regex
    ; This leaves the key that was pressed
    WinGet, id, ID, A
    WinGetTitle, windowTitle, ahk_id %id%


    chopped := StrSplit(windowTitle , "-" , " ")
    windowTitle := chopped[chopped.MaxIndex()]
	
    ;MsgBox %chopped[2]%
	;MsgBox %windowTitle%

        if(windowTitle = "Autodesk Fusion 360 (Education License)"){
            hotkeysToUse := Fusion
        }
		else if(chopped[1] = "JupyterLab"){
            hotkeysToUse := Math
        }
		else if(windowTitle = "Mozilla Firefox"){
            hotkeysToUse := Firefox
        }
		else if(windowTitle = "Google Chrome"){
            hotkeysToUse := Chrome
        }
		else if(windowTitle = "Visual Studio Code"){
            hotkeysToUse := VSCode
        }
		else if(chopped[1] = "Autodesk Maya 2019"){
            hotkeysToUse := Maya
        }
		else{
            hotkeysToUse := Other
        }

		

        hk  := RegExReplace(A_ThisHotkey, "^\$", "")


        ; If toggle is turned on...
        if (toggle = 1){

			;mathWorks := hotkeysToUse[keysToIndecies[("" hk "")]]
			;MsgBox %mathWorks%

        ; ...use hka s an index to get it's associated key from the array
            ;MsgBox % hotkeysToUse[keysToIndecies[("" hk "")]]
            SendInput, % hotkeysToUse[keysToIndecies[("" hk "")]]

            ;workaround to have ahk replicate a press and hold
            if(hk = 6 && hotkeysToUse = FusionToggles){
                keyWait, 6
		        send, {Shift up}{MButton up}
            }

			if(hk = 6 && hotkeysToUse = MayaToggles){
                keyWait, 6
				send, {Alt up}{LButton up}
            }

			if(hk = 1 && hotkeysToUse = VSToggles){
				keyWait, 1
				send, {Shift up}{Alt up}{LButton up}
			}

        ; If toggle is turned off...
        }Else{
            ; ...send the key you just pressed
            Send, % "{" hk "}"
		}


return

; F4 toggles alt sending
$*F4::
	;run this first so a single press is instant
	toggle := 1 
	KeyWait, F4, T0.15
    if (ErrorLevel = 0)
        sendInput, . ;tap the toggle key to send a period
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


	SetTimer, Multipress, -600 ; Wait for more presses within a 600 millisecond window then run multipress
	return

Multipress:

	if (togglekeyPresses = 2){ ; The key was pressed twice.
		printHotkeyState() ; tell the user if hotkeys are enabled
	}else if (togglekeyPresses = 3){
    	Suspend, Toggle ; enable or disable hotkeys
		printHotkeyState() ; tell the user
	}else if (togglekeyPresses >= 4){
		if(!A_IsSuspended){
    		Send {AltDown}{f4}{AltUp} ;Delete the period and close the window
		}
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



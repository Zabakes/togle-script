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



; Associative array for mapping the keys
keysToIndecies := {"1":1 ,"2":2 ,"3":3 ,"4":4 ,"5":5 ,"6":6 ,"7":7 ,"8":8 ,"9":9 ,"0":10 ,"-":11 ,"Delete":12}


/*
	   fusion 360 keys
		1 -> e for extrude
		2 -> l for line
		3 -> d for dimension
		4 -> c for circle 
		5 -> r for rectangle
		6 -> Shift+middle mouse for camera controls
		7 -> p for project
		8 -> i for inspect/mesure
		9 -> x for normal construction
		0 -> j for joint
		- -> v for visibility toggle
		del -> Enter 
*/
;fusionWindowName = "Autodesk Fusion 360 (Education License)"
FusionToggles  :=  ["e" 
,"l" 
,"d" 
,"c" 
,"r" 
,"{Shift down}{MButton down}" 
,"p" 
,"i" 
,"x" 
,"j" 
,"v" 
,"{Enter}"]


/*
	   firefox keys
		1 -> Xbutton1 for back
		2 -> f5 for refresh
        3 -> Xbutton two for forward
		4 -> ctrl pgup for next tab
		5 -> ctrl t for new tab 
		6 -> ctrl pgdwn for previous tab
		7 -> open google drive in new tab
		8 -> open gmail in new tab
		9 -> open pitt in new tab
		0 -> ctrl f for find in page
		- -> ctrl p for print
		del -> Enter 
*/
;firefoxWindowName = "Mozilla Firefox"
firefoxToggles := ["{XButton1}"
, "{f5}"
,"{XButton2}"
, "{Control down}{PgUp}{Control up}" 
, "{Control down}{t}{Control up}"
, "{Control down}{PgDn}{Control up}"
, "{Control down}{t}{Control up}drive.google.com {enter}"
, "{Control down}{t}{Control up}gmail.com {enter}"
, "{Control down}{t}{Control up}my.pitt.edu {enter}"
, "{Control down}{f}{Control up}"
, "{Control down}{p}{Control up}"
, "{Enter}"]


/*
	   firefox keys
		1 -> Xbutton1 for back
		2 -> f5 for refresh
        3 -> Xbutton two for forward
		4 -> ctrl tab for next tab
		5 -> ctrl t for new tab 
		6 -> ctrl shift tab for previous tab
		7 -> open google drive in new tab
		8 -> open gmail in new tab
		9 -> open pitt in new tab
		0 -> ctrl f for find in page
		- -> ctrl p for print
		del -> Enter 
*/
;chromeWindowName = "Google Chrome"
chromeToggles := ["{XButton1}"
, "{f5}" 
,"{XButton2}"
, "{Control down}{Shift down}{Tab}{Shift up}{Control up}" 
, "{Control down}{t}{Control up}"
, "{Control down}{Tab}{Control up}"
, "{Control down}{t}{Control up}drive.google.com{enter}"
, "{Control down}{t}{Control up}gmail.com{enter}"
, "{Control down}{t}{Control up}my.pitt.edu{enter}"
, "{Control down}{f}{Control up}"
, "{Control down}{p}{Control up}"
, "{Enter}"]


/*
	   default keys
		1 -> Alt tab for changing windows
		2 -> ctrl s for save
        3 -> play pause
		4 -> volume down
		5 -> ctrl t for new tab mute
		6 -> voulume up
		7 -> ctrl shift left to seleft the word to the left
		8 -> windows to open windows key
		9 -> ctrl shift right to select the word to the right
		0 -> ctrl f for find in page
		- -> ctrl p for print
		del -> Enter 
*/
other :=    ["^!{Tab}"
, "{Control down}{s}{Control up}"
, "{Media_Play_Pause}"
, "{Volume_Down}" 
, "{Volume_Mute}"
, "{Volume_Up}"
, "{Control down}{Shift down}{Left}{Shift up}{Control up}"
, "{LWin}", "{Control down}{Shift down}{Right}{Shift up}{Control up}"
, "{Control down}{f}{Control up}"
, "{Control down}{p}{Control up}"
,"{Enter}"]

; Default toggle stateke
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
    ;MsgBox %windowTitle%

        if(windowTitle = "Autodesk Fusion 360 (Education License)"){
            hotkeysToUse := FusionToggles
        }else if(windowTitle = "Mozilla Firefox"){
            hotkeysToUse := firefoxToggles
        }else if(windowTitle = "Google Chrome"){
            hotkeysToUse := chromeToggles
        }else{
            hotkeysToUse := other
        }

        hk  := RegExReplace(A_ThisHotkey, "^\$", "")
       
       
        ; If toggle is turned on...
        if (toggle = 1){
        ; ...use hka s an index to get it's associated key from the array1
            ;MsgBox % hotkeysToUse[keysToIndecies[("" hk "")]]
            SendInput, % hotkeysToUse[keysToIndecies[("" hk "")]]

            ;workaround to have ahk replicate a press and hold
            if(hk = 6 && hotkeysToUse = FusionToggles){
                keyWait, 6
		        send, {Shift up}{MButton up}
            }

        ; If toggle is turned off...
        }Else{
            ; ...send the key you just pressed
            Send, % "{" hk "}"
		}
    
    
return

; F4 toggles alt sending
$*F4::
toggle := 1
KeyWait, F4, T0.15
    if (ErrorLevel = 0)
        sendInput, . ;tap the toggle key to send a period
KeyWait, f4
toggle := 0
return



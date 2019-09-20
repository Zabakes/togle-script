Gui, Add, Text, x450 y10, Window Title:
Gui, Add, Edit, x250 y40 w500 h20 vWindowTitle,

ExistingFiles := ""
Loop, Files, %A_ScriptDir%\Hotkeys\*.*, FR
{
    ExistingFiles .=A_LoopFileName
    ExistingFiles .= "|"
}

Gui, Add, Text, x450 y70, File Name:
Gui, Add, ComboBox, x250 y100 w500 h20 r5 vFileName, %ExistingFiles%


Y = 150
num = 1
Loop, 4
{
X = 75
    loop, 3
    {   
        X += 25
        Gui, Add, Text, x%X% y%Y%, %num%
        Y += 25
        X -= 25
        ;MsgBox, %X% - %Y% - %num%
        Gui, Add, Edit, x%X% y%Y% w250 h30 vB%num%Down,
        Y += 30
        Gui, Add, Edit, x%X% y%Y% w250 h30 vB%num%Up,
        X += 300
        Y -= 55
        num++
    }
    Y+=175
} 
        
Gui, Add, Button, x0 y850 w500 h50 ,Done 
Gui, Add, Button, x500 y850 w500 h50 ,Load
Gui, Show, h900 w1000, New GUI Window 
Return 

ButtonLoad:
    
    num = 1
    loop, 12{
        GuiControl,, B%num%Up, 
        GuiControl,, B%num%Down,
        num++ 
    }

    Gui, Submit, NoHide ;
    FileReadLine, GotWindowTitle, %A_ScriptDir%\Hotkeys\%FileName%, 1
    GuiControl,, WindowTitle, %GotWindowTitle%

    FileReadLine, keysDown, %A_ScriptDir%\Hotkeys\%FileName%, 3
    KeysDownSplit := StrSplit(keysDown, ",", """")
    
    for index, keys in KeysDownSplit{
         GuiControl,, B%index%Down, %keys%
    }

    FileReadLine, keysUp, %A_ScriptDir%\Hotkeys\%FileName%, 5
    if (InStr(keysUp, ",")){
		keysUp := StrSplit(keysUp, ",")
		for index, keys in keysUp{
            MsgBox, %keys%
			keysSplit := StrSplit(keys, ":")
            keyNum := keysSplit[1]
            GuiControl,, B%keyNum%Up, % keysSplit[2]
		}
	}else{
		keysSplit := StrSplit(keysUp, ":")
        keyNum := keysSplit[1]
        GuiControl,, B%keyNum%Up, % keysSplit[2]
	}
*/

Return

ButtonDone:
Gui, Submit, NoHide ; will get ("refresh") all gui variables
HKS = "
HKSU := ""
num = 1
loop, 12{
    HKS .= B%num%down
    HKS .= """"

    if (B%num%up){
        if (InStr(HKSU, ":"))
            HKSU .= ","
        HKSU .= ("" num "")
        HKSU .= ":"       
        HKSU .= B%num%up
    }

    if (num < 12)
    {
        HKS .= ","
        HKS .= """"
    }
    num++
}
if ( InStr( FileName, ".ini")){
    FileDelete, %A_ScriptDir%\Hotkeys\%FileName%
    FileAppend, %WindowTitle%`n`n%HKS%`n`n%HKSU%, %A_ScriptDir%\Hotkeys\%FileName%
}Else{
    FileDelete, %A_ScriptDir%\Hotkeys\%FileName%.ini
    FileAppend, %WindowTitle%`n`n%HKS%`n`n%HKSU%, %A_ScriptDir%\Hotkeys\%FileName%.ini
}

Return 

GuiClose: 
ExitApp
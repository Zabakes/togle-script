


Gui, Add, Text, x450 y10, Window Title:
Gui, Add, Edit, x250 y40 w500 h20 vWindowTitle,
Gui, +resize

ExistingFiles := ""
Loop, Files, %A_ScriptDir%\Hotkeys\*.*, FR
{
    ExistingFiles .=A_LoopFileName
    ExistingFiles .= "|"
}


    Gui, Add, Text, x450 y70, File Name:
    Gui, Add, ComboBox, x250 y100 w500 h20 r5 vFileName, %ExistingFiles%

    Gui, Add, Text, x10 y50, Toggle Key :
    Gui, Add, Edit, x10 y75 w100 h30 vToggleKey
    GuiControl, Hide, ToggleKey
    GuiControl, Hide, Toggle Key :

    Gui, Add, Checkbox, x10 y10 vConfig gToConfig, Config

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

    Gui, Add, Button, x0 y850 w500 h50 ,Save 
    Gui, Add, Button, x500 y850 w500 h50 ,Load
    Gui, Show, h900 w1000, Set your keys, AutoSize

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
    if (!Config){
        if (InStr(keysUp, ",")){
		keysUp := StrSplit(keysUp, ",")
		for index, keys in keysUp{
			keysSplit := StrSplit(keys, ":")
            keyNum := keysSplit[1]
            GuiControl,, B%keyNum%Up, % keysSplit[2]
		}
	    }else{
		    keysSplit := StrSplit(keysUp, ":")
            keyNum := keysSplit[1]
            GuiControl,, B%keyNum%Up, % keysSplit[2]
	    }
    }else{
        KeysUpSplit := StrSplit(keysUp, ",", """")
        for index, keys in KeysUpSplit{
            GuiControl,, B%index%up, %keys%
        }
        FileReadLine, ToggleKey,  %A_ScriptDir%\Hotkeys\%FileName%, 7
        GuiControl,, ToggleKey, % ToggleKey
    }


    Return

ButtonSave:
    Gui, Submit, NoHide ; will get ("refresh") all gui variables
    HKS = "
    if (Config) {
        HKSU = "
    }else{
        HKSU := ""
    }
    num = 1
    loop, 12{
        HKS .= B%num%down
        HKS .= """"

        if (!Config){
            if (B%num%up){
                if (InStr(HKSU, ":"))
                    HKSU .= ","
                HKSU .= ("" num "")
                HKSU .= ":"       
                HKSU .= B%num%up
            }
        }else{
            HKSU .= B%num%up
            HKSU .= """"
            if (num < 12){
                HKSU .= ","
                HKSU .= """"
            }
            }

        if (num < 12)
        {
            HKS .= ","
            HKS .= """"
        }
        num++
    }

    if (Config){
        WindowTitle = Config
    }

    fileContents = %WindowTitle%`n`n%HKS%`n`n%HKSU%

    if (Config){
        fileContents = %fileContents%`n`n%ToggleKey%
    }

    if ( InStr( FileName, ".ini")){
        FileDelete, %A_ScriptDir%\Hotkeys\%FileName%
        FileAppend, %fileContents%, %A_ScriptDir%\Hotkeys\%FileName%
    }Else{
        FileDelete, %A_ScriptDir%\Hotkeys\%FileName%.ini
        FileAppend, %fileContents%, %A_ScriptDir%\Hotkeys\%FileName%.ini
    }

    ExistingFiles := ""
    Loop, Files, %A_ScriptDir%\Hotkeys\*.*, FR
    {
        ExistingFiles .= A_LoopFileName
        ExistingFiles .= "|"
    }
    
    Return 

GuiSize:

    GuiControl, Move, Window Title:, % "x" (2*A_GuiWidth/3-A_GuiWidth/6)/2 "y" 10
    GuiControl, Move, WindowTitle, % "x" (2*A_GuiWidth/3-A_GuiWidth/6)/2 "y" 40 "w" A_GuiWidth/6 "h" 20

    GuiControl, Move, File Name:, % "x" (4*A_GuiWidth/3-A_GuiWidth/6)/2 "y" 10
    GuiControl, Move, FileName, % "x" (4*A_GuiWidth/3-A_GuiWidth/6)/2 "y" 40 "w" A_GuiWidth/6 "h" 150

    Y = 150
    num = 1
    Loop, 4
    {
    X := (A_GuiWidth/3-A_GuiWidth/6)/2
        loop, 3
        {   
            X += A_GuiWidth/12
            GuiControl, Move, %num%, x%X% y%Y%, %num%
            Y += 25
            X -= A_GuiWidth/12
            
            GuiControl, Move, B%num%Down, % "x" X "y" Y "w" A_GuiWidth/6 "h" 30
            Y += 30
            
            GuiControl, Move, B%num%Up,  % "x" X "y" Y "w" A_GuiWidth/6 "h" 30
            
            X += (A_GuiWidth)/3
            Y -= 55
            num++
        }
        Y+= A_GuiHeight/4-50
    } 

    GuiControl, Move, Save, % "x" 0 "y" A_GuiHeight-50 "w" A_GuiWidth/2 h50 ,Save 
    GuiControl, Move, Load, % "x" A_GuiWidth/2 "y" A_GuiHeight-50 "w" A_GuiWidth/2 h50 ,Load
    Return 

Return

ToConfig:
    Gui, Submit, NoHide

    if (Config == 1){
        GuiControl, ChooseString, FileName, Config.ini
        GuiControl,, WindowTitle, Config
        GuiControl, Disabled, WindowTitle
        GuiControl, Disabled, FileName

        GuiControl, Show, ToggleKey
        GuiControl, Show, Toggle Key :
    }else{
        GuiControl, Enabled, WindowTitle
        GuiControl, Enabled, FileName  

        GuiControl, Hide, ToggleKey
        GuiControl, Hide, Toggle Key :      
    }
/*     
    num = 1
    loop, 12{
        if (Config == 1){
            GuiControl, Hide, B%num%Up
            GuiControl, Show, ToggleKey
            GuiControl, Show, Toggle Key :
        }else{
            GuiControl, Show, B%num%Up
            GuiControl, Hide, ToggleKey
            GuiControl, Hide, Toggle Key :
        }
        num++
    } 
*/

Return

GuiClose: 
ExitApp
# togle-script
this uses ahk to toggle the functions of specific keys

This script uses the F4 key to toggle bettween numbers and hotkeys for use on a MM0 mouse it does this based on the active aplication.
  
 Each set of toggled keys is stored in an array in order. the keypresses on the mouse are mapped to the indecies of the array with the "keysToIndecies" linked list.
 A hotkey is set up for each key in the linked list. when the hotkey is pressed the script checks what window is active.
 if there is a toggle array for the active app the script uses that array to define the toggles. otherwise it uses the default toggles
    
   To add aditional apps create another array keep in mind the order of the array matters. The order is how the script knows what to bind to your toggles.
   Next add to the if else tree on line 94. check for when "wintitle" equals the name of the aplication you want to have toggles for. finnaly set "ToggleKeysToUse" to your array.
   if you don't know the name of the aplication uncomment "MsgBox %windowTitle%" on line 93 then hit any key that becomes toggled with the app you want to use as your active application.
   a messege box will pop up with the name of your aplication copy this name exatly into the if else tre e.

Thanks /u/GroggyOtter for helping to make it clean

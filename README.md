# togle-script
this uses ahk to toggle the functions of specific keys

This script uses the F4 key to toggle between numbers and hotkeys for use on a MM0 mouse it does this based on the application your mouse is currently over (it will maker this the active window).
  
Each application has a .ini file in the Hotkeys Folder with it's keymaps on them

line 1 of this file is the applications name as it appears to AHK
Line 3 of this file has all array of all the hotkeys that this application will send on a keypress
line 5 of this file has all the keys to send on key release

to add applications run the hotkey setter script and fill in the values for each input. this will generate an .ini file for you. The top box is keys to send on press and the lower is on release.
run this same script and pick from the dropdown to re-write an existing file **THIS WILL OVERWRITE THE ENTIRE FILE** so make sure to fill in all your hotkeys. you can load hotkeys by selecting the file from the dropdown and hitting load.


Thanks /u/GroggyOtter for helping to make it clean

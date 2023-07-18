# toggle-script

# What is this script
This program does 2 things:

- One of the things it does is add a layer behind a "toggle key" to a set of keys that can be configured based on the active application.

- The other thing the script does is create a pop-up to show what a key will do when the toggle is being held. 

This script currently only works on windows. This isn't ideal but none of this code is "ideal". It's quick and dirty and it evolved from a much simpler script. To be robust and ready for non-technical users the code will probably need to be re-factored. I'm releasing this to see if it's features are something other people like. If so I'll work on increasing the code quality and supporting other features. 

# Use

By default pressing the toggle key is brings up a window like this ![GUI example](Images\GUI_example.png)  
You can change where the keys go with the [layout](#layout--path)

Right clicking on a key allows you to edit the json associated with that key. You can then click escape to discard the changes or ctrl+s to save the changes. 
![GUI example edit](Images\GUI_edit.png) 
# Configuration

The script is designed to be highly configurable. There are 3 configurable parts of the script.

## Configuring the keys being re-mapped (Config.json)
The keys that are used by the script are configured in config.json. If an option does not have a default it is required.

The attributes in config.json are as follows:

### Keys : list[Key]
This is a list of all the keys to be re-mapped. The order of the list should match the order of the [hks](#hks--listaction--listlistaction) Each key has the following attributes.  

--- Start Key obj attributes ---
#### remap : str
This is the key to re-map.

#### baseLayer : [action](#actions--obj)
This is an [action](#actions--obj) to take when the key is pressed without the toggle key.

Example :

    "keys":[
        {
            "remap": "foo",   
            "baseLayer" : {  
                "press" : "bar"  
            }  
        },
        ...
    ],
This makes it so that when 'foo' is pressed 'bar' is sent.  

--- End key obj attributes---

### toggleKey : str
This is the key that activates the GUI and the application specific keymap.

### doRemapping : bool
Should the script re-map the keys listed in keys based on an application. The toggle key is still modified.

Default - true

### drawGUI : bool
Should the script show use resources to show a GUI when the toggle key is held. 

Default - true

### layout : path
This is the path the keyboard layout json. This does not support rotation. The layout can be generated/downloaded from [here](http://www.keyboard-layout-editor.com/#/) (This is not my work but it's cool so I used the same format). The legends in this layout should match the [remap](#remap--str) name.

Default - "Layouts\keyboard-layout-4.json"

### ToggleActions : obj
It would be a shame to waste a key. ToggleActions allows actions to be configured for when the toggle key is pressed without pressing an action key.  

--- Start ToggleActions attributes  ---
#### tap : [action](#actions--obj)
This is the action to take when the toggle key is tapped and released without pressing another key.

#### tap : [action](#actions--obj)
This is the action to take when the toggle key is held and then released without pressing another key.  
   
--- End ToggleActions attributes  --- 

### Funcs : List[obj]

These are the prefixes for use in [actions](#actions--obj) using these prefixes actions can invoke pyhton functions defined in the customFuncs module. each object should contain :  

--- start function attributes ---
#### prefix : char
This is the prefix for the function action beginning with this character will be mapped to the ... 

#### function : str
This is the name of the python function to be called. The argument to this function is whatever follows th 
--- end function attributes ---

## Application specific configs

### appName : str

This is the name of the application that this config applies to. This takes priority over the [regex](#regex--str). 

### regex : str
Regex to match with the full window title.

### priority : int
This is the priority for the regex. This is the priority for the regex match. If multiple regex patterns match the map with the higher priority will be applied.  


### hks : list[[action](#actions--obj)] | list[list[[action](#actions--obj)]]
This is a list of actions to map to the keys to the keys specified in [Keys](#keys--listkey), this is done based on index. If a list of actions is used instead of an action those actions will be added to layers. The default layer is the first entry. 

You can create an action to set/change the current layer by invoking the [setLayer](#setLayer) [function](#Function--obj).

default : Use the actions in the map with the name "default"

## Common configs

## Actions : obj 
Actions are the object that define what a key will do. Actions have the following attributes.

--- Start actions attributes  --- 

### Press : [Function](#Function--obj) | [command](#command--str)
This is what happens when the key is pressed. It can be either a function or a command.

default : Nothing

### Rel : [Function](#Function--obj) | [command](#command--str)
This is what happens when the key is released. It can be either a function or a command.

default : Nothing

### icon path
This is an image to be displayed on the GUI when this layer is active. This will be displayed if it present otherwise use the description.

default : No image use the description

### description : str
This is a description to be displayed on the GUI when this layer is active. This will only be displayed if no icon is specified.

default : Raw json for the actions

--- End actions attributes  --- 

### Function : obj

This is a function call to a python function with named arguments.

Example :

    {
    "function" : "foo",
    "args" : {
        "type" :"set",
        "val": 2
        }
    }

    is equivalent to a call foo(type="set", val=2)

### Command : str
A command to send when it is parsed using the regex :  
`(?<!\\){(?P<cmd>.*?)((?P<down> down)|(?P<up> up))?(?<!\\)}|(?P<str>[^\{]+)`

For each match in the command. 
-If the string group matches send that string.
-If the cmd group matches check for a prefix from [Funcs](#funcs--listobj) if it is present strip it and pass the rest of the command to the function as a string.
    -If the down group matches press and hold the specified key until it is released with an up group
    -If the up group matches release the specified key

Example :

    {
        "press": "{Shift down}",
        "rel": "{Shift up}",
        "description": "rotate camera"
    }

This presses shift when the key is pressed and releases it when the associated key is released


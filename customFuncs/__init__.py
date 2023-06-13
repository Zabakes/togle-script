from subprocess import run as runReal
import re
from tokenize import group

parse = re.compile(r""""?(?P<cmd>.*\.exe|.*\.ahk?)"?(?P<args>.*)""")

def run(s):
    match = re.search(parse, s)
    if (args := match.group("args")):
        args = [m.group(0).strip("\"") for m in re.finditer(r"""(\".+?\")|([^\"\s]+)""", args)]
    else:
        args = []

    if match.group("cmd").endswith(".ahk"):
        cmd = f"""C:\Program Files\AutoHotkey\AutoHotkey.exe"""
        args.insert(0, match.group("cmd"))
    else:
        cmd = match.group("cmd")

    print([cmd, *args])
    try:
        runReal([cmd, *args])
    except:
        pass
    
    print("Done")
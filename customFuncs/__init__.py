from subprocess import run as runReal
import re
from tokenize import group

parse = re.compile(r""""?(?P<cmd>.*\.exe?)"?(?P<args>.*)""")

def run(s):
    match = re.search(parse, s)
    if (args := match.group("args")):
        args = args.split()
    else:
        args = []

    runReal([match.group("cmd"), *args])
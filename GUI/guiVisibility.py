import common

def hideGUI():
    if not common.isEditing:
        common.showGUI.clear()
        
def showGUI():
    common.redrawGui
    if not common.disableGUI:
        common.showGUI.set()

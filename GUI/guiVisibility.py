import common

def hideGUI():
    if not common.isEditing:
        common.showGUI.clear()
        
def showGUI():
    if common.getAppName() in common.disabledApps:
        return

    common.redrawGui = True
    if not common.disableGUI:
        common.showGUI.set()

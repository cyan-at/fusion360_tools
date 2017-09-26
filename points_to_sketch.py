import adsk.core
import adsk.fusion
import traceback

import os
import sys
sys.path.append(os.path.dirname(__file__))
from itertools import chain

IDEAL_NOTCH_WIDTH = 4
# global set of event handlers to keep them referenced for the duration of the command
handlers = []
app = adsk.core.Application.get()
if app:
    ui = app.userInterface
    product_units_mgr = app.activeProduct.unitsManager

def add_points(component):
    sketch = component.sketches.add(component.xYConstructionPlane)
    all_points = {
        '230,260': [230.238, 260.281],
        '238,279': [238.73, 279.504],
        '252,248': [252.973, 248.219],
        '271,254': [271.637, 254.676],
        '307,242': [307.027, 242.738],
        '308,321': [308.41, 321.383],
        '317,282': [317.516, 282.176],
        '318,343': [318.281, 343.078],
        '338,207': [338.883, 207.203],
        '345,290': [345.535, 290.27]}
    for p in all_points:
        point = all_points[p]
        adsk_point = adsk.core.Point3D.create(point[0], point[1], 0)
        ret = sketch.sketchPoints.add(adsk_point)

class BoxMakerCommandExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            command = args.firingEvent.sender
            design = app.activeProduct
            if not design:
                ui.messageBox('No active Fusion design', 'No Design')
                return
            component = design.rootComponent
            unitsMgr = design.unitsManager
            add_points(component)
            args.isValidResult = True
        except:
            if ui:
                ui.messageBox(
                    'Failed:\n{}'.format(traceback.format_exc()))
class BoxMakerCommandDestroyHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
class BoxMakerCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = args.command
            onExecute = BoxMakerCommandExecuteHandler()
            onDestroy = BoxMakerCommandDestroyHandler()
            cmd.execute.add(onExecute)
            cmd.destroy.add(onDestroy)
            # keep the handler referenced globally
            handlers.append(onExecute)
            handlers.append(onDestroy)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def main():
    try:
        commandId = 'points_to_sketch'
        commandName = 'points_to_sketch'
        commandDescription = 'Create boxes with notched box-joint panels.'
        cmdDef = ui.commandDefinitions.itemById(commandId)
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition(
                commandId,
                commandName,
                commandDescription,
                './resources'
            )

        onCommandCreated = BoxMakerCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)

        # keep the handler referenced globally
        handlers.append(onCommandCreated)

        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        # prevent this module from being terminated when the script returns,
        # because we are waiting for event handlers to fire
        adsk.autoTerminate(False)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

main()
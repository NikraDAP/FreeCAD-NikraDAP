# ********************************************************************************
# *                                                                              *
# *   This program is free software; you can redistribute it and/or modify       *
# *   it under the terms of the GNU Lesser General Public License (LGPL)         *
# *   as published by the Free Software Foundation; either version 3 of          *
# *   the License, or (at your option) any later version.                        *
# *   for detail see the LICENCE text file.                                      *
# *                                                                              *
# *   This program is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of             *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                       *
# *   See the GNU Library General Public License for more details.               *
# *                                                                              *
# *   You should have received a copy of the GNU Library General Public          *
# *   License along with this program; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston,                      *
# *   MA 02111-1307, USA                                                         *
# *_____________________________________________________________________________ *
# *                                                                              *
# *        ##########################################################            *
# *       #### Nikra-DAP FreeCAD WorkBench Revision 2.0 (c) 2023: ####           *
# *        ##########################################################            *
# *                                                                              *
# *                     Authors of this workbench:                               *
# *                   Cecil Churms <churms@gmail.com>                            *
# *             Lukas du Plessis (UP) <lukas.duplessis@up.ac.za>                 *
# *                                                                              *
# *               This file is a sizeable expansion of the:                      *
# *                "Nikra-DAP-Rev-1" workbench for FreeCAD                       *
# *        with increased functionality and inherent code documentation          *
# *                  by means of expanded variable naming                        *
# *                                                                              *
# *     Which in turn, is based on the MATLAB code Complementary to              *
# *                  Chapters 7 and 8 of the textbook:                           *
# *                                                                              *
# *                     "PLANAR MULTIBODY DYNAMICS                               *
# *         Formulation, Programming with MATLAB, and Applications"              *
# *                          Second Edition                                      *
# *                         by P.E. Nikravesh                                    *
# *                          CRC Press, 2018                                     *
# *                                                                              *
# *     Authors of Rev-1:                                                        *
# *            Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>         *
# *            Lukas du Plessis (UP) <lukas.duplessis@up.ac.za>                  *
# *            Dewald Hattingh (UP) <u17082006@tuks.co.za>                       *
# *            Varnu Govender (UP) <govender.v@tuks.co.za>                       *
# *                                                                              *
# * Copyright (c) 2023 Cecil Churms <churms@gmail.com>                           *
# * Copyright (c) 2023 Lukas du Plessis (UP) <lukas.duplessis@up.ac.za>          *
# * Copyright (c) 2022 Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za> *
# * Copyright (c) 2022 Dewald Hattingh (UP) <u17082006@tuks.co.za>               *
# * Copyright (c) 2022 Varnu Govender (UP) <govender.v@tuks.co.za>               *
# *                                                                              *
# *             Please refer to the Documentation and README for                 *
# *         more information regarding this WorkBench and its usage              *
# *                                                                              *
# ********************************************************************************
import FreeCAD as CAD
import numpy as np

from os import path
from math import degrees

import DapToolsMod as DT
if CAD.GuiUp:
    import FreeCADGui as CADGui
    from PySide import QtGui, QtCore
global Debug
Debug = False
# =============================================================================
class CommandDapAnimationC:
    if Debug:
        DT.Mess("CommandDapAnimationC-CLASS")
    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by FreeCAD when 'CADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""
        if Debug:
            DT.Mess("CommandDapAnimationC-GetResourcesC")

        return {
            "Pixmap": path.join(DT.getDapModulePath(), "icons", "Icon8n.png"),
            "MenuText": QtCore.QT_TRANSLATE_NOOP("DapAnimationAlias", "Animate solution"),
            "ToolTip": QtCore.QT_TRANSLATE_NOOP("DapAnimationAlias", "Animates the motion of the moving bodies"),
        }
    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if there are already some results stored in the solver object
        i.e. Determine if the animate command/icon must be active or greyed out"""
        if Debug:
            DT.Mess("CommandDapAnimationC-IsActive")

        # Look for the results valid flag in the DapSolver object
        activeContainer = DT.getActiveContainerObject()
        for groupMember in activeContainer.Group:
            if "DapSolver" in groupMember.Name:
                self.solverObj = groupMember
                return groupMember.DapResultsValid
        # Return False if we didn't find a DapSolver object at all
        return False
    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Animation command is run"""
        if Debug:
            DT.Mess("CommandDapAnimationC-Activated")

        # Get the identity of the DAP document
        # (which is the active document on entry)
        self.dapDocument = CAD.ActiveDocument

        # Find the ground object name in the container
        containerObj = DT.getActiveContainerObject()
        groundName = containerObj.groundBodyName

        # Set an existing "Animation" document active
        # or create it if it does not exist yet
        if "Animation" in CAD.listDocuments():
            CAD.setActiveDocument("Animation")
        else:
            CAD.newDocument("Animation")
        self.animationDocument = CAD.ActiveDocument

        # Add the ground object to the animation view (and forget about it)
        groundObj = self.dapDocument.findObjects(Name="^" + groundName + "$")[0]
        animObj = self.animationDocument.addObject("Part::FeaturePython", ("Ani_" + groundName))
        animObj.Shape = groundObj.Shape
        if CAD.GuiUp:
            ViewProviderDapAnimateC(animObj.ViewObject)

        # Generate the list of bodies to be animated and
        # create an object for each, with their shapes, in the animationDocument
        animationIndex = 0
        for bodyName in self.solverObj.BodyNames:
            bodyObj = self.dapDocument.findObjects(Name="^"+bodyName+"$")[0]
            
            animObj = self.animationDocument.addObject("Part::FeaturePython", ("Ani_"+bodyName))
            # Add the shape to the newly created object
            animObj.Shape = bodyObj.Shape
            # Instantiate the class to handle the Gui stuff
            if CAD.GuiUp:
                ViewProviderDapAnimateC(animObj.ViewObject)

        # Request the animation window zoom to be set to fit the entire system
        CADGui.SendMsgToActiveView("ViewFit")

        # Edit the parameters by calling the task dialog
        taskd = TaskPanelDapAnimateC(
            self.solverObj,
            self.dapDocument,
            self.animationDocument,
        )
        CADGui.Control.showDialog(taskd)
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("CommandDapAnimC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("CommandDapAnimC-__setstate__")
# =============================================================================
class ViewProviderDapAnimateC:
    """ A view provider for the DapAnimate container object """
    # -------------------------------------------------------------------------------------------------
    def __init__(self, vobj):
        vobj.Proxy = self
    # -------------------------------------------------------------------------------------------------
    def getIcon(self):
        icon_path = path.join(DT.getDapModulePath(), "Gui", "Resources", "icons", "Icon2n.png")
        return icon_path
    # -------------------------------------------------------------------------------------------------
    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
        self.bubbles = None
    # -------------------------------------------------------------------------------------------------
    def updateData(self, obj, prop):
        return
    # -------------------------------------------------------------------------------------------------
    def onChanged(self, vobj, prop):
        return
    # -------------------------------------------------------------------------------------------------
    def doubleClicked(self, vobj):
        if not DT.getActiveAnalysis() == self.Object:
            if FreeCADGui.activeWorkbench().name() != 'DapWorkbench':
                FreeCADGui.activateWorkbench("DapWorkbench")
            DT.setActiveAnalysis(self.Object)
            return True
        return True
    # -------------------------------------------------------------------------------------------------
    def __getstate__(self):
        return None
    # -------------------------------------------------------------------------------------------------
    def __setstate__(self, state):
        return None
# =============================================================================
class TaskPanelDapAnimateC:
    """Taskpanel for Running an animation"""
    if Debug:
        DT.Mess("TaskPanelDapAnimateC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(
        self,
        solverObj,
        dapDocument,
        animationDocument,
    ):
        """Run on first instantiation of a TaskPanelDapAnimate class"""
        if Debug:
            DT.Mess("TaskPanelDapAnimateC-__init__")

        # Here we get the list of objects from the animation document
        self.animationBodyObjects = CAD.ActiveDocument.Objects

        # Transfer the called parameters to the instance variables
        self.solverObj = solverObj
        self.dapDocument = dapDocument
        self.animationDocument = animationDocument

        # Set play back period to mid-range
        self.playBackPeriod = 100  # msec

        # Load the Dap Animate ui form
        uiPath = path.join(path.dirname(__file__), "TaskPanelDapAnimate.ui")
        self.form = CADGui.PySideUic.loadUi(uiPath)

        # Define callback functions when changes are made in the dialog
        self.form.horizontalSlider.valueChanged.connect(self.moveObjects)
        self.form.startButton.clicked.connect(self.playStart)
        self.form.stopButton.clicked.connect(self.stopStop)
        self.form.playSpeed.valueChanged.connect(self.changePlaySpeed)

        # Fetch the animation object for all the bodies and place in a list
        self.animationBodyObj = []
        for animationBodyName in self.solverObj.BodyNames:
            self.animationBodyObj.append(self.animationDocument.findObjects(Name="^Ani_"+animationBodyName+"$")[0])

        # Load the calculated values of positions/angles from the results file
        self.Positions = np.loadtxt(path.join(self.solverObj.Directory, "DapAnimation.csv"))
        self.nTimeSteps = len(self.Positions.T[0])

        # Positions matrix is:
        # timeValue : body1X body1Y body1phi : body2X body2Y body2phi : ....
        # next time tick

        # Shift all the values relative to the starting point of each body
        startTick = self.Positions[0, :]
        self.startX = []
        self.startY = []
        self.startPhi = []
        for animationIndex in range(len(self.solverObj.BodyNames)):
            self.startX.append(startTick[animationIndex * 3 + 1])
            self.startY.append(startTick[animationIndex * 3 + 2])
            self.startPhi.append(startTick[animationIndex * 3 + 3])
        for tick in range(self.nTimeSteps):
            thisTick = self.Positions[tick, :]
            for animationIndex in range(len(self.solverObj.BodyNames)):
                thisTick[animationIndex * 3 + 1] -= self.startX[animationIndex]
                thisTick[animationIndex * 3 + 2] -= self.startY[animationIndex]
                thisTick[animationIndex * 3 + 3] -= self.startPhi[animationIndex]
            self.Positions[tick, :] = thisTick

        # Set up the timer parameters
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.playBackPeriod)
        self.timer.timeout.connect(self.onTimerTimeout)  # callback function after each tick

        # Set up the values displayed on the dialog
        self.form.horizontalSlider.setRange(0, self.nTimeSteps - 1)
        self.form.timeStepLabel.setText("0.000s of {0:5.3f}s".format(self.solverObj.TimeLength))

    #  -------------------------------------------------------------------------
    def reject(self):
        """Run when we press the Close button
        Closes document and sets the active document
        back to the solver document"""
        if Debug:
            DT.Mess("TaskPanelDapAnimateC-reject")

        CADGui.Control.closeDialog()
        CAD.closeDocument(self.animationDocument.Name)
        CAD.setActiveDocument(self.dapDocument.Name)
    #  -------------------------------------------------------------------------
    def getStandardButtons(self):
        """Set up button attributes for the dialog ui"""
        if Debug:
            DT.Mess("TaskPanelDapAnimateC-getStandardButtons")
        return 0x00200000
    #  -------------------------------------------------------------------------
    def playStart(self):
        """Start the Qt timer when the play button is pressed"""
        if Debug:
            DT.Mess("TaskPanelDapAnimateC-playStart")

        self.timer.start()
    #  -------------------------------------------------------------------------
    def stopStop(self):
        """Stop the Qt timer when the stop button is pressed"""
        if Debug:
            DT.Mess("TaskPanelDapAnimateC-stopStop")

        self.timer.stop()
    #  -------------------------------------------------------------------------
    def onTimerTimeout(self):
        """Increment the tick position in the player, looping, if requested"""
        if Debug:
            DT.Mess("TaskPanelDapAnimateC-onTimerTimeout")

        tickPosition = self.form.horizontalSlider.value()
        tickPosition += 1
        if tickPosition >= self.nTimeSteps:
            if self.form.loopCheckBox.isChecked():
                tickPosition: int = 0
            else:
                self.timer.stop()

        # Update the slider in the dialog
        self.form.horizontalSlider.setValue(tickPosition)
    #  -------------------------------------------------------------------------
    def changePlaySpeed(self, newSpeed):
        """Alter the playback period by a factor of 1/newSpeed"""
        if Debug:
            DT.Mess("TaskPanelDapAnimateC-changePlaySpeed")

        self.timer.setInterval(self.playBackPeriod * (1.0 / newSpeed))
    #  -------------------------------------------------------------------------
    def moveObjects(self, tick):
        """Move all the bodies to their pose at this clock tick"""
        if Debug:
            DT.Mess("TaskPanelDapAnimateC-moveObjects")

        self.form.timeStepLabel.setText(
            "{0:5.3f}s of {1:5.3f}s".format(
                tick * self.solverObj.DeltaTime,
                self.solverObj.TimeLength
            )
        )

        thisTick = self.Positions[tick, :]
        for animationIndex in range(len(self.solverObj.BodyNames)):
            X = thisTick[animationIndex*3 + 1]
            Y = thisTick[animationIndex*3 + 2]
            Phi = thisTick[animationIndex*3 + 3]
            self.animationBodyObj[animationIndex].Placement = CAD.Placement(CAD.Vector(X, Y, 0.0),
                                                                            CAD.Rotation(CAD.Vector(0.0, 0.0, 1.0),degrees(Phi)),
                                                                            CAD.Vector(self.startX[animationIndex],
                                                                                       self.startY[animationIndex],
                                                                                       0.0))
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("TaskPanelDapAnimationC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("TaskPanelDapAnimationC-__setstate__")
# =============================================================================

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

from os import path
from math import sin, cos, tan, asin, acos, atan, tanh, degrees, pi

import DapToolsMod as DT
if CAD.GuiUp:
    import FreeCADGui as CADGui
    from PySide import QtGui, QtCore
    import Part
    from pivy import coin
global Debug
Debug = False
#  ----------------------------------------------------------------------------
def makeDapForce(name="DapForce"):
    """Create an empty Force Object"""
    if Debug:
        DT.Mess("makeDapFor")

    forceObject = CAD.ActiveDocument.addObject("Part::FeaturePython", name)
    DapForceC(forceObject)
    if CAD.GuiUp:
        ViewProviderDapForceC(forceObject.ViewObject)

    return forceObject
# =============================================================================
class CommandDapForceC:
    if Debug:
        DT.Mess("CommandDapForceC-CLASS")
    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by CAD when 'CADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""
        if Debug:
            DT.Mess("CommandDapForceC-GetResources")

        return {
            "Pixmap": path.join(DT.getDapModulePath(), "icons", "Icon6n.png"),
            "MenuText": QtCore.QT_TRANSLATE_NOOP("DapForceAlias", "Add Force"),
            "ToolTip": QtCore.QT_TRANSLATE_NOOP("DapForceAlias", "Creates and defines a force for the DAP analysis"),
        }
    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out
        Only activate it when there is at least one body defined"""
        if Debug:
            DT.Mess("CommandDapForceC-IsActive(query)")

        return len(DT.getDictionary("DapBody")) > 1
    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Force Selection command is run"""
        if Debug:
            DT.Mess("CommandDapForceC-Activated")

        # This is where we create a new empty Dap Force object
        activeContainer = DT.getActiveContainerObject()
        activeContainer.addObject(makeDapForce())
        # Switch on the Task Dialog
        CADGui.ActiveDocument.setEdit(CAD.ActiveDocument.ActiveObject.Name)
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("TaskPanelDapForceC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("TaskPanelDapForceC-__setstate__")
# =============================================================================
class DapForceC:
    if Debug:
        DT.Mess("DapForceC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(self, forceObject):
        """Initialise an instantiation of a new force object"""
        if Debug:
            DT.Mess("DapForceC-__init__")

        # Initialise all the properties in the force object
        # Call a separate function to do this so we can reuse it
        # when we restore the document
        self.initProperties(forceObject)

        forceObject.Proxy = self
    #  -------------------------------------------------------------------------
    def initProperties(self, forceObject):
        """Initialse all the properties of the force object"""
        if Debug:
            DT.Mess("DapForceC-initProperties")

        DT.addObjectProperty(forceObject, "actuatorType", 0, "App::PropertyInteger", "", "Types of actuators/forces")

        DT.addObjectProperty(forceObject, "bodyHEADName", "", "App::PropertyString", "", "Name of the head body")
        DT.addObjectProperty(forceObject, "bodyHEADLabel", "", "App::PropertyString", "", "Label of the head body")
        DT.addObjectProperty(forceObject, "bodyHEADindex", 0, "App::PropertyInteger", "", "Index of the head body in the NumPy array")

        DT.addObjectProperty(forceObject, "bodyTAILName", "", "App::PropertyString", "", "Name of the tail body")
        DT.addObjectProperty(forceObject, "bodyTAILLabel", "", "App::PropertyString", "", "Label of the tail body")
        DT.addObjectProperty(forceObject, "bodyTAILindex", 0, "App::PropertyInteger", "", "Index of the tail body in the NumPy array")

        DT.addObjectProperty(forceObject, "pointHEADName", "", "App::PropertyString", "", "Name of the head point of the force")
        DT.addObjectProperty(forceObject, "pointHEADLabel", "", "App::PropertyString", "", "Label of the head point of the force")
        DT.addObjectProperty(forceObject, "pointHEADindex", 0, "App::PropertyInteger", "", "Index of the head of the force in the NumPy array")

        DT.addObjectProperty(forceObject, "pointTAILName", "", "App::PropertyString", "", "Name of the tail point of the force")
        DT.addObjectProperty(forceObject, "pointTAILLabel", "", "App::PropertyString", "", "Label of the tail point of the force")
        DT.addObjectProperty(forceObject, "pointTAILindex", 0, "App::PropertyInteger", "", "Index of the tail of the force in the NumPy array")

        DT.addObjectProperty(forceObject, "unitLocal", CAD.Vector(), "App::PropertyVector", "UnitVector", "Xi and Eta coordinates of unit vector")
        DT.addObjectProperty(forceObject, "unitWorld", CAD.Vector(), "App::PropertyVector", "UnitVector", "World placement of unit vector")
        DT.addObjectProperty(forceObject, "unitWorldDot", CAD.Vector(), "App::PropertyVector", "UnitVector", "Unit Vector Velocity in world coordinates")

        DT.addObjectProperty(forceObject, "Stiffness", 0.0, "App::PropertyFloat", "", "Spring Stiffness")
        DT.addObjectProperty(forceObject, "Value0", 0.0, "App::PropertyFloat", "", "Undeformed Length/Angle")
        DT.addObjectProperty(forceObject, "DampingCoeff", 0, "App::PropertyFloat", "", "Damping coefficient")
        DT.addObjectProperty(forceObject, "forceActuator", 0.0, "App::PropertyFloat", "", "Constant actuator force")
        DT.addObjectProperty(forceObject, "torqueActuator", 0.0, "App::PropertyFloat", "", "Constant actuator torque")
        DT.addObjectProperty(forceObject, "localForce", CAD.Vector(), "App::PropertyVector", "", "Constant force in local frame")
        DT.addObjectProperty(forceObject, "constForce", CAD.Vector(), "App::PropertyVector", "", "Constant force in x-y frame")
        DT.addObjectProperty(forceObject, "constTorque", 0.0, "App::PropertyFloat", "", "Constant torque in x-y frame")
    #  -------------------------------------------------------------------------
    def onDocumentRestored(self, forceObject):
        if Debug:
            DT.Mess("DapForceC-onDocumentRestored")

        self.initProperties(forceObject)
    #  -------------------------------------------------------------------------
    def onChanged(self, forceObject, propertee):
        # if Debug:
        #    DT.Mess("DapForceC-onChanged")
        return
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("DapForceC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("DapForceC-__setstate__")
# =============================================================================
class ViewProviderDapForceC:
    if Debug:
        DT.Mess("ViewProviderDapForceC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(self, forceViewObject):
        if Debug:
            DT.Mess("ViewProviderDapForceC-__init__")
        forceViewObject.Proxy = self
    #  -------------------------------------------------------------------------
    def getIcon(self):
        if Debug:
            DT.Mess("ViewProviderDapForceC-getIcon")

        iconPath = path.join(DT.getDapModulePath(), "icons", "Icon6n.png")

        return iconPath
    #  -------------------------------------------------------------------------
    def attach(self, forceViewObject):
        if Debug:
            DT.Mess("ViewProviderDapForceC-attach")
        self.forceViewObject = forceViewObject
        self.forceViewObjectObject = forceViewObject.Object
        self.standard = coin.SoGroup()
        forceViewObject.addDisplayMode(self.standard, "Standard")
    #  -------------------------------------------------------------------------
    def getDisplayModes(self, forceViewObject):
        """Return an empty list of modes when requested"""
        if Debug:
            DT.Mess("ViewProviderDapForceC-getDisplayModes")
        return []
    #  -------------------------------------------------------------------------
    def getDefaultDisplayMode(self):
        if Debug:
            DT.Mess("ViewProviderDapForceC-getDefaultDisplayMode")
        return "Flat Lines"
    #  -------------------------------------------------------------------------
    def setDisplayMode(self, mode):
        if Debug:
            DT.Mess("ViewProviderDapForceC-setDisplayMode")
        return mode
    #  -------------------------------------------------------------------------
    def updateData(self, forceViewObject, prop):
        # if Debug:
        # DT.Mess("ViewProviderDapForceC-updateData")
        return
    #  -------------------------------------------------------------------------
    def doubleClicked(self, viewobj):
        if Debug:
            DT.Mess("ViewProviderDapForceC-doubleClicked")

        Document = CADGui.getDocument(self.forceViewObjectObject.Document)
        if not Document.getInEdit():
            Document.setEdit(self.forceViewObjectObject.Name)
        else:
            CAD.Console.PrintError("Task dialog already active\n")
        return True
    #  -------------------------------------------------------------------------
    def setEdit(self, forceViewObject, mode):
        """Edit the parameters by calling the task dialog"""
        if Debug:
            DT.Mess("ViewProviderDapForceC-setEdit")
        taskDialog = TaskPanelDapForceC(self.forceViewObjectObject)
        CADGui.Control.showDialog(taskDialog)
        return True
    #  -------------------------------------------------------------------------
    def unsetEdit(self, forceViewObject, mode):
        if Debug:
            DT.Mess("ViewProviderDapForceC-unsetEdit")
        CADGui.Control.closeDialog()
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("ViewProviderDapForceC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("ViewProviderDapForceC-__setstate__")
# =============================================================================
class TaskPanelDapForceC:
    """Taskpanel for adding DAP Force"""
    if Debug:
        DT.Mess("TaskPanelDapForceC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(self, forceTaskObject):
        """Run on first instantiation of a TaskPanelDapForce class"""
        if Debug:
            DT.Mess("TaskPanelDapForceC-__init__")

        self.forceTaskObject = forceTaskObject
        forceTaskObject.Proxy = self

        # Load up the task panel layout definition
        uiPath = path.join(path.dirname(__file__), "TaskPanelDapForces.ui")
        self.form = CADGui.PySideUic.loadUi(uiPath)

        # Set up the force/actuator combobox
        self.form.actuatorCombo.clear()
        self.form.actuatorCombo.addItems(DT.FORCE_TYPE)
        self.form.actuatorCombo.setCurrentIndex(self.forceTaskObject.actuatorType)
        self.form.actuatorCombo.currentIndexChanged.connect(self.actuatorChangedCallbackF)
        self.actuatorChangedCallbackF()

        # Copy the state of the variables from the existing Force object to the form
        containerObject = DT.getActiveContainerObject()
        if containerObject.gravityVector.x != 0.0:
            self.form.gravityX.setChecked(True)
        if containerObject.gravityVector.y != 0.0:
            self.form.gravityY.setChecked(True)
        if containerObject.gravityVector.z != 0.0:
            self.form.gravityZ.setChecked(True)

        self.form.linSpringLength.setValue(self.forceTaskObject.Value0)
        self.form.linSpringStiffness.setValue(self.forceTaskObject.Stiffness)
        self.form.rotSpringAngle.setValue(self.forceTaskObject.Value0)
        self.form.rotSpringStiffness.setValue(self.forceTaskObject.Stiffness)
        self.form.linSpringDamp.setValue(self.forceTaskObject.DampingCoeff)
        self.form.linSpringDampLength.setValue(self.forceTaskObject.Value0)
        self.form.linSpringDampStiffness.setValue(self.forceTaskObject.Stiffness)
        self.form.rotSpringDamp.setValue(self.forceTaskObject.DampingCoeff)
        self.form.rotSpringDampAngle.setValue(self.forceTaskObject.Value0)
        self.form.rotSpringDampStiffness.setValue(self.forceTaskObject.Stiffness)
        
        # Populate the body object list
        self.bodyObjDict = DT.getDictionary("DapBody")

        # Add the list of possible bodies to both the head and the tail list in the form
        self.bodyLabels = []
        self.bodyNames = []
        for bodyName in self.bodyObjDict:
            bodyObj = self.bodyObjDict[bodyName]
            self.bodyLabels.append(bodyObj.Label)
            self.bodyNames.append(bodyObj.Name)

        self.form.bodyLabelOneTwo.clear()
        self.form.bodyLabelOneTwo.addItems(self.bodyLabels)

        self.form.bodyHeadLabelTwoOne.clear()
        self.form.bodyHeadLabelTwoOne.addItems(self.bodyLabels)
        self.form.bodyTailLabelTwoOne.clear()
        self.form.bodyTailLabelTwoOne.addItems(self.bodyLabels)

        self.form.bodyHeadLabelTwoTwo.clear()
        self.form.bodyHeadLabelTwoTwo.addItems(self.bodyLabels)
        self.form.bodyTailLabelTwoTwo.clear()
        self.form.bodyTailLabelTwoTwo.addItems(self.bodyLabels)

        # Set defaults in the force object if we don't have a value yet
        if self.forceTaskObject.bodyHEADName == "":
            for bodyName in self.bodyObjDict:
                bodyObj = self.bodyObjDict[bodyName]
                self.forceTaskObject.bodyHEADName = bodyObj.Name
                self.forceTaskObject.bodyTAILName = bodyObj.Name
                self.forceTaskObject.bodyHEADLabel = bodyObj.Label
                self.forceTaskObject.bodyTAILLabel = bodyObj.Label
                break

        # Populate the bodies combo and the matching available points
        # based on the current values in the force object
        (self.pointListHEADNames, self.pointListHEADLabels, pointHEADindex) = DT.getHEADPoints(self.forceTaskObject, self.bodyObjDict)
        (self.pointListTAILNames, self.pointListTAILLabels, pointTAILindex) = DT.getTAILPoints(self.forceTaskObject, self.bodyObjDict)
        self.form.pointHeadLabelOneTwo.clear()
        self.form.pointHeadLabelOneTwo.addItems(self.pointListHEADLabels)
        self.form.pointHeadLabelOneTwo.setCurrentIndex(pointHEADindex)
        self.form.pointLabelTwoOne.clear()
        self.form.pointLabelTwoOne.addItems(self.pointListHEADLabels)
        self.form.pointLabelTwoOne.setCurrentIndex(pointHEADindex)
        self.form.pointHeadLabelTwoTwo.clear()
        self.form.pointHeadLabelTwoTwo.addItems(self.pointListHEADLabels)
        self.form.pointHeadLabelTwoTwo.setCurrentIndex(pointHEADindex)
        self.form.pointTailLabelTwoTwo.clear()
        self.form.pointTailLabelTwoTwo.addItems(self.pointListHEADLabels)
        self.form.pointTailLabelTwoTwo.setCurrentIndex(pointHEADindex)

        (self.pointListTAILNames, self.pointListTAILLabels, pointTAILindex) = DT.getTAILPoints(self.forceTaskObject, self.bodyObjDict)
        self.form.pointTailLabelOneTwo.clear()
        self.form.pointTailLabelOneTwo.addItems(self.pointListTAILLabels)
        self.form.pointTailLabelOneTwo.setCurrentIndex(pointTAILindex)
        self.form.pointTailLabelTwoTwo.clear()
        self.form.pointTailLabelTwoTwo.addItems(self.pointListTAILLabels)
        self.form.pointTailLabelTwoTwo.setCurrentIndex(pointTAILindex)

        self.form.bodyLabelOneTwo.currentIndexChanged.connect(self.bodyHEADChangedCallbackF)
        self.form.bodyHeadLabelTwoOne.currentIndexChanged.connect(self.bodyHEADChangedCallbackF)
        self.form.bodyTailLabelTwoOne.currentIndexChanged.connect(self.bodyTAILChangedCallbackF)
        self.form.bodyHeadLabelTwoTwo.currentIndexChanged.connect(self.bodyHEADChangedCallbackF)
        self.form.bodyTailLabelTwoTwo.currentIndexChanged.connect(self.bodyTAILChangedCallbackF)

        self.form.gravityX.toggled.connect(self.gravityXChangedCallbackF)
        self.form.gravityY.toggled.connect(self.gravityYChangedCallbackF)
        self.form.gravityZ.toggled.connect(self.gravityZChangedCallbackF)
    #  -------------------------------------------------------------------------
    def getStandardButtons(self):
        if Debug:
            DT.Mess("TaskPanelDapForceC-getStandardButtons")
        return int(QtGui.QDialogButtonBox.Ok)
    #  -------------------------------------------------------------------------
    def accept(self):
        """Run when we press the OK button"""
        if Debug:
            DT.Mess("TaskPanelDapForceC-accept")

        self.forceTaskObject.actuatorType = self.form.actuatorCombo.currentIndex()

        # Transfer all values from the form to the force object
        # The Gravity actuator option
        if self.forceTaskObject.actuatorType == 0:
            containerObject = DT.getActiveContainerObject()
            # Remove the other gravity entry if one already exists
            if containerObject.gravityVector != CAD.Vector():
                CAD.Console.PrintError("You have already defined gravity as a force.\n")
                CAD.Console.PrintError("As a result, that definition will be replaced by this one.\n")
                taskDocument = CAD.getDocument(self.forceTaskObject.Document.Name)
                forceList = taskDocument.findObjects(Name="DapForce")
                # If another gravity exists, the list will have at least two forces
                if len(forceList) > 1:
                    # Find the first gravity force - the other one will be the new one
                    for forceObj in forceList:
                        if forceObj.actuatorType == 0:
                            CAD.ActiveDocument.removeObject(forceObj.Name)
                            break
            # Add gravity acceleration of -9810 mm/s^2 to the axis selected
            if self.form.gravityX.isChecked():
                containerObject.gravityVector.x = -9810
            else:
                containerObject.gravityVector.x = 0.0
            if self.form.gravityY.isChecked():
                containerObject.gravityVector.y = -9810
            else:
                containerObject.gravityVector.y = 0.0
            if self.form.gravityZ.isChecked():
                containerObject.gravityVector.z = -9810
            else:
                containerObject.gravityVector.z = 0.0

        elif self.forceTaskObject.actuatorType <= 4:
            # Two Bodies Two Points for linear spring and rotational spring
            # Transfer the body names to the forceTaskObject
            self.forceTaskObject.bodyHEADName = self.bodyNames[self.form.bodyHeadLabelTwoTwo.currentIndex()]
            self.forceTaskObject.bodyHEADLabel = self.bodyLabels[self.form.bodyHeadLabelTwoTwo.currentIndex()]
            self.forceTaskObject.bodyHEADindex = self.form.bodyHeadLabelTwoTwo.currentIndex()
            self.forceTaskObject.bodyTAILName = self.bodyNames[self.form.bodyTailLabelTwoTwo.currentIndex()]
            self.forceTaskObject.bodyTAILLabel = self.bodyLabels[self.form.bodyTailLabelTwoTwo.currentIndex()]
            self.forceTaskObject.bodyTAILindex = self.form.bodyTailLabelTwoTwo.currentIndex()

            # Transfer the point names to the forceTaskObject
            self.forceTaskObject.pointHEADName = self.pointListHEADNames[self.form.pointHeadLabelTwoTwo.currentIndex()]
            self.forceTaskObject.pointHEADLabel = self.pointListHEADLabels[self.form.pointHeadLabelTwoTwo.currentIndex()]
            self.forceTaskObject.pointHEADindex = self.form.pointHeadLabelTwoTwo.currentIndex()
            self.forceTaskObject.pointTAILName = self.pointListTAILNames[self.form.pointTailLabelTwoTwo.currentIndex()]
            self.forceTaskObject.pointTAILLabel = self.pointListTAILLabels[self.form.pointTailLabelTwoTwo.currentIndex()]
            self.forceTaskObject.pointTAILindex = self.form.pointTailLabelTwoTwo.currentIndex()

            # The Spring options
            if self.forceTaskObject.actuatorType == 1:
                self.forceTaskObject.Value0 = self.form.linSpringLength.value()
                self.forceTaskObject.Stiffness = self.form.linSpringStiffness.value()
            elif self.forceTaskObject.actuatorType == 2:
                self.forceTaskObject.DampingCoeff = self.form.linSpringDamp.value()
                self.forceTaskObject.Value0 = self.form.linSpringDampLength.value()
                self.forceTaskObject.Stiffness = self.form.linSpringDampStiffness.value()
            elif self.forceTaskObject.actuatorType == 3:
                self.forceTaskObject.Value0 = self.form.rotSpringAngle.value()
                self.forceTaskObject.Stiffness = self.form.rotSpringStiffness.value()
            elif self.forceTaskObject.actuatorType == 4:
                self.forceTaskObject.DampingCoeff = self.form.rotSpringDamp.value()
                self.forceTaskObject.Value0 = self.form.rotSpringDampAngle.value()
                self.forceTaskObject.Stiffness = self.form.rotSpringDampStiffness.value()

            # Draw an arrow as long as the distance of the vector between the points
            llen = (Point1 - Point2).Length
            if llen > 1e-6:
                # Direction of the arrow is the direction of the vector between the two points
                lin_move_dir = (Point2 - Point1).normalize()
                cylinder = Part.makeCylinder(
                    diameter*0.6,
                    0.60 * llen,
                    Point1 + 0.2 * llen * lin_move_dir,
                    lin_move_dir,
                )
                # Draw the two arrow heads
                cone1 = Part.makeCone(0, diameter, 0.2 * llen, Point1, lin_move_dir)
                cone2 = Part.makeCone(0, diameter, 0.2 * llen, Point2, -lin_move_dir)
                return Part.makeCompound([cylinder, cone1, cone2])

        # All the other options we have not yet handled
        else:
            self.forceTaskObject.Shape = Part.Shape()

        #  Recompute document to update view provider based on the shapes
        Document = CADGui.getDocument(self.forceTaskObject.Document)
        Document.resetEdit()
        self.forceTaskObject.recompute()
    #  -------------------------------------------------------------------------
    def bodyHEADChangedCallbackF(self):
        """Populate with a new list of points when a body is changed"""
        if Debug:
            DT.Mess("TaskPanelDapForceC-bodyHEADChangedCallbackF")

        (self.pointListHEADNames, self.pointListHEADLabels, pointHEADindex) = DT.getHEADPoints(self.forceTaskObject, self.bodyObjDict)
        # Load the new set of points in the specified body into the form
        self.form.pointHeadLabelTwoTwo.clear()
        self.form.pointHeadLabelTwoTwo.addItems(self.pointListHEADLabels)
        self.form.pointHeadLabelTwoTwo.setCurrentIndex(0)
    #  -------------------------------------------------------------------------
    def bodyTAILChangedCallbackF(self):
        """Populate with a new list of points when a body is changed"""
        if Debug:
            DT.Mess("TaskPanelDapForceC-bodyTAILChangedCallbackF")

        # Load the new set of points in the specified body into the form
        (self.pointListTAILNames, self.pointListTAILLabels,  pointTAILindex) = DT.getTAILPoints(self.forceTaskObject, self.bodyObjDict)
        self.form.pointTailLabelTwoTwo.clear()
        self.form.pointTailLabelTwoTwo.addItems(self.pointListTAILLabels)
        self.form.pointTailLabelTwoTwo.setCurrentIndex(0)
    #  -------------------------------------------------------------------------
    def gravityXChangedCallbackF(self):
        """Note the change in gravity tickboxes"""
        if Debug:
            DT.Mess("TaskPanelDapForceC-gravityXChangedCallbackF")

        if self.form.gravityX.isChecked():
            # X has been checked, uncheck Y and Z
            self.form.gravityY.setChecked(False)
            self.form.gravityZ.setChecked(False)
    #  -------------------------------------------------------------------------
    def gravityYChangedCallbackF(self):
        """Note the change in gravity tickboxes"""
        if Debug:
            DT.Mess("TaskPanelDapForceC-gravityYChangedCallbackF")

        if self.form.gravityY.isChecked():
            # X has been checked, uncheck X and Z
            self.form.gravityX.setChecked(False)
            self.form.gravityZ.setChecked(False)
    #  -------------------------------------------------------------------------
    def gravityZChangedCallbackF(self):
        """Note the change in gravity tickboxes"""
        if Debug:
            DT.Mess("TaskPanelDapForceC-gravityZChangedCallbackF")

        if self.form.gravityZ.isChecked():
            # X has been checked, uncheck X and Y
            self.form.gravityX.setChecked(False)
            self.form.gravityY.setChecked(False)
    #  -------------------------------------------------------------------------
    def actuatorChangedCallbackF(self):
        """Hide the stuff not used for gravity or not"""
        if Debug:
            DT.Mess("TaskPanelDapForceC-actuatorChangedCallbackF")

        # Hide or show pages according to the actuator choice
        index = self.form.actuatorCombo.currentIndex()
        if index == 0:
            self.form.bodyPointData.setHidden(True)
            self.form.forceData.setCurrentIndex(11)
        else:
            self.form.bodyPointData.setVisible(True)
            self.form.forceData.setCurrentIndex(index-1)

        if index >= 1 and index <= 4:
            self.form.bodyPointData.setCurrentIndex(2)
        elif index == 5:
            self.form.bodyPointData.setCurrentIndex(0)
        elif index == 6:
            self.form.bodyPointData.setCurrentIndex(1)
        else:
            self.form.bodyPointData.setHidden(True)
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("TaskPanelDapForceC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("TaskPanelDapForceC-__setstate__")
# =============================================================================
        #    springLength = (forceHEADLCS - forceTAILLCS).Length
        #    pitch = springLength / 10
        #    radius = springLength / 10
        #    creationAxis = CAD.Vector(0, 0, 1.0)

        #      if springLength > 0:
        #          springDirection = (forceTAILLCS - forceHEADLCS).normalize()
        #          angle = degrees(acos(springDirection * creationAxis))
        #          axis = creationAxis.cross(springDirection)
        #          helix = Part.makeHelix(pitch, springLength, radius)
        #         forceObject.Shape = helix
        #         if forceObject.actuatorType == "Spring":
        #             forceObject.ViewObject.LineColor = 0.0, 0.0, 0.0, 0.0
        #         elif forceObject.actuatorType == "Linear Spring Damper":
        #             forceObject.ViewObject.LineColor = 0.0, 250.0, 20.0, 0.0

        #         # First reset the placement in case multiple recomputes are performed
        #         #forceObject.Placement.Base = CAD.Vector(0, 0, 0)
        #         #forceObject.Placement.Rotation = CAD.Rotation(0, 0, 0, 1)
        #         #forceObject.Placement.rotate(CAD.Vector(0, 0, 0), axis, angle)
        #         #forceObject.Placement.translate(forceHEADLCS)
        #     else:
        #         # An empty shape if the length is zero
        #         forceObject.Shape = Part.Shape()

            DT.Mess("Rotational")
        #     vol1 = 0
        #     vol2 = 0
        #     if forceObject.bodyHEADName != "Origin":
        #         vol1 = Document.getObjectsByName(forceObject.bodyHEADName)[0].Shape.Volume
        #     if forceObject.bodyTAILName != "Origin":
        #         vol2 = Document.getObjectsByName(forceObject.bodyTAILName)[0].Shape.Volume
        #     if vol1 + vol2 == 0:
        #         vol1 = 100000
        #     scale = (vol1 + vol2) / 30000

        #     spiral = document.addObject("Part::Spiral", "Spiral")
        #     spiral.Radius = 2 * scale
        #     spiral.Growth = r / 2
        #     spiral.Rotations = 4
        #     spiral.Placement.Base = CAD.Vector(0, 0, 0)

        #     spiralShape = document.getObject("Spiral").Shape
        #     forceObject.Shape = spiralShape

        #     if forceObject.actuatorType == "Rotational Spring":
        #         forceObject.ViewObject.LineColor = 0.0, 0.0, 0.0, 0.0
        #     elif forceObject.actuatorType == "Rotational Spring Damper":
        #         forceObject.ViewObject.LineColor = 0.0, 250.0, 20.0, 0.0

        #     forceObject.Placement.Base = forceHEADLCS

        #    document.removeObject("Spiral")

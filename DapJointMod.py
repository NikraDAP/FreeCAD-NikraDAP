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
import DapToolsMod as DT
import DapFunctionMod

import Part
import math
if CAD.GuiUp:
    import FreeCADGui as CADGui
    from PySide import QtGui, QtCore
    from pivy import coin
global Debug
Debug = False
#  ----------------------------------------------------------------------------
def makeDapJoint(name="DapJoint"):
    if Debug:
        DT.Mess("makeDapJoint")
    objJoint = CAD.ActiveDocument.addObject("Part::FeaturePython", name)
    DapJointC(objJoint)
    if CAD.GuiUp:
        ViewProviderDapJointC(objJoint.ViewObject)
    return objJoint
# =============================================================================
class CommandDapJointC:
    if Debug:
        DT.Mess("CommandDapJointC-CLASS")
    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by CAD when 'CADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""
        if Debug:
            DT.Mess("CommandDapJointC-GetResourcesC")

        return {
            "Pixmap": path.join(DT.getDapModulePath(), "icons", "Icon4n.png"),
            "MenuText": QtCore.QT_TRANSLATE_NOOP("Dap_Joint_alias", "Add New Joint Between Bodies"),
            "ToolTip": QtCore.QT_TRANSLATE_NOOP("Dap_Joint_alias", "Add a new relative movement between two bodies"),
        }
    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out.
        Only activate it when there are at least two bodies defined
        [Called explicitly by FreeCAD]"""
        if Debug:
            DT.Mess("CommandDapJointC-IsActive(query)")
        return len(DT.getDictionary("DapBody")) > 1
    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Dap Joint command is run
        [Called explicitly by FreeCAD]"""
        if Debug:
            DT.Mess("CommandDapJointC-Activated")
        # This is where we create the new dap joint object
        DT.getActiveContainerObject().addObject(makeDapJoint())
        # Switch on the TaskPanel
        CADGui.ActiveDocument.setEdit(CAD.ActiveDocument.ActiveObject.Name)
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("CommandDapJointC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("CommandDapJointC-__setstate__")
# =============================================================================
class DapJointC:
    if Debug:
        DT.Mess("DapJointC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(self, jointObject):
        if Debug:
            DT.Mess("DapJointC-__init__")

        self.jointObject = jointObject
        jointObject.Proxy = self

        # A separate function so it can be re-used when the Document is Restored
        self.initProperties(jointObject)
    #  -------------------------------------------------------------------------
    def initProperties(self, jointObject):
        if Debug:
            DT.Mess("DapJointC-initProperties")

        DT.addObjectProperty(jointObject, "JointType", 0, "App::PropertyInteger", "Joint", "Type of Joint")

        DT.addObjectProperty(jointObject, "bodyHEADName", "", "App::PropertyString", "Points", "Name of Body at HEAD of Joint")
        DT.addObjectProperty(jointObject, "bodyHEADLabel", "", "App::PropertyString", "Points", "Label of Body at HEAD of Joint")
        DT.addObjectProperty(jointObject, "bodyHEADindex", -1, "App::PropertyInteger", "", "Index of the head body in the NumPy array")

        DT.addObjectProperty(jointObject, "bodyTAILName", "", "App::PropertyString", "Points", "Name of Body at TAIL of Joint")
        DT.addObjectProperty(jointObject, "bodyTAILLabel", "", "App::PropertyString", "Points", "Label of Body at TAIL of Joint")
        DT.addObjectProperty(jointObject, "bodyTAILindex", -1, "App::PropertyInteger", "", "Index of the tail body in the NumPy array")

        DT.addObjectProperty(jointObject, "pointHEADName", "", "App::PropertyString", "Points", "Name of Point at head of joint")
        DT.addObjectProperty(jointObject, "pointHEADLabel", "", "App::PropertyString", "Points", "Label of Point at head of joint")
        DT.addObjectProperty(jointObject, "pointHEADindex", -1, "App::PropertyInteger", "", "Index of the head point in the NumPy array")

        DT.addObjectProperty(jointObject, "pointTAILName", "", "App::PropertyString", "Points", "Name of Point at tail of joint")
        DT.addObjectProperty(jointObject, "pointTAILLabel", "", "App::PropertyString", "Points", "Label of c Point at tail of joint")
        DT.addObjectProperty(jointObject, "pointTAILindex", -1, "App::PropertyInteger", "", "Index of the tail point in the NumPy array")

        DT.addObjectProperty(jointObject, "fixDof", False, "App::PropertyBool", "Bodies and constraints", "Fix the Degrees of Freedom")
        DT.addObjectProperty(jointObject, "lengthLink", 1.0, "App::PropertyFloat", "", "Link length")

        DT.addObjectProperty(jointObject, "FunctClass", "", "App::PropertyPythonObject", "Function Driver", "A machine which is set up to generate a driver function")
        DT.addObjectProperty(jointObject, "FunctType", -1, "App::PropertyInteger", "Function Driver", "Analytical function type")
        DT.addObjectProperty(jointObject, "Coeff0", 0, "App::PropertyFloat", "Function Driver", "Drive Func coefficient 'c0'")
        DT.addObjectProperty(jointObject, "Coeff1", 0, "App::PropertyFloat", "Function Driver", "Drive Func coefficient 'c1'")
        DT.addObjectProperty(jointObject, "Coeff2", 0, "App::PropertyFloat", "Function Driver", "Drive Func coefficient 'c2'")
        DT.addObjectProperty(jointObject, "Coeff3", 0, "App::PropertyFloat", "Function Driver", "Drive Func coefficient 'c3'")
        DT.addObjectProperty(jointObject, "Coeff4", 0, "App::PropertyFloat", "Function Driver", "Drive Func coefficient 'c4'")
        DT.addObjectProperty(jointObject, "Coeff5", 0, "App::PropertyFloat", "Function Driver", "Drive Func coefficient 'c5'")
        DT.addObjectProperty(jointObject, "startTimeDriveFunc", 0, "App::PropertyFloat", "Function Driver", "Drive Function Start time")
        DT.addObjectProperty(jointObject, "endTimeDriveFunc", 0, "App::PropertyFloat", "Function Driver", "Drive Function End time")
        DT.addObjectProperty(jointObject, "startValueDriveFunc", 0, "App::PropertyFloat", "Function Driver", "Drive Func value at start")
        DT.addObjectProperty(jointObject, "endValueDriveFunc", 0, "App::PropertyFloat", "Function Driver", "Drive Func value at end")
        DT.addObjectProperty(jointObject, "endDerivativeDriveFunc", 0, "App::PropertyFloat", "Function Driver", "Drive Func derivative at end")
        DT.addObjectProperty(jointObject, "Radius", 1.0, "App::PropertyFloat", "Starting Values", "Body Radius")
        DT.addObjectProperty(jointObject, "world0", CAD.Vector(), "App::PropertyVector", "Starting Values", "initial condition for disc")
        DT.addObjectProperty(jointObject, "phi0", 0, "App::PropertyFloat", "Starting Values", "initial condition for disc")
        DT.addObjectProperty(jointObject, "d0", CAD.Vector(), "App::PropertyVector", "Starting Values", "initial condition (rigid)")

        DT.addObjectProperty(jointObject, "nMovBodies", 2, "App::PropertyInteger", "Bodies and constraints", "Number of moving bodies involved")
        DT.addObjectProperty(jointObject, "mConstraints", 2, "App::PropertyInteger", "Bodies and constraints", "Number of rows (constraints)")
        DT.addObjectProperty(jointObject, "rowStart", -1, "App::PropertyInteger", "Bodies and constraints", "Row starting index")
        DT.addObjectProperty(jointObject, "rowEnd", -1, "App::PropertyInteger", "Bodies and constraints", "Row ending index")
    #  -------------------------------------------------------------------------
    def onDocumentRestored(self, jointObject):
        if Debug:
            DT.Mess("DapJointC-onDocumentRestored")
        self.initProperties(jointObject)
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("DapJointC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("DapJointC-__setstate__")
#  ============================================================================
class ViewProviderDapJointC:
    if Debug:
        DT.Mess("ViewProviderDapJointC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(self, jointViewObject):
        if Debug:
            DT.Mess("ViewProviderDapJointC-__init__")
        jointViewObject.Proxy = self
    #  -------------------------------------------------------------------------
    def getIcon(self):
        if Debug:
            DT.Mess("ViewProviderDapJointC-getIcon")
        icon_path = path.join(DT.getDapModulePath(), "icons", "Icon4n.png")
        return icon_path
    #  -------------------------------------------------------------------------
    def attach(self, jointViewObject):
        if Debug:
            DT.Mess("ViewProviderDapJointC-attach")
        self.jointViewObjectObject = jointViewObject.Object
        standard = coin.SoGroup()
        jointViewObject.addDisplayMode(standard, "Standard")
    #  -------------------------------------------------------------------------
    def getDisplayModes(self, jointViewObject):
        """Return an empty list of modes when requested"""
        if Debug:
            DT.Mess("ViewProviderDapJointC-getDisplayModes")
        return []
    #  -------------------------------------------------------------------------
    def getDefaultDisplayMode(self):
        if Debug:
            DT.Mess("ViewProviderDapJointC-getDefaultDisplayMode")
        return "Shaded"
    #  -------------------------------------------------------------------------
    def setDisplayMode(self, mode):
        if Debug:
            DT.Mess("ViewProviderDapJointC-setDisplayMode")
        return mode
    #  -------------------------------------------------------------------------
    def updateData(self, jointViewObject, prop):
        # if Debug:
        # DT.Mess("ViewProviderDapJointC-updateData")
        return
    #  -------------------------------------------------------------------------
    def onChanged(self, jointViewObject, prop):
        # if Debug:
        # DT.Mess("ViewProviderDapJointC-onChanged")
        return
    #  -------------------------------------------------------------------------
    def doubleClicked(self, jointViewObject):
        """Activate the dialog if the joint item is double-clicked
        If it is already active, raise a benign warning in the console"""
        if Debug:
            DT.Mess("ViewProviderDapJointC-doubleClicked")

        Document = CADGui.getDocument(jointViewObject.Object.Document)
        if not Document.getInEdit():
            Document.setEdit(jointViewObject.Object.Label)
        else:
            CAD.Console.PrintError("Task dialog already active\n")
        return True
    #  -------------------------------------------------------------------------
    def setEdit(self, jointViewObject, mode):
        """Edit the parameters by calling the task dialog"""
        if Debug:
            DT.Mess("ViewProviderDapJointC-setEdit")
        CADGui.Control.showDialog(TaskPanelDapJointC(self.jointViewObjectObject))
        return True
    #  -------------------------------------------------------------------------
    def unsetEdit(self, jointViewObject, mode):
        """We have finished with the task dialog so close it"""
        if Debug:
            DT.Mess("ViewProviderDapJointC-unsetEdit")
        CADGui.Control.closeDialog()
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("ViewProviderDapJointC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("ViewProviderDapJoint-__setstate__")
# =============================================================================
class TaskPanelDapJointC:
    """Taskpanel for editing DAP Joints"""
    if Debug:
        DT.Mess("TaskPanelDapJointC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(self, jointTaskObject):
        """Run on first instantiation of a TaskPanelJoint class"""
        if Debug:
            DT.Mess("TaskPanelDapJointC-__init__")

        self.jointTaskObject = jointTaskObject
        jointTaskObject.Proxy = self
        
        # Load up the Task panel dialog definition file
        ui_path = path.join(path.dirname(__file__), "TaskPanelDapJoints.ui")
        self.form = CADGui.PySideUic.loadUi(ui_path)

        # Set the joint type combo box up according to the jointObject - default 0
        self.form.jointType.clear()
        self.form.jointType.addItems(DT.JOINT_TYPE)
        self.form.jointType.setCurrentIndex(self.jointTaskObject.JointType)

        # Populate the body object Dictionary
        self.bodyObjDict = DT.getDictionary("DapBody")
        # Make up the list of possible bodies
        # and place them into both the head and the tail lists in the form
        bodyLabels = []
        self.bodyObjects = []
        for bodyName in self.bodyObjDict:
            bodyObj = self.bodyObjDict[bodyName]
            bodyLabels.append(bodyObj.Label)
            self.bodyObjects.append(bodyObj)
        self.form.bodyHeadLabel.clear()
        self.form.bodyHeadLabel.addItems(bodyLabels)
        self.form.bodyHeadLabel.setCurrentIndex(self.jointTaskObject.bodyHEADindex)
        self.form.bodyTailLabel.clear()
        self.form.bodyTailLabel.addItems(bodyLabels)
        self.form.bodyTailLabel.setCurrentIndex(self.jointTaskObject.bodyTAILindex)

        # Populate the available points specific to each body in the form
        (ListHEADNames, ListHEADLabels, pointHEADindex) = DT.getHEADPoints(jointTaskObject, self.bodyObjDict)
        self.form.pointHeadLabel.clear()
        self.form.pointHeadLabel.addItems(ListHEADLabels)
        self.form.pointHeadLabel.setCurrentIndex(pointHEADindex)

        (ListTAILNames, ListTAILLabels, pointTAILindex) = DT.getTAILPoints(jointTaskObject, self.bodyObjDict)
        self.form.pointTailLabel.clear()
        self.form.pointTailLabel.addItems(ListTAILLabels)
        self.form.pointTailLabel.setCurrentIndex(pointTAILindex)

        # Update things by means of the callback functions
        self.bodyHEADChanged_CallbackF()
        self.bodyTAILChanged_CallbackF()
        self.pointHEADChanged_CallbackF()
        self.pointTAILChanged_CallbackF()
        self.jointChanged_CallbackF()
        
        # Transfer the applicable parameters from the object to the applicable page in the form
        # Transfer all the possible values so some will be set up in case the user changes the driver type
        # "Rotation"
        self.form.FuncACoeff0.setValue(self.jointTaskObject.Coeff0)
        self.form.FuncACoeff1.setValue(self.jointTaskObject.Coeff1)
        self.form.FuncACoeff2.setValue(self.jointTaskObject.Coeff2)
        self.form.FuncAendTime.setValue(self.jointTaskObject.endTimeDriveFunc)

        #  "Translation"
        self.form.FuncBstartTime.setValue(self.jointTaskObject.startTimeDriveFunc)
        self.form.FuncBendTime.setValue(self.jointTaskObject.endTimeDriveFunc)
        self.form.FuncBstartValue.setValue(self.jointTaskObject.startValueDriveFunc)
        self.form.FuncBendValue.setValue(self.jointTaskObject.endValueDriveFunc)

        # "Rotation-Rotation"
        self.form.FuncCstartTime.setValue(self.jointTaskObject.startTimeDriveFunc)
        self.form.FuncCendTime.setValue(self.jointTaskObject.endTimeDriveFunc)
        self.form.FuncCstartValue.setValue(self.jointTaskObject.startValueDriveFunc)
        self.form.FuncCendDeriv.setValue(self.jointTaskObject.endDerivativeDriveFunc)

        # "Rotation-Translation"
        self.form.FuncDCoeff0.setValue(self.jointTaskObject.Coeff0)
        self.form.FuncDCoeff1.setValue(self.jointTaskObject.Coeff1)
        self.form.FuncDCoeff2.setValue(self.jointTaskObject.Coeff2)
        self.form.FuncDCoeff3.setValue(self.jointTaskObject.Coeff3)
        self.form.FuncDCoeff4.setValue(self.jointTaskObject.Coeff4)
        self.form.FuncDstartTime.setValue(self.jointTaskObject.startTimeDriveFunc)
        self.form.FuncDendTime.setValue(self.jointTaskObject.endTimeDriveFunc)

        # "Relative-Rotation"
        self.form.FuncFCoeff0.setValue(self.jointTaskObject.Coeff0)
        self.form.FuncFCoeff1.setValue(self.jointTaskObject.Coeff1)
        self.form.FuncFCoeff2.setValue(self.jointTaskObject.Coeff2)
        self.form.FuncFCoeff3.setValue(self.jointTaskObject.Coeff3)
        self.form.FuncFCoeff4.setValue(self.jointTaskObject.Coeff4)
        self.form.FuncFstartTime.setValue(self.jointTaskObject.startTimeDriveFunc)
        self.form.FuncFendTime.setValue(self.jointTaskObject.endTimeDriveFunc)
        self.form.funcAequationGrey.setVisible(True)
        self.form.funcAequation.setHidden(True)

        # "Relative-Translation"
        self.form.FuncFCoeff0.setValue(self.jointTaskObject.Coeff0)
        self.form.FuncFCoeff1.setValue(self.jointTaskObject.Coeff1)
        self.form.FuncFCoeff2.setValue(self.jointTaskObject.Coeff2)
        self.form.FuncFCoeff3.setValue(self.jointTaskObject.Coeff3)
        self.form.FuncFCoeff4.setValue(self.jointTaskObject.Coeff4)
        self.form.FuncFstartTime.setValue(self.jointTaskObject.startTimeDriveFunc)
        self.form.FuncFendTime.setValue(self.jointTaskObject.endTimeDriveFunc)

        # "Rigid"
        self.form.FuncECoeff0.setValue(self.jointTaskObject.Coeff0)
        self.form.FuncECoeff1.setValue(self.jointTaskObject.Coeff1)
        self.form.FuncECoeff2.setValue(self.jointTaskObject.Coeff2)
        self.form.FuncECoeff3.setValue(self.jointTaskObject.Coeff3)
        self.form.FuncECoeff4.setValue(self.jointTaskObject.Coeff4)
        self.form.FuncEstartTime.setValue(self.jointTaskObject.startTimeDriveFunc)
        self.form.FuncEendTime.setValue(self.jointTaskObject.endTimeDriveFunc)

        # "Disc"
        self.form.FuncFCoeff0.setValue(self.jointTaskObject.Coeff0)
        self.form.FuncFCoeff1.setValue(self.jointTaskObject.Coeff1)
        self.form.FuncFCoeff2.setValue(self.jointTaskObject.Coeff2)
        self.form.FuncFCoeff3.setValue(self.jointTaskObject.Coeff3)
        self.form.FuncFCoeff4.setValue(self.jointTaskObject.Coeff4)
        self.form.FuncFstartTime.setValue(self.jointTaskObject.startTimeDriveFunc)
        self.form.FuncFendTime.setValue(self.jointTaskObject.endTimeDriveFunc)

        # Set up the callback functions for when anything changes
        self.form.jointType.currentIndexChanged.connect(self.jointChanged_CallbackF)
        self.form.radioButtonA.toggled.connect(self.DriveFuncChanged_CallbackF)
        self.form.radioButtonB.toggled.connect(self.DriveFuncChanged_CallbackF)
        self.form.radioButtonC.toggled.connect(self.DriveFuncChanged_CallbackF)
        self.form.radioButtonD.toggled.connect(self.DriveFuncChanged_CallbackF)
        self.form.radioButtonE.toggled.connect(self.DriveFuncChanged_CallbackF)
        self.form.radioButtonF.toggled.connect(self.DriveFuncChanged_CallbackF)
        self.form.bodyHeadLabel.currentIndexChanged.connect(self.bodyHEADChanged_CallbackF)
        self.form.bodyTailLabel.currentIndexChanged.connect(self.bodyTAILChanged_CallbackF)
        self.form.pointHeadLabel.currentIndexChanged.connect(self.pointHEADChanged_CallbackF)
        self.form.pointTailLabel.currentIndexChanged.connect(self.pointTAILChanged_CallbackF)

        # Set the current driver function, should it be already defined
        if self.jointTaskObject.FunctType != -1:
            self.form.funcType.setEnabled(True)
            self.form.funcCoeff.setEnabled(True)
            if self.jointTaskObject.FunctType == 0:
                self.form.radioButtonA.setChecked(True)
            elif self.jointTaskObject.FunctType == 1:
                self.form.radioButtonB.setChecked(True)
            elif self.jointTaskObject.FunctType == 2:
                self.form.radioButtonC.setChecked(True)
            elif self.jointTaskObject.FunctType == 3:
                self.form.radioButtonD.setChecked(True)
            elif self.jointTaskObject.FunctType == 4:
                self.form.radioButtonE.setChecked(True)
            elif self.jointTaskObject.FunctType == 5:
                self.form.radioButtonF.setChecked(True)
            else:
                self.form.funcType.setDisabled(True)
                self.form.funcCoeff.setDisabled(True)

        # Make the jointTaskObject be "Observed" when the cursor is on it / it is selected
        CADGui.Selection.addObserver(self.jointTaskObject)
    #  -------------------------------------------------------------------------
    def accept(self):
        """Run when we press the OK button"""
        if Debug:
            DT.Mess("TaskPanelDapJointC-accept")

        # Transfer the HEAD and TAIL values
        self.jointTaskObject.bodyHEADindex = self.form.bodyHeadLabel.currentIndex()
        self.jointTaskObject.bodyTAILindex = self.form.bodyTailLabel.currentIndex()
        self.jointTaskObject.pointHEADindex = self.form.pointHeadLabel.currentIndex()
        self.jointTaskObject.pointTAILindex = self.form.pointTailLabel.currentIndex()
        # Refuse to accept the values when either body is not defined yet
        if self.jointTaskObject.bodyHEADindex == -1 or self.jointTaskObject.bodyTAILindex == -1:
            CAD.Console.PrintError("You have not defined both bodies yet\n")
            return False

        # Check whether a drive function has been selected where appropriate
        self.jointTaskObject.JointType = self.form.jointType.currentIndex()
        if self.jointTaskObject.JointType == 4 or self.jointTaskObject.JointType == 5:
            if self.form.radioButtonA.isChecked():
                self.jointTaskObject.FunctType = 0
                self.jointTaskObject.Coeff0 = self.form.FuncACoeff0.value()
                self.jointTaskObject.Coeff1 = self.form.FuncACoeff1.value()
                self.jointTaskObject.Coeff2 = self.form.FuncACoeff2.value()
                self.jointTaskObject.endTimeDriveFunc = self.form.FuncAendTime.value()
            elif self.form.radioButtonB.isChecked():
                self.jointTaskObject.FunctType = 1
                self.jointTaskObject.startTimeDriveFunc = self.form.FuncBstartTime.value()
                self.jointTaskObject.endTimeDriveFunc = self.form.FuncBendTime.value()
                self.jointTaskObject.startValueDriveFunc = self.form.FuncBstartValue.value()
                self.jointTaskObject.endValueDriveFunc = self.form.FuncBendValue.value()
            elif self.form.radioButtonC.isChecked():
                self.jointTaskObject.FunctType = 2
                self.jointTaskObject.startTimeDriveFunc = self.form.FuncCstartTime.value()
                self.jointTaskObject.endTimeDriveFunc = self.form.FuncCendTime.value()
                self.jointTaskObject.startValueDriveFunc = self.form.FuncCstartValue.value()
                self.jointTaskObject.endDerivDriveFunc = self.form.FuncCendDeriv.value()
            elif self.form.radioButtonD.isChecked():
                self.jointTaskObject.FunctType = 3
                self.jointTaskObject.startTimeDriveFunc = self.form.FuncDstartTime.value()
                self.jointTaskObject.endTimeDriveFunc = self.form.FuncDendTime.value()
                self.jointTaskObject.Coeff0 = self.form.FuncDCoeff0.value()
                self.jointTaskObject.Coeff1 = self.form.FuncDCoeff1.value()
                self.jointTaskObject.Coeff2 = self.form.FuncDCoeff2.value()
                self.jointTaskObject.Coeff3 = self.form.FuncDCoeff3.value()
                self.jointTaskObject.Coeff4 = self.form.FuncDCoeff4.value()
                self.jointTaskObject.Coeff5 = self.form.FuncDCoeff5.value()
            elif self.form.radioButtonE.isChecked():
                self.jointTaskObject.FunctType = 4
                self.jointTaskObject.startTimeDriveFunc = self.form.FuncEstartTime.value()
                self.jointTaskObject.endTimeDriveFunc = self.form.FuncEendTime.value()
                self.jointTaskObject.Coeff0 = self.form.FuncECoeff0.value()
                self.jointTaskObject.Coeff1 = self.form.FuncECoeff1.value()
                self.jointTaskObject.Coeff2 = self.form.FuncECoeff2.value()
                self.jointTaskObject.Coeff3 = self.form.FuncECoeff3.value()
                self.jointTaskObject.Coeff4 = self.form.FuncECoeff4.value()
                self.jointTaskObject.Coeff5 = self.form.FuncECoeff5.value()
            elif self.form.radioButtonF.isChecked():
                self.jointTaskObject.FunctType = 5
                self.jointTaskObject.startTimeDriveFunc = self.form.FuncstartTime.value()
                self.jointTaskObject.endTimeDriveFunc = self.form.FuncendTime.value()
                self.jointTaskObject.Coeff0 = self.form.FuncFCoeff0.value()
                self.jointTaskObject.Coeff1 = self.form.FuncFCoeff1.value()
                self.jointTaskObject.Coeff2 = self.form.FuncFCoeff2.value()
                self.jointTaskObject.Coeff3 = self.form.FuncFCoeff3.value()
                self.jointTaskObject.Coeff4 = self.form.FuncFCoeff4.value()
                self.jointTaskObject.Coeff5 = self.form.FuncFCoeff5.value()
            else:
                CAD.Console.PrintError("You have not selected a driver function type yet\n")
                return False
        else:
            self.jointTaskObject.FunctType = -1

        # Instantiate the function class according to the parameters
        if self.jointTaskObject.FunctType >= 0:
            FunctionCallList = [
                self.jointTaskObject.FunctType,
                self.jointTaskObject.Coeff0,
                self.jointTaskObject.Coeff1,
                self.jointTaskObject.Coeff2,
                self.jointTaskObject.Coeff3,
                self.jointTaskObject.Coeff4,
                self.jointTaskObject.startTimeDriveFunc,
                self.jointTaskObject.endTimeDriveFunc,
                self.jointTaskObject.startValueDriveFunc,
                self.jointTaskObject.endValueDriveFunc,
                self.jointTaskObject.endDerivativeDriveFunc
            ]
            self.jointTaskObject.FunctClass = DapFunctionMod.FunctionC(FunctionCallList)

        # Put the appropriate decorations at the head and tail points
        DT.decorateObject(self.jointTaskObject,
                          self.bodyObjects[self.jointTaskObject.bodyHEADindex],
                          self.bodyObjects[self.jointTaskObject.bodyTAILindex])

        self.jointTaskObject.recompute()
        CADGui.getDocument(self.jointTaskObject.Document).resetEdit()
    #  -------------------------------------------------------------------------
    def DriveFuncChanged_CallbackF(self):
        if Debug:
            DT.Mess("TaskPanelDapJointC-DriveFuncChanged_CallbackF")

        # Change the function type in the jointTaskObject
        # and show/grey out the function description
        if self.form.radioButtonA.isChecked():
            self.jointTaskObject.FunctType = 0
            self.form.funcAequation.setVisible(True)
            self.form.funcAequationGrey.setHidden(True)
        elif self.form.radioButtonB.isChecked():
            self.jointTaskObject.FunctType = 1
            self.form.funcBequation.setVisible(True)
            self.form.funcBequationGrey.setHidden(True)
        elif self.form.radioButtonC.isChecked():
            self.jointTaskObject.FunctType = 2
            self.form.funcCequation.setVisible(True)
            self.form.funcCequationGrey.setHidden(True)
        elif self.form.radioButtonD.isChecked():
            self.jointTaskObject.FunctType = 3
            self.form.funcDequation.setVisible(True)
            self.form.funcDequationGrey.setHidden(True)
        elif self.form.radioButtonE.isChecked():
            self.jointTaskObject.FunctType = 4
            self.form.funcEequation.setVisible(True)
            self.form.funcEequationGrey.setHidden(True)
        elif self.form.radioButtonF.isChecked():
            self.jointTaskObject.FunctType = 5

        # Set the current index of the funcCoeff stacked widget
        self.form.funcCoeff.setCurrentIndex(self.jointTaskObject.FunctType)
    #  -------------------------------------------------------------------------
    def jointChanged_CallbackF(self):
        """When we have changed the joint movement type"""
        if Debug:
            DT.Mess("TaskPanelDapJointC-jointChanged_CallbackF")

        # Transfer the new joint Type to the jointTaskObject
        formJointType = self.form.jointType.currentIndex()
        self.jointTaskObject.JointType = formJointType

        # Set up which page of body definition we must see (twoBodies twoPoints / oneBody onePoint
        # And whether the driven function stuff is available
        if formJointType == DT.JOINT_TYPE_DICTIONARY["Rotation"]:
            self.form.definitionWidget.setCurrentIndex(0)
            self.greyAllEquationsF()
        elif formJointType == DT.JOINT_TYPE_DICTIONARY["Translation"]:
            self.form.definitionWidget.setCurrentIndex(0)
            self.greyAllEquationsF()
        elif formJointType == DT.JOINT_TYPE_DICTIONARY["Rotation-Rotation"]:
            self.form.definitionWidget.setCurrentIndex(0)
            self.greyAllEquationsF()
        elif formJointType == DT.JOINT_TYPE_DICTIONARY["Rotation-Translation"]:
            self.form.definitionWidget.setCurrentIndex(0)
            self.greyAllEquationsF()
        elif formJointType == DT.JOINT_TYPE_DICTIONARY["Driven-Rotation"]:
            self.form.definitionWidget.setCurrentIndex(1)
            self.showAllEquationsF()
        elif formJointType == DT.JOINT_TYPE_DICTIONARY["Driven-Translation"]:
            self.form.definitionWidget.setCurrentIndex(1)
            self.showAllEquationsF()
        elif formJointType == DT.JOINT_TYPE_DICTIONARY["Disc"]:
            self.form.definitionWidget.setCurrentIndex(1)
            self.greyAllEquationsF()
        elif formJointType == DT.JOINT_TYPE_DICTIONARY["Rigid"]:
            self.form.definitionWidget.setCurrentIndex(0)
            self.greyAllEquationsF()
        else:
            CAD.Console.PrintError("Unknown joint type - this should never occur\n")
    #  -------------------------------------------------------------------------
    def greyAllEquationsF(self):
        self.form.funcCoeff.setDisabled(True)
        self.form.funcType.setDisabled(True)
        self.form.funcAequationGrey.setVisible(True)
        self.form.funcAequation.setHidden(True)
        self.form.funcBequationGrey.setVisible(True)
        self.form.funcBequation.setHidden(True)
        self.form.funcCequationGrey.setVisible(True)
        self.form.funcCequation.setHidden(True)
        self.form.funcDequationGrey.setVisible(True)
        self.form.funcDequation.setHidden(True)
        self.form.funcEequationGrey.setVisible(True)
        self.form.funcEequation.setHidden(True)
        self.form.funcFequationGrey.setVisible(True)
        self.form.funcFequation.setHidden(True)
    #  -------------------------------------------------------------------------
    def showAllEquationsF(self):
        self.form.funcCoeff.setEnabled(True)
        self.form.funcType.setEnabled(True)
        self.form.funcAequationGrey.setHidden(True)
        self.form.funcAequation.setVisible(True)
        self.form.funcBequationGrey.setHidden(True)
        self.form.funcBequation.setVisible(True)
        self.form.funcCequationGrey.setHidden(True)
        self.form.funcCequation.setVisible(True)
        self.form.funcDequationGrey.setHidden(True)
        self.form.funcDequation.setVisible(True)
        self.form.funcEequationGrey.setHidden(True)
        self.form.funcEequation.setVisible(True)
        self.form.funcFequationGrey.setHidden(True)
        self.form.funcFequation.setVisible(True)
    #  -------------------------------------------------------------------------
    def bodyHEADChanged_CallbackF(self):
        """The Body HEAD combo box current index has changed"""
        if Debug:
            DT.Mess("TaskPanelDapJointC-bodyHEADChanged_CallbackF")

        # Update the body stuff
        bodyHEADind = self.form.bodyHeadLabel.currentIndex()
        self.jointTaskObject.bodyHEADName = self.bodyObjects[bodyHEADind].Name
        self.jointTaskObject.bodyHEADLabel = self.bodyObjects[bodyHEADind].Label

        # Set up a new pointHEADLabel combo in the form
        List = []
        for index in range(len(self.bodyObjects[bodyHEADind].pointNames)):
            List.append(self.bodyObjects[bodyHEADind].pointLabels[index])
        self.form.pointHeadLabel.clear()
        self.form.pointHeadLabel.addItems(List)
        self.form.pointHeadLabel.setCurrentIndex(0)

        # Highlight the current item in the GUI
        CADGui.Selection.clearSelection()
        CADGui.Selection.addSelection(self.bodyObjects[bodyHEADind])
    #  -------------------------------------------------------------------------
    def bodyTAILChanged_CallbackF(self):
        """The Body TAIL combo box current index has changed"""
        if Debug:
            DT.Mess("TaskPanelDapJointC-bodyTAILChanged_CallbackF")

        # Update the body stuff
        bodyTAILindex = self.form.bodyTailLabel.currentIndex()
        self.jointTaskObject.bodyTAILName = self.bodyObjects[bodyTAILindex].Name
        self.jointTaskObject.bodyTAILLabel = self.bodyObjects[bodyTAILindex].Label

        # Set up a new pointTAILLabel combo in the form
        List = []
        for index in range(len(self.bodyObjects[bodyTAILindex].pointNames)):
            List.append(self.bodyObjects[bodyTAILindex].pointLabels[index])
        self.form.pointTailLabel.clear()
        self.form.pointTailLabel.addItems(List)
        self.form.pointTailLabel.setCurrentIndex(0)

        # Highlight the current item in the GUI
        CADGui.Selection.clearSelection()
        CADGui.Selection.addSelection(self.bodyObjects[bodyTAILindex])
    #  -------------------------------------------------------------------------
    def pointHEADChanged_CallbackF(self):
        """The Point HEAD combo box current index has changed"""
        if Debug:
            DT.Mess("TaskPanelDapJointC-pointHEADChanged_CallbackF")

        bodyHEADind = self.form.bodyHeadLabel.currentIndex()
        pointNames = self.bodyObjects[bodyHEADind].pointNames
        pointLabels = self.bodyObjects[bodyHEADind].pointLabels
            
        pointHEADindex = self.form.pointHeadLabel.currentIndex()
        self.jointTaskObject.pointHEADName = pointNames[pointHEADindex]
        self.jointTaskObject.pointHEADLabel = pointLabels[pointHEADindex]
    #  -------------------------------------------------------------------------
    def pointTAILChanged_CallbackF(self):
        """The Point TAIL combo box current index has changed"""
        if Debug:
            DT.Mess("TaskPanelDapJointC-pointTAILChanged_CallbackF")

        bodyTAILindex = self.form.bodyTailLabel.currentIndex()
        pointNames = self.bodyObjects[bodyTAILindex].pointNames
        pointLabels = self.bodyObjects[bodyTAILindex].pointLabels
            
        pointTAILindex = self.form.pointTailLabel.currentIndex()
        self.jointTaskObject.pointTAILName = pointNames[pointTAILindex]
        self.jointTaskObject.pointTAILLabel = pointLabels[pointTAILindex]
    #  -------------------------------------------------------------------------
    def getStandardButtons(self):
        if Debug:
            DT.Mess("TaskPanelDapJointC-getStandardButtons")

        return int(QtGui.QDialogButtonBox.Ok)
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("TaskPanelDapJointC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("TaskPanelDapJointC-__setstate__")
# =============================================================================

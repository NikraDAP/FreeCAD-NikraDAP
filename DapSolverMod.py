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
# *                 This file a sizeable expansion of the:                       *
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

from os import path, getcwd
from math import sin, cos, tan, asin, acos, atan2, pi

import DapToolsMod as DT
import DapMainMod
import Part
import time
if CAD.GuiUp:
    import FreeCADGui as CADGui
    from PySide import QtGui, QtCore
    from pivy import coin
# Select if we want to be in debug mode
global Debug
Debug = False
# =============================================================================
def makeDapSolver(name="DapSolver"):
    """Create a Dap Solver object"""

    if Debug:
        DT.Mess("makeDapSolver")

    objSolver = CAD.ActiveDocument.addObject("Part::FeaturePython", name)

    DapSolverC(objSolver)

    if CAD.GuiUp:
        ViewProviderDapSolverC(objSolver.ViewObject)

    if Debug:
        DT.Mess("-" * 10 + "makeDapSolver")
        DT.Mess(str(objSolver.__dict__) + "")
        DT.Mess("-" * 40 + "")

    return objSolver
# =============================================================================
class CommandDapSolverC:

    if Debug:
        DT.Mess("CommandDapSolverC-CLASS")

    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by CAD when 'CADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""
        if Debug:
            DT.Mess("CommandDapSolverC-GetResources")

        return {
            "Pixmap": path.join(DT.getDapModulePath(), "icons", "Icon7n.png"),
            "MenuText": QtCore.QT_TRANSLATE_NOOP("Dap_Solver_alias", "Run the analysis"),
            "ToolTip": QtCore.QT_TRANSLATE_NOOP("Dap_Solver_alias", "Run the analysis."),
        }

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out"""

        if Debug:
            DT.Mess("CommandDapSolverC-IsActive(query)")

        return DT.getActiveContainerObject() is not None and DT.getMaterialObject() is not None

    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Solver command is run"""

        if Debug:
            DT.Mess("CommandDapSolverC-Activated")

        # Re-use the old solver object if it exists
        # Otherwise create a new solver object
        activeContainer = DT.getActiveContainerObject()
        solverObject = None
        for groupMember in activeContainer.Group:
            if "DapSolver" in groupMember.Name:
                solverObject = groupMember
                break
            
        if solverObject is None:
            DT.getActiveContainerObject().addObject(makeDapSolver())
            CADGui.ActiveDocument.setEdit(CAD.ActiveDocument.ActiveObject.Name)
        else:
            CADGui.ActiveDocument.setEdit(solverObject.Name)

    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("TaskPanelDapSolverC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("TaskPanelDapSolverC-__setstate__")
    # -------------------------------------------------------------------------------------------------
    def __str__(self):
        return str(self.__dict__)
# =============================================================================
class DapSolverC:
    if Debug:
        DT.Mess("DapSolverC-CLASS")

    #  -------------------------------------------------------------------------
    def __init__(self, solverObject):
        """Initialise on instantiation of a new solver object"""

        if Debug:
            DT.Mess("DapSolverC-__init__")

        # Set up the initial properties of the Dap Solver
        self.initProperties(solverObject)

        solverObject.Proxy = self

    #  -------------------------------------------------------------------------
    def initProperties(self, solverObject):
        """Initialse all the properties of the solver object"""

        if Debug:
            DT.Mess("DapSolverC-initProperties")

        DT.addObjectProperty(solverObject, "Directory", "", "App::PropertyString", "", "Directory to save data")
        DT.addObjectProperty(solverObject, "StartTime", 0.0, "App::PropertyFloat", "", "Start Time")
        DT.addObjectProperty(solverObject, "EndTime", 10.0, "App::PropertyFloat", "", "End Time")
        DT.addObjectProperty(solverObject, "DeltaTime", 0.01, "App::PropertyFloat", "", "Length of time steps")
        DT.addObjectProperty(solverObject, "DapResultsValid", False, "App::PropertyBool", "", "")
        DT.addObjectProperty(solverObject, "BodyNames", [], "App::PropertyStringList", "", "")
        DT.addObjectProperty(solverObject, "BodyCoG", [], "App::PropertyVectorList", "", "")
    #  -------------------------------------------------------------------------
    def onDocumentRestored(self, solverObject):
        """Initialise again from scratch"""

        if Debug:
            DT.Mess("DapSolverC-onDocumentRestored")

        self.initProperties(solverObject)

    #  -------------------------------------------------------------------------
    def execute(self, solverObject):

        if Debug:
            DT.Mess("DapSolverC-execute")

    #  -------------------------------------------------------------------------
    def onChanged(self, solverObject, property):
        
        #if Debug:
        #    DT.Mess("DapSolverC-onChanged")
        return
    
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("DapSolverC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("DapSolverC-__setstate__")
    # -------------------------------------------------------------------------------------------------
    def __str__(self):
        return str(self.__dict__)
# =============================================================================
class ViewProviderDapSolverC:

    if Debug:
        DT.Mess("ViewProviderDapSolverC-CLASS")

    #  -------------------------------------------------------------------------
    def __init__(self, solverViewObject):

        if Debug:
            DT.Mess("ViewProviderDapSolverC-__init__")

        solverViewObject.Proxy = self

    #  -------------------------------------------------------------------------
    def getIcon(self):

        if Debug:
            DT.Mess("ViewProviderDapSolverC-getIcon")

        icon_path = path.join(DT.getDapModulePath(), "icons", "Icon7n.png")

        return icon_path

    #  -------------------------------------------------------------------------
    def attach(self, solverViewObject):

        if Debug:
            DT.Mess("ViewProviderDapSolverC-attach")

        self.ViewObject = solverViewObject
        self.solverViewObjectObject = solverViewObject.Object
        self.standard = coin.SoGroup()
        solverViewObject.addDisplayMode(self.standard, "Standard")

    #  -------------------------------------------------------------------------
    def getDisplayModes(self, obj):
        """Return an empty list of modes when requested"""

        if Debug:
            DT.Mess("ViewProviderDapSolverC-getDisplayModes")

        modes = []

        return modes

    #  -------------------------------------------------------------------------
    def getDefaultDisplayMode(self):

        if Debug:
            DT.Mess("ViewProviderDapSolverC-getDefaultDisplayMode")

        return "Shaded"

    #  -------------------------------------------------------------------------
    def setDisplayMode(self, mode):

        if Debug:
            DT.Mess("ViewProviderDapSolverC-setDisplayMode")

        return mode

    #  -------------------------------------------------------------------------
    def updateData(self, obj, prop):

        # if Debug:
        # DT.Mess("ViewProviderDapSolverC-updateData")

        return

    #  -------------------------------------------------------------------------
    def doubleClicked(self, solverViewObject):
        """Open up the TaskPanel if it is not open"""
        
        if Debug:
            DT.Mess("ViewProviderDapSolverC-doubleClicked")

        Document = CADGui.getDocument(solverViewObject.Object.Document)
        if not Document.getInEdit():
            Document.setEdit(solverViewObject.Object.Name)
        else:
            CAD.Console.PrintError("Task dialog already active\n")

        return True

    #  -------------------------------------------------------------------------
    def setEdit(self, solverViewObject, mode):
        """Edit the parameters by switching on the task dialog"""

        if Debug:
            DT.Mess("ViewProviderDapSolverC-setEdit")

        taskDialog = TaskPanelDapSolverC(self.solverViewObjectObject)
        CADGui.Control.showDialog(taskDialog)

        return True

    #  -------------------------------------------------------------------------
    def unsetEdit(self, viewobj, mode):
        """Shut down the task dialog"""

        if Debug:
            DT.Mess("ViewProviderDapSolverC-unsetEdit")

        CADGui.Control.closeDialog()

    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("ViewProviderDapSolverC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("ViewProviderDapSolverC-__setstate__")
    # -------------------------------------------------------------------------------------------------
    def __str__(self):
        return str(self.__dict__)
# =============================================================================
class TaskPanelDapSolverC:
    """Taskpanel for Executing DAP Solver User Interface"""

    if Debug:
        DT.Mess("TaskPanelDapSolverC-CLASS")

    #  -------------------------------------------------------------------------
    def __init__(self, solverTaskObject):
        """Run on first instantiation of a TaskPanelDapSolver class"""

        if Debug:
            DT.Mess("TaskPanelDapSolverC-__init__")

        self.solverTaskObject = solverTaskObject
        self.Document = CAD.ActiveDocument

        # Get the directory name to store results in
        if solverTaskObject.Directory == "":
            solverTaskObject.Directory = getcwd()
        self.Directory = solverTaskObject.Directory

        # Load the taskDialog form information
        ui_path = path.join(path.dirname(__file__), "TaskPanelDapSolver.ui")
        self.form = CADGui.PySideUic.loadUi(ui_path)

        # Set up actions on the solver button and fileDirectory browser
        self.form.solveButton.clicked.connect(self.solveButtonClicked)
        self.form.pbBrowseFileDirectory.clicked.connect(self.getFolderDirectory)

        # Set the time in the form
        self.form.startTime.setValue(self.solverTaskObject.StartTime)
        self.form.endTime.setValue(self.solverTaskObject.EndTime)
        self.form.reportingTime.setValue(self.solverTaskObject.DeltaTime)
        self.form.lnedFileDirectory.setText(self.Directory)

        # Set the accuracy in the form
        self.Accuracy = 5
        self.form.Accuracy.setValue(self.Accuracy)
        self.form.Accuracy.valueChanged.connect(self.accuracyChanged)
    #  -------------------------------------------------------------------------
    def accept(self):
        """Run when we press the OK button"""

        if Debug:
            DT.Mess("TaskPanelDapSolverC-accept")

        # Run the routine to close the dialog
        Document = CADGui.getDocument(self.solverTaskObject.Document)
        Document.resetEdit()

        #  Recompute document to update viewprovider based on the shapes
        solverDocName = str(self.solverTaskObject.Document.Name)
        CAD.getDocument(solverDocName).recompute()

    #  -------------------------------------------------------------------------
    def getStandardButtons(self):

        if Debug:
            DT.Mess("TaskPanelDapSolverC-getStandardButtons")

        # Create only an 'OK' button for the solver taskDialog
        return int(QtGui.QDialogButtonBox.Ok)

    #  -------------------------------------------------------------------------
    def storeTimeValues(self):
        """Transfer the times selected in the dialog to our object"""

        if Debug:
            DT.Mess("TaskPanelDapSolverC-storeTimeValues")

        self.solverTaskObject.StartTime = self.form.startTime.value()
        self.solverTaskObject.EndTime = self.form.endTime.value()
        self.solverTaskObject.DeltaTime = self.form.reportingTime.value()

    #  -------------------------------------------------------------------------
    def checkValidityOfTime(self):
        """Reject an incorrect time setting"""

        if Debug:
            DT.Mess("TaskPanelDapSolverC-checkValidityOfTime")

        if self.solverTaskObject.StartTime > self.solverTaskObject.EndTime:
            CAD.Console.PrintError("Start time is greater than end time\n")
            return False
        if self.solverTaskObject.DeltaTime > (self.solverTaskObject.EndTime - self.solverTaskObject.StartTime):
            CAD.Console.PrintError("Reporting time period is greater than the entire time\n")
            return False

        return True

    #  -------------------------------------------------------------------------
    def solveButtonClicked(self):
        """Call the MainSolve() method in the DapMainC class"""

        if Debug:
            DT.Mess("TaskPanelDapSolverC-solveButtonClicked")

        # Change the solve button to red with 'Solving' on it
        self.form.solveButton.setDisabled(True)
        self.form.solveButton.setText("Solving")
        self.form.solveButton.repaint()
        self.form.solveButton.update()
        t = 0.0
        for f in range(1000000):
            t += f/10.0
        self.form.solveButton.repaint()
        self.form.solveButton.update()

        self.solverTaskObject.Directory = self.form.lnedFileDirectory.text()
        self.storeTimeValues()
        if self.checkValidityOfTime() is True:

            # Instantiate the DapMainC class and run the solver
            self.DapMainC_Instance = DapMainMod.DapMainC(self.solverTaskObject.StartTime,
                                                         self.solverTaskObject.EndTime,
                                                         self.solverTaskObject.DeltaTime,
                                                         self.Accuracy,
                                                         self.form.correctInitial.isChecked())
            if self.DapMainC_Instance.initialised is True:
                self.DapMainC_Instance.MainSolve()

        # Return the solve button to green with 'Solve' on it
        self.form.solveButton.setText("Solve")
        self.form.solveButton.setDisabled(False)
        # We end here after the solving has been completed
        # and will wait for the OK button to be clicked
    #  -------------------------------------------------------------------------
    def getFolderDirectory(self):
        """Request the directory where the .csv result files will be written"""
        if Debug:
            DT.Mess("TaskPanelDapSolverC-getFolderDirectory")

        self.solverTaskObject.Directory = QtGui.QFileDialog.getExistingDirectory()
        self.form.lnedFileDirectory.setText(self.solverTaskObject.Directory)

    #  -------------------------------------------------------------------------
    def accuracyChanged(self):
        """Change the accuracy setting when slider has been adjusted"""
        self.Accuracy = self.form.Accuracy.value()
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("TaskPanelDapSolverC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("TaskPanelDapSolverC-__setstate__")
    # -------------------------------------------------------------------------------------------------
    def __str__(self):
        return str(self.__dict__)

    # =============================================================================

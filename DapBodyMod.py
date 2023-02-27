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
import math
import DapToolsMod as DT
if CAD.GuiUp:
    import FreeCADGui as CADGui
    import Part
    from PySide import QtGui, QtCore
    from pivy import coin
global Debug
Debug = False
# ------------------------------------------------------------------------------
def makeDapBody(name="DapBody"):
    """Create a Dap Body object"""
    if Debug:
        DT.Mess("makeDapBody")

    # Create the FreeCAD body Object
    bodyObject = CAD.ActiveDocument.addObject("Part::FeaturePython", name)
    # Instantiate and initialise the DapBodyC class
    DapBodyC(bodyObject)
    # Instantiate the class to handle the Gui stuff
    if CAD.GuiUp:
        ViewProviderDapBodyC(bodyObject.ViewObject)

    return bodyObject
# ==============================================================================
class CommandDapBodyC:
    if Debug:
        DT.Mess("CommandDapBodyC-CLASS")
    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by FreeCAD when 'CADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""
        if Debug:
            DT.Mess("CommandDapBodyC-GetResources")

        return {
            "Pixmap": path.join(DT.getDapModulePath(), "icons", "Icon3n.png"),
            "MenuText": QtCore.QT_TRANSLATE_NOOP("Dap_Body_alias", "Body Definition"),
            "ToolTip": QtCore.QT_TRANSLATE_NOOP("Dap_Body_alias", "Creates and defines a body for the DAP analysis"), }
    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out
        Only activate it when there is at least a container defined"""
        if Debug:
            DT.Mess("CommandDapBodyC-IsActive(query)")
        # Allow the body icon to be active only if we have a DAP container instantiated already
        return DT.getActiveContainerObject() is not None
    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Body Selection command is run"""
        if Debug:
            DT.Mess("CommandDapBodyC-Activated")

        # This is where we create a new empty Dap Body object
        DT.getActiveContainerObject().addObject(makeDapBody())
        # Call the task panel to edit any parameters as necessary
        CADGui.ActiveDocument.setEdit(CAD.ActiveDocument.ActiveObject.Name)
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("CommandDapBody-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("CommandDapBodyC-__setstate__")
# ==============================================================================
class DapBodyC:
    if Debug:
        DT.Mess("DapBodyC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(self, bodyObject):
        """Initialise on instantiation of a new DAP body object"""
        if Debug:
            DT.Mess("DapBodyC-__init__")

        bodyObject.Proxy = self

        # Set up the initial properties of the Dap Body
        # Call a separate function to do this, so we can reuse it
        # when we restore the document (i.e. when loading a saved model)
        self.initProperties(bodyObject)
    #  -------------------------------------------------------------------------
    def onDocumentRestored(self, bodyObject):
        """Initialise again from scratch when we load a DAP model etc."""
        if Debug:
            DT.Mess("DapBodyC-onDocumentRestored")
        self.initProperties(bodyObject)
    #  -------------------------------------------------------------------------
    def initProperties(self, bodyObject):
        """Initialise the properties on instantiation of a new body object
        or on Document Restored"""
        if Debug:
            DT.Mess("DapBodyC-initProperties")

        DT.addObjectProperty(bodyObject, "movingBody", True, "App::PropertyBool", "Body", "Body moves or is Stationary")

        DT.addObjectProperty(bodyObject, "ass4SolidsNames", [], "App::PropertyStringList", "Body", "Names of Assembly 4 Solid Parts comprising this body")
        DT.addObjectProperty(bodyObject, "ass4SolidsLabels", [], "App::PropertyStringList", "Body", "Labels of Assembly 4 Solid Parts comprising this body")

        DT.addObjectProperty(bodyObject, "Mass", 1.0, "App::PropertyFloat", "Body", "Mass")
        DT.addObjectProperty(bodyObject, "centreOfGravity", CAD.Vector(), "App::PropertyVector", "Body", "Centre of gravity")
        DT.addObjectProperty(bodyObject, "weightVector", CAD.Vector(), "App::PropertyVector", "Body", "Weight as a force vector")
        DT.addObjectProperty(bodyObject, "momentInertia", 1.0, "App::PropertyFloat", "Body", "Moment of inertia")

        DT.addObjectProperty(bodyObject, "world", CAD.Placement(), "App::PropertyPlacement", "X Y Z Phi", "Body LCS relative to origin")
        DT.addObjectProperty(bodyObject, "worldDot", CAD.Vector(), "App::PropertyVector", "X Y Z Phi", "Time derivative of x y z")
        DT.addObjectProperty(bodyObject, "phiDot", 0.0, "App::PropertyFloat", "X Y Z Phi", "Angular velocity of phi")

        # All the sub-part bodies [including the main body] are included in the point lists as extra points
        # All points/bodies are local and relative to world placement above

        DT.addObjectProperty(bodyObject, "pointNames", [], "App::PropertyStringList", "Points", "List of Point names associated with this body")
        DT.addObjectProperty(bodyObject, "pointLabels", [], "App::PropertyStringList", "Points", "List of Point labels associated with this body")
        DT.addObjectProperty(bodyObject, "pointLocals", [], "App::PropertyVectorList", "Points", "Vectors relative to local LCS")
    #  -------------------------------------------------------------------------
    def onChanged(self, bodyObject, newproperty):
        # if Debug:
        #    DT.Mess("DapBodyC-onChanged")
        return
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("DapBodyC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("DapBodyC-__setstate__")
# ==============================================================================
class ViewProviderDapBodyC:
    """A class which handles all the gui overheads"""
    if Debug:
        DT.Mess("ViewProviderDapBodyC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(self, bodyViewObject):
        if Debug:
            DT.Mess("ViewProviderDapBodyC-__init__")
        bodyViewObject.Proxy = self
    #  -------------------------------------------------------------------------
    def getIcon(self):
        if Debug:
            DT.Mess("ViewProviderDapBodyC-getIcon")
        return path.join(DT.getDapModulePath(), "icons", "Icon3n.png")
    #  -------------------------------------------------------------------------
    def attach(self, bodyViewObject):
        if Debug:
            DT.Mess("ViewProviderDapBodyC-attach")
        bodyViewObject.addDisplayMode(coin.SoGroup(), "Standard")
    #  -------------------------------------------------------------------------
    def getDisplayModes(self, bodyViewObject):
        """Return an empty list of modes when requested"""
        if Debug:
            DT.Mess("ViewProviderDapBodyC-getDisplayModes")
        return []
    #  -------------------------------------------------------------------------
    def getDefaultDisplayMode(self):
        if Debug:
            DT.Mess("ViewProviderDapBodyC-getDefaultDisplayMode")
        return "Shaded"
    #  -------------------------------------------------------------------------
    def setDisplayMode(self, mode):
        if Debug:
            DT.Mess("ViewProviderDapBodyC-setDisplayMode")
        return mode
    #  -------------------------------------------------------------------------
    def updateData(self, obj, prop):
        # if Debug:
        # DT.Mess("ViewProviderDapBodyC-updateData")
        return
    #  -------------------------------------------------------------------------
    def doubleClicked(self, bodyViewObject):
        """Activate the dialog if the document item is double-clicked
        If it is already active, raise a benign warning in the console"""
        if Debug:
            DT.Mess("ViewProviderDapBodyC-doubleClicked")

        Document = CADGui.getDocument(bodyViewObject.Object.Document)
        if not Document.getInEdit():
            Document.setEdit(bodyViewObject.Object.Name)
        else:
            DT.Mess("Task dialog already active")
        return True
    #  -------------------------------------------------------------------------
    def setEdit(self, bodyViewObject, mode):
        """Edit the parameters by calling the task dialog"""
        if Debug:
            DT.Mess("ViewProviderDapBodyC-setEdit")
        CADGui.Control.showDialog(TaskPanelDapBodyC(bodyViewObject.Object))
        return True
    #  -------------------------------------------------------------------------
    def unsetEdit(self, bodyViewObject, mode):
        """We have finished with the task dialog so close it"""
        if Debug:
            DT.Mess("ViewProviderDapBodyC-unsetEdit")
        CADGui.Control.closeDialog()
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("ViewProviderDapBodyC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("ViewProviderDapBodyC-__setstate__")
# ==============================================================================
class TaskPanelDapBodyC:
    """Task panel for adding and editing DAP Bodies"""
    if Debug:
        DT.Mess("TaskPanelDapBodyC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(self, bodyObj):
        """Run on first instantiation of a TaskPanelDapBody class
        or when the body is re-built on loading of saved model etc
        [Called explicitly by FreeCAD]"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-__init__")

        # Remember stuff to refer to later
        self.bodyObj = bodyObj
        self.taskDocument = CAD.getDocument(self.bodyObj.Document.Name)
        self.bodyObj.Proxy = self
        
        # Set up the form used to create the dialog box
        ui_path = path.join(path.dirname(__file__), "TaskPanelDapBodies.ui")
        self.form = CADGui.PySideUic.loadUi(ui_path)

        # Give the body a nice transparent blue colour
        self.bodyObj.ViewObject.Transparency = 80
        self.bodyObj.ViewObject.ShapeColor = (0.0, 0.0, 1.0, 1.0)
        CADGui.Selection.addObserver(self.bodyObj)

        # --------------------------------------------------------
        # Set up the movement plane normal stuff in the dialog box
        # --------------------------------------------------------
        # Fetch the movementPlaneNormal vector from the container and
        # normalize the LARGEST coordinate to 1
        # (i.e. it is easier to visualise [0, 1, 1] instead of [0, 0.707, 0.707] or [0.577, 0.577, 0.577])
        self.movementPlaneNormal = DT.getActiveContainerObject().movementPlaneNormal
        maxCoordinate = 1
        if self.movementPlaneNormal.Length == 0:
            CAD.Console.PrintError("The plane normal vector is the null vector - this should never occur\n")
        else:
            if abs(self.movementPlaneNormal.x) > abs(self.movementPlaneNormal.y):
                if abs(self.movementPlaneNormal.x) > abs(self.movementPlaneNormal.z):
                    maxCoordinate = abs(self.movementPlaneNormal.x)
                else:
                    maxCoordinate = abs(self.movementPlaneNormal.z)
            else:
                if abs(self.movementPlaneNormal.y) > abs(self.movementPlaneNormal.z):
                    maxCoordinate = abs(self.movementPlaneNormal.y)
                else:
                    maxCoordinate = abs(self.movementPlaneNormal.z)
        self.movementPlaneNormal /= maxCoordinate

        # Tick the checkboxes where the Plane Normal has a non-zero value
        self.form.planeX.setChecked(abs(self.movementPlaneNormal.x) > 1e-6)
        self.form.planeY.setChecked(abs(self.movementPlaneNormal.y) > 1e-6)
        self.form.planeZ.setChecked(abs(self.movementPlaneNormal.z) > 1e-6)
        # Transfer the X/Y/Z plane normal coordinates to the form
        self.form.planeXdeci.setValue(self.movementPlaneNormal.x)
        self.form.planeYdeci.setValue(self.movementPlaneNormal.y)
        self.form.planeZdeci.setValue(self.movementPlaneNormal.z)
        
        # Set the Define Plane tick box as un-ticked
        self.form.definePlaneNormal.setChecked(False)
        # TEMPORARY #######################################################
        # Temporarily disable changing to an alternative movement plane
        self.form.definePlaneNormal.setDisabled(True)
        self.form.definePlaneNormalLabel.setDisabled(True)
        # TEMPORARY #######################################################
        # Disable the PlaneNormal tick boxes
        self.form.planeX.setEnabled(False)
        self.form.planeY.setEnabled(False)
        self.form.planeZ.setEnabled(False)
        self.form.planeXdeci.setEnabled(False)
        self.form.planeYdeci.setEnabled(False)
        self.form.planeZdeci.setEnabled(False)

        # Clean things up to reflect what we have changed
        self.PlaneNormal_CallbackF()
        
        # -----------------------------
        # Set up the assembly 4 objects
        # -----------------------------
        # Get any existing list of ass4Solids in this body
        self.ass4SolidsNames = self.bodyObj.ass4SolidsNames
        self.ass4SolidsLabels = self.bodyObj.ass4SolidsLabels

        # Get the list of ALL possible ass4Solids in the whole kaboodle
        self.modelAss4SolidsNames, self.modelAss4SolidsLabels, self.modelAss4SolidObjectsList = DT.getAllSolidsLists()
            
        # Set up the model ass4Solids list in the combo selection box
        self.form.partLabel.clear()
        self.form.partLabel.addItems(self.modelAss4SolidsLabels)
        self.form.partLabel.setCurrentIndex(0)
        self.selectedAss4SolidsToFormF()

        # -------------------------------------------
        # Set up the rest of the things in the dialog
        # -------------------------------------------
        # Set up moving or not
        self.form.movingBody.setChecked(self.bodyObj.movingBody)
        self.movingBodyChanged_CallbackF()

        # Populate the form with velocities
        self.velocitiesToFormXF()
        self.velocitiesToFormYF()
        self.velocitiesToFormZF()
        self.angularVelToFormValF()

        # Set the Radians and m/s radio buttons as the default
        self.form.radians.setChecked(True)
        self.form.mms.setChecked(True)

        # --------------------------------------------------------
        # Set up the callback functions for various things changed
        # --------------------------------------------------------
        self.form.buttonRemovePart.clicked.connect(self.buttonRemovePartClicked_CallbackF)
        self.form.buttonAddPart.clicked.connect(self.buttonAddPartClicked_CallbackF)
        self.form.partsList.currentRowChanged.connect(self.partsListRowChanged_CallbackF)
        self.form.movingBody.toggled.connect(self.movingBodyChanged_CallbackF)
        self.form.planeX.toggled.connect(self.PlaneNormal_CallbackF)
        self.form.planeY.toggled.connect(self.PlaneNormal_CallbackF)
        self.form.planeZ.toggled.connect(self.PlaneNormal_CallbackF)
        self.form.planeXdeci.valueChanged.connect(self.PlaneNormal_CallbackF)
        self.form.planeYdeci.valueChanged.connect(self.PlaneNormal_CallbackF)
        self.form.planeZdeci.valueChanged.connect(self.PlaneNormal_CallbackF)
        self.form.definePlaneNormal.toggled.connect(self.PlaneNormal_CallbackF)

        self.form.velocityX.valueChanged.connect(self.velocitiesFromFormXF)
        self.form.velocityY.valueChanged.connect(self.velocitiesFromFormYF)
        self.form.velocityZ.valueChanged.connect(self.velocitiesFromFormZF)
        self.form.angularVelocity.valueChanged.connect(self.angularVelFromFormValF)

        self.form.mms.toggled.connect(self.velocitiesToFormXF)
        self.form.mms.toggled.connect(self.velocitiesToFormYF)
        self.form.mms.toggled.connect(self.velocitiesToFormZF)
        self.form.ms.toggled.connect(self.velocitiesToFormXF)
        self.form.ms.toggled.connect(self.velocitiesToFormYF)
        self.form.ms.toggled.connect(self.velocitiesToFormZF)
        self.form.degrees.toggled.connect(self.angularVelToFormValF)
        self.form.radians.toggled.connect(self.angularVelToFormValF)
    #  -------------------------------------------------------------------------
    def accept(self):
        """Run when we press the OK button - we have finished all the hard work
           now transfer it into the DAP body object"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-accept")

        # Refuse to 'OK' if no part references have been defined
        if len(self.ass4SolidsLabels) == 0:
            CAD.Console.PrintError("No Parts have been added to this body\n")
            CAD.Console.PrintError("First add at least one Part to this body\n")
            CAD.Console.PrintError("        or alternatively:\n")
            CAD.Console.PrintError("add any part to it, 'OK' the body,\n")
            CAD.Console.PrintError("and then delete it from the DapContainer tree\n\n")
            return

        # Store the normalised plane Normal into the container object
        # If it is still undefined (zero vector) then set plane normal to z
        if self.movementPlaneNormal == CAD.Vector(0, 0, 0):
            self.movementPlaneNormal.z = 1.0
        self.movementPlaneNormal /= self.movementPlaneNormal.Length
        DT.getActiveContainerObject().movementPlaneNormal = self.movementPlaneNormal

        # Run through the sub-parts and add all Shapes into a ShapeList
        ShapeList = []
        for ass4Solids in self.ass4SolidsNames:
            solidObject = self.taskDocument.findObjects(Name="^" + ass4Solids + "$")[0]
            # Put all the referenced shapes into a list
            ShapeList.append(solidObject.Shape)

        # Start off with an empty shape
        self.bodyObj.Shape = Part.Shape()
        # Replace empty shape with a new compound one
        if len(ShapeList) > 0:
            # Make a Part.Compound shape out of all the Referenced shapes in the list
            CompoundShape = Part.makeCompound(ShapeList)
            if CompoundShape is not None:
                # Store this compound shape into the body object
                self.bodyObj.Shape = CompoundShape
            else:
                # Otherwise flag that no object has a shape
                CAD.Console.PrintError("Compound Body has no shape - this should not occur\n")

        # Transfer the names and labels to the bodyObj
        self.bodyObj.ass4SolidsNames = self.ass4SolidsNames
        self.bodyObj.ass4SolidsLabels = self.ass4SolidsLabels

        # Save the information to the point lists
        pointNames = []
        pointLabels = []
        pointLocals = []
        
        # Get the info for the main (first) Assembly-4 Solid in the DapBody
        mainSolidObject = self.taskDocument.findObjects(Name="^" + self.ass4SolidsNames[0] + "$")[0]

        # Save this world body PLACEMENT in the body object -
        # POA_O is P-lacement from O-rigin to body A LCS in world (O-rigin) coordinates
        POA_O = mainSolidObject.Placement
        self.bodyObj.world = POA_O

        # Process all POINTS belonging to the main Solid (Solid A)
        # VAa_A is the local V-ector from solid A to point a in solid A local coordinates
        for mainPoint in mainSolidObject.Group:
            if hasattr(mainPoint, 'MapMode') and not \
                    ('Wire' in str(mainPoint.Shape)) and not \
                    ('Sketch' in str(mainPoint.Name)):
                pointNames.append(mainSolidObject.Name + "-{" + mainPoint.Name + "}")     # the name of the associated point
                pointLabels.append(mainSolidObject.Label + "-{" + mainPoint.Label + "}")  # the label of the associated point
                VAa_A = CAD.Vector(mainPoint.Placement.Base)
                pointLocals.append(VAa_A)

                if Debug:
                    DT.MessNoLF("Local vector from " + mainSolidObject.Label +
                                " to point " + mainPoint.Label +
                                " in " + mainSolidObject.Label + " coordinates: ")
                    DT.PrintVec(VAa_A)

        # Now convert all other solids (i.e. from 1 onward) and their points into points relative to the solid A LCS
        if len(self.ass4SolidsNames) > 1:
            for assIndex in range(1, len(self.ass4SolidsNames)):
                subAss4SolidsObject = self.taskDocument.findObjects(Name="^" + self.ass4SolidsNames[assIndex] + "$")[0]
                # Find the relationship between the subAss4SolidsPlacement and the mainSolidObject.Placement
                # i.e. from LCS of solid A to the LCS of solid B (in terms of the local coordinates of A)
                pointNames.append(subAss4SolidsObject.Name + "-{" + self.ass4SolidsNames[assIndex] + "}")
                pointLabels.append(subAss4SolidsObject.Label + "-{" + self.ass4SolidsLabels[assIndex] + "}")
                POB_O = subAss4SolidsObject.Placement
                VAB_A = POA_O.toMatrix().inverse().multVec(POB_O.Base)
                pointLocals.append(VAB_A)

                if Debug:
                    DT.MessNoLF("Vector from origin to " +
                            subAss4SolidsObject.Label + " in world coordinates: ")
                    DT.PrintVec(POB_O.Base)
                    DT.MessNoLF("Local vector from " + mainSolidObject.Label +
                                " to " + subAss4SolidsObject.Label +
                                " in " + mainSolidObject.Label + " coordinates: ")
                    DT.PrintVec(VAB_A)

                # Now handle all the points which are inside Solid B
                for sub_member in subAss4SolidsObject.Group:
                    if hasattr(sub_member, 'MapMode'):
                        if not ('Wire' in str(sub_member.Shape)):
                            if not ('Sketch' in str(sub_member.Label)):
                                pointNames.append(subAss4SolidsObject.Name + "-{" + sub_member.Name + "}")
                                pointLabels.append(subAss4SolidsObject.Label + "-{" + sub_member.Label + "}")
                                VBb_B = sub_member.Placement.Base                 # VBb_B: the local vector from the LCS of solid B to the point b
                                VOb_O = POB_O.toMatrix().multVec(VBb_B)           # VOb_O: the vector from the origin to the point b in solid B
                                VAb_A = POA_O.toMatrix().inverse().multVec(VOb_O) # VAb_A: the local vector from solid A LCS to the point b in solid B
                                pointLocals.append(VAb_A)

                                if Debug:
                                    DT.MessNoLF("Vector from origin to " + subAss4SolidsObject.Label +
                                                " in world coordinates: ")
                                    DT.PrintVec(POB_O.Base)
                                    DT.MessNoLF("Relationship between the " + subAss4SolidsObject.Label +
                                            " Vector and the " + mainSolidObject.Label +
                                            " Vector in " + mainSolidObject.Label + " coordinates: ")
                                    DT.PrintVec(VAB_A)
                                    DT.MessNoLF("Local vector from " + subAss4SolidsObject.Label +
                                            " to the point " + sub_member.Label + ": ")
                                    DT.PrintVec(VBb_B)
                                    DT.MessNoLF("Vector from the origin to the point " + sub_member.Label +
                                            " in body " + subAss4SolidsObject.Label + ": ")
                                    DT.PrintVec(VOb_O)
                                    DT.MessNoLF("Local vector from " + mainSolidObject.Label +
                                            " to the point " + sub_member.Label +
                                            " in body " + subAss4SolidsObject.Label + ": ")
                                    DT.PrintVec(VAb_A)
        if Debug:
            DT.Mess("Names: ")
            DT.Mess(pointNames)
            DT.Mess("Labels: ")
            DT.Mess(pointLabels)
            DT.Mess("Locals: ")
            for vec in pointLocals:
                DT.PrintVec(vec)

        # Condense all the duplicate points into one
        # And save them in the bodyObject
        self.condensePointsF(pointNames, pointLabels, pointLocals)
        self.bodyObj.pointNames = pointNames
        self.bodyObj.pointLabels = pointLabels
        self.bodyObj.pointLocals = pointLocals

        # Recompute document to update view provider based on the shapes
        self.bodyObj.recompute()

        # Switch off the Task panel
        GuiDocument = CADGui.getDocument(self.bodyObj.Document)
        GuiDocument.resetEdit()
    #  -------------------------------------------------------------------------
    def getStandardButtons(self):
        """ Set which button will appear at the top of the TaskDialog
        [Called from FreeCAD]"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-getStandardButtons")
        return int(QtGui.QDialogButtonBox.Ok)
    #  -------------------------------------------------------------------------
    def selectedAss4SolidsToFormF(self):
        """The ass4Solids list is the list of all the parts which make up this body.
        Rebuild the ass4Solids list in the task panel dialog form from our copy of it"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-selectedAss4SolidsToFormF")
        self.form.partsList.clear()
        for subBody in self.ass4SolidsLabels:
            self.form.partsList.addItem(subBody)
    #  -------------------------------------------------------------------------
    def velocitiesToFormXF(self):
        """Rebuild the velocities in the form when we have changed the X component"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-velocitiesToFormF")
        # If we have checked m/s units then convert to meters per second
        if self.form.ms.isChecked():
            self.form.velocityX.setValue(self.bodyObj.worldDot.x / 1000.0)
        else:
            self.form.velocityX.setValue(self.bodyObj.worldDot.x)
    #  -------------------------------------------------------------------------
    def velocitiesToFormYF(self):
        """Rebuild the velocities in the form when we have changed the Y component"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-velocitiesToFormF")
        # If we have checked m/s units then convert to meters per second
        if self.form.ms.isChecked():
            self.form.velocityY.setValue(self.bodyObj.worldDot.y / 1000.0)
        else:
            self.form.velocityY.setValue(self.bodyObj.worldDot.y)
    #  -------------------------------------------------------------------------
    def velocitiesToFormZF(self):
        """Rebuild the velocities in the form when we have changed the Z component"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-velocitiesToFormF")
        # If we have checked m/s units then convert to meters per second
        if self.form.ms.isChecked():
            self.form.velocityZ.setValue(self.bodyObj.worldDot.z / 1000.0)
        else:
            self.form.velocityZ.setValue(self.bodyObj.worldDot.z)
    #  -------------------------------------------------------------------------
    def angularVelToFormValF(self):
        """Rebuild the velocities in the form when we have changed the angular velocity"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-velocitiesToFormF")
        # If we have checked degrees units then convert to deg/s from rad/s
        if self.form.degrees.isChecked():
            self.form.angularVelocity.setValue(self.bodyObj.phiDot * 180.0 / math.pi)
        else:
            self.form.angularVelocity.setValue(self.bodyObj.phiDot)
    #  -------------------------------------------------------------------------
    def velocitiesFromFormXF(self):
        """Rebuild when we have changed something"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-velocitiesFromFormF")
        # If we have checked m/s units then convert from meters per second
        if self.form.ms.isChecked():
            self.bodyObj.worldDot.x = self.form.velocityX.value() * 1000.0
        else:
            self.bodyObj.worldDot.x = self.form.velocityX.value()
    #  -------------------------------------------------------------------------
    def velocitiesFromFormYF(self):
        """Rebuild when we have changed something"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-velocitiesFromFormF")
        # If we have checked m/s units then convert from meters per second
        if self.form.ms.isChecked():
            self.bodyObj.worldDot.y = self.form.velocityY.value() * 1000.0
        else:
            self.bodyObj.worldDot.y = self.form.velocityY.value()
    #  -------------------------------------------------------------------------
    def velocitiesFromFormZF(self):
        """Rebuild when we have changed something"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-velocitiesFromFormF")
        # If we have checked m/s units then convert from meters per second
        if self.form.ms.isChecked():
            self.bodyObj.worldDot.z = self.form.velocityZ.value() * 1000.0
        else:
            self.bodyObj.worldDot.z = self.form.velocityZ.value()
    #  -------------------------------------------------------------------------
    def angularVelFromFormValF(self):
        """Rebuild when we have changed something"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-velocitiesFromFormF")
        # If we have checked degrees units then convert to rad/s from deg/s
        if self.form.degrees.isChecked():
            self.bodyObj.phiDot = self.form.angularVelocity.value() * math.pi / 180.0
        else:
            self.bodyObj.phiDot = self.form.angularVelocity.value()
    # --------------------------------------------------------------------------
    def condensePointsF(self, pointNames, pointLabels, pointLocals):
        """Condense all the duplicate points into one"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-condensePointsF")

        # Condense all the duplicate points in this specific body into one
        numPoints = len(pointLocals)
        i = 0
        while i < numPoints:
            j = i + 1
            while j < numPoints:
                if abs(pointLocals[i].x - pointLocals[j].x) < 1.0e-10:
                    if abs(pointLocals[i].y - pointLocals[j].y) < 1.0e-10:
                        if abs(pointLocals[i].z - pointLocals[j].z) < 1.0e-10:
                            # Compare the body names (i.e. the string from beginning to '{'
                            labeli = pointLabels[i][:pointLabels[i].index('{')]
                            labelj = pointLabels[j][:pointLabels[j].index('{')]
                            if labeli == labelj:
                                if Debug:
                                    DT.MessNoLF("Combining: ")
                                    DT.MessNoLF(pointLabels[i])
                                    DT.MessNoLF(" and ")
                                    DT.Mess(pointLabels[j])
                                pointNames[i] = pointNames[i] + "-" + pointNames[j][pointNames[j].index('{'):]
                                pointLabels[i] = pointLabels[i] + "-" + pointLabels[j][pointLabels[j].index('{'):]
                                # Shift the others up to remove the duplicate
                                k = j + 1
                                while k < numPoints:
                                    pointNames[k - 1] = pointNames[k]
                                    pointLabels[k - 1] = pointLabels[k]
                                    pointLocals[k - 1] = pointLocals[k]
                                    k += 1
                                # Pop the bottom item off the lists
                                pointNames.pop()
                                pointLabels.pop()
                                pointLocals.pop()
                                numPoints -= 1
                j += 1
            i += 1
        # Now, condense all the duplicate points into one, irrespective of body name
        numPoints = len(pointLocals)
        i = 0
        while i < numPoints:
            j = i + 1
            while j < numPoints:
                if abs(pointLocals[i].x - pointLocals[j].x) < 1.0e-10:
                    if abs(pointLocals[i].y - pointLocals[j].y) < 1.0e-10:
                        if abs(pointLocals[i].z - pointLocals[j].z) < 1.0e-10:
                            if Debug:
                                DT.MessNoLF("Combining: ")
                                DT.MessNoLF(pointLabels[i])
                                DT.MessNoLF(" and ")
                                DT.Mess(pointLabels[j])
                            pointNames[i] = pointNames[i] + "-" + pointNames[j]
                            pointLabels[i] = pointLabels[i] + "-" + pointLabels[j]
                            if Debug:
                                DT.Mess(pointLabels[i])
                            # Shift the others up to remove the duplicate
                            k = j + 1
                            while k < numPoints:
                                pointNames[k - 1] = pointNames[k]
                                pointLabels[k - 1] = pointLabels[k]
                                pointLocals[k - 1] = pointLocals[k]
                                k += 1
                            # Pop the bottom item off the lists
                            pointNames.pop()
                            pointLabels.pop()
                            pointLocals.pop()
                            numPoints -= 1
                j += 1
            i += 1

        # If we are debugging, Print out all the body's and point's placements etc
        if Debug:
            DT.Mess("===================================================================")
            DT.Mess("Body: " + self.bodyObj.Label + "")
            DT.Mess("===================================================================")
            BodyPlacementMatrix = self.bodyObj.world.toMatrix()
            for index in range(len(pointNames)):
                DT.Mess("-------------------------------------------------------------------")
                DT.Mess("Point Name: " + str(pointNames[index]))
                DT.Mess("Point Label:  " + str(pointLabels[index]))
                DT.Mess("")
                DT.MessNoLF("Point Local Vector:")
                DT.PrintVec(pointLocals[index])
                DT.MessNoLF("Point World Vector:")
                DT.PrintVec(CAD.Vector(BodyPlacementMatrix.multVec(pointLocals[index])))
                DT.Mess("")
    #  -------------------------------------------------------------------------
    def PlaneNormal_CallbackF(self):
        """Rebuild when we have changed something to do with the plane normal"""
        if Debug:
            DT.Mess("PlaneNormal_CallbackF")

        if not self.form.definePlaneNormal.isChecked():
            # Hide the movementPlaneNormal tick boxes if the define tickbox is unchecked
            self.form.planeX.setEnabled(False)
            self.form.planeY.setEnabled(False)
            self.form.planeZ.setEnabled(False)
            self.form.planeXdeci.setEnabled(False)
            self.form.planeYdeci.setEnabled(False)
            self.form.planeZdeci.setEnabled(False)

            self.taskDocument.recompute()
            return

        # Show the tick boxes
        self.form.planeX.setEnabled(True)
        self.form.planeY.setEnabled(True)
        self.form.planeZ.setEnabled(True)
        self.form.planeXdeci.setEnabled(True)
        self.form.planeYdeci.setEnabled(True)
        self.form.planeZdeci.setEnabled(True)

        # All the following paraphanalia is to handle various methods of defining the plane vector
        if self.form.planeX.isChecked():
            self.movementPlaneNormal.x = self.form.planeXdeci.value()
            if self.movementPlaneNormal.x == 0:
                self.movementPlaneNormal.x = 1.0
                self.form.planeXdeci.setValue(1.0)
        else:
            self.movementPlaneNormal.x = 0.0
            self.form.planeXdeci.setValue(0.0)

        if self.form.planeY.isChecked():
            self.movementPlaneNormal.y = self.form.planeYdeci.value()
            if self.movementPlaneNormal.y == 0:
                self.movementPlaneNormal.y = 1.0
                self.form.planeYdeci.setValue(1.0)
        else:
            self.movementPlaneNormal.y = 0.0
            self.form.planeYdeci.setValue(0.0)

        if self.form.planeZ.isChecked():
            self.movementPlaneNormal.z = self.form.planeZdeci.value()
            if self.movementPlaneNormal.z == 0:
                self.movementPlaneNormal.z = 1.0
                self.form.planeZdeci.setValue(1.0)
        else:
            self.movementPlaneNormal.z = 0.0
            self.form.planeZdeci.setValue(0.0)

        if self.movementPlaneNormal == CAD.Vector(0, 0, 0):
            self.movementPlaneNormal.z = 1.0

        # Make a temporary plane and normal vector in the object view box to show the movement plane
        cylinder = Part.makeCylinder(5, 300, CAD.Vector(0, 0, 0), self.movementPlaneNormal)
        plane = Part.makeCylinder(500, 1, CAD.Vector(0, 0, 0), self.movementPlaneNormal)
        cone = Part.makeCone(10, 0, 20, CAD.Vector(self.movementPlaneNormal).multiply(300), self.movementPlaneNormal)
        planeNormal = Part.makeCompound([cylinder, plane, cone])

        self.bodyObj.Shape = planeNormal
        self.bodyObj.ViewObject.Transparency = 80
        self.bodyObj.ViewObject.ShapeColor = (0.0, 1.0, 0.0, 1.0)

        self.taskDocument.recompute()
    #  -------------------------------------------------------------------------
    def movingBodyChanged_CallbackF(self):
        """Run when we have changed the Fixed/Moving tick box"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-movingBodyChanged_CallbackF")

        self.bodyObj.movingBody = self.form.movingBody.isChecked()

        # Check that we have only one ground body defined and require change if necessary
        containerObject = DT.getActiveContainerObject()
        groundBodyName = containerObject.groundBodyName
        groundBodyLabel = containerObject.groundBodyLabel
        if self.bodyObj.movingBody is False:
            self.form.velocityGroup.setDisabled(True)
            # If there is no ground body yet, set this one to be the ground body
            if groundBodyName == "":
                containerObject.groundBodyName = self.bodyObj.Name
                containerObject.groundBodyLabel = self.bodyObj.Label
                self.form.velocityGroup.setDisabled(True)
            else:
                # We already have a different ground body, so warn the user to change one of them
                if containerObject.groundBodyName != self.bodyObj.Name:
                    CAD.Console.PrintError("One and only one ground object must be defined\n")
                    CAD.Console.PrintError("Consolidate all stationary objects into '" + str(groundBodyLabel) + "'\n")
                    CAD.Console.PrintError("or first change body '" + str(groundBodyLabel) + "' to a moving body\n\n")
                    self.form.movingBody.setChecked(True)
                    return
        else:
            # This is a moving body, so enable the velocity inputs
            self.form.velocityGroup.setEnabled(True)
            # Cancel the groundBodyName if it previously was a non-moving Body
            if groundBodyName == self.bodyObj.Name:
                containerObject.groundBodyName = ""
                containerObject.groundBodyLabel = ""
            
        # If ground (not moving) then there can be no velocity
        if self.bodyObj.movingBody is False:
            self.bodyObj.worldDot = CAD.Vector()
            self.bodyObj.phiDot = 0
    #  -------------------------------------------------------------------------
    def buttonAddPartClicked_CallbackF(self):
        """Run when we click the add part button"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-buttonAddPartClicked_CallbackF")

        # Find the object for the part name we have selected
        partIndex = self.form.partLabel.currentIndex()
        addPartObject = self.modelAss4SolidObjectsList[partIndex]
        # Add it to the list of ass4SolidsLabels if it is not already there
        if addPartObject.Name not in self.ass4SolidsNames:
            self.ass4SolidsNames.append(self.modelAss4SolidsNames[partIndex])
            self.ass4SolidsLabels.append(self.modelAss4SolidsLabels[partIndex])

        # Highlight the current item
        CADGui.Selection.clearSelection()
        CADGui.Selection.addSelection(addPartObject)

        # Rebuild the subBody's List in the form
        self.selectedAss4SolidsToFormF()
    #  -------------------------------------------------------------------------
    def buttonRemovePartClicked_CallbackF(self):
        """Run when we remove a body already added"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-buttonRemovePartClicked_CallbackF")

        # Remove the current row
        if len(self.ass4SolidsNames) > 0:
            row = self.form.partsList.currentRow()
            self.ass4SolidsNames.pop(row)
            self.ass4SolidsLabels.pop(row)

        # Rebuild the subBodies in the form
        self.selectedAss4SolidsToFormF()
    #  -------------------------------------------------------------------------
    def partsListRowChanged_CallbackF(self, row):
        """Actively select the part in the requested row,
           to make it visible when viewing parts already in list"""
        if Debug:
            DT.Mess("TaskPanelDapBodyC-partsListRowChanged_CallbackF")

        if len(self.ass4SolidsNames) > 0:
            # Clear the highlight on the previous item selected
            CADGui.Selection.clearSelection()
            # Highlight the current item
            selection_object = self.taskDocument.findObjects(Name="^"+self.ass4SolidsNames[row]+"$")[0]
            CADGui.Selection.addSelection(selection_object)
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("TaskPanelDapBodyC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("TaskPanelDapBodyC-__setstate__")
# ==============================================================================

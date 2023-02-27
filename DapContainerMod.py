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
    from PySide import QtCore
global Debug
Debug = False
#  ----------------------------------------------------------------------------
def makeDapContainer(name="DapContainer"):
    """Create Dap Container FreeCAD group object"""

    if Debug:
        DT.Mess("makeDapContainer")

    containerObject = CAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", name)

    # Instantiate a DapContainer object
    DapContainerC(containerObject)

    # Instantiate the Gui side of the DapContainer
    if CAD.GuiUp:
        ViewProviderDapContainerC(containerObject.ViewObject)

    return containerObject
# =============================================================================
class CommandDapContainerC:
    """The Dap Container command definition"""
    if Debug:
        DT.Mess("CommandDapContainerC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(self):
        """Nothing needs to be initialised"""
        if Debug:
            DT.Mess("CommandDapContainerC-__init__")
    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by CAD when 'CADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""
        if Debug:
            DT.Mess("CommandDapContainerC-GetResources")
        return {
            "Pixmap": path.join(DT.getDapModulePath(), "icons", "Icon2n.png"),
            "MenuText": QtCore.QT_TRANSLATE_NOOP("Dap_Container_alias", "Create a New Dap Container"),
            "ToolTip": QtCore.QT_TRANSLATE_NOOP("Dap_Container_alias", "Creates a Dap solver container"),
        }
    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out"""
        if Debug:
            DT.Mess("CommandDapContainerC-IsActive(query)")

        # Return True if we have an Assembly4 FreeCAD model document which is loaded and Active
        if CAD.ActiveDocument is None:
            CAD.Console.PrintErrorMessage("No active document is loaded into FreeCAD for Nikra-DAP to use")
            return False

        for obj in CAD.ActiveDocument.Objects:
            if hasattr(obj, "Type") and obj.Type == 'Assembly':
                return True

        CAD.Console.PrintErrorMessage("No Assembly4 Model found for Nikra-DAP to use")
        return False
    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the create Container command is run by either pressing
        the tool Icon, or running it from one of the available menus.
        Then we create the DapContainer and set it to be Active"""
        if Debug:
            DT.Mess("CommandDapContainerC-Activated")
            
        if DT.setActiveContainer(makeDapContainer()) is False:
            CAD.Console.PrintError("Failed to create DAP container")
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("TaskPanelDapContainerC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("TaskPanelDapContainerC-__setstate__")
# =============================================================================
class DapContainerC:
    """The Dap analysis container class"""
    if Debug:
        DT.Mess("DapContainerC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(self, containerObject):
        """Initialise on entry"""
        if Debug:
            DT.Mess("DapContainerC-__init__")

        containerObject.Proxy = self

        # Call the initialisation via a separate function because we
        # want to use the same function when we restore the document
        self.initProperties(containerObject)
    #  -------------------------------------------------------------------------
    def initProperties(self, containerObject):
        """Run by '__init__'  and 'onDocumentRestored' to initialise the empty container members"""
        if Debug:
            DT.Mess("DapContainerC-initProperties")

        DT.addObjectProperty(containerObject, "activeContainer", False, "App::PropertyBool", "", "Flag as Active analysis object in document")
        DT.addObjectProperty(containerObject, "movementPlaneNormal", CAD.Vector(0, 0, 1), "App::PropertyVector", "", "Defines the rotation plane in this Nikra-DAP run")
        DT.addObjectProperty(containerObject, "groundBodyName", "", "App::PropertyString", "", "The name of the ground body")
        DT.addObjectProperty(containerObject, "groundBodyLabel", "", "App::PropertyString", "", "The label of the ground body")
        DT.addObjectProperty(containerObject, "gravityVector", CAD.Vector(0.0, 0.0, 0.0), "App::PropertyVector", "", "Gravitational acceleration Components")

        DT.setActiveContainer(containerObject)
    #  -------------------------------------------------------------------------
    def onDocumentRestored(self, containerObject):
        """Re-initialise when document is restored on load Model etc"""
        if Debug:
            DT.Mess("DapContainerC-onDocumentRestored")

        self.initProperties(containerObject)
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("DapContainerC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("DapContainerC-__setstate__")
# =============================================================================
class ViewProviderDapContainerC:
    """A view provider for the DapContainer container object"""
    if Debug:
        DT.Mess("ViewProviderDapContainerC-CLASS")
    #  -------------------------------------------------------------------------
    def __init__(self, containerViewObject):
        if Debug:
            DT.Mess("ViewProviderDapContainerC-__init__")

        containerViewObject.Proxy = self
    #  -------------------------------------------------------------------------
    def doubleClicked(self, containerViewObject):
        """Set the container to be the active one"""
        if Debug:
            DT.Mess("ViewProviderDapContainerC-doubleClicked")
        
        DT.setActiveContainer(containerViewObject.Object)
        
        return DT.getActiveContainerObject()
    #  -------------------------------------------------------------------------
    def getIcon(self):
        """Returns the full path to the container icon (Icon2n.png)"""
        if Debug:
            DT.Mess("ViewProviderDapContainer-getIcon")

        icon_path = path.join(DT.getDapModulePath(), "icons", "Icon2n.png")
        return icon_path
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("TaskPanelDapContainerC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("TaskPanelDapContainerC-__setstate__")
    # --------------------------------------------------------------------------
# =============================================================================

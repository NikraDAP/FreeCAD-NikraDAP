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
import FreeCADGui as CADGui

import Part
from os import path
import math
import numpy as np
Debug = False
#  -------------------------------------------------------------------------
# These are the string constants used in various places throughout the code
JOINT_TYPE = ["Rotation",
              #"Translation",
              #"Rotation-Rotation",
              #"Rotation-Translation",
              #"Driven-Rotation",
              #"Driven-Translation",
              #"Disc",
              #"Rigid",
              ]
JOINT_TYPE_DICTIONARY = {"Rotation": 0,
                         "Translation": 1,
                         "Rotation-Rotation": 2,
                         "Rotation-Translation": 3,
                         "Driven-Rotation": 4,
                         "Driven-Translation": 5,
                         "Disc": 6,
                         "Rigid": 7,
                         }
FORCE_TYPE = ["Gravity",
              # "Spring",
              # "Rotational Spring",
              # "Linear Spring Damper",
              # "Rotational Spring Damper",
              # "Unilateral Spring Damper",
              # "Constant Force Local to Body",
              # "Constant Global Force",
              # "Constant Torque about a Point",
              # "Contact Friction",
              # "Motor",
              #"Motor with Air Friction"
              ]
FORCE_TYPE_HELPER_TEXT = [
    "Universal force of attraction between all matter",
    "Linear Spring connecting two points with stiffness and undeformed length",
    "Device that stores energy when twisted and exerts a torque in the opposite direction",
    "A device used to limit or retard linear vibration ",
    "Device used to limit movement and vibration caused by rotation",
    "A Device used to dampen vibration in only the one direction",
    "A constant force with direction relative to the Body coordinates",
    "A constant force in a specific global direction",
    "A constant torque about a point on a body",
    "Contact friction between two bodies",
    "A motor with characteristics defined by an equation",
    "A motor defined by an equation, but with air friction associated with body movement"]
NIKRAVESH_EXAMPLES = [
    'Double A-Arm Suspension',
    'MacPherson Suspension A',
    'MacPherson Suspension B',
    'MacPherson Suspension C',
    'Cart A',
    'Cart B',
    'Cart C',
    'Cart D',
    'Conveyor Belt and Friction',
    'Rod Impacting Ground',
    'Sliding Pendulum',
    'Generic Sliding Pendulum']
NIKRAVESH_EXAMPLES_DICTIONARY = {
    'Double A-Arm Suspension': 'AA',
    'MacPherson Suspension A': 'MP_A',
    'MacPherson Suspension B': 'MP_B',
    'MacPherson Suspension C': 'MP_C',
    'Cart A': 'CART_A',
    'Cart B': 'CART_B',
    'Cart C': 'CART_C',
    'Cart D': 'CART_D',
    'Conveyor Belt and Friction': 'CB',
    'Rod Impacting Ground': 'Rod',
    'Sliding Pendulum': 'SP',
    'Generic Sliding Pendulum': 'GSP'}
NIKRAVESH_EXAMPLES_HELPER_TEXT = [
    'Double A-Arm Suspension - Nikravesh pp 170–173, 371–372',
    'MacPherson Suspension A - Nikravesh pp 173-175',
    'MacPherson Suspension B - Nikravesh pp 175-176',
    'MacPherson Suspension C - Nikravesh pp 176-177',
    'Cart_A - Nikravesh pp. 177–178',
    'Cart_B - Nikravesh pp. 178–179',
    'Cart_C - Nikravesh pp. 179-180',
    'Cart_D - Nikravesh pg. 180',
    'Conveyor Belt and Friction - Nikravesh 180–182, 358',
    'Rod Impacting Ground - Nikravesh pp. 176-177',
    'Sliding Pendulum - Nikravesh pp. 94, 118–120',
    'Generic Sliding Pendulum']
####################################################################
# HERE IS THE 'DICTIONARY' to the  DICTIONARIES in the DAP workbench
# ####################################################################
#
# bodyObjDict:          Dap Body Object Container Name --> Dap Body Object
# jointObjDict:         Dap Joint Container Name --> Dap Joint Container object
# forceObjDict:         Dap Force Container Name --> Dap Force Container object
# DictionaryOfPoints:   Dap Body Object Container Name -->
#                       Dict: FreeCAD point name --> index number in the point list in the Body container
# driverObjDict:        driver number --> driver function name
# cardID2cardData:      materialID --> cardData --> data on card
# cardID2cardName:      materiaID --> material name in the card

####################################################################
# List of available buttons in the task dialog
####################################################################
# NoButton        = 0x00000000,     Ok     = 0x00000400,     Save    = 0x00000800,
# SaveAll         = 0x00001000,     Open   = 0x00002000,     Yes     = 0x00004000,
# YesToAll        = 0x00008000,     No     = 0x00010000,     NoToAll = 0x00020000,
# Abort           = 0x00040000,     Retry  = 0x00080000,     Ignore  = 0x00100000,
# Close           = 0x00200000,     Cancel = 0x00400000,     Discard = 0x00800000,
# Help            = 0x01000000,     Apply  = 0x02000000,     Reset   = 0x04000000,
# RestoreDefaults = 0x08000000,

#  -------------------------------------------------------------------------
def getActiveContainerObject():
    """Return the container object which is currently active"""
    if Debug:
        Mess("DapTools-getActiveContainerObject")
    # The module must be imported here for "isinstance" to work below
    from DapContainerMod import DapContainerC
    for container in CAD.ActiveDocument.Objects:
        if hasattr(container, "Proxy") and isinstance(container.Proxy, DapContainerC):
            if container.activeContainer is True:
                return container
    return None
#  -------------------------------------------------------------------------
def setActiveContainer(containerObj):
    """Sets the container object to activeContainer=True
       and makes all the other containers false"""
    if Debug:
        Mess("DapTools-setActiveContainer")
    # The module must be imported here for "isinstance" to work below
    from DapContainerMod import DapContainerC
    Found = False
    for container in CAD.ActiveDocument.Objects:
        if hasattr(container, "Proxy") and isinstance(container.Proxy, DapContainerC):
            if container == containerObj:
                containerObj.activeContainer = True
                Found = True
            else:
                container.activeContainer = False
    
    # Return True/False if we found one or not
    return Found
#  -------------------------------------------------------------------------
def getHEADPoints(taskObject, bodyObjDict):
    """Generate the Point lists which correspond to the current body head name
    stored in the taskObject (i.e. jointObject or forceObject)
    also return the index of the point pointed to by taskObject.pointHEADName"""
    if Debug:
        Mess("DapTools-getHEADPoints")
    # Find the bodyIndex corresponding to the taskObject.bodyHEADName
    ListHEADNames = []
    ListHEADLabels = []
    pointHEADindex = -1
    if taskObject.bodyHEADName != "":
        bodyHEADObj = bodyObjDict[taskObject.bodyHEADName]
        for index in range(len(bodyHEADObj.pointNames)):
            ListHEADNames.append(bodyHEADObj.pointNames[index])
            ListHEADLabels.append(bodyHEADObj.pointLabels[index])

        # Find the pointIndex corresponding to taskObject.pointHEADName
        if taskObject.pointHEADName != "":
            pointHEADindex = bodyHEADObj.pointNames.index(taskObject.pointHEADName)

    return ListHEADNames, ListHEADLabels, pointHEADindex
#  -------------------------------------------------------------------------
def getTAILPoints(taskObject, bodyObjDict):
    """Generate the Point lists which correspond to the current body TAIL name
    stored in the taskObject (i.e. jointObject or forceObject)
    also return the index of the point pointed to by taskObject.pointTAILName"""
    if Debug:
        Mess("DapTools-getTAILPoints")
    # Find the bodyIndex corresponding to the taskObject.bodyTAILName
    ListTAILNames = []
    ListTAILLabels = []
    pointTAILindex = -1
    if taskObject.bodyTAILName != "":
        bodyTAILObj = bodyObjDict[taskObject.bodyTAILName]
        for index in range(len(bodyTAILObj.pointNames)):
            ListTAILNames.append(bodyTAILObj.pointNames[index])
            ListTAILLabels.append(bodyTAILObj.pointLabels[index])

        # Find the pointIndex corresponding to taskObject.pointTAILName
        if taskObject.pointTAILName != "":
            pointTAILindex = bodyTAILObj.pointNames.index(taskObject.pointTAILName)

    return ListTAILNames, ListTAILLabels, pointTAILindex
# --------------------------------------------------------------------------
def addObjectProperty(newobject, newproperty, initVal, newtype, *args):
    """Call addObjectProperty on the object if it does not yet exist"""
    if Debug:
        Mess("DapTools-addObjectProperty")
    # Only add it if the property does not exist there already
    added = False
    if newproperty not in newobject.PropertiesList:
        added = newobject.addProperty(newtype, newproperty, *args)
    if added:
        setattr(newobject, newproperty, initVal)
        return True
    else:
        return False
#  -------------------------------------------------------------------------
def getDictionary(DAPName):
    """Run through the Active Container group and
    return a dictionary with 'DAPName', vs objects"""
    if Debug:
        Mess("DapToolsC-getDictionary")
    DAPDictionary = {}
    activeContainer = getActiveContainerObject()
    for groupMember in activeContainer.Group:
        if DAPName in groupMember.Name:
            DAPDictionary[groupMember.Name] = groupMember
    return DAPDictionary
#  -------------------------------------------------------------------------
def getAllSolidsLists():
    """Run through the Solids and return lists of Names / Labels
    and a list of all the actual assembly objects"""
    allSolidsNames = []
    allSolidsLabels = []
    allSolidsObjects = []

    # Run through all the whole document's objects, looking for the Solids
    objects = CAD.ActiveDocument.Objects
    for obj in objects:
        if hasattr(obj, "Type") and obj.Type == 'Assembly':
            if Debug:
                Mess(obj.Name)
            SolidsObject = obj
            break
    else:
        Mess("No Assembly 4 object found")
        return allSolidsNames, allSolidsLabels, allSolidsObjects
        
    # Find all the parts
    # A part is searched for as something which is attached to something,
    # by means of something, and which has a shape
    for groupMember in SolidsObject.Group:
        if hasattr(groupMember, 'AttachedTo') and \
           hasattr(groupMember, 'AttachedBy') and \
           hasattr(groupMember, 'Shape'):
            if "^"+groupMember.Name+"$" in allSolidsNames:
                CAD.Console.PrintError("Duplicate Shape Name found: " + groupMember.Name + "\n")

            allSolidsNames.append(groupMember.Name)
            allSolidsLabels.append(groupMember.Label)
            allSolidsObjects.append(groupMember)

    return allSolidsNames, allSolidsLabels, allSolidsObjects
#  -------------------------------------------------------------------------
def getDictionaryOfPoints():
    """Run through the active document and
    return a dictionary of a dictionary of
    point names of bodyObjects"""
    if Debug:
        Mess("DapToolsC-getDictionaryOfPoints")
    dictionaryOfBodyPoints = {}
    activeContainer = getActiveContainerObject()
    for groupMember in activeContainer.Group:
        if "DapBody" in groupMember.Name:
            PointDict = {}
            for index in range(len(groupMember.pointNames)):
                PointDict[groupMember.pointNames[index]] = index
            dictionaryOfBodyPoints[groupMember.Name] = PointDict.copy()
            
    return dictionaryOfBodyPoints
#  -------------------------------------------------------------------------
def getMaterialObject():
    """Return the Material object if a Material Object container is contained in the active container"""
    if Debug:
        Mess("DapToolsMod-getMaterialObject")
    activeContainer = getActiveContainerObject()
    for groupMember in activeContainer.Group:
        if "DapMaterial" in groupMember.Name:
            return groupMember
    return None
#  -------------------------------------------------------------------------
def getDapModulePath():
    """Returns the path where the current DAP module is stored
    Determines where this file is running from, so DAP workbench works regardless of whether
    the module is installed in the app's module directory or the user's app data folder.
    (The second overrides the first.)"""
    if Debug:
        Mess("DapTools-getDapModulePath")
    return path.dirname(__file__)
#  -------------------------------------------------------------------------
def computeCoGAndMomentInertia(bodyObj):
    """ Computes:
    1. The world centre of mass of each body based on the weighted sum
    of each solid's centre of mass
    2. The moment of inertia of the whole body, based on the moment of Inertia for the
    solid through its CoG axis + solid mass * (perpendicular distance
    between the axis through the solid's CoG and the axis through the whole body's
    CoG) squared.   Both axes should be normal to the plane of movement and
    will hence be parallel if everything is OK.
    *************************************************************************
    IMPORTANT:  FreeCAD and Nikra-DAP work internally with a mm-kg-s system
    *************************************************************************
    """

    # Get the Material object (i.e. list of densities) which has been defined in the appropriate DAP routine
    theMaterialObject = getMaterialObject()

    # Determine the vectors and matrices to convert movement in the selected base plane to the X-Y plane
    MovePlaneNormal = getActiveContainerObject().movementPlaneNormal
    xyzToXYRotation = CAD.Rotation(CAD.Vector(0, 0, 1), MovePlaneNormal)

    # Clear the variables and lists for filling
    totalBodyMass = 0
    CoGWholeBody = CAD.Vector()
    massList = []
    solidMoIThroughCoGNormalToMovePlaneList = []
    solidCentreOfGravityXYPlaneList = []

    # Run through all the solids in the assemblyObjectList
    for assemblyPartName in bodyObj.ass4SolidsNames:
        assemblyObj = bodyObj.Document.findObjects(Name="^" + assemblyPartName + "$")[0]
        if Debug:
            Mess(str("assembly4 Part Name:  ")+str(assemblyPartName))

        # Translate this assemblyObj to where assembly4 put it
        # assemblyObj.applyRotation(assemblyObj.Placement.Rotation)
        # assemblyObj.applyTranslation(assemblyObj.Placement.Base)

        # Volume of this assemblyObj in cubic mm
        volume = assemblyObj.Shape.Volume
        # Density of this assemblyObj in kg per cubic mm
        index = theMaterialObject.solidsNameList.index(assemblyPartName)
        density = theMaterialObject.materialsDensityList[index] * 1e-9
        # Calculate the mass in kg
        mass = density * volume
        massList.append(mass)
        if Debug:
            Mess(str("Volume [mm^3]:  ") + str(volume))
            Mess("Density [kg/mm^3]:  "+str(density))
            Mess("Mass [kg]:  "+str(mass))

        # Add the Centre of gravities to the list to use in parallel axis theorem
        solidCentreOfGravityXYPlaneList.append(xyzToXYRotation.toMatrix().multVec(assemblyObj.Shape.CenterOfGravity))
        solidCentreOfGravityXYPlaneList[-1].z = 0.0

        # MatrixOfInertia[MoI] around an axis through the CoG of the Placed assemblyObj
        # and normal to the MovePlaneNormal
        MoIVec = assemblyObj.Shape.MatrixOfInertia.multVec(MovePlaneNormal)
        MoIVecLength = MoIVec.Length * 1e-6
        solidMoIThroughCoGNormalToMovePlaneList.append(MoIVecLength * mass)

        totalBodyMass += mass
        CoGWholeBody += mass * solidCentreOfGravityXYPlaneList[-1]
    # Next assemblyIndex

    bodyObj.Mass = totalBodyMass
    CoGWholeBody /= totalBodyMass
    bodyObj.centreOfGravity = CoGWholeBody
    bodyCentreOfGravityXYPlane = xyzToXYRotation.toMatrix().multVec(bodyObj.centreOfGravity)
    bodyCentreOfGravityXYPlane.z = 0.0

    # Using parallel axis theorem to compute the moment of inertia through the CoG
    # of the full body comprised of multiple shapes
    momentInertiaWholeBody = 0
    for MoIIndex in range(len(solidMoIThroughCoGNormalToMovePlaneList)):
        if Debug:
            Mess("Sub-Body MoI: "+str(solidMoIThroughCoGNormalToMovePlaneList[MoIIndex]))
        distanceBetweenAxes = (bodyCentreOfGravityXYPlane - solidCentreOfGravityXYPlaneList[MoIIndex]).Length
        momentInertiaWholeBody += solidMoIThroughCoGNormalToMovePlaneList[MoIIndex] + massList[MoIIndex] * (distanceBetweenAxes ** 2)
    bodyObj.momentInertia = momentInertiaWholeBody

    # Gravity vector is acceleration of gravity in mm / s^2 - weight vector is force of gravity in kg mm / s^2
    bodyObj.weightVector = getActiveContainerObject().gravityVector * totalBodyMass
    if Debug:
        Mess("Body Total Mass [kg]:  "+str(totalBodyMass))
        MessNoLF("Body Centre of Gravity [mm]:  ")
        PrintVec(CoGWholeBody)
        Mess("Body moment of inertia [kg mm^2):  "+str(momentInertiaWholeBody))
        Mess("")

    return True
# --------------------------------------------------------------------------
def decorateObject(objectToDecorate, bodyHEADobject, bodyTAILobject):
    # Get the world coordinates etc. of the HEAD point
    solidNameHEADList = []
    solidPlacementHEADList = []
    solidBoxHEADList = []
    worldPointHEAD = CAD.Vector()
    if objectToDecorate.pointHEADName != "":
        # Find the bounding boxes of the component solids
        # solidNameList - names of the solids
        # solidPlacementList - The Placement.Base are the world coordinates of the solid origin
        # solidBoxList - The BoundBox values are the rectangular cartesian world coordinates of the bounding box
        Document = CAD.ActiveDocument
        for solidName in bodyHEADobject.ass4SolidsNames:
            solidObj = Document.findObjects(Name="^" + solidName + "$")[0]
            solidNameHEADList.append(solidName)
            solidPlacementHEADList.append(solidObj.Placement)
            solidBoxHEADList.append(solidObj.Shape.BoundBox)

        # Get the HEAD world Placement of the compound DAP body
        worldHEADPlacement = bodyHEADobject.world
        if Debug:
            MessNoLF("Main Body World HEAD Placement: ")
            Mess(worldHEADPlacement)
        pointIndex = bodyHEADobject.pointNames.index(objectToDecorate.pointHEADName)
        pointHEADLocal = bodyHEADobject.pointLocals[pointIndex]
        worldPointHEAD = worldHEADPlacement.toMatrix().multVec(pointHEADLocal)

    # Get the world coordinates etc. of the TAIL of the point
    solidNameTAILList = []
    solidPlacementTAILList = []
    solidBoxTAILList = []
    worldPointTAIL = CAD.Vector()
    if objectToDecorate.pointTAILName != "":
        # Find the bounding boxes of the component solids
        Document = CAD.ActiveDocument
        for solidName in bodyTAILobject.ass4SolidsNames:
            solidObj = Document.findObjects(Name="^" + solidName + "$")[0]
            solidNameTAILList.append(solidName)
            solidPlacementTAILList.append(solidObj.Placement)
            solidBoxTAILList.append(solidObj.Shape.BoundBox)

        # Get the TAIL world Placement of the compound DAP body
        worldTAILPlacement = bodyTAILobject.world
        if Debug:
            MessNoLF("Main Body World TAIL Placement: ")
            Mess(worldTAILPlacement)
        pointIndex = bodyTAILobject.pointNames.index(objectToDecorate.pointTAILName)
        pointTAILLocal = bodyTAILobject.pointLocals[pointIndex]
        worldPointTAIL = worldTAILPlacement.toMatrix().multVec(pointTAILLocal)

    if Debug:
        Mess("Solid lists:")
        for i in range(len(solidNameHEADList)):
            MessNoLF(solidNameHEADList[i])
            MessNoLF(" -- ")
            MessNoLF(solidPlacementHEADList[i])
            MessNoLF(" -- ")
            Mess(solidBoxHEADList[i])
        for i in range(len(solidNameTAILList)):
            MessNoLF(solidNameTAILList[i])
            MessNoLF(" -- ")
            MessNoLF(solidPlacementTAILList[i])
            MessNoLF(" -- ")
            Mess(solidBoxTAILList[i])
        MessNoLF("World HEAD point: ")
        PrintVec(worldPointHEAD)
        MessNoLF("World TAIL point: ")
        PrintVec(worldPointTAIL)

    # Identify in which solid bounding box, the HEAD and TAIL points are
    HEADSolidIndex = TAILSolidIndex = 1
    for boxIndex in range(len(solidBoxHEADList)):
        if solidBoxHEADList[boxIndex].isInside(worldPointHEAD):
            if Debug:
                MessNoLF("HEAD point inside: ")
                Mess(solidNameHEADList[boxIndex])
            HEADSolidIndex = boxIndex
    for boxIndex in range(len(solidBoxTAILList)):
        if solidBoxTAILList[boxIndex].isInside(worldPointTAIL):
            if Debug:
                MessNoLF("TAIL point inside: ")
                Mess(solidNameTAILList[boxIndex])
            TAILSolidIndex = boxIndex

    if objectToDecorate.pointHEADName != "" and objectToDecorate.pointTAILName != "":
        # Draw some shapes in the gui, to show the point positions
        boxIntersection = solidBoxHEADList[HEADSolidIndex].intersected(solidBoxTAILList[TAILSolidIndex])
        CurrentJointType = objectToDecorate.JointType
        planeNormal = getActiveContainerObject().movementPlaneNormal
        pointHEAD = CAD.Vector(worldPointHEAD)
        pointTAIL = CAD.Vector(worldPointTAIL)

        # Do some calculation of the torus sizes for Rev and Rev-Rev points
        if CurrentJointType == 0 or CurrentJointType == 2:
            # Depending on the plane normal:
            # Move the two thickness coordinates to their average,
            # Squash the thickness to zero, and
            # Set the point Diameter to the middle value of the Intersection box's xlength ylength zlength
            if planeNormal.x > 1e-6:
                pointHEAD.x = (worldPointHEAD.x + worldPointTAIL.x) / 2.0
                pointTAIL.x = pointHEAD.x
            elif planeNormal.y > 1e-6:
                pointHEAD.y = (worldPointHEAD.y + worldPointTAIL.y) / 2.0
                pointTAIL.y = pointHEAD.y
            elif planeNormal.z > 1e-6:
                pointHEAD.z = (worldPointHEAD.z + worldPointTAIL.z) / 2.0
                pointTAIL.z = pointHEAD.z

        # Draw the yellow circular arrow in the case of 'Rev' point
        if CurrentJointType == 0 \
                and objectToDecorate.pointHEADName != "" \
                and objectToDecorate.pointTAILName != "":
            pointDiam = minMidMax3(boxIntersection.XLength,
                                   boxIntersection.YLength,
                                   boxIntersection.ZLength,
                                   2)
            # Only draw if the diameter non-zero
            if pointDiam > 1e-6:
                # Draw the Left side
                # False == Left side
                Shape1 = DrawRotArrow(pointHEAD, False, pointDiam)
                # Draw the Right side
                # True == Right side
                Shape2 = DrawRotArrow(pointTAIL, True, pointDiam)
                Shape = Part.makeCompound([Shape1, Shape2])
                objectToDecorate.Shape = Shape
                objectToDecorate.ViewObject.ShapeColor = (1.0, 1.0, 0.0)
                objectToDecorate.ViewObject.Transparency = 70

        # Draw a straight red arrow in the case of 'trans' point
        elif CurrentJointType == 1:
            Shape = DrawTransArrow(worldPointTAIL, worldPointHEAD, 15)
            objectToDecorate.Shape = Shape
            objectToDecorate.ViewObject.ShapeColor = (1.0, 0.0, 0.0)
            objectToDecorate.ViewObject.Transparency = 70

        # Draw the two circular arrows and a line in the case of 'Rotation-Rotation' point
        elif CurrentJointType == 2:
            pointHEADDiam = minMidMax3(solidBoxHEADList[HEADSolidIndex].XLength,
                                       solidBoxHEADList[HEADSolidIndex].YLength,
                                       solidBoxHEADList[HEADSolidIndex].ZLength,
                                       2)
            pointTAILDiam = minMidMax3(solidBoxTAILList[TAILSolidIndex].XLength,
                                       solidBoxTAILList[TAILSolidIndex].YLength,
                                       solidBoxTAILList[TAILSolidIndex].ZLength,
                                       2)
            # Draw both left and right sides of the torus
            Shape1 = DrawRotArrow(pointHEAD, True, pointHEADDiam / 2)
            Shape2 = DrawRotArrow(pointHEAD, False, pointHEADDiam / 2)
            Shape3 = DrawRotArrow(pointTAIL, True, pointTAILDiam / 2)
            Shape4 = DrawRotArrow(pointTAIL, False, pointTAILDiam / 2)
            # Draw the arrow
            Shape5 = DrawTransArrow(pointHEAD, pointTAIL, pointHEADDiam / 2)
            Shape = Part.makeCompound([Shape1, Shape2, Shape3, Shape4, Shape5])
            objectToDecorate.Shape = Shape
            objectToDecorate.ViewObject.ShapeColor = (1.0, 0.0, 1.0)
            objectToDecorate.ViewObject.Transparency = 70
            objectToDecorate.lengthLink = (pointHEAD - pointTAIL).Length

        # Draw a circular arrow and a line in the case of 'Rotation-Translation' point
        elif CurrentJointType == 3:
            Shape1 = DrawRotArrow(worldPointHEAD, True, 3)
            Shape2 = DrawRotArrow(worldPointHEAD, False, 3)
            Shape3 = DrawTransArrow(worldPointHEAD, worldPointTAIL, 15)
            Shape = Part.makeCompound([Shape1, Shape2, Shape3])
            objectToDecorate.Shape = Shape
            objectToDecorate.ViewObject.ShapeColor = (0.0, 1.0, 1.0)
            objectToDecorate.ViewObject.Transparency = 70

        # Draw a Bolt in the case of 'Rigid' point
        elif CurrentJointType == 7:
            pointHEADlen = minMidMax3(boxIntersection.XLength,
                                      boxIntersection.YLength,
                                      boxIntersection.ZLength,
                                      3)
            pointHEADdiam = minMidMax3(boxIntersection.XLength,
                                       boxIntersection.YLength,
                                       boxIntersection.ZLength,
                                       2)
            objectToDecorate.Shape = DrawRigidBolt(worldPointHEAD, pointHEADdiam / 3, pointHEADlen / 3)
            objectToDecorate.ViewObject.ShapeColor = (1.0, 0.0, 0.0, 1.0)
            objectToDecorate.ViewObject.Transparency = 70

        else:
            # Add a null shape to the object for the other more fancy types
            # TODO: The appropriate shapes may be added at a later time
            objectToDecorate.Shape = Part.Shape()
#  -------------------------------------------------------------------------
def DrawRotArrow(Point, LeftRight, diameter):
    """Draw a yellow circle arrow around a rotation point
    We first draw it relative to the X-Y plane
    and then rotate it relative to the defined movement plane"""
    radiusRing = diameter
    thicknessRing = diameter / 5
    torus_direction = CAD.Vector(0, 0, 1)
    cone_direction = CAD.Vector(0, 1, 0)

    # Make either a left half or a right half of the torus
    if LeftRight:
        torus = Part.makeTorus(radiusRing, thicknessRing, CAD.Vector(0, 0, radiusRing), torus_direction, -180, 180, 90)
        cone_position = CAD.Vector(radiusRing, -5 * thicknessRing, radiusRing)
        cone = Part.makeCone(0, 2 * thicknessRing, 5 * thicknessRing, cone_position, cone_direction)
    else:
        torus = Part.makeTorus(radiusRing, thicknessRing, CAD.Vector(0, 0, radiusRing), -torus_direction, -180, 180, 90)
        cone_position = CAD.Vector(-radiusRing, -5 * thicknessRing, radiusRing)
        cone = Part.makeCone(0, 2 * thicknessRing, 5 * thicknessRing, cone_position, cone_direction)
    # Make a cone to act as an arrow on the end of the half torus
    torus_w_arrows = Part.makeCompound([torus, cone])
    # Rotate torus to be relative to the defined movement plane
    rotationToMovementPlane = CAD.Rotation(CAD.Vector(0, 0, 1), getActiveContainerObject().movementPlaneNormal)
    torus_w_arrows.applyRotation(rotationToMovementPlane)
    # Translate the torus to be located at the point
    torus_w_arrows.applyTranslation(Point)

    return torus_w_arrows
#  -------------------------------------------------------------------------
def DrawRigidBolt(Point, diam, length):
    bolt = Part.makeCylinder(
        diam,
        length * 2,
        Point - CAD.Vector(0, 0, length),
        CAD.Vector(0, 0, 1)
    )

    # FORMAT OF MAKE WEDGE:
    # ====================
    # makeWedge (xbotleftbase, basey, zbotleftbase,
    #            zbotleftroof,xbotleftroof,
    #            xtoprightbase,roofy,ztoprightbase,
    #            ztoprightroof,xtoprightroof

    sin = math.sin(math.pi / 3)
    cos = math.cos(math.pi / 3)

    nuta = Part.makeWedge(-diam, -diam * 2 * sin, -length * 2 / 9,
                          -length * 2 / 9, 0,
                          diam, 0, length * 2 / 9,
                          length * 2 / 9, 0)
    nutb = nuta.copy().mirror(CAD.Vector(0, 0, 0), CAD.Vector(sin, cos, 0))
    nutc = nuta.copy().mirror(CAD.Vector(0, 0, 0), CAD.Vector(sin, -cos, 0))
    nutd = nuta.fuse([nutb, nutc])
    nute = nutd.copy().mirror(CAD.Vector(0, 0, 0), CAD.Vector(0, 1, 0))
    nutf = nutd.fuse([nute])
    nutg = nutf.copy()
    nutf.translate(Point - CAD.Vector(0, 0, length * 0.7))
    nutg.translate(Point + CAD.Vector(0, 0, length * 0.7))

    return bolt.fuse([nutf, nutg])
#  -------------------------------------------------------------------------
def DrawTransArrow(Point1, Point2, diameter):
    # Draw an arrow as long as the distance of the vector between the points
    llen = (Point1 - Point2).Length
    if llen > 1e-6:
        # Direction of the arrow is the direction of the vector between the two points
        lin_move_dir = (Point2 - Point1).normalize()
        cylinder = Part.makeCylinder(
            diameter * 0.3,
            0.60 * llen,
            Point1 + 0.2 * llen * lin_move_dir,
            lin_move_dir,
        )
        # Draw the two arrow heads
        cone1 = Part.makeCone(0, diameter, 0.2 * llen, Point1, lin_move_dir)
        cone2 = Part.makeCone(0, diameter, 0.2 * llen, Point2, -lin_move_dir)
        return Part.makeCompound([cylinder, cone1, cone2])
    return Part.Shape()
#  -------------------------------------------------------------------------
def minMidMax(x, y, z, minMidMax):
    """Given three numbers, return the minimum, or the middle or the maximum one
        minimum: if minMidMax == 1
        middle:  if minMidMax == 2
        maximum: if minMidMax == 3
    """
    x = abs(x)
    y = abs(y)
    z = abs(z)
    if x >= y:
        if y >= z:
            # x >= y >= z
            if minMidMax == 1:
                return z
            elif minMidMax == 2:
                return y
            else:
                return x
        elif x >= z:
            # x >= z > y
            if minMidMax == 1:
                return y
            elif minMidMax == 2:
                return z
            else:
                return x
        # z > x >= y
        elif minMidMax == 1:
            return y
        elif minMidMax == 2:
            return x
        else:
            return z
    # y > x
    elif x >= z:
        # y >= x >= z
        if minMidMax == 1:
            return z
        elif minMidMax == 2:
            return x
        else:
            return y
    # y > x and z > x
    elif y >= z:
        # y >= z > x
        if minMidMax == 1:
            return x
        elif minMidMax == 2:
            return z
        else:
            return y
    # z > y > x
    elif minMidMax == 1:
        return x
    elif minMidMax == 2:
        return y
    else:
        return z
#  -------------------------------------------------------------------------
def minMidMaxVec(Vector, minMidMax):
    """Given coordinates in a vector, return the minimum, or the middle or the maximum one
        minimum: if minMidMax == 1
        middle:  if minMidMax == 2
        maximum: if minMidMax == 3
    """
    Vec = CAD.Vector(Vector)
    Vec.x = abs(x)
    Vec.y = abs(y)
    Vec.z = abs(z)
    if Vec.x >= Vec.y:
        if Vec.y >= Vec.z:
            # Vec.x >= Vec.y >= Vec.z
            if minMidMax == 1:
                return Vec.z
            elif minMidMax == 2:
                return Vec.y
            else:
                return Vec.x
        if Vec.x >= Vec.z:
            # Vec.x >= Vec.z > Vec.y
            if minMidMax == 1:
                return Vec.y
            elif minMidMax == 2:
                return Vec.z
            else:
                return Vec.x
        # Vec.z > Vec.x >= Vec.y
        if minMidMax == 1:
            return Vec.y
        elif minMidMax == 2:
            return Vec.x
        else:
            return Vec.z
    # y > x
    if Vec.x >= Vec.z:
        # Vec.y >= Vec.x >= Vec.z
        if minMidMax == 1:
            return Vec.z
        elif minMidMax == 2:
            return Vec.x
        else:
            return Vec.y
    # y > x and z > x
    if Vec.y >= Vec.z:
        # Vec.y >= Vec.z > Vec.x
        if minMidMax == 1:
            return Vec.x
        elif minMidMax == 2:
            return Vec.z
        else:
            return Vec.y
    # Vec.z > Vec.y > Vec.x
    if minMidMax == 1:
        return Vec.x
    elif minMidMax == 2:
        return Vec.y
    else:
        return Vec.z
#  -------------------------------------------------------------------------
def RotationMatrixNp(phi):
    """ This function computes the rotational transformation matrix
    in the format of a 2X2 NumPy array"""
    return np.array([[math.cos(phi), -math.sin(phi)],
                     [math.sin(phi),  math.cos(phi)]])
#  -------------------------------------------------------------------------
def Mess(string):
    CAD.Console.PrintMessage(str(string)+"\n")
#  -------------------------------------------------------------------------
def MessNoLF(string):
    CAD.Console.PrintMessage(str(string))
#  -------------------------------------------------------------------------
def PrintVec(vec):
    CAD.Console.PrintMessage("[" + str(Round(vec.x)) + ":" + str(Round(vec.y)) + ":" + str(Round(vec.z)) + "]\n")
#  -------------------------------------------------------------------------
def Np3D(arr):
    for x in arr:
        for y in x:
            s = "[ "
            for z in y:
                ss = str(Round(z))+"                 "
                s = s + ss[:12]
            s = s + " ]"
            CAD.Console.PrintMessage(s+"\n")
        CAD.Console.PrintMessage("\n")
#  -------------------------------------------------------------------------
def Np2D(arr):
    for x in arr:
        s = "[ "
        for y in x:
            ss = str(Round(y))+"                 "
            s = s + ss[:12]
        s = s + " ]"
        CAD.Console.PrintMessage(s+"\n")
#  -------------------------------------------------------------------------
def Np1D(LF, arr):
    s = "[ "
    for y in arr:
        ss = str(Round(y))+"                 "
        s = s + ss[:12]
    s = s + " ]"
    if LF:
        CAD.Console.PrintMessage(s+"\n")
    else:
        CAD.Console.PrintMessage(s+" ")
#  -------------------------------------------------------------------------
def Np1Ddeg(LF, arr):
    s = "[ "
    for y in arr:
        ss = str(Round(y*180.0/math.pi))+"                 "
        s = s + ss[:12]
    s = s + " ]"
    if LF:
        CAD.Console.PrintMessage(s+"\n")
    else:
        CAD.Console.PrintMessage(s+" ")
#  -------------------------------------------------------------------------
def Round(num):
    if num >= 0.0:
        return int((100.0 * num + 0.5))/100.0
    else:
        return int((100.0 * num - 0.5))/100.0
# --------------------------------------------------------------------------

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

import os
import DapToolsMod as DT
import DapFunctionMod
import numpy as np
from scipy.integrate import solve_ivp
import math
if CAD.GuiUp:
    import FreeCADGui as CADGui
    import PySide
global Debug
Debug = False
############################################################################################
# Never try to change an item in a list inside the body/joint/force/materials/solver object
# NB NB NB Pull the list out, change the item in the list, and put the list back NB NB NB NB
############################################################################################

# =============================================================================
class DapMainC:
    """Instantiated when the 'solve' button is clicked in the task panel"""
    #  -------------------------------------------------------------------------
    def __init__(self, simEnd, simDelta, Accuracy, correctInitial):
        if Debug:
            DT.Mess("DapMainC-__init__")
        # Save the time steps passed via the __init__ function
        self.simEnd = simEnd
        self.simDelta = simDelta
        self.correctInitial = correctInitial
        # Store the requred accuracy figures
        self.relativeTolerance = 10**(-Accuracy-2)
        self.absoluteTolerance = 10**(-Accuracy-4)
        # Have the solver object handy
        self.solverObj = CAD.ActiveDocument.findObjects(Name="^DapSolver$")[0]
        # Set a variable to flag whether we have reached the end error-free
        # It will be available to DapSolverMod as an instance variable
        self.initialised = False

        # Dictionary of the pointers for Dynamic calling of the Acceleration functions
        self.dictAccelerationFunctions = {
            0: self.revolute_Acc,
            1: self.translational_Acc,
            2: self.revolute_revolute_Acc,
            3: self.revolute_translational_Acc,
            4: self.relative_rotational_Acc,
            5: self.relative_translational_Acc,
            6: self.disc_Acc,
            7: self.rigid_Acc,
        }
        # Dictionary of the pointers for Dynamic calling of the Constraint functions
        self.dictConstraintFunctions = {
            0: self.revolute_Constraint,
            1: self.translational_Constraint,
            2: self.revolute_revolute_Constraint,
            3: self.revolute_translational_Constraint,
            4: self.relative_rotational_Constraint,
            5: self.relative_translational_Constraint,
            6: self.disc_Constraint,
            7: self.rigid_Constraint,
        }
        # Dictionary of the pointers for Dynamic calling of the Jacobian functions
        self.dictJacobianFunctions = {
            0: self.revolute_Jacobian,
            1: self.translational_Jacobian,
            2: self.revolute_revolute_Jacobian,
            3: self.revolute_translational_Jacobian,
            4: self.relative_rotational_Jacobian,
            5: self.relative_translational_Jacobian,
            6: self.disc_Jacobian,
            7: self.rigid_Jacobian,
        }
        ############
        # BODY STUFF
        ############
        # Load the body and point dictionaries and convert to lists for quick indexing in numpy
        bodyObjDict = DT.getDictionary("DapBody")
        DictionaryOfPoints = DT.getDictionaryOfPoints()
        self.bodyName2Index = {}
        self.bodyObjList = []
        self.pointDictList = []
        self.numPointsInDict = []
        # Also check if we have one (and only one) ground body
        bodyIndex = 0
        foundGround = False
        for bodyName in bodyObjDict:
            bodyObj = bodyObjDict[bodyName]
            # Append bodyObj and DictionaryOfPoints[bodyName] to the lists
            self.bodyObjList.append(bodyObj)
            self.pointDictList.append(DictionaryOfPoints[bodyName])
            self.numPointsInDict.append(len(DictionaryOfPoints[bodyName]))

            # Swap the stationary body to 0 in the list if applicable
            # i.e. We swap the current zero'th body with the current item
            # and make the [only] stationary body the zero'th one in the list.
            # We have made sure that only one is stationary at definition time
            # and we have requested the user to put all the stationary objects into one body
            # [ and didn't allow him/her to do otherwise :-) ]

            # First handle the moving body
            if bodyObj.movingBody is True:
                self.bodyName2Index[bodyName] = bodyIndex
            # This is what we do for the non-moving body
            else:
                foundGround = True
                # Only swap if it is not already body #0
                if bodyIndex != 0:
                    # Swap the items in the body Object list
                    self.bodyObjList[0], self.bodyObjList[bodyIndex] = self.bodyObjList[bodyIndex], self.bodyObjList[0]
                    # Swap the items in the point Dictionary list
                    self.pointDictList[0], self.pointDictList[bodyIndex] = self.pointDictList[bodyIndex], self.pointDictList[0]
                    # Swap the items in the "Number of points in Dictionary" list
                    self.numPointsInDict[bodyIndex], self.numPointsInDict[0] = self.numPointsInDict[0], self.numPointsInDict[bodyIndex]
                    # This complicated line is a reverse lookup in the dictionary
                    # so that we can find the name of the body which was the zero'th one
                    zerosName = next(key for key, value in self.bodyName2Index.items() if value == 0)
                    self.bodyName2Index[zerosName] = bodyIndex
                # Set the index pointer to the new body in the zero'th position
                self.bodyName2Index[bodyName] = 0
            bodyIndex += 1
        # Next bodyName

        # Handy variables calculated from numBodies
        self.numBodies = bodyIndex
        self.numMovBodies = self.numBodies-1
        self.numMovBodiesx3 = self.numMovBodies * 3

        # Make sure we have found a ground
        if foundGround is False:
            CAD.Console.PrintError("No ground (stationary / non-moving) body found\n")
            CAD.Console.PrintError("One (and only one) ground body must be defined\n\n")
            return

        # Clean up the space taken by the bodyObjDict
        bodyObjDict = {}

        #############
        # JOINT STUFF
        #############
        # Load the joint dictionary and convert to a list for quick indexing in numpy
        jointObjDict = DT.getDictionary("DapJoint")
        self.jointObjList = []
        for jointName in jointObjDict:
            jointObj = jointObjDict[jointName]
            self.jointObjList.append(jointObj)
            # Insert the applicable indices into the joint object
            jointObj.bodyHEADindex = self.bodyName2Index[jointObj.bodyHEADName]
            jointObj.pointHEADindex = self.pointDictList[jointObj.bodyHEADindex][jointObj.pointHEADName]
            jointObj.bodyTAILindex = self.bodyName2Index[jointObj.bodyTAILName]
            jointObj.pointTAILindex = self.pointDictList[jointObj.bodyTAILindex][jointObj.pointTAILName]
        self.numJoints = len(self.jointObjList)
        # Clean up the space taken by the jointObjDictionary
        jointObjDict = {}
            
        #############
        # FORCE STUFF
        #############
        # Load the force dictionary and convert to a list for quick indexing in numpy
        forceObjDict = DT.getDictionary("DapForce")
        self.forceObjList = []
        for forceName in forceObjDict:
            forceObj = forceObjDict[forceName]
            self.forceObjList.append(forceObj)
            # Only fix up the indices if it is not gravity
            # because with gravity, a specific body and point makes no sense
            if forceObj.actuatorType != 0:
                # Insert the applicable indices into the force object
                forceObj.bodyHEADindex = self.bodyName2Index[forceObj.bodyHEADName]
                forceObj.pointHEADindex = self.pointDictList[forceObj.bodyHEADindex][forceObj.pointHEADName]
                forceObj.bodyTAILindex = self.bodyName2Index[forceObj.bodyTAILName]
                forceObj.pointTAILindex = self.pointDictList[forceObj.bodyTAILindex][forceObj.pointTAILName]
        self.numForces = len(self.forceObjList)
        # Clean up the space taken by the forceObjDictionary
        forceObjDict = {}

        # Get the plane normal rotation matrix from the main DAP container
        xyzToXYRotation = CAD.Rotation(CAD.Vector(0, 0, 1), DT.getActiveContainerObject().movementPlaneNormal)
        # Find the maximum number of points in any body
        self.maxNumPoints = 0
        for bodyIndex in range(self.numBodies):
            if self.numPointsInDict[bodyIndex] > self.maxNumPoints:
                self.maxNumPoints = self.numPointsInDict[bodyIndex]
        # Initialise the size of all the NumPy arrays and fill with zeros
        self.initNumPyArrays()

        # Transfer all the 3D stuff into the numpy arrays
        # while doing the projection onto the X-Y plane
        for bodyIndex in range(self.numBodies):
            bodyObj = self.bodyObjList[bodyIndex]
            # Bring the body Mass, CoG, MoI and Weight up-to-date
            DT.computeCoGAndMomentInertia(bodyObj)
            # All Mass and weight stuff
            self.MassNp[bodyIndex] = bodyObj.Mass
            self.momentInertiaNp[bodyIndex] = bodyObj.momentInertia
            npVec = self.vecToNumpyF(xyzToXYRotation.toMatrix().multVec(bodyObj.weightVector))
            self.WeightNp[bodyIndex] = npVec

            # Change the local vectors to be relative to the CoG, rather than the body origin
            # The CoG in world coordinates are the world coordinates of the body
            # All points are relative to this point

            # World
            CoG = xyzToXYRotation.toMatrix().multVec(bodyObj.centreOfGravity)
            npVec = self.vecToNumpyF(CoG)
            self.worldNp[bodyIndex, 0:2] = npVec.copy()
            self.worldRotNp[bodyIndex, 0:2] = self.Rot90NumpyF(npVec)
            # WorldDot
            npVec = self.vecToNumpyF(xyzToXYRotation.toMatrix().multVec(bodyObj.worldDot))
            self.worldDotNp[bodyIndex, 0:2] = npVec
            self.worldDotRotNp[bodyIndex, 0:2] = self.Rot90NumpyF(npVec)
            # WorldDotDot
            self.worldDotDotNp[bodyIndex, 0:2] = np.zeros((1, 2))
            # Transform the points from model Placement to World X-Y plane relative to the CoG
            bodyPointsLocal = bodyObj.pointLocals.copy()
            vectorsRelativeCoG = bodyPointsLocal.copy()
            for localIndex in range(len(bodyPointsLocal)):
                bodyPointsLocal[localIndex] = xyzToXYRotation.toMatrix(). \
                    multiply(bodyObj.world.toMatrix()). \
                    multVec(bodyPointsLocal[localIndex])
                vectorsRelativeCoG[localIndex] = bodyPointsLocal[localIndex] - CoG
            # Take some trouble to make phi as nice an angle as possible
            # Because the user will maybe use it manually later and will appreciate it
            self.phiNp[bodyIndex] = self.nicePhiPlease(vectorsRelativeCoG)
            if Debug:
                DT.Mess("Best Phi: "+str(phi)+"'"+str(phi*180/math.pi)+"]")

            # The phiDot axis vector is by definition perpendicular to the movement plane,
            # so we don't have to do any rotating from the value set in bodyObj
            self.phiDotNp[bodyIndex] = bodyObj.phiDot

            # We will now calculate the rotation matrix and use it to find the coordinates of the points
            self.RotMatPhiNp[bodyIndex] = DT.RotationMatrixNp(self.phiNp[bodyIndex])
            for pointIndex in range(len(vectorsRelativeCoG)):
                # Point Local - vector from module body CoG to the point, in body LCS coordinates
                # [This is what we needed phi for, to fix the orientation of the body]
                npVec = self.vecToNumpyF(vectorsRelativeCoG[pointIndex])
                self.pointLocalNp[bodyIndex, pointIndex, 0:2] = npVec @ self.RotMatPhiNp[bodyIndex]
                # Point Vector - vector from body CoG to the point in world coordinates
                self.pointVectorNp[bodyIndex, pointIndex, 0:2] = npVec.copy()
                self.pointVectorRotNp[bodyIndex][pointIndex] = self.Rot90NumpyF(npVec)
                # Point Vector Dot
                self.pointVectorDotNp[bodyIndex][pointIndex] = np.zeros((1, 2))
                # Point World - coordinates of the point relative to the system origin - in world coordinates
                npVec = self.vecToNumpyF(bodyPointsLocal[pointIndex])
                self.pointWorldNp[bodyIndex, pointIndex] = npVec.copy()
                self.pointWorldRotNp[bodyIndex, pointIndex] = self.Rot90NumpyF(npVec)
                # Point World Dot
                self.pointWorldDotNp[bodyIndex][pointIndex] = np.zeros((1, 2))
            # Next pointIndex
        # Next bodyIndex

        if 1==1: # Debug:
            DT.Mess("Point Dictionary: ")
            for bodyIndex in range(self.numBodies):
                DT.Mess(self.pointDictList[bodyIndex])
            DT.Mess("Mass: [g]")
            DT.Np1D(True, self.MassNp * 1.0e3)
            DT.Mess("")
            DT.Mess("Mass: [kg]")
            DT.Np1D(True, self.MassNp)
            DT.Mess("")
            DT.Mess("Weight Vector: [kg mm /s^2 = mN]")
            DT.Np2D(self.WeightNp)
            DT.Mess("")
            DT.Mess("MomentInertia: [kg.mm^2]")
            DT.Mess(self.momentInertiaNp)
            DT.Mess("")
            DT.Mess("Forces: [kg.mm/s^2 = mN]")
            DT.Np2D(self.sumForcesNp)
            DT.Mess("")
            DT.Mess("Moments: [N.mm]")
            DT.Np1D(True, self.sumMomentsNp)
            DT.Mess("")
            DT.Mess("World [CoG]: [mm]")
            DT.Np2D(self.worldNp)
            DT.Mess("")
            DT.Mess("WorldDot: [mm/s]")
            DT.Np2D(self.worldDotNp)
            DT.Mess("")
            DT.MessNoLF("phi: [deg]")
            DT.Np1Ddeg(True, self.phiNp)
            DT.Mess("")
            DT.MessNoLF("phi: [rad]")
            DT.Np1D(True, self.phiNp)
            DT.Mess("")
            DT.MessNoLF("phiDot: [deg/sec]")
            DT.Np1Ddeg(True, self.phiDotNp)
            DT.Mess("")
            DT.MessNoLF("phiDot: [rad/sec]")
            DT.Np1D(True, self.phiDotNp)
            DT.Mess("")
            DT.MessNoLF("Number of Points: ")
            DT.Mess(self.numPointsInDict)
            DT.Mess("")
            DT.Mess("PointLocal: [mm]")
            DT.Np3D(self.pointLocalNp)
            DT.Mess("")
            DT.Mess("PointVector: [mm]")
            DT.Np3D(self.pointVectorNp)
            DT.Mess("")
            DT.Mess("PointWorld: [mm]")
            DT.Np3D(self.pointWorldNp)
            DT.Mess("")

        # counter of function evaluations
        self.Counter = 0
        
        # Stuff for the penetration / Friction calculations
        self.flags = [False for index in range(10)]
        self.pen_d0 = [0.0 for index in range(10)]

        # Make an array with the respective body Mass and moment of inertia
        self.massArrayNp = np.zeros(self.numMovBodiesx3)
        for index in range(1, self.numBodies):
            bodyObj = self.bodyObjList[index]
            self.massArrayNp[(index-1)*3:index*3] = bodyObj.Mass, bodyObj.Mass, bodyObj.momentInertia

        # Make all Force unit vectors which are attached to ground, have their coordinates relative to world
        for forceIndex in range(self.numForces):
            forceObj = self.forceObjList[forceIndex]
            # Only do this for non-gravity forces
            if forceObj.actuatorType != 0:
                if forceObj.bodyHEADindex == 0 or forceObj.bodyTAILindex == 0:
                    self.forceUnitWorldNp[forceIndex] = self.forceUnitLocalNp[forceIndex].copy()
                    self.forceUnitWorldRotNp[forceIndex] = self.Rot90NumpyF(self.forceUnitWorldNp[forceIndex])
                if Debug:
                    DT.MessNoLF("ForceUnitLocal: ")
                    DT.Np2D(self.forceUnitLocalNp)
                    DT.MessNoLF("ForceUnitWorld: ")
                    DT.Np2D(self.forceUnitWorldNp)
                    DT.MessNoLF("ForceUnitWorldRot: ")
                    DT.Np2D(self.forceUnitWorldRotNp)

        # Assign number of constraints and number of bodies to each defined joint type
        for jointObj in self.jointObjList:
            bodyHEAD = jointObj.bodyHEADindex
            bodyTAIL = jointObj.bodyTAILindex

            if jointObj.JointType == DT.JOINT_TYPE_DICTIONARY["Rotation"]:
                jointObj.mConstraints = 2
                jointObj.nMovBodies = 2
                if jointObj.fixDof is True:
                    jointObj.mConstraints = 3
                    if bodyHEAD == 0:
                        jointObj.phi0 = -self.phiNp[bodyTAIL]
                    elif bodyTAIL == 0:
                        jointObj.phi0 = self.phiNp[bodyHEAD]
                    else:
                        jointObj.phi0 = self.phiNp[bodyHEAD] - self.phiNp[bodyTAIL]
            elif jointObj.JointType == DT.JOINT_TYPE_DICTIONARY["Translation"]:
                jointObj.mConstraints = 2
                jointObj.nMovBodies = 2
                if jointObj.fixDof is True:
                    jointObj.mConstraints = 3
                    if bodyHEAD == 0:
                        jointObj.phi0 = (+ self.pointWorldNp[bodyHEAD][pointHEADindex]
                                         - self.worldNp[bodyTAIL]
                                         - self.RotMatPhiNp[bodyTAIL] @
                                         self.pLocalsNp[bodyTAIL][pointTAILindex]).length()
                    elif bodyTAIL == 0:
                        jointObj.phi0 = (- self.pointWorldNp[bodyTAIL][pointTAILindex]
                                         + self.worldNp[bodyHEAD]
                                         + self.RotMatPhiNp[bodyHEAD] @
                                         self.pLocalsNp[bodyHEAD][pointHEADindex]).length()
                    else:
                        jointObj.phi0 = (+ self.worldNp[bodyHEAD]
                                         + self.RotMatPhiNp[bodyHEAD] @
                                         self.pLocalsNp[bodyHEAD][pointHEADindex]
                                         - self.worldNp[bodyTAIL]
                                         - self.RotMatPhiNp[bodyTAIL] @
                                         self.pLocalsNp[bodyTAIL][pointTAILindex]).length()
            elif jointObj.JointType == DT.JOINT_TYPE_DICTIONARY["Rotation-Rotation"]:
                jointObj.mConstraints = 1
                jointObj.nMovBodies = 2
            elif jointObj.JointType == DT.JOINT_TYPE_DICTIONARY["Rotation-Translation"]:
                jointObj.mConstraints = 1
                jointObj.nMovBodies = 2
            elif jointObj.JointType == DT.JOINT_TYPE_DICTIONARY["Driven-Rotation"]:
                jointObj.mConstraints = 1
                jointObj.nMovBodies = 1
            elif jointObj.JointType == DT.JOINT_TYPE_DICTIONARY["Driven-Translation"]:
                jointObj.mConstraints = 1
                jointObj.nMovBodies = 1
            elif jointObj.JointType == DT.JOINT_TYPE_DICTIONARY["Disc"]:
                jointObj.mConstraints = 2
                jointObj.nMovBodies = 1
            elif jointObj.JointType == DT.JOINT_TYPE_DICTIONARY["Rigid"]:
                jointObj.mConstraints = 3
                jointObj.nMovBodies = 2
                if bodyHEAD == 0:
                    A = -self.RotMatPhiNp[bodyTAIL].T @ self.worldNp[bodyTAIL]
                    jointObj.phi0 = -self.phiNp[bodyTAIL]
                elif bodyTAIL == 0:
                    A = self.worldNp[bodyHEAD]
                    jointObj.phi0 = self.phiNp[bodyHEAD]
                else:
                    A = self.RotMatPhiNp[bodyTAIL].T @ \
                        (self.worldNp[bodyHEAD] - self.worldNp[bodyTAIL])
                    jointObj.phi0 = self.phiNp[bodyHEAD] - self.phiNp[bodyTAIL]
                jointObj.d0.x = A[0]
                jointObj.d0.y = A[1]
            else:
                CAD.Console.PrintError("Unknown Joint Type - this should never occur\n")
        # Next Joint Object

        # Run through the joints and find if any of them use a driver function
        # if so, then initialize the parameters for the driver function routine
        self.driverObjDict = {}
        for jointIndex in range(self.numJoints):
            jointObj = self.jointObjList[jointIndex]
            # If there is a driver function, then
            # store an instance of the class in driverObjDict and initialize its parameters
            if jointObj.FunctType != -1:
                self.driverObjDict[jointObj.Name] = DapFunctMod.FunctionC(
                    [jointObj.FunctType,
                     jointObj.startTimeDriveFunc, jointObj.endTimeDriveFunc,
                     jointObj.startValueDriveFunc, jointObj.endValueDriveFunc,
                     jointObj.endDerivativeDriveFunc,
                     jointObj.Coeff0, jointObj.Coeff1, jointObj.Coeff2, jointObj.Coeff3, jointObj.Coeff4]
                )

        # Add up all the numbers of constraints and allocate row start and end pointers
        self.numConstraints = 0
        for jointObj in self.jointObjList:
            jointObj.rowStart = self.numConstraints
            jointObj.rowEnd = self.numConstraints + jointObj.mConstraints
            self.numConstraints = jointObj.rowEnd

        # Return with a flag to show we have reached the end of init error-free
        self.initialised = True
    #  -------------------------------------------------------------------------
    def MainSolve(self):
        if self.numConstraints != 0 and self.correctInitial:
            # Correct for initial conditions consistency
            if self.correctInitialConditions() is False:
                CAD.Console.PrintError("Initial Conditions not successfully calculated")
                return

        # Determine any redundancy between constraints
        Jacobian = self.getJacobianF()
        if Debug:
            DT.Mess("Jacobian calculated to determine rank of solution")
            DT.Np2D(Jacobian)
        redundant = np.linalg.matrix_rank(Jacobian)
        if redundant < self.numConstraints:
            CAD.Console.PrintError('The Constraints exhibit Redundancy\n')
            return

        # Velocity correction
        velCorrArray = np.zeros((self.numMovBodiesx3,), dtype=np.float64)
        # Move velocities to the corrections array
        for bodyIndex in range(1, self.numBodies):
            velCorrArray[(bodyIndex-1) * 3: bodyIndex*3] = \
                self.worldDotNp[bodyIndex, 0], \
                self.worldDotNp[bodyIndex, 1], \
                self.phiDotNp[bodyIndex]
        # Solve for velocity at time = 0
        # Unless the joint is relative-rotational or relative-translational
        # RHSVel = [0,0,...]   (i.e. a list of zeros)
        solution = np.linalg.solve(Jacobian @ Jacobian.T, (Jacobian @ velCorrArray) - self.RHSVel(0))
        deltaVel = -Jacobian.T @ solution
        if Debug:
            DT.MessNoLF("Velocity Correction Array: ")
            DT.Np1D(True, velCorrArray)
            DT.MessNoLF("Velocity Correction Solution: ")
            DT.Np1D(True, solution)
            DT.MessNoLF("Delta velocity: ")
            DT.Np1D(True, deltaVel)
        # Move corrected velocities back into the system
        for bodyIndex in range(1, self.numBodies):
            self.worldDotNp[bodyIndex, 0] += deltaVel[(bodyIndex-1)*3]
            self.worldDotNp[bodyIndex, 1] += deltaVel[(bodyIndex-1)*3+1]
            self.phiDotNp[bodyIndex] +=      deltaVel[(bodyIndex-1)*3+2]
        # Report corrected coordinates and velocities
        if Debug:
            DT.Mess("Corrected Positions: [mm]")
            DT.Np2D(self.worldNp)
            DT.Np1Ddeg(True, self.phiNp)
            DT.Mess("Corrected Velocities [mm/s]")
            DT.Np2D(self.worldDotNp)
            DT.Np1Ddeg(True, self.phiDotNp)

        ##############################
        # START OF THE SOLUTION PROPER
        ##############################
        # Pack coordinates and velocities into the numpy uArray
        uArray = np.zeros((self.numMovBodies * 6,), dtype=np.float64)
        index1 = 0
        index2 = self.numMovBodiesx3
        for bodyIndex in range(1, self.numBodies):
            uArray[index1:index1+2] = self.worldNp[bodyIndex]
            uArray[index1+2] = self.phiNp[bodyIndex]
            uArray[index2:index2+2] = self.worldDotNp[bodyIndex]
            uArray[index2+2] = self.phiDotNp[bodyIndex]
            index1 += 3
            index2 += 3
        if Debug:
            DT.Mess("uArray:")
            DT.Np1D(True, uArray)
        # Set up the list of time intervals over which to integrate
        self.Tspan = np.arange(0.0, self.simEnd, self.simDelta)

        # ###################################################################################
        # Matrix Integration Function
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
        # ###################################################################################
        
        # scipy.integrate.solve_ivp
        # INPUTS:
        #       fun,                      Function name
        #       t_span,                   (startTime, endTime)
        #       y0,                       Initial values array [uArray]
        #       method='RK45',            RK45 | RK23 | DOP853 | Radau | BDF | LSODA
        #       t_eval=None,              times to evaluate at
        #       dense_output=False,       continuous solutiion or not
        #       events=None,              events to track
        #       vectorized=False,         whether fun is vectorized (i.e. parallelized)
        #       args=None,
        #       first_step=None,          none means algorithm chooses
        #       max_step=inf,             default is inf
        #       rtol=1e-3, atol=1e-6      relative and absolute tolerances
        #       jacobian,                 required for Radau, BDF and LSODA
        #       jac_sparsity=None,        to help algorithm when it is sparse
        #       lband=inf, uband=inf,     lower and upper bandwidth of Jacobian
        #       min_step=0                minimum step (required for LSODA)
        # RETURNS:
        #       t                         time array
        #       y                         values array
        #       sol                       instance of ODESolution (when dense_output=True)
        #       t_events                  array of event times
        #       y_events                  array of values at the event_times
        #       nfev                      number of times the rhs was evaluated
        #       njev                      number of times the Jacobian was evaluated
        #       nlu                       number of LU decompositions
        #       status                    -1 integration step failure | +1 termination event | 0 Successful
        #       message                   Human readable error message
        #       success                   True if 0 or +1 above
        # ###################################################################################

        # Solve the equations: <analysis function> (<start time>, <end time>) <pos & vel array> <times at which to evaluate>
        solution = solve_ivp(self.Analysis,
                             (0.0, self.simEnd),
                             uArray,
                             t_eval=self.Tspan,
                             rtol=self.relativeTolerance,
                             atol=self.absoluteTolerance)

        # Output the positions/angles results file
        self.PosFILE = open(os.path.join(self.solverObj.Directory, "DapAnimation.csv"), 'w')
        Sol = solution.y.T
        for tick in range(len(solution.t)):
            self.PosFILE.write(str(solution.t[tick])+" ")
            for body in range(self.numBodies-1):
                self.PosFILE.write(str(Sol[tick, body * 3]) + " ")
                self.PosFILE.write(str(Sol[tick, body * 3 + 1]) + " ")
                self.PosFILE.write(str(Sol[tick, body * 3 + 2]) + " ")
            self.PosFILE.write("\n")
        self.PosFILE.close()

        # Save the most important stuff into the solver object
        BodyNames = []
        BodyCoG = []
        for bodyIndex in range(1, len(self.bodyObjList)):
            BodyNames.append(self.bodyObjList[bodyIndex].Name)
            BodyCoG.append(self.bodyObjList[bodyIndex].centreOfGravity)
        self.solverObj.BodyNames = BodyNames
        self.solverObj.BodyCoG = BodyCoG
        self.solverObj.DeltaTime = self.simDelta
        # Flag that the results are valid
        self.solverObj.DapResultsValid = True

        if self.solverObj.FileName != "-":
            self.outputResults(solution.t, solution.y.T)
    #####################################
    #   This is the end of the solution
    # The rest are all called subroutines
    #####################################
    #  -------------------------------------------------------------------------
    def Analysis(self, tick, uArray):
        """The Analysis function which takes a
        uArray consisting of a world 3vector and a velocity 3vector"""
        if Debug:
            DT.Mess("Input to 'Analysis'")
            DT.Np1D(True, uArray)

        # Unpack uArray into world coordinate and world velocity sub-arrays
        index1 = 0
        index2 = self.numMovBodiesx3
        for bodyIndex in range(1, self.numBodies):
            self.worldNp[bodyIndex, 0] = uArray[index1]
            self.worldNp[bodyIndex, 1] = uArray[index1+1]
            self.phiNp[bodyIndex] = uArray[index1+2]
            self.worldDotNp[bodyIndex, 0] = uArray[index2]
            self.worldDotNp[bodyIndex, 1] = uArray[index2+1]
            self.phiDotNp[bodyIndex] = uArray[index2+2]
            index1 += 3
            index2 += 3
        if Debug:
            DT.Np2D(self.worldNp)
            DT.Np1Ddeg(True, self.phiNp)
            DT.Np2D(self.worldDotNp)
            DT.Np1Ddeg(True, self.phiDotNp)

        # Update the point stuff accordingly
        self.updatePointPositions()
        self.updatePointVelocities()

        # array of applied forces
        self.makeForceArray()
        # find the accelerations ( a = F / m )
        accel = []
        if self.numConstraints == 0:
            for index in range(self.numMovBodiesx3):
                accel.append = self.massInvArray[index] * self.forceArrayNp[index]
        # We go through this if we have any constraints
        else:
            Jacobian = self.getJacobianF()
            if Debug:
                DT.Mess("Jacobian")
                DT.Np2D(Jacobian)

            # Create the Jacobian-Mass-Jacobian matrix
            # [ diagonal masses ---- Jacobian transpose ]
            # [    |                        |           ]
            # [  Jacobian      ------     Zeros         ]
            numBodPlusConstr = self.numMovBodiesx3 + self.numConstraints
            JacMasJac = np.zeros((numBodPlusConstr, numBodPlusConstr), dtype=np.float64)
            JacMasJac[0: self.numMovBodiesx3, 0: self.numMovBodiesx3] = np.diag(self.massArrayNp)
            JacMasJac[self.numMovBodiesx3:, 0: self.numMovBodiesx3] = Jacobian
            JacMasJac[0: self.numMovBodiesx3, self.numMovBodiesx3:] = -Jacobian.T
            if Debug:
                DT.Mess("Jacobian-MassDiagonal-JacobianT Array")
                DT.Np2D(JacMasJac)

            # get r-h-s of acceleration constraints at this time
            rhsAccel = self.RHSAcc(tick)
            if Debug:
                DT.Mess("rhsAccel")
                DT.Np1D(True, rhsAccel)
            # Combine Force Array and rhs of Acceleration Constraints into one array
            rhs = np.zeros((numBodPlusConstr,), dtype=np.float64)
            rhs[0: self.numMovBodiesx3] = self.forceArrayNp
            rhs[self.numMovBodiesx3:] = rhsAccel
            if Debug:
                DT.Mess("rhs")
                DT.Np1D(True, rhs)
            # Solve the JacMasJac augmented with the rhs
            solvedVector = np.linalg.solve(JacMasJac, rhs)
            # First half of solution are the acceleration values
            accel = solvedVector[: self.numMovBodiesx3]
            # Second half is Lambda which is reported in the output results routine
            self.Lambda = solvedVector[self.numMovBodiesx3:]
            if Debug:
                DT.MessNoLF("Accelerations: ")
                DT.Np1D(True, accel)
                DT.MessNoLF("Lambda: ")
                DT.Np1D(True, self.Lambda)

        # Transfer the accelerations back into the worldDotDot/phiDotDot and uDot/uDotDot Arrays
        for bodyIndex in range(1, self.numBodies):
            accelIndex = (bodyIndex-1)*3
            self.worldDotDotNp[bodyIndex] = accel[accelIndex], accel[accelIndex+1]
            self.phiDotDotNp[bodyIndex] = accel[accelIndex+2]
        uDotArray = np.zeros((self.numMovBodies * 6), dtype=np.float64)
        index1 = 0
        index2 = self.numMovBodiesx3
        for bodyIndex in range(1, self.numBodies):
            uDotArray[index1:index1+2] = self.worldDotNp[bodyIndex]
            uDotArray[index1+2] = self.phiDotNp[bodyIndex]
            uDotArray[index2:index2+2] = self.worldDotDotNp[bodyIndex]
            uDotArray[index2+2] = self.phiDotDotNp[bodyIndex]
            index1 += 3
            index2 += 3

        # Increment number of function evaluations
        self.Counter += 1

        return uDotArray
    #  -------------------------------------------------------------------------
    def correctInitialConditions(self):
        """This function corrects the supplied initial conditions by making
        the body coordinates and velocities consistent with the constraints"""
        if Debug:
            DT.Mess("DapMainMod-correctInitialConditions")
        # Try Newton-Raphson iteration for n up to 20
        for n in range(20):
            # Update the points positions
            self.updatePointPositions()

            # Evaluate DeltaConstraint of the constraints at time=0
            DeltaConstraints = self.Constraints(0)
            if Debug:
                DT.Mess("Delta Constraints Result:")
                DT.Np1D(True, DeltaConstraints)
                
            # Evaluate Jacobian
            Jacobian = self.getJacobianF()
            if Debug:
                DT.Mess("Jacobian:")
                DT.Np2D(Jacobian)

            # Determine any redundancy between constraints
            redundant = np.linalg.matrix_rank(Jacobian) 
            if redundant < self.numConstraints:
                CAD.Console.PrintError('The Constraints exhibit Redundancy\n')
                return False

            # We have successfully converged if the ||DeltaConstraint|| is very small
            DeltaConstraintLengthSq = 0
            for index in range(self.numConstraints):
                DeltaConstraintLengthSq += DeltaConstraints[index] ** 2
            if Debug:
                DT.Mess("Total Constraint Error: " + str(math.sqrt(DeltaConstraintLengthSq)))
            if DeltaConstraintLengthSq < 1.0e-16:
                return True

            # Solve for the new corrections
            solution = np.linalg.solve(Jacobian @ Jacobian.T, DeltaConstraints)
            delta = - Jacobian.T @ solution
            # Correct the estimates
            for bodyIndex in range(1, self.numBodies):
                self.worldNp[bodyIndex, 0] += delta[(bodyIndex-1)*3]
                self.worldNp[bodyIndex, 1] += delta[(bodyIndex-1)*3+1]
                self.phiNp[bodyIndex] +=      delta[(bodyIndex-1)*3+2]
                
        CAD.Console.PrintError("Newton-Raphson Correction failed to converge\n\n")
        return False
    #  -------------------------------------------------------------------------
    def updatePointPositions(self):
        for bodyIndex in range(1, self.numBodies):
            # Compute the Rotation Matrix
            self.RotMatPhiNp[bodyIndex] = DT.RotationMatrixNp(self.phiNp[bodyIndex])

            if Debug:
                DT.Mess("Local                   Vector                  Rotated                 World")
            for pointIndex in range(self.numPointsInDict[bodyIndex]):
                pointVector = self.RotMatPhiNp[bodyIndex] @ self.pointLocalNp[bodyIndex, pointIndex]
                self.pointVectorNp[bodyIndex, pointIndex] = pointVector
                self.pointWorldNp[bodyIndex, pointIndex] =  self.worldNp[bodyIndex] + pointVector
                self.pointVectorRotNp[bodyIndex][pointIndex] = self.Rot90NumpyF(pointVector)
                if Debug:
                    DT.Np1D(False, self.pointLocalNp[bodyIndex][pointIndex])
                    DT.MessNoLF("   ")
                    DT.Np1D(False, self.pointVectorNp[bodyIndex][pointIndex])
                    DT.MessNoLF("   ")
                    DT.Np1D(False, self.pointVectorRotNp[bodyIndex][pointIndex])
                    DT.MessNoLF("   ")
                    DT.Np1D(True, self.pointWorldNp[bodyIndex][pointIndex])
                    
        for forceIndex in range(self.numForces):
            forceObj = self.forceObjList[forceIndex]
            if forceObj.bodyHEADindex != 0:
                unitVector = self.RotMatPhiNp[forceObj.bodyHEADindex] @ self.forceUnitLocalNp[forceIndex]
                self.forceUnitWorldNp[forceIndex] = unitVector
                self.forceUnitWorldRotNp[forceIndex] = self.Rot90NumpyF(unitVector)
        if Debug:
            DT.MessNoLF("Unit Force Vector: ")
            DT.Np2D(self.forceUnitLocalNp)
            DT.MessNoLF("ForceUnitWorld: ")
            DT.Np2D(self.forceUnitWorldNp)
            DT.MessNoLF("ForceUnitWorldRot: ")
            DT.Np2D(self.forceUnitWorldRotNp)
    #  -------------------------------------------------------------------------
    def updatePointVelocities(self):
        if Debug:
            DT.Mess("DapMainMod-updatePointVelocities")
        for bodyIndex in range(1, self.numBodies):
            for pointIndex in range(self.numPointsInDict[bodyIndex]):
                velVector = self.pointVectorRotNp[bodyIndex, pointIndex] * self.phiDotNp[bodyIndex]
                self.pointVectorDotNp[bodyIndex, pointIndex] = velVector
                self.pointWorldDotNp[bodyIndex, pointIndex] = self.worldDotNp[bodyIndex] + velVector
        for forceObj in self.forceObjList:
            if forceObj.actuatorType != 0:
                if forceObj.bodyHEADindex != 0:
                    forceObj.unitWorldDot = self.Rot90NumpyF(forceObj.unitWorld) * self.phiDotNp[forceObj.bodyHEADindex]
    #  =============================================================================
    def Constraints(self, tick):
        if Debug:
            DT.Mess("DapMainMod-Constraints")
        DeltaConstraint = np.zeros((self.numConstraints,), dtype=np.float64)
        # Call the applicable function which is pointed to by the Constraints dictionary
        for jointObj in self.jointObjList:
            constraint = self.dictConstraintFunctions[jointObj.JointType](jointObj, tick)
            if Debug:
                DT.Mess(constraint)
            DeltaConstraint[jointObj.rowStart: jointObj.rowEnd] = constraint
        return DeltaConstraint
    #  -------------------------------------------------------------------------
    def revolute_Constraint(self, jointObj, tick):
        if Debug:
            DT.Mess("DapMainMod-revolute_Constraint")
        # Evaluate the constraints for a revolute joint
        bodyHEAD = jointObj.bodyHEADindex
        bodyTAIL = jointObj.bodyTAILindex
        constraint = self.pointWorldNp[bodyHEAD, jointObj.pointHEADindex] - self.pointWorldNp[bodyTAIL, jointObj.pointTAILindex]
        if jointObj.fixDof:
            if bodyHEAD == 0:
                constraint = np.array([constraint[0], constraint[1], -self.phiNp[bodyTAIL] - jointObj.phi0])
            elif bodyTAIL == 0:
                constraint = np.array([constraint[0], constraint[1],  self.phiNp[bodyHEAD] - jointObj.phi0])
            else:
                constraint = np.array([constraint[0], constraint[1],  self.phiNp[bodyHEAD] - self.phiNp[bodyTAIL] - jointObj.phi0])
        return constraint
    #  -------------------------------------------------------------------------
    def disc_Constraint(self, jointObject, tick):
        bodyHEAD = jointObject.bodyHEADindex
        return np.array([(self.worldNp[bodyHEAD, 1] - jointObject.Radius),
                         ((self.worldNp[bodyHEAD,0] - jointObject.x0) + jointObject.Radius *
                          (self.phiNp[bodyHEAD] - jointObject.phi0))])
    #  -------------------------------------------------------------------------
    def relative_rotational_Constraint(self, jointObject, tick):
        [func, funcDot, funcDotDot] = DapFunctionMod.GetFofT(jointObject.FunctType, tick)
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        if bodyHEAD == 0:
            f = -self.phiNp[bodyTAIL] - func
        elif bodyTAIL == 0:
            f = self.phiNp[bodyHEAD] - func
        else:
            f = self.phiNp[bodyHEAD] - self.phiNp[bodyTAIL] - func
        return np.array([f])
    #  -------------------------------------------------------------------------
    def relative_translational_Constraint(self, jointObject, tick):
        [func, funcDot, funcDotDot] = DapFunctionMod.GetFofT(jointObject.FunctType, tick)
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        pointHEAD = jointObject.pointHEADindex
        pointTAIL = jointObject.pointTAILindex
        diff = self.worldNp[bodyHEAD, pointHEAD] - self.worldNp[bodyTAIL, pointTAIL]
        return np.array([(diff.dot(diff) - func ** 2) / 2])
    #  -------------------------------------------------------------------------
    def revolute_revolute_Constraint(self, jointObject, tick):
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        pointHEAD = jointObject.pointHEADindex
        pointTAIL = jointObject.pointTAILindex
        diff = self.pointWorldNp[bodyHEAD, pointHEAD] - self.pointWorldNp[bodyTAIL, pointTAIL]
        Length = jointObject.lengthLink
        unitVec = diff / Length
        return np.array([(unitVec.dot(diff) - Length) / 2.0])
    #  -------------------------------------------------------------------------
    def revolute_translational_Constraint(self, jointObject, tick):
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        pointHEAD = jointObject.pointHEADindex
        pointTAIL = jointObject.pointTAILindex
        unitHEADRot = self.UnitVecRotNp[bodyHEAD]
        diff = self.pointWorldNp[bodyHEAD, pointHEAD] - self.pointWorldNp[bodyTAIL, pointTAIL]
        return np.array([unitHEADRot.dot(diff) - jointObject.Length])
    #  -------------------------------------------------------------------------
    def rigid_Constraint(self, jointObject):
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        TAILVec = self.RotMatPhiNp[bodyTAIL] @ (self.vecToNumpyF(jointObject.d0))
        if bodyHEAD == 0:
            return np.array([-self.worldNp[bodyTAIL] + TAILVec,
                             -self.phiNp[bodyTAIL] - jointObject.phi0])
        if bodyTAIL == 0:
            return np.array([self.worldNp[bodyHEAD] - self.vecToNumpyF(jointObject.d0),
                             self.phiNp[bodyHEAD] - jointObject.phi0])
        else:
            return np.array([self.worldNp[bodyHEAD] - self.worldNp[bodyTAIL] + TAILvec,
                             self.phiNp[bodyHEAD] - self.phiNp[bodyTAIL] - jointObject.phi0])
    #  -------------------------------------------------------------------------
    def translational_Constraint(self, jointObject, tick):
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        pointHEAD = jointObject.pointHEADindex
        pointTAIL = jointObject.pointTAILindex
        unitTAILRot = self.forceUnitWorldRotNp[bodyTAIL]
        unitHEAD = self.forceUnitWorldNp[bodyHEAD]
        diff = self.pointWorldNp[bodyHEAD, pointHEAD] - self.pointWorldNp[bodyTAIL, pointTAIL]
        if self.jointObject.fixDof:
            return np.array(
                [unitTAILRot.dot(diff), unitTAILRot.dot(unitHEAD), unitHEADRot.dot(diff) - jointObject.phi0 / 2])
        else:
            return np.array([unitTAILRot.dot(diff), unitTAILRot.dot(unitHEAD)])
    #  =========================================================================
    def getJacobianF(self):
        if Debug:
            DT.Mess("DapMainMod-Jacobian")
        Jacobian = np.zeros((self.numConstraints, self.numMovBodiesx3,))
        for jointObj in self.jointObjList:
            # Call the applicable function which is pointed to by the Jacobian dictionary
            JacobianHEAD, JacobianTAIL = self.dictJacobianFunctions[jointObj.JointType](jointObj)
            # Fill in the values in the Jacobian
            rowStart = jointObj.rowStart
            rowEnd = jointObj.rowEnd
            if jointObj.bodyHEADindex != 0:
                columnHEADStart = (jointObj.bodyHEADindex-1) * 3
                columnHEADEnd = jointObj.bodyHEADindex * 3
                Jacobian[rowStart: rowEnd, columnHEADStart: columnHEADEnd] = JacobianHEAD
            if jointObj.bodyTAILindex != 0:
                columnTAILStart = (jointObj.bodyTAILindex-1) * 3
                columnTAILEnd = jointObj.bodyTAILindex * 3
                Jacobian[rowStart: rowEnd, columnTAILStart: columnTAILEnd] = JacobianTAIL
        return Jacobian
    #  -------------------------------------------------------------------------
    def revolute_Jacobian(self, jointObj):
        if Debug:
            DT.Mess("DapMainMod-revolute_Jacobian")
        # Jacobian sub-matrices for a revolute joint
        if jointObj.fixDof:
            JacobianHEAD = np.array([
                [1.0, 0.0, - self.pointVectorNp[jointObj.bodyHEADindex, jointObj.pointHEADindex, 1]],
                [0.0, 1.0, self.pointVectorNp[jointObj.bodyHEADindex, jointObj.pointHEADindex, 0]],
                [0.0, 0.0, 1.0]])
            JacobianTAIL = np.array([
                [-1.0, 0.0, self.pointVectorNp[jointObj.bodyTAILindex, jointObj.pointTAILindex, 1]],
                [0.0, -1.0, - self.pointVectorNp[jointObj.bodyTAILindex, jointObj.pointTAILindex, 0]],
                [0.0, 0.0, -1.0]])
        else:
            JacobianHEAD = np.array([
                [1.0, 0.0, - self.pointVectorNp[jointObj.bodyHEADindex, jointObj.pointHEADindex, 1]],
                [0.0, 1.0, self.pointVectorNp[jointObj.bodyHEADindex, jointObj.pointHEADindex, 0]]])
            JacobianTAIL = np.array([
                [-1.0, 0.0, self.pointVectorNp[jointObj.bodyTAILindex, jointObj.pointTAILindex, 1]],
                [0.0, -1.0, - self.pointVectorNp[jointObj.bodyTAILindex, jointObj.pointTAILindex, 0]]])
        return JacobianHEAD, JacobianTAIL
    #  =========================================================================
    def disc_Jacobian(self, jointObject):
        # Jacobian sub-matrices for a disk joint between a body and the ground
        JacobianHEAD = np.array([[0.0, 1.0, 0.0],
                                 [1.0, 0.0, jointObject.Radius]])
        return JacobianHEAD, JacobianHEAD
    #  -------------------------------------------------------------------------
    def relative_rotational_Jacobian(self, jointObject):
        JacobianHEAD = np.array([0.0, 0.0, 1.0])
        JacobianTAIL = np.array([0.0, 0.0, -1.0])
        return JacobianHEAD, JacobianTAIL
    #  -------------------------------------------------------------------------
    def relative_translational_Jacobian(self, jointObject):
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        pointHEAD = jointObject.pointHEADindex
        pointTAIL = jointObject.pointTAILindex
        diff = self.pointWorldNp[bodyHEAD, pointHEAD] - self.pointWorldNp[bodyTAIL, pointTAIL]

        JacobianHEAD = np.array([diff[0], diff[1], diff.dot(self.pointVectorRotNp[bodyHEAD, pointHEAD])])
        JacobianTAIL = np.array([-diff[0], -diff[1], -diff.dot(self.pointVectorRotNp[bodyHEAD, pointTAIL])])
        return JacobianHEAD, JacobianTAIL
    #  -------------------------------------------------------------------------
    def revolute_revolute_Jacobian(self, jointObject):
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        pointHEAD = jointObject.pointHEADindex
        pointTAIL = jointObject.pointTAILindex
        diff = self.pointWorldNp[bodyHEAD, pointHEAD] - self.pointWorldNp[bodyTAIL, pointTAIL]
        unitVec = diff / jointObject.lengthLink

        JacobianHEAD = np.array([unitVec[0], unitVec[1], unitVec.dot(self.pointVectorRotNp[bodyHEAD, pointHEAD])])
        JacobianTAIL = np.array([-unitVec[0], -unitVec[1], -unitVec.dot(self.pointVectorRotNp[bodyTAIL, pointTAIL])])
        return JacobianHEAD, JacobianTAIL
    #  -------------------------------------------------------------------------
    def revolute_translational_Jacobian(self, jointObject):
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        pointHEAD = jointObject.pointHEADindex
        pointTAIL = jointObject.pointTAILindex
        unitVec = self.forceUnitWorldNp[bodyHEAD]
        unitVecRot = self.forceUnitWorldRotNp[bodyHEAD]
        diff = self.pointWorldNp[bodyHEAD, pointHEAD] - self.pointWorldNp[bodyTAIL, pointTAIL]

        JacobianHEAD = np.array([unitVecRot[0], unitVecRot[1], unitVec.dot(self.pointVectorNp[bodyHEAD, pointHEAD] - diff)])
        JacobianTAIL = np.array([-unitVecRot[0], -unitVecRot[1], -unitVec.dot(self.pointVectorNp[bodyTAIL, pointTAIL])])
        return JacobianHEAD, JacobianTAIL
    #  -------------------------------------------------------------------------
    def rigid_Jacobian(self, jointObject):
        bodyTAIL = jointObject.bodyTAILindex
        JacobianHEAD = np.array([[1.0, 0.0, 0.0],
                                 [0.0, 1.0, 0.0],
                                 [0.0, 0.0, 1.0]])
        if bodyTAIL != 0:
            BodAJoint = self.RotMatPhiNp[bodyTAIL] @ self.vecToNumpyF(jointObject.d0)
            JacobianTAIL = np.array([[-1.0, 0.0, -self.Rot90NumpyF(BodAJoint)[0]],
                                     [0.0, -1.0, -self.Rot90NumpyF(BodAJoint)[1]],
                                     [0.0, 0.0, -1.0]])
        return JacobianHEAD, JacobianTAIL
    #  -------------------------------------------------------------------------
    def translational_Jacobian(self, jointObject):
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        pointHEAD = jointObject.pointHEADindex
        pointTAIL = jointObject.pointTAILindex
        unitTAILVec = self.forceUnitWorldNp[bodyTAIL]
        unitTAILVecRot = self.forceUnitWorldRotNp[bodyTAIL]
        diff = self.pointWorldNp[bodyHEAD, pointHEAD] - self.pointWorldNp[bodyTAIL, pointTAIL]

        if jointObject.fixDof:
            JacobianHEAD = np.array(
                [[unitTAILVecRot[0], unitTAILVecRot[1], unitTAILVec.dot(self.pointVectorNp[bodyHEAD, pointHEAD])],
                 [0.0, 0.0, 1.0],
                 [unitTAILVec[0], unitTAILVec[1], unitTAILVec.dot(self.pointVectorRotNp[bodyHEAD, pointHEAD])]])
            JacobianTAIL = np.array(
                [[-unitTAILVecRot[0], -unitTAILVecRot[1],
                  -unitTAILVec.dot(self.pointVectorNp[bodyTAIL, pointTAIL] + diff)],
                 [0.0, 0.0, -1.0],
                 [-unitTAILVec[0], -unitTAILVec[1], -unitTAILVec.dot(self.pointVectorRotNp[bodyTAIL, pointTAIL])]])
        else:
            JacobianHEAD = np.array(
                [[unitTAILVecRot[0], unitTAILVecRot[1], unitTAILVec.dot(self.pointVectorNp[bodyHEAD, pointHEAD])],
                  [0.0, 0.0, 1.0]])
            JacobianTAIL = np.array(
                [[-unitTAILVecRot[0], -unitTAILVecRot[1],
                  -unitTAILVec.dot(self.pointVectorNp[bodyTAIL, pointTAIL] + diff)],
                 [-unitTAILVec.dot(bodyTAILindex.pointVectorNp[pointTAILindex] + diff)]])
        return JacobianHEAD, JacobianTAIL
    #  =========================================================================
    def RHSVel(self, tick):
        if Debug:
            DT.Mess("DapMainMod-RHSVel")
        # Call the applicable relative-rotation or relative-translation function where applicable
        rhsVel = np.zeros((self.numConstraints,), dtype=np.float64)
        for jointObj in self.jointObjList:
            if jointObj.JointType == 4:  # 'Driven-Rotation':
                [func, funcDot, funcDotDot] = DapFunctionMod.GetFofT(self.jointObject.FunctType, tick)
                fVelocity = func * funcDot
                rhsVel[jointObj.rowStart: jointObj.rowEnd] = fVelocity
            elif jointObj.JointType == 5:  # 'Driven-Translation':
                [func, funcDot, funcDotDot] = DapFunctionMod.GetFofT(self.jointObject.FunctType, tick)
                fVelocity = funcDot
                rhsVel[jointObj.rowStart: jointObj.rowEnd] = fVelocity
        return rhsVel
    #  =========================================================================
    def RHSAcc(self, tick):
        if Debug:
            DT.Mess("DapMainMod-RHSAcc")
        # Determine the Right=Hand-Side of the acceleration equation (gamma)
        rhsAcc = np.zeros((self.numConstraints,), dtype=np.float64)
        # Call the applicable function which is pointed to by the Acceleration dictionary
        for jointObj in self.jointObjList:
            gamma = self.dictAccelerationFunctions[jointObj.JointType](jointObj, tick)
            rhsAcc[jointObj.rowStart: jointObj.rowEnd] = gamma
        return rhsAcc
    #  =========================================================================
    def revolute_Acc(self, jointObj, tick):
        if Debug:
            DT.Mess("DapMainMod-revolute_Acc")
        bodyHEAD = jointObj.bodyHEADindex
        bodyTAIL = jointObj.bodyTAILindex
        pointHEAD = jointObj.pointHEADindex
        pointTAIL = jointObj.pointTAILindex
        if bodyHEAD == 0:
            gammaF = self.Rot90NumpyF(self.pointVectorDotNp[bodyTAIL, pointTAIL]) * self.phiDotNp[bodyTAIL]
        elif bodyTAIL == 0:
            gammaF = -self.Rot90NumpyF(self.pointVectorDotNp[bodyHEAD, pointHEAD]) * self.phiDotNp[bodyHEAD]
        else:
            gammaF = -self.Rot90NumpyF(self.pointVectorDotNp[bodyHEAD, pointHEAD]) * self.phiDotNp[bodyHEAD] + \
                     self.Rot90NumpyF(self.pointVectorDotNp[bodyTAIL, pointTAIL]) * self.phiDotNp[bodyTAIL]
        if jointObj.fixDof:
            gammaF = np.array([[gammaF[0], gammaF[1]],
                               [0.0, 0.0]])
        return gammaF
    #  -------------------------------------------------------------------------
    def disc_Acc(self, jointObject, tick):
        return np.array([0.0, 0.0])
    #  -------------------------------------------------------------------------
    def revolute_revolute_Acc(self, jointObject, tick):
        """ DAP_BC_12_2023/Formulation/"""
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        pointHEAD = jointObject.pointHEADindex
        pointTAIL = jointObject.pointTAILindex
        diff = self.pointWorldNp[bodyHEAD, pointHEAD] - self.pointWorldNp[bodyTAIL, pointTAIL]
        diffDot = self.pointWorldDotNp[bodyHEAD, pointHEAD] - self.pointWorldDotNp[bodyTAIL, pointTAIL]
        unit = diff/jointObject.lengthLink
        unitDotNp = diffDot/jointObject.lengthLink
        f = -unitDotNp.dot(diffDot)
        if bodyHEAD == 0:
            f += unit.dot(self.Rot90NumpyF(self.pointVectorDotNp[bodyTAIL, pointTAIL]) * self.phiDotNp[bodyTAIL])
        elif bodyTAIL == 0:
            f -= unit.dot(self.Rot90NumpyF(self.pointVectorDotNp[bodyHEAD, pointHEAD]) * self.phiDotNp[bodyHEAD])
        else:
            f += unit.dot(self.Rot90NumpyF(self.pointVectorDotNp[bodyTAIL, pointTAIL]) * self.phiDotNp[bodyTAIL]) \
                 -unit.dot(self.Rot90NumpyF(self.pointVectorDotNp[bodyHEAD, pointHEAD]) * self.phiDotNp[bodyHEAD])
        return f
    #  -------------------------------------------------------------------------
    def revolute_translational_Acc(self, jointObject, tick):
        bodyHEADindex = jointObject.bodyHEADindex
        bodyTAILindex = jointObject.bodyTAILindex
        pointHEADindex = jointObject.pointHEADindex
        pointTAILindex = jointObject.pointTAILindex
        unitHEAD = self.forceUnitWorldNp[bodyHEAD]
        unitHEADDot = self.forceUnitWorldNp[bodyHEAD]
        diff = self.pointWorldNp[bodyHEAD, pointHEAD] - self.pointWorldNp[bodyTAIL, pointTAIL]
        diffDot = self.pointWorldDotNp[bodyHEAD, pointHEAD] - self.pointWorldDotNp[bodyTAIL, pointTAIL]
        if bodyHEAD == 0:
            f = unitHEAD.dot(self.pointVectorDotNp[bodyTAIL, pointTAIL] * self.phiDotNp[bodyTAIL])
        elif bodyTAIL == 0:
            f = unitHEADDot.dot(diff * self.phiDotNp[bodyTAIL] + 2 * self.Rot90NumpyF(diffDot)) - \
                unitHEAD.dot(self.pointVectorDotNp[bodyHEAD, pointHEAD] * self.phiDotNp[bodyHEAD])
        else:
            f = unitHEADDotNp.dot(diff * self.phiDotNp[bodyHEAD] + 2 * self.Rot90NumpyF(diffDot)) - \
                unitHEAD.dot(self.pointVectorDotNp[bodyHEAD, pointHEAD] * self.phiDotNp[bodyHEAD] -
                             self.pointVectorDotNp[bodyTAIL, pointTAIL] * self.phiDotNp[bodyTAIL])
        return f
    #  -------------------------------------------------------------------------
    def rigid_Acc(self, jointObject, tick):
        bodyTAIL = jointObject.bodyTAILindex
        if bodyTAIL != 0:
            tailVector = -self.RotMatPhiNp[bodyTAIL] @ (self.vecToNumpyF(jointObject.d0) * (self.phiDotNp[bodyTAIL]**2))
            return np.array([tailVector[0], tailVector[1], 0.0])
        else:
            return np.array([0.0, 0.0, 0.0])
    #  -------------------------------------------------------------------------
    def translational_Acc(self, jointObject, tick):
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        pointHEAD = jointObject.pointHEADindex
        pointTAIL = jointObject.pointTAILindex
        unitTAILDot = self.forceUnitWorldDotNp[bodyTAIL]
        unitTAILDotRot = self.Rot90NumpyF(unitTAILDot)
        if bodyHEAD == 0:
            f2 = 0
        elif bodyTAIL == 0:
            f2 = 0
        else:
            f2 = unitTAILDot.dot(self.worldNp[bodyHEAD] - self.worldNp[bodyTAIL]) * self.phiDotNp[bodyHEAD] - \
                2 * unitTAILDotRot.dot(self.worldDotNp[bodyHEAD] - self.worldDotNp[bodyTAIL])
        if jointObject.fixDof:
            diff = self.pointWorldNp[bodyHEAD, pointHEAD] - self.pointWorldNp[bodyTAIL, pointTAIL]
            diffDot = self.pointWorldDotNp[bodyHEAD, pointHEAD] - self.pointWorldDotNp[bodyTAIL, pointTAIL]
            Length = jointObject.phi0
            unitVec = diff/Length
            unitVecDot = diffDot/Length
            f3 = -unitVecDot.dot(diffDot)
            if bodyHEAD == 0:
                f3 += unitVec.dot(self.Rot90NumpyF(bodyTAILindex.pointVectorDotNp[pointTAILindex]) * bodyTAILindex.phiDotNp)
            elif bodyObjTAIL == 0:
                f3 -= unit.dot(self.Rot90NumpyF(self.pointVectorDotNp[bodyHEAD, pointHEAD]) * self.phiDotNp[bodyHEAD])
            else:
                f3 -= unit.dot(self.Rot90NumpyF(self.pointVectorDotNp[bodyHEAD, pointHEAD] * self.phiDotNp[bodyHEAD] -
                               self.pointVectorDotNp[bodyTAIL, pointTAIL]) * self.phiDotNp[bodyTAIL])
            return np.array([f2, 0.0, f3])
        else:
            return np.array([f2, 0.0])
    #  -------------------------------------------------------------------------
    def relative_rotational_Acc(self, jointObject, tick):
        [func, funcDot, funcDotDot] = DapFunctionMod.GetFofT(self.jointObject.FunctType, tick)
        return funcDotDot
    #  -------------------------------------------------------------------------
    def relative_translational_Acc(self, jointObject, tick):
        [func, funcDot, funcDotDot] = DapFunctionMod.GetFofT(self.jointObject.FunctType, tick)
        bodyHEAD = jointObject.bodyHEADindex
        bodyTAIL = jointObject.bodyTAILindex
        pointHEAD = jointObject.pointHEADindex
        pointTAIL = jointObject.pointTAILindex
        diff = self.pointWorldNp[bodyHEAD, pointHEAD] - self.pointWorldNp[bodyTAIL, pointTAIL]
        diffDot = self.pointWorldDotNp[bodyHEAD, pointHEAD] - self.pointWorldDotNp[bodyTAIL, pointTAIL]
        f = func * funcDotDot + funcDot**2
        if bodyHEAD == 0:
            f += diff.dot(self.Rot90NumpyF(self.pointVectorDotNp[bodyTAIL, pointTAIL] * self.phiDotNp[bodyTAIL]))
        elif bodyTAIL == 0:
            f -= diff.dot(self.Rot90NumpyF(self.pointVectorDotNp[bodyHEAD, pointHEAD]) * self.phiDotNp[bodyHEAD]) - diffDot.dot(diffDot)
        else:
            f += diff.dot(self.Rot90NumpyF(self.pointVectorDotNp[bodyTAIL, pointTAIL] * self.phiDotNp[bodyTAIL]))\
                - diff.dot(self.Rot90NumpyF(self.pointVectorDotNp[bodyHEAD, pointHEAD]) * self.phiDotNp[bodyHEAD]) - diffDot.dot(diffDot)
        return f
    #  =========================================================================
    def LinearSpringDamperActuator(self, forceObject):
        bodyHEAD = forceObject.bodyHEADindex
        bodyTAIL = forceObject.bodyTAILindex
        # Get a dictionary of all points
        pointHEAD = forceObject.pointHEADindex
        pointTAIL = forceObject.pointTAILindex
        diffVector = self.pointWorldNp[bodyHEAD, pointHEAD] - \
            self.pointWorldNp[bodyTAIL, pointTAILindex]
        diffVectorDot = self.pointWorldDotNp[bodyHEAD, pointHEAD] - \
            self.pointWorldDotNp[bodyTAIL, pointTAILindex]
        L = diffVector.Length
        LDot = diffVector.dot(diffVectorDot) / L
        delta = L - forceObject.Value0
        unitDiffVector = diffVector / L
        force = forceObject.Stiffness * delta + \
            forceObject.DampingCoeff * LDot + \
            forceObject.forceActuator

        # Find the component of the force in the direction of
        # the vector between the head and the tail of the force
        forceProjection = force.dot(unitDiffVector)
        if bodyHEAD != 0:
            self.sumForcesNp[bodyHEAD] -= forceProjection
            self.sumMomentsNp[bodyHEAD] -= self.Rot90NumpyF(self.pointVectorNp[bodyHEAD, pointHEAD]).dot(forceProjection)
        if bodyTAIL != 0:
            self.sumForcesNp[bodyTAIL] += forceProjection
            self.sumMomentsNp[bodyTAIL] += self.Rot90NumpyF(self.pointVectorNp[bodyTAIL, pointTAIL]).dot(forceProjection)
    # -------------------------------------------------------------------------
    def RotationalSpringDamperActuator(self, forceObject):
        bodyHEAD = forceObject.bodyHEADindex
        bodyTAIL = forceObject.bodyTAILindex
        if bodyHEAD == 0:
            theta = -self.phiNp[bodyTAIL]
            thetaDot = -self.phiDotNp[bodyTAIL]
            Torque = forceObject.Stiffness * (theta - forceObject.Value0) + \
                forceObject.DampingCoeff * thetaDot + \
                forceObject.torqueActuator
            self.sumMomentsNp[bodyTAIL] += Torque
        elif bodyTAIL == 0:
            theta = self.phiNp[bodyHEAD]
            thetaDot = self.phiDotNp[bodyHEAD]
            Torque = forceObject.Stiffness * (theta - forceObject.Value0) + \
                forceObject.DampingCoeff * thetaDot + \
                forceObject.torqueActuator
            self.sumMomentsNp[bodyHEAD] -= Torque
        else:
            theta = self.phiNp[bodyHEAD] - self.phiNp[bodyTAIL]
            thetadot = self.phiDotNp[bodyHEAD] - self.phiDotNp[bodyTAIL]
            Torque = forceObject.Stiffness * (theta - forceObject.theta0) + \
                forceObject.DampingCoeff * thetaDot + \
                forceObject.torqueActuator
            self.sumMomentsNp[bodyHEAD] -= Torque
            self.sumMomentsNp[bodyTAIL] += Torque
    # -------------------------------------------------------------------------
    def futureImplementation(self, forceObject):
        return
    #  -------------------------------------------------------------------------
    def Contact(self, constraintIndex, indexPoint, bodyObj, kConst, eConst, FlagsList, penetrationDot0List, contact_LN_or_FM=True):
        penetration = -bodyObj.pointWorldNp[indexPoint].y
        if penetration > 0:
            penetrationDot = -bodyObj.pointWorldDotNp[indexPoint].y
            if FlagsList[constraintIndex] is False:
                penetrationDot0List[constraintIndex] = penetrationDot
                FlagsList[constraintIndex] = True

            if contact_LN_or_FM is True:
                forceY = Contact_LN(penetration, penetrationDot, penetrationDot0List[constraintIndex], kConst, eConst)
            else:
                forceY = Contact_FM(penetration, penetrationDot, penetrationDot0List[constraintIndex], kConst, eConst)

            Friction = CAD.Vector(0.0, forceY, 0.0)
            bodyObj.sumForces = bodyObj.sumForces + Friction
            bodyObj.sumMoments = bodyObj.sumMoments + bodyObj.pVecRot[indexPoint].dot(Friction)
        else:
            FlagsList[constraintIndex] = False
    #  -------------------------------------------------------------------------
    def Contact_FM(self, delta, deltaDot, deltaDot0, kConst, eConst):
        return kConst * (delta**1.5) * (1 + 8 * (1 - eConst) * deltaDot / (5 * eConst * deltaDot0))
    #  -------------------------------------------------------------------------
    def Contact_LN(self, delta, deltaDot, deltaDot0, kConst, eConst):
        return kConst * (delta**1.5) * (1 + 3 * (1 - eConst * eConst) * deltaDot / (4 * deltaDot0))
    #  -------------------------------------------------------------------------
    def Friction_A(self, mu_s, mu_d, v_s, p, k_t, v, fN):
        return fN * (mu_d + (mu_s - mu_d) * exp(-(abs(v) / v_s)**p)) * tanh(k_t * v)
    #  -------------------------------------------------------------------------
    def Friction_B(self, mu_s, mu_d, mu_v, v_t, fnt, v, fN):
        vr = v / v_t
        return fN * (mu_d * tanh(4 * vr) + (mu_s - mu_d) *
                     vr / (0.25 * vr * vr + 0.75)**2) + mu_v * v * tanh(4 * fN / fnt)
    #  =========================================================================
    def outputResults(self, timeValues, uResults):
        if Debug:
            DT.Mess("DapMainMod-outputResults")
        # Compute body accelerations, Lagrange multipliers, coordinates and
        #    velocity of all points, kinetic and potential energies,
        #             at every reporting time interval
        self.solverObj = CAD.ActiveDocument.findObjects(Name="^DapSolver$")[0]
        fileName = self.solverObj.Directory+"/"+self.solverObj.FileName+".csv"
        DapResultsFILE = open(fileName, 'w')
        numTicks = len(timeValues)

        # Create the vertical headings list
        # To write each body name into the top row of the spreadsheet,
        # would make some columns very big by default
        # So body names and point names are also written vertically in
        # The column before the body/point data is written
        VerticalHeaders = []
        # Write the column headers
        # Time
        for twice in range(2):
            ColumnCounter = 0
            DapResultsFILE.write("Time: ")
            # Bodies Heading
            for bodyIndex in range(1, self.numBodies):
                if twice==0:
                    VerticalHeaders.append(self.bodyObjList[bodyIndex].Label)
                    DapResultsFILE.write("Bod" + str(bodyIndex))
                    DapResultsFILE.write(" x y phi(r) phi(d) dx/dt dy/dt dphi/dt(r) dphi/dt(d) d2x/dt2 d2y/dt2 d2phi/dt2(r) d2phi/dt2(d) ")
                else:
                    DapResultsFILE.write(VerticalHeaders[ColumnCounter] + " -"*12 + " ")
                ColumnCounter += 1
                # Points Heading
                for index in range(self.numPointsInDict[bodyIndex]):
                    if twice == 0:
                        VerticalHeaders.append(self.bodyObjList[bodyIndex].pointLabels[index])
                        DapResultsFILE.write("Pnt" + str(index) + " x y dx/dt dy/dt ")
                    else:
                        DapResultsFILE.write(VerticalHeaders[ColumnCounter] + " -"*4 + " ")
                    ColumnCounter += 1
            # Lambda Heading
            if self.numConstraints > 0:
                for bodyIndex in range(1, self.numBodies):
                    if twice == 0:
                        VerticalHeaders.append(self.bodyObjList[bodyIndex].Label)
                        DapResultsFILE.write("Lam" + str(bodyIndex) + " x y ")
                    else:
                        DapResultsFILE.write(VerticalHeaders[ColumnCounter] + " - - ")
                    ColumnCounter += 1
            # Kinetic Energy Heading
            for bodyIndex in range(1, self.numBodies):
                if twice==0:
                    VerticalHeaders.append(self.bodyObjList[bodyIndex].Label)
                    DapResultsFILE.write("Kin" + str(bodyIndex) + " - ")
                else:
                    DapResultsFILE.write(VerticalHeaders[ColumnCounter] + " - ")
                ColumnCounter += 1

            # Potential Energy Heading
            for forceIndex in range(self.numForces):
                forceObj = self.forceObjList[forceIndex]
                if forceObj.actuatorType == 0:
                    for bodyIndex in range(1, self.numBodies):
                        if twice == 0:
                            VerticalHeaders.append(self.bodyObjList[bodyIndex].Label)
                            DapResultsFILE.write("Pot" + str(bodyIndex) + " - ")
                        else:
                            DapResultsFILE.write(VerticalHeaders[ColumnCounter] + " - ")
                        ColumnCounter += 1

            # Energy Totals Heading
            if twice == 0:
                DapResultsFILE.write("TotKin TotPot Total\n")
            else:
                DapResultsFILE.write("\n")

        # Do the calculations for each point in time
        # Plus an extra one at time=0 (with no printing)
        FirstTimeAround = True
        VerticalCounter = 0
        TickRange = [0]
        TickRange += range(numTicks)
        for timeIndex in TickRange:
            tick = timeValues[timeIndex]
            ColumnCounter = 0

            # Do the analysis on the stored uResults
            self.Analysis(tick, uResults[timeIndex])

            # Write Time
            if not FirstTimeAround:
                DapResultsFILE.write(str(tick) + " ")

            # Write All the Bodies position, positionDot, positionDotDot
            for bodyIndex in range(1, self.numBodies):
                if not FirstTimeAround:
                    # Body Name vertically
                    if VerticalCounter < len(VerticalHeaders[ColumnCounter]):
                        character = VerticalHeaders[ColumnCounter][VerticalCounter]
                        if character in "0123456789":
                            DapResultsFILE.write("'" + character + "' ")
                        else:
                            DapResultsFILE.write(character + " ")
                    else:
                        DapResultsFILE.write("- ")
                    ColumnCounter += 1
                    # X Y
                    DapResultsFILE.write(str(self.worldNp[bodyIndex]*1e-3) + " ")
                    # Phi (rad)
                    DapResultsFILE.write(str(self.phiNp[bodyIndex]) + " ")
                    # Phi (deg)
                    DapResultsFILE.write(str(self.phiNp[bodyIndex] * 180.0 / math.pi) + " ")
                    # Xdot Ydot
                    DapResultsFILE.write(str(self.worldDotNp[bodyIndex]*1e-3) + " ")
                    # PhiDot (rad)
                    DapResultsFILE.write(str(self.phiDotNp[bodyIndex]) + " ")
                    # PhiDot (deg)
                    DapResultsFILE.write(str(self.phiDotNp[bodyIndex] * 180.0 / math.pi) + " ")
                    # Xdotdot Ydotdot
                    DapResultsFILE.write(str(self.worldDotDotNp[bodyIndex]*1e-3) + " ")
                    # PhiDotDot (rad)
                    DapResultsFILE.write(str(self.phiDotDotNp[bodyIndex]) + " ")
                    # PhiDotDot (deg)
                    DapResultsFILE.write(str(self.phiDotDotNp[bodyIndex] * 180.0 / math.pi) + " ")

                # Write all the points position and positionDot in the body
                for index in range(self.numPointsInDict[bodyIndex]):
                    if not FirstTimeAround:
                        # Point Name vertically
                        if VerticalCounter < len(VerticalHeaders[ColumnCounter]):
                            character = VerticalHeaders[ColumnCounter][VerticalCounter]
                            if character in "0123456789":
                                DapResultsFILE.write("'" + character + "' ")
                            else:
                                DapResultsFILE.write(character + " ")
                        else:
                            DapResultsFILE.write("- ")
                        ColumnCounter += 1
                        # Point X Y
                        DapResultsFILE.write(str(self.pointWorldNp[bodyIndex, index]*1e-3) + " ")
                        # Point Xdot Ydot
                        DapResultsFILE.write(str(self.pointWorldDotNp[bodyIndex, index]*1e-3) + " ")

            # Write the Lambdas
            if self.numConstraints > 0:
                if not FirstTimeAround:
                    # Lambda
                    for bodyIndex in range(self.numMovBodies):
                        # Body Name vertically
                        if VerticalCounter < len(VerticalHeaders[ColumnCounter]):
                            character = VerticalHeaders[ColumnCounter][VerticalCounter]
                            if character in "0123456789":
                                DapResultsFILE.write("'" + character + "' ")
                            else:
                                DapResultsFILE.write(character + " ")
                        else:
                            DapResultsFILE.write("- ")
                        ColumnCounter += 1
                        DapResultsFILE.write(str(self.Lambda[bodyIndex*2] * 1e-3) + " " + str(self.Lambda[bodyIndex*2 + 1] * 1e-3) + " ")

            # Compute kinetic and potential energies in Joules
            totKinEnergy = 0
            for bodyIndex in range(1, self.numBodies):
                kinEnergy = 0.5 * (
                            (self.massArrayNp[(bodyIndex-1) * 3] *
                            (self.worldDotNp[bodyIndex, 0] ** 2 + self.worldDotNp[bodyIndex, 1] ** 2))
                            +
                            (self.massArrayNp[(bodyIndex - 1) * 3 + 2] *
                            (self.phiDotNp[bodyIndex] ** 2))
                            ) * 1e-6

                # Kinetic Energy (m^2 = mm^2 * 1e-6)
                if not FirstTimeAround:
                    # Body Name vertically
                    if VerticalCounter < len(VerticalHeaders[ColumnCounter]):
                        character = VerticalHeaders[ColumnCounter][VerticalCounter]
                        if character in "0123456789":
                            DapResultsFILE.write("'" + character + "' ")
                        else:
                            DapResultsFILE.write(character + " ")
                    else:
                        DapResultsFILE.write("- ")
                    ColumnCounter += 1
                    DapResultsFILE.write(str(kinEnergy) + " ")
                totKinEnergy += kinEnergy

            # Currently, calculate only gravitational potential energy
            totPotEnergy = 0
            for forceIndex in range(self.numForces):
                forceObj = self.forceObjList[forceIndex]
                # Potential Energy
                if forceObj.actuatorType == 0:
                    for bodyIndex in range(1, self.numBodies):
                        potEnergy = -self.WeightNp[bodyIndex].dot(self.worldNp[bodyIndex]) * 1e-6 - self.potEnergyZeroPointNp[bodyIndex]
                        totPotEnergy += potEnergy
                        if FirstTimeAround:
                            self.potEnergyZeroPointNp[bodyIndex] = potEnergy
                        else:
                            # Body Name vertically
                            if VerticalCounter < len(VerticalHeaders[ColumnCounter]):
                                character = VerticalHeaders[ColumnCounter][VerticalCounter]
                                if character in "0123456789":
                                    DapResultsFILE.write("'" + character + "' ")
                                else:
                                    DapResultsFILE.write(character + " ")
                            else:
                                DapResultsFILE.write("- ")
                            ColumnCounter += 1
                            DapResultsFILE.write(str(potEnergy) + " ")
                elif forceObj.actuatorType == "Point-to-point":
                    LinearSpringDamperActuator(forceObj)
                    potEnergy += 0.5 * forceObj.k * delta**2
                elif forceObj.actuatorType == "Rotational Spring Damper Actuator":
                    RotationalSpringDamperActuator(forceObj)
                elif forceObj.actuatorType == "Constant Local Force":
                    bodyHEAD = forceObj.bodyHEADindex
                    self.sumForcesNp[bodyHEAD] += self.RotMatPhiNp[bodyHEAD].multVec(forceObj.localForce)
                    self.sumForcesNp[bodyHEAD] += self.RotMatPhiNp[bodyHEAD] * self.forceUnitLocalNp[bodyHEAD]
                elif forceObj.actuatorType == "Constant Force":
                    bodyHEAD = forceObj.bodyHEADindex
                    self.sumForcesNp[bodyHEAD] += forceObj.constForce
                elif forceObj.actuatorType == "Constant Torque":
                    bodyHEAD = forceObj.bodyHEADindex
                    self.sumMomentsNp[bodyHEAD] += forceObj.constTorque
                elif forceObj.actuatorType == "Contact Friction":
                    futureImplementation(forceObj)
                elif forceObj.actuatorType == "Unilateral Spring Damper(Y)":
                    futureImplementation(forceObj)
                elif forceObj.actuatorType == "Unilateral Spring Damper(Z)":
                    futureImplementation(forceObj)
                elif forceObj.actuatorType == "Motor":
                    futureImplementation(forceObj)
                elif forceObj.actuatorType == "Motor-Air Friction":
                    futureImplementation(forceObj)

            if FirstTimeAround:
                FirstTimeAround = False
                VerticalCounter = 0
            else:
                DapResultsFILE.write(str(totKinEnergy) + " ")
                DapResultsFILE.write(str(totPotEnergy) + " ")
                DapResultsFILE.write(str(totKinEnergy + totPotEnergy) + " ")
                DapResultsFILE.write("\n")
                VerticalCounter += 1

        # Next timeIndex

        DapResultsFILE.close()
    #  -------------------------------------------------------------------------
    def makeForceArray(self):
        if Debug:
            DT.Mess("makeForceArray")
        # Reset all forces and moments to zero
        for bodyIndex in range(1, self.numBodies):
            self.sumForcesNp[bodyIndex] = np.zeros((2,), dtype=np.float64)
            self.sumMomentsNp[bodyIndex] = np.zeros((1,), dtype=np.float64)
        # Add up all the body force vectors for all the bodies
        for forceIndex in range(self.numForces):
            forceObj = self.forceObjList[forceIndex]
            if forceObj.actuatorType == 0:
                for bodyIndex in range(1, self.numBodies):
                    self.sumForcesNp[bodyIndex] += self.WeightNp[bodyIndex]
            # Handle all the other forces CLCCLCCLC

        # Next forceIndex

        # The force array has three values for every body
        # x and y are the sum of forces in Np and z is the sum of moments
        # Store all the bodies force/moments into the ForceArray
        for bodyIndex in range(1, self.numBodies):
            self.forceArrayNp[(bodyIndex - 1) * 3: bodyIndex * 3 - 1] = self.sumForcesNp[bodyIndex]
            self.forceArrayNp[bodyIndex * 3 - 1] = self.sumMomentsNp[bodyIndex]
        if Debug:
            DT.MessNoLF("Force Array:  ")
            DT.Np1D(True, self.forceArrayNp)
    #  =========================================================================
    def initNumPyArrays(self):
        # Initialize all the Numpy arrays with zeros
        self.MassNp = np.zeros((self.numBodies,), dtype=np.float64)
        self.WeightNp = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.momentInertiaNp = np.zeros((self.numBodies,), dtype=np.float64)
        self.sumForcesNp = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.sumMomentsNp = np.zeros((self.numBodies,), dtype=np.float64)
        self.worldNp = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.worldRotNp = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.worldDotNp = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.worldDotRotNp = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.worldDotDotNp = np.zeros((self.numBodies, 2,), dtype=np.float64)
        self.phiNp = np.zeros((self.numBodies,), dtype=np.float64)
        self.phiDotNp = np.zeros((self.numBodies,), dtype=np.float64)
        self.phiDotDotNp = np.zeros((self.numBodies,), dtype=np.float64)
        self.RotMatPhiNp = np.zeros((self.numBodies, 2, 2,), dtype=np.float64)

        self.pointLocalNp = np.zeros((self.numBodies, self.maxNumPoints, 2,), dtype=np.float64)
        self.pointVectorNp = np.zeros((self.numBodies, self.maxNumPoints, 2,), dtype=np.float64)
        self.pointVectorRotNp = np.zeros((self.numBodies, self.maxNumPoints, 2,), dtype=np.float64)
        self.pointVectorDotNp = np.zeros((self.numBodies, self.maxNumPoints, 2,), dtype=np.float64)
        self.pointWorldNp = np.zeros((self.numBodies, self.maxNumPoints, 2,), dtype=np.float64)
        self.pointWorldRotNp = np.zeros((self.numBodies, self.maxNumPoints, 2,), dtype=np.float64)
        self.pointWorldDotNp = np.zeros((self.numBodies, self.maxNumPoints, 2,), dtype=np.float64)

        self.forceUnitLocalNp = np.zeros((self.numForces, 2,), dtype=np.float64)
        self.forceUnitWorldNp = np.zeros((self.numForces, 2,), dtype=np.float64)
        self.forceUnitWorldRotNp = np.zeros((self.numForces, 2,), dtype=np.float64)

        self.forceArrayNp = np.zeros((self.numMovBodiesx3,), dtype=np.float64)
        self.potEnergyZeroPointNp = np.zeros((self.numBodies,), dtype=np.float64)
    #  -------------------------------------------------------------------------
    def nicePhiPlease(self, vectorsRelativeCoG):

        # Start off by looking at the longest vector and its orientation
        maxLength = 0
        maxVectorIndex = 0
        for localIndex in range(len(vectorsRelativeCoG) - 1):
            if vectorsRelativeCoG[localIndex].Length > maxLength:
                maxLength = vectorsRelativeCoG[localIndex].Length
                maxVectorIndex = localIndex
        
        # Start off with a big phi to mark that a good one hasn't been found yet
        phi = 1e6
        
        # Approximate phi from the longest local point vector
        x = vectorsRelativeCoG[maxVectorIndex].x
        y = vectorsRelativeCoG[maxVectorIndex].y
        if abs(x) < 1e-8:
            phi = math.pi / 2.0
        elif abs(y) < 1e-8:
            phi = 0
        elif abs(1.0 - abs(y / x)) < 1e-8:
            if y / x >= 0.0:
                phi = math.pi / 4.0
            else:
                phi = -math.pi / 4.0
        elif abs(0.57735026919 - abs(y / x)) < 1e-8:
            if y / x >= 0.0:
                phi = math.pi / 6.0
            else:
                phi = -math.pi / 6.0
        elif abs(1.73205080757 - abs(y / x)) < 1e-8:
            if y / x >= 0:
                phi = math.pi / 3.0
            else:
                phi = -math.pi / 3.0
        
        # If not, be satisfied with any other nice phi
        # of any other local point vector longer than 1/10 of the max one
        
        # Try for a multiple of 90 degrees
        if phi == 1e6:
            for localIndex in range(len(vectorsRelativeCoG) - 1):
                length = vectorsRelativeCoG[localIndex].Length
                if length > maxLength / 10.0:
                    x = vectorsRelativeCoG[maxVectorIndex].x
                    y = vectorsRelativeCoG[maxVectorIndex].y
                    if abs(x) < 1e-8:
                        phi = math.pi / 2.0
                        break
                    elif abs(y) < 1e-8:
                        phi = 0.0
                        break
        # If not found, try for a multiple of 45 degrees
        if phi == 1e6:
            for localIndex in range(len(vectorsRelativeCoG) - 1):
                length = vectorsRelativeCoG[localIndex].Length
                if length > maxLength / 10.0:
                    x = vectorsRelativeCoG[maxVectorIndex].x
                    y = vectorsRelativeCoG[maxVectorIndex].y
                    if abs(1.0 - abs(y / x)) < 1e-8:
                        if y / x >= 0.0:
                            phi = math.pi / 4.0
                            break
                        else:
                            phi = -math.pi / 4.0
                            break
        # Next try for a multiple of 30 degrees
        if phi == 1e6:
            for localIndex in range(len(vectorsRelativeCoG) - 1):
                length = vectorsRelativeCoG[localIndex].Length
                if length > maxLength / 10.0:
                    x = vectorsRelativeCoG[maxVectorIndex].x
                    y = vectorsRelativeCoG[maxVectorIndex].y
                    if abs(0.57735026919 - abs(y / x)) < 1e-8:
                        if y / x >= 0.0:
                            phi = math.pi / 6.0
                            break
                        else:
                            phi = -math.pi / 6.0
                            break
                    if abs(1.73205080757 - abs(y / x)) < 1e-8:
                        if y / x >= 0:
                            phi = math.pi / 3.0
                            break
                        else:
                            phi = -math.pi / 3.0
                            break
        # Give up trying to find a nice one - at least we tried!
        if phi == 1e6:
            phi = math.atan2(vectorsRelativeCoG[maxVectorIndex].y, vectorsRelativeCoG[maxVectorIndex].x)
        
        # Make -90 < phi < 90
        if abs(phi) > math.pi:
            if phi < 0.0:
                phi += math.pi
            else:
                phi -= math.pi
        if abs(phi) > math.pi / 2.0:
            if phi < 0.0:
                phi += math.pi
            else:
                phi -= math.pi

        return phi
    #  =========================================================================
    def vecToNumpyF(self, CADVec):
        # if Debug:
        #    DT.Mess("vecToNumpyF")
        a = np.zeros((2,))
        a[0] = CADVec.x
        a[1] = CADVec.y
        return a
    #  -------------------------------------------------------------------------
    def Rot90NumpyF(self, a):
        b = np.zeros((2))
        b[0], b[1] = -a[1], a[0]
        return b
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("TaskPanelDapMainC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("TaskPanelDapMainC-__setstate__")
    #  -------------------------------------------------------------------------

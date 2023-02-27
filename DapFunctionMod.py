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
from math import degrees, sin, cos
import numpy as np
if CAD.GuiUp:
    import FreeCADGui as CADGui
    from PySide import QtGui, QtCore
global Debug
Debug = False
# ============================================================================
class FunctionC:
    """
    This class encapsulates the function evaluations of Nikravesh et.al.

    The initialisation list passed on instantiation, in FuncParameterList,
    has the following form:
        [
        0...5,
        <timeStart>, <timeEnd>,
        <value of function at Start>, <value of function at End>,
        <dfdt at End>,
        <C0>, <C1>, <C2>,<C3>, <C4>
        ]
    Values not needed for the specific function type are ignored

    A call to FuncsC.getFofT(t) returns a list at time t:
        [f(t), fDot(t), fDotDot(t)]
    """

    if Debug:
        DT.Mess("FunctionsC-CLASS")

    #  ------------------------------------------------------------------------
    def __init__(self, FuntionParameterList):
        """ Called with a list:
        Constants[FuncType, timeStart, timeEnd, valueAtStart, valueAtEnd, dfdtEnd, Cp, Cq, Cr, Cs, Ct]
        """
        # Set up the dispatcher dictionary to jump to the applicable functions
        # based on the function type
        self.functDictionary = {0: self.function_a,
                                1: self.function_b,
                                2: self.function_c,
                                3: self.function_d,
                                4: self.function_e,
                                5: self.function_f}

        # Copy over the parameters which were passed in the init call
        FuncType = FuntionParameterList[0]
        timeStart = FuntionParameterList[1]
        timeEnd = FuntionParameterList[2]
        valueAtStart = FuntionParameterList[3]
        valueAtEnd = FuntionParameterList[4]
        dfdtEnd = FuntionParameterList[5]

        Cp = FuntionParameterList[6]
        Cq = FuntionParameterList[7]
        Cr = FuntionParameterList[8]
        Cs = FuntionParameterList[9]
        Ct = FuntionParameterList[10]

        # Make aliases of the function Types
        functionTypeA = 0
        functionTypeB = 1
        functionTypeC = 2
        functionTypeD = 3
        functionTypeE = 4
        functionTypeF = 5

        # Make an alias for an undefined value
        undefined = 0

        #  -----------------------------------------
        # Func type 'a'
        #    tt before timeStart:
        #        f(tt) = valueAtStart
        #        df_dtt     = 0
        #        d2_f_dtt2  = 0
        #    tt between timeStart and timeEnd:
        #         t = tt - timeStart
        #         f(tt)      = valueAtStart + Cp t + Cq t^2
        #         df_dtt     = Cp + 2 Cq t
        #         d2_f_dtt2  = 2 Cq
        #    tt after timeEnd:
        #        t = timeEnd - timeStart
        #        f(tt) = valueAtStart + Cp t + Cq t^2
        #        df_dtt     = 0
        #        d2_f_dtt2  = 0
        if FuncType == functionTypeA:
            self.Constants = [timeStart,
                               timeEnd,
                               valueAtStart,
                               undefined,
                               undefined,
                               Cp,
                               Cq,
                               undefined,
                               undefined,
                               undefined]
        #  -----------------------------------------
        # Func type 'b'
        #    tt before timeStart:
        #        f(tt) = valueAtStart
        #        df_dtt     = 0
        #        d2_f_dtt2  = 0
        #    tt between timeStart and timeEnd:
        #         t = tt - timeStart
        #         f(tt)     = valueAtStart + a3 t^3 + a4 t^4 + a5 t^5
        #         df_dtt   = 3 a3 t^2 + 4 a4 t^3 + 5 a5 t^4
        #         d2f_dtt2 = 6 a3 t + 12 a4 t^2 + 20 a5 t^3
        #             a's solved by program
        #        t = timeEnd - timeStart
        #        f(tt)     = valueAtStart + a3 t^3 + a4 t^4 + a5 t^5
        #        df_dtt     = dfdtEnd
        #        d2_f_dtt2  = 0
        #    tt after timeEnd:
        #        f(tt) = valueAtEnd
        #        df_dtt = 0
        #        d2f_dtt2 = 0
        elif FuncType == functionTypeB:
            xe = timeEnd - timeStart
            fe = valueAtEnd - valueAtStart
            C = np.array(
                [
                    [    xe ** 3,     xe ** 4,      xe ** 5],
                    [3 * xe ** 2, 4 * xe ** 3,  5 * xe ** 4],
                    [6 * xe,     12 * xe ** 2, 20 * xe ** 3]
                ]
            )
            solvedVector = np.linalg.solve(C, np.array([[fe], [0], [0]]))
            self.Constants = [timeStart,
                               timeEnd,
                               valueAtStart,
                               valueAtEnd,
                               undefined,
                               solvedVector[0],
                               solvedVector[1],
                               solvedVector[2],
                               undefined,
                               undefined]
        #  -----------------------------------------
        # Func type 'c'
        #    tt before timeStart:
        #        f(tt) = valueAtStart
        #        df_dtt     = 0
        #        d2_f_dtt2  = 0
        #    tt between timeStart and timeEnd:
        #         t = tt - timeStart
        #         f(tt)    = valueAtStart + a4 t^4 + a5 t^5 + a6 t^6
        #         df_dtt   = 4 a4 t^3 + 5 a5 t^4 + 6 a6 t^5
        #         d2f_dtt2 = 12 a4 t^2 + 20 a5 t^3 + 30 a6 t^4
        #             a's solved by program
        #    tt after timeEnd:
        #        t = timeEnd - timeStart
        #        f(tt) = valueAtStart + a4 t^4 + a5 t^5 + a6 t^6
        #        df_dtt = dfdtEnd
        #        d2f_dtt2 = 0
        elif self.FuncType == functionTypeC:
            xe = timeEnd - timeStart
            fpe = dfdtEnd
            C = np.array(
                [
                    [4 * xe ** 3,  5 * xe ** 4,  6 * xe ** 5],
                    [12 * xe ** 2, 20 * xe ** 3, 30 * xe ** 4],
                    [24 * xe,      60 * xe ** 2, 120 * xe ** 3]
                ]
            )
            solvedVector = np.linalg.solve(C, np.array([[fpe], [0], [0]]))
            self.Constants = [timeStart,
                               timeEnd,
                               valueAtStart,
                               undefined,
                               dfdtEnd,
                               solvedVector[0],
                               solvedVector[1],
                               solvedVector[2],
                               undefined,
                               undefined]
        #  -----------------------------------------
        # Func type 'd'
        #    tt before timeStart:
        #        f(tt) = valueAtStart
        #        df_dt = 0
        #        d2f_dt2 = 0
        #    tt between timeStart and timeEnd:
        #         t = tt - timeStart
        #         f(tt)      = valueAtStart + Cp t + Cq t^2 + Cr t^3 + Cs t^4 + Ct t^5
        #         df_dtt     = Cp + 2 Cq t + 3 Cr t^2 + 4 Cs t^3 + 5 Ct t^4
        #         d2f_dtt2   = 2 Cq + 6 Cr t + 12 Cs t^2 + 20 Ct t^3
        #    tt after timeEnd:
        #        t = timeEnd - timeStart
        #        f(tt)      = valueAtStart + Cp t + Cq t^2 + Cr t^3 + Cs t^4 + Ct t^5
        #        df_dtt = 0
        #        d2f_dtt2 = 0
        elif self.FuncType == functionTypeD:
            self.Constants = [timeStart,
                               timeEnd,
                               valueAtStart,
                               undefined,
                               undefined,
                               Cp,
                               Cq,
                               Cr,
                               Cs,
                               Ct]
        #  -----------------------------------------
        # Func type 'e'
        #    tt before timeStart:
        #        f(tt) = valueAtStart
        #        df_dt = 0
        #        d2f_dt2 = 0
        #    tt between timeStart and timeEnd:
        #       t = tt - timeStart
        #       f(tt)   = valueAtStart + Cp  sin(2pi Cr t + Ct) + Cq cos(2pi Cs t + Ct)
        #       df_dtt  =                Cp  cos(2pi Cr t + Ct) - Cq sin(2pi Cs t + Ct)
        #       d2f_dtt =                Cp -sin(2pi Cr t + Ct) + Cq cos(2pi Cs t + Ct)
        #    tt after timeEnd:
        #       t = timeEnd - timeStart
        #       f(tt)   = valueAtStart + Cp  sin(2pi Cr t + Ct) + Cq cos(2pi Cs t + Ct)
        #       df_dtt = 0
        #       d2f_dtt2 = 0
        elif self.FuncType == functionTypeE:
            self.Constants = [timeStart,
                               timeEnd,
                               valueAtStart,
                               undefined,
                               undefined,
                               Cp,
                               Cq,
                               Cr,
                               Cs,
                               Ct]
        #  -----------------------------------------
        # Func type 'f'
        # room for expansion - Taylor series???
        elif self.FuncType == functionTypeF:
            self.Constants = [timeStart,
                               timeEnd,
                               valueAtStart,
                               valueAtEnd,
                               dfdtEnd,
                               Cp,
                               Cq,
                               Cr,
                               Cs,
                               Ct]
        else:
            CAD.Console.PrintError("Illegal Function Type specified\n")

    #  ------------------------------------------------------------------------
    def getFofT(self, t):
        """
        # ========================= MATLAB CODE =========================
        # =========functs.m==========
        # function [f, f_d, f_dd] = functs(Ci, t)
        #     include_global
        # 
        #     switch (Functs(Ci).type)
        #         case {'a'}
        #             [f, f_d, f_dd] = funct_a(Ci, t);
        #         case {'b'}
        #             [f, f_d, f_dd] = funct_b(Ci, t);
        #         case {'c'}
        #             [f, f_d, f_dd] = funct_c(Ci, t);
        #         case {'d'}
        #             [f, f_d, f_dd] = funct_d(Ci, t);
        #     end
        # ====================== End of MATLAB CODE =====================
        """

        # Run the applicable function as set up in the dictionary above
        return self.functDictionary[self.FuncType](t)

    #  ------------------------------------------------------------------------
    def function_a(self, tt):
        """
        Between time = timeStart and time = timeEnd:
            t = time - timeStart
        f(t) = a0 + a1 t + a2 t^2
        """
        if tt <= self.Constants[0]:
            func_t = self.Constants[2]
            d_func_dt = 0
            d2_func_dt2 = 0
        else:
            if tt >= self.Constants[1]:
                t = self.Constants[1] - self.Constants[0]
            else:
                t = tt - self.Constants[0]

            func_t = self.Constants[2] + (self.Constants[3] + self.Constants[4] * t) * t
            d_func_dt = self.Constants[3] + self.Constants[4] * 2 * t
            d2_func_dt2 = self.Constants[4] * 2

        return [func_t, d_func_dt, d2_func_dt2]
        #  ------------------------------------------------------------------------
    def function_b(self, tt):
        """ Func type 'b' -> 1
            between time = timeStart and time = timeEnd:
                t = time - timeStart
            f(t)      = a0 + a3 t^3 + a4 t^4 + a5 t^5
            df_dt   = 3 a3 t^2 + 4 a4 t^3 + 5 a5 t^4
            d2f_dt2 = 6 a3 t + 12 a4 t^2 + 20 a5 t^3
            with first and second derivative zero at tStart and tEnd
        """
        if tt <= self.Constants[0]:
            func_t = self.Constants[2]
            d_func_dt = 0
            d2_func_dt2 = 0
        elif tt <= self.Constants[1]:
            t = tt - self.Constants[0]
            func_t = self.Constants[2] + (self.Constants[4] + (
                    self.Constants[5] + self.Constants[6] * t) * t) * t * t * t
            d_func_dt = (3*self.Constants[4] + 4*(self.Constants[5] + 5*self.Constants[6] * t) * t) * t * t
            d2_func_dt2 = (6*self.Constants[4] + 12*(self.Constants[5] + 20*self.Constants[6] * t) * t) * t
        else:
            func_t = self.Constants[3]
            d_func_dt = 0
            d2_func_dt2 = 0

        return [func_t, d_func_dt, d2_func_dt2]
    #  ------------------------------------------------------------------------
    def function_c(self, tt):
        """
        Between time = timeStart and time = timeEnd:
                t = time - timeStart
        f(t)      = a0 + a4 t^4 + a5 t^5 + a6 t^6
        df_dt   = 4 a4 t^3 + 5 a5 t^4 + 6 a6 t^5
        d2f_dt2 = 12 a4 t^2 + 20 a5 t^3 + 30 a6 t^4
        """
        if tt <= self.Constants[0]:
            func_t = self.Constants[2]
            return [func_t, 0.0, 0.0]
        elif tt <= self.Constants[1]:
            t = tt - self.timeStart
        else:
            t = self.timeEnd

        func_t = self.Constants[2] + (self.Constants[4] + (self.Constants[5] + self.Constants[6] * t) * t) * t * t
        if tt >= self.Constants[1]:
            d_func_dt = self.Constants[3]
            return [func_t, d_func_dt, 0.0]
        else:
            d_func_dt = (4 * self.Constants[4] + (5 * self.Constants[5] + 6 * self.Constants[6] * t) * t) * t * t
            d2_func_dt2 = (12 * self.Constants[4] + (20 * self.Constants[5] + 30 * self.Constants[6] * t) * t) * t * t

        return [func_t, d_func_dt, d2_func_dt2]
    #  ------------------------------------------------------------------------
    def function_d(self, tt):
        """
        Between time = timeStart and time = timeEnd:
                t = time - timeStart
        f(t)    =  a0 + a3 t^3 +  a4 t^4 +  a5 t^5 +  a6 t^6 +  a7 t^7
        df_dt   = 3 a3 t^3 + 4 a4 t^4 + 5 a5 t^5
        d2f_dt2 = 9 a3 t^2 + 16 a5 t^3 + 25 a5 t^4
        """
        if tt <= self.Constants[0]:
            func_t = self.Constants[2]
            d_func_dt = 0
            d2_func_dt2 = 0
        else:
            if tt >= self.Constants[1]:
                t = self.Constants[1] - self.Constants[0]
            else:
                t = tt - self.Constants[0]

        if tt <= self.Constants[0]:
            func_t = self.Constants[2]
            d_func_dt = 0
            d2_func_dt2 = 0
        elif tt <= self.timeEnd:
            t = tt - self.timeStart
            func_t = (self.ConstTypeD[0] + (self.ConstTypeD[1] + (self.ConstTypeD[2] + (self.ConstTypeD[3] + self.ConstTypeD[4] * t) * t) * t) * t) * t * t * t + self.valueAtStart
            d_func_dt = (self.ConstTypeD[5] + (self.ConstTypeD[6] + (self.ConstTypeD[7] + (self.ConstTypeD[8] + self.ConstTypeD[9] * t) * t) * t) * t) * t * t
            d2_func_dt2 = (self.ConstTypeD[10] + (self.ConstTypeD[11] + (self.ConstTypeD[12] + (self.ConstTypeD[13] + self.ConstTypeD[14] * t) * t) * t) * t) * t
        else:
            func_t = self.valueAtEnd
            d_func_dt = 0
            d2_func_dt2 = 0

        return [func_t, d_func_dt, d2_func_dt2]

    #  ------------------------------------------------------------------------
    def function_e(self, t):
        # Func type 'e'
        # ft      = C(0) + C(1) * sin(C(2) * t) + C(3) * cos(C(4) * t)
        # df_dt   =        C(1) * C(2) * cos(C(2) * t) - C(3) * C(4) * sin(C(4) * t)
        # d2f_dt2 =      - C(1) * C(2)^2 * sin(C(2) * t) - C(3) * C(4)^2 * cos(C(4) * t)
        if tt <= self.timeStart:
            func_t = self.valueAtStart
            d_func_dt = 0
            d2_func_dt2 = 0
        elif tt > self.timeStart and tt < self.timeEnd:
            func_t = self.ConstTypeE[0] + self.ConstTypeE[1] * sin(self.ConstTypeE[2] * t) + self.ConstTypeE[3] * cos(self.ConstTypeE[4] * t)
            d_func_dt = self.ConstTypeE[1] * self.ConstTypeE[2] * cos(self.ConstTypeE[2] * t) - self.ConstTypeE[3] * self.ConstTypeE[4] * sin(self.ConstTypeE[4] * t)
            d2_func_dt2 = -self.ConstTypeE[1] * self.ConstTypeE[2] ^ 2 * sin(self.ConstTypeE[2] * t) - self.ConstTypeE[3] * self.ConstTypeE[4] ^ 2 * cos(self.ConstTypeE[4] * t)
        else:
            func_t = self.valueAtEnd
            d_func_dt = 0
            d2_func_dt2 = 0

        return [func_t, d_func_dt, d2_func_dt2]

    #  ------------------------------------------------------------------------
    def function_f(self, t):
        # Func type 'f'
        #     ft      =  c(0) +  c(1)*t +  c(2)*t^2 +  c(3)*t^3 +  c(4)*t^4 + f0
        #     df_dt   =  c(5) +  c(6)*t +  c(7)*t^2 +  c(8)*t^3
        #     d2f_dt2 =  c(9) + c(10)*t + c(11)*t^2
        if tt <= self.timeStart:
            func_t = self.valueAtStart
            d_func_dt = 0
            d2_func_dt2 = 0
        elif tt > self.timeStart and tt < self.timeEnd:
            t = tt - self.timeStart
            func_t = self.ConstTypeF[0] + (self.ConstTypeF[1] + (self.ConstTypeF[2] + (self.ConstTypeF[3] + self.ConstTypeF[4] * t) * t) * t) * t + self.valueAtStart
            d_func_dt = self.ConstTypeF[5] + (self.ConstTypeF[6] + (self.ConstTypeF[7] + self.ConstTypeF[8] * t) * t) * t
            d2_func_dt2 = self.ConstTypeF[9] + (self.ConstTypeF[10] + self.ConstTypeF[11] * t) * t
        else:
            func_t = self.valueAtEnd
            d_func_dt = 0
            d2_func_dt2 = 0

        return [func_t, d_func_dt, d2_func_dt2]
    #  -------------------------------------------------------------------------
    def __getstate__(self):
        if Debug:
            DT.Mess("TaskPanelDapFunctionC-__getstate__")
    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        if Debug:
            DT.Mess("TaskPanelDapFunctionC-__setstate__")
    # -------------------------------------------------------------------------------------------------
    def __str__(self):
        return str(self.__dict__)
# =============================================================================

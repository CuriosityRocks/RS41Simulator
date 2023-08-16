# -*- coding: utf-8 -*-
"""
RS41 protocol and measurements read-write operations
"""

#############################################
# The following functions are a part of an  #
# RS41-SG/P radiosonde simulation framework.#
# The functions are protocol and            #
# measurements read-write functions,        #
# compatible with the RS41-SG/P'            #
# transmission protocol.                    #
#                                           #
# These functions were written by Paz       #
# Hameiri in 2023                           #
#                                           #
# For more information regarding the RS41'  #
# transmission protocol, see bazjo's work   #
# on RS41 radiosonde at:                    #
# https://github.com/bazjo/RS41_Decoding    #
#############################################

import numpy as np
import math
import datetime
from skyfield.api import load, wgs84
from numpy import array2string
import pymap3d

from RS41SubframeRW import *
from RS41BlocksRW import *

# %% Data whitening function
###########################
# Data whitening function #
###########################

BitReverseTable256 = np.uint8([
  0x00, 0x80, 0x40, 0xC0, 0x20, 0xA0, 0x60, 0xE0, 0x10, 0x90, 0x50, 0xD0, 0x30, 0xB0, 0x70, 0xF0, 
  0x08, 0x88, 0x48, 0xC8, 0x28, 0xA8, 0x68, 0xE8, 0x18, 0x98, 0x58, 0xD8, 0x38, 0xB8, 0x78, 0xF8, 
  0x04, 0x84, 0x44, 0xC4, 0x24, 0xA4, 0x64, 0xE4, 0x14, 0x94, 0x54, 0xD4, 0x34, 0xB4, 0x74, 0xF4, 
  0x0C, 0x8C, 0x4C, 0xCC, 0x2C, 0xAC, 0x6C, 0xEC, 0x1C, 0x9C, 0x5C, 0xDC, 0x3C, 0xBC, 0x7C, 0xFC, 
  0x02, 0x82, 0x42, 0xC2, 0x22, 0xA2, 0x62, 0xE2, 0x12, 0x92, 0x52, 0xD2, 0x32, 0xB2, 0x72, 0xF2, 
  0x0A, 0x8A, 0x4A, 0xCA, 0x2A, 0xAA, 0x6A, 0xEA, 0x1A, 0x9A, 0x5A, 0xDA, 0x3A, 0xBA, 0x7A, 0xFA,
  0x06, 0x86, 0x46, 0xC6, 0x26, 0xA6, 0x66, 0xE6, 0x16, 0x96, 0x56, 0xD6, 0x36, 0xB6, 0x76, 0xF6, 
  0x0E, 0x8E, 0x4E, 0xCE, 0x2E, 0xAE, 0x6E, 0xEE, 0x1E, 0x9E, 0x5E, 0xDE, 0x3E, 0xBE, 0x7E, 0xFE,
  0x01, 0x81, 0x41, 0xC1, 0x21, 0xA1, 0x61, 0xE1, 0x11, 0x91, 0x51, 0xD1, 0x31, 0xB1, 0x71, 0xF1,
  0x09, 0x89, 0x49, 0xC9, 0x29, 0xA9, 0x69, 0xE9, 0x19, 0x99, 0x59, 0xD9, 0x39, 0xB9, 0x79, 0xF9, 
  0x05, 0x85, 0x45, 0xC5, 0x25, 0xA5, 0x65, 0xE5, 0x15, 0x95, 0x55, 0xD5, 0x35, 0xB5, 0x75, 0xF5,
  0x0D, 0x8D, 0x4D, 0xCD, 0x2D, 0xAD, 0x6D, 0xED, 0x1D, 0x9D, 0x5D, 0xDD, 0x3D, 0xBD, 0x7D, 0xFD,
  0x03, 0x83, 0x43, 0xC3, 0x23, 0xA3, 0x63, 0xE3, 0x13, 0x93, 0x53, 0xD3, 0x33, 0xB3, 0x73, 0xF3, 
  0x0B, 0x8B, 0x4B, 0xCB, 0x2B, 0xAB, 0x6B, 0xEB, 0x1B, 0x9B, 0x5B, 0xDB, 0x3B, 0xBB, 0x7B, 0xFB,
  0x07, 0x87, 0x47, 0xC7, 0x27, 0xA7, 0x67, 0xE7, 0x17, 0x97, 0x57, 0xD7, 0x37, 0xB7, 0x77, 0xF7, 
  0x0F, 0x8F, 0x4F, 0xCF, 0x2F, 0xAF, 0x6F, 0xEF, 0x1F, 0x9F, 0x5F, 0xDF, 0x3F, 0xBF, 0x7F, 0xFF])

XorArray = np.uint8([0x96, 0x83, 0x3E, 0x51, 0xB1, 0x49, 0x08, 0x98,
            0x32, 0x05, 0x59, 0x0E, 0xF9, 0x44, 0xC6, 0x26,
            0x21, 0x60, 0xC2, 0xEA, 0x79, 0x5D, 0x6D, 0xA1,
            0x54, 0x69, 0x47, 0x0C, 0xDC, 0xE8, 0x5C, 0xF1,
            0xF7, 0x76, 0x82, 0x7F, 0x07, 0x99, 0xA2, 0x2C,
            0x93, 0x7C, 0x30, 0x63, 0xF5, 0x10, 0x2E, 0x61,
            0xD0, 0xBC, 0xB4, 0xB6, 0x06, 0xAA, 0xF4, 0x23,
            0x78, 0x6E, 0x3B, 0xAE, 0xBF, 0x7B, 0x4C, 0xC1])

# Prefrom data whitening: Xor message bytes with a predefined xor mask
def DataWhitening(FrameLength, MessageBytes):
    EncryptedMessageBytes = np.zeros(FrameLength, dtype=np.uint8)
    
    TempStartIndex = 0
    TempEndIndex = 0
    while TempStartIndex < FrameLength:
        if (FrameLength - TempStartIndex) >= 64:
            TempEndIndex = TempStartIndex + 64
        else:
            TempEndIndex = FrameLength
        EncryptedMessageBytes[TempStartIndex:TempEndIndex] = np.bitwise_xor(MessageBytes[TempStartIndex:TempEndIndex], XorArray[0:(TempEndIndex-TempStartIndex)]) 
        TempStartIndex = TempEndIndex
    
    # Reverse bits order MSB->LSB, LSB->MSB
    ReversedEncryptedMessageBytes = bytearray(BitReverseTable256[EncryptedMessageBytes])
    return ReversedEncryptedMessageBytes 

# %% Ambient temperature calculations functions
##############################################
# Ambient temperature calculations functions #
##############################################

def AmbTempFrameParamsCalc(Temperature, TempRefRes1, TempRefRes2,
                    TempCalCoeff1, TempCalCoeff2, TempCalCoeff3,
                    TempPolCoeff1, TempPolCoeff2, TempPolCoeff3):
    '''
    RS41 Ambient temperature frame parameters calculation.
    '''
    
    RtoTratio = 169.5 # empirical. TODO: Change the value according to external temperature
    RtoToffset = 3160 # empirical. TODO: Change the value according to external temperature
    
    c = TempPolCoeff1 + TempCalCoeff2 - ( Temperature / (1.0 + TempCalCoeff3) )
    R1 = (-TempPolCoeff2 + math.sqrt(pow(TempPolCoeff2,2)-4*TempPolCoeff3*c))/(2*TempPolCoeff3)
    R2 = (-TempPolCoeff2 - math.sqrt(pow(TempPolCoeff2,2)-4*TempPolCoeff3*c))/(2*TempPolCoeff3)
    Rc1 = R1/TempCalCoeff1
    Rc2 = R2/TempCalCoeff1
    if (abs(Rc1-1000) < abs(Rc2-1000)):
        Rc=Rc1
    else:
        Rc=Rc2
    TemperatureMain = int(RtoTratio * Rc + RtoToffset)
    TemperatureRef1 = int(RtoTratio * TempRefRes1 + RtoToffset)
    TemperatureRef2 = int(RtoTratio * TempRefRes2 + RtoToffset)

    return TemperatureMain, TemperatureRef1 , TemperatureRef2 

def AmbMainTempFrameCalc(Temperature, TemperatureRef1, TemperatureRef2,
                    TempRefRes1, TempRefRes2,
                    TempCalCoeff1, TempCalCoeff2, TempCalCoeff3,
                    TempPolCoeff1, TempPolCoeff2, TempPolCoeff3):
    '''
    RS41 Ambient temperature frame main parameter calculation.
    '''
        
    c = TempPolCoeff1 + TempCalCoeff2 - ( Temperature / (1.0 + TempCalCoeff3) )
    R1 = (-TempPolCoeff2 + math.sqrt(pow(TempPolCoeff2,2)-4*TempPolCoeff3*c))/(2*TempPolCoeff3)
    R2 = (-TempPolCoeff2 - math.sqrt(pow(TempPolCoeff2,2)-4*TempPolCoeff3*c))/(2*TempPolCoeff3)
    Rc1 = R1/TempCalCoeff1
    Rc2 = R2/TempCalCoeff1
    if (abs(Rc1-1000) < abs(Rc2-1000)):
        Rc=Rc1
    else:
        Rc=Rc2
        
    TtoRratio  = (TemperatureRef2 - TemperatureRef1) / (TempRefRes2 - TempRefRes1)
    Rb = (TemperatureRef1 * TempRefRes2 - TemperatureRef2 * TempRefRes1) / (TemperatureRef2 - TemperatureRef1)
    TemperatureMain = int((Rc + Rb) * TtoRratio)

    return TemperatureMain


def AmbTempCalc(TemperatureMain, TemperatureRef1, TemperatureRef2,
                    TempRefRes1, TempRefRes2,
                    TempCalCoeff1, TempCalCoeff2, TempCalCoeff3,
                    TempPolCoeff1, TempPolCoeff2, TempPolCoeff3):
    '''
    RS41 Ambient temperature calculation from frame parameters and subframes.
    '''

    TtoRratio  = (TemperatureRef2 - TemperatureRef1) / (TempRefRes2 - TempRefRes1)
    Rb = (TemperatureRef1 * TempRefRes2 - TemperatureRef2 * TempRefRes1) / (TemperatureRef2 - TemperatureRef1)
    Rc = TemperatureMain/TtoRratio - Rb
    R = Rc * TempCalCoeff1
    Temperature = (TempPolCoeff1 + TempPolCoeff2*R + TempPolCoeff3*R*R + TempCalCoeff2)*(1.0 + TempCalCoeff3)

    return Temperature

def SetAmbientTemperature(Temperature, SubFrameArray, MessageBytes):
    '''
    Set RS41 Ambient temperature parameters in RS41 message byte array.
    '''
    # Read parameters from the subframes array
    TempRefRes = GetTempRefRes(SubFrameArray)
    TempCalCoeff = GetTempCalCoeff(SubFrameArray)
    TempPolCoeff = GetTempPolCoeff(SubFrameArray)
    
    # Calculate the ambient temperature parameters for the RS41 message byte array
    (TemperatureMain,
    TemperatureRef1,
    TemperatureRef2) = AmbTempFrameParamsCalc(Temperature, TempRefRes[0], TempRefRes[1],
                                              TempCalCoeff[0], TempCalCoeff[1], TempCalCoeff[2],
                                              TempPolCoeff[0], TempPolCoeff[1], TempPolCoeff[2])
    
    # Set the calculated parameters in the RS 41 message byte array                                                     
    SetTemperatureMain(TemperatureMain, MessageBytes)
    SetTemperatureRef1(TemperatureRef1, MessageBytes)
    SetTemperatureRef2(TemperatureRef2, MessageBytes)

def SetMainAmbientTemperature(Temperature, SubFrameArray, MessageBytes):
    '''
    Set RS41 Main ambient temperature parameter in RS41 message byte array.
    '''
    # Get reference ambient temperature parameters from the RS41 message byte array
    TemperatureRef1 = GetTemperatureRef1(MessageBytes)
    TemperatureRef2 = GetTemperatureRef2(MessageBytes)
    
    # Read parameters from the subframes array
    TempRefRes = GetTempRefRes(SubFrameArray)
    TempCalCoeff = GetTempCalCoeff(SubFrameArray)
    TempPolCoeff = GetTempPolCoeff(SubFrameArray)
    
    # Calculate the main ambient temperature parameter for the RS41 message byte array
    TemperatureMain = AmbMainTempFrameCalc(Temperature, TemperatureRef1, TemperatureRef2,
                                           TempRefRes[0], TempRefRes[1],
                                           TempCalCoeff[0], TempCalCoeff[1], TempCalCoeff[2],
                                           TempPolCoeff[0], TempPolCoeff[1], TempPolCoeff[2])
    
    # Set the calculated main parameter in the RS 41 message byte array                                                     
    SetTemperatureMain(TemperatureMain, MessageBytes)

def GetAmbientTemperature(SubFrameArray, MessageBytes):
    '''
    Get RS41 Ambient temperature from the parameters in RS41 message byte array.
    '''
    # Get ambient temperature parameters from the RS41 message byte array
    TemperatureMain = GetTemperatureMain(MessageBytes)
    TemperatureRef1 = GetTemperatureRef1(MessageBytes)
    TemperatureRef2 = GetTemperatureRef2(MessageBytes)
    
    # Read parameters from the subframes array
    TempRefRes = GetTempRefRes(SubFrameArray)
    TempCalCoeff = GetTempCalCoeff(SubFrameArray)
    TempPolCoeff = GetTempPolCoeff(SubFrameArray)
    
    # Calculate the ambient temperature parameters for the RS41 message byte array
    Temperature = AmbTempCalc(TemperatureMain, TemperatureRef1, TemperatureRef2, 
                              TempRefRes[0], TempRefRes[1],
                              TempCalCoeff[0], TempCalCoeff[1], TempCalCoeff[2],
                              TempPolCoeff[0], TempPolCoeff[1], TempPolCoeff[2])

    return Temperature

# %% Heater temperature calculations functions
#############################################
# Heater temperature calculations functions #
#############################################

def HeaterTempFrameParamsCalc(HeaterTemperature, TempRefRes1, TempRefRes2,
                          HeaterTempCalCoeff1, HeaterTempCalCoeff2, HeaterTempCalCoeff3,
                          HeaterTempPolCoeff1, HeaterTempPolCoeff2, HeaterTempPolCoeff3):
    '''
    RS41 Heater temperature frame parameters calculation.
    '''
    RtoTratio = 169.5 # empirical. TODO: Change the value according to external temperature
    RtoToffset = 3160 # empirical. TODO: Change the value according to external temperature
    
    Hc = HeaterTempPolCoeff1 + HeaterTempCalCoeff2 - ( HeaterTemperature / (1.0 + HeaterTempCalCoeff3) )
    HR1 = (-HeaterTempPolCoeff2 + math.sqrt(pow(HeaterTempPolCoeff2,2)-4*HeaterTempPolCoeff3*Hc))/(2*HeaterTempPolCoeff3)
    HR2 = (-HeaterTempPolCoeff2 - math.sqrt(pow(HeaterTempPolCoeff2,2)-4*HeaterTempPolCoeff3*Hc))/(2*HeaterTempPolCoeff3)
    HRc1 = HR1/HeaterTempCalCoeff1
    HRc2 = HR2/HeaterTempCalCoeff1
    if (abs(HRc1-1000) < abs(HRc2-1000)):
        HRc=HRc1
    else:
        HRc=HRc2
    HeaterTemperatureMain = int(RtoTratio * HRc)
    HeaterTemperatureRef1 = int(RtoTratio * TempRefRes1)
    HeaterTemperatureRef2 = int(RtoTratio * TempRefRes2)

    return HeaterTemperatureMain, HeaterTemperatureRef1 , HeaterTemperatureRef2

def HeaterMainTempFrameCalc(HeaterTemperature, HeaterTemperatureRef1, HeaterTemperatureRef2,
                            TempRefRes1, TempRefRes2,
                            HeaterTempCalCoeff1, HeaterTempCalCoeff2, HeaterTempCalCoeff3,
                            HeaterTempPolCoeff1, HeaterTempPolCoeff2, HeaterTempPolCoeff3):
    '''
    RS41 heater temperature frame main parameter calculation.
    '''
    
    Hc = HeaterTempPolCoeff1 + HeaterTempCalCoeff2 - ( HeaterTemperature / (1.0 + HeaterTempCalCoeff3) )
    HR1 = (-HeaterTempPolCoeff2 + math.sqrt(pow(HeaterTempPolCoeff2,2)-4*HeaterTempPolCoeff3*Hc))/(2*HeaterTempPolCoeff3)
    HR2 = (-HeaterTempPolCoeff2 - math.sqrt(pow(HeaterTempPolCoeff2,2)-4*HeaterTempPolCoeff3*Hc))/(2*HeaterTempPolCoeff3)
    HRc1 = HR1/HeaterTempCalCoeff1
    HRc2 = HR2/HeaterTempCalCoeff1
    if (abs(HRc1-1000) < abs(HRc2-1000)):
        HRc=HRc1
    else:
        HRc=HRc2
        
    HTtoRratio  = (HeaterTemperatureRef2 - HeaterTemperatureRef1) / (TempRefRes2 - TempRefRes1)
    HRb = (HeaterTemperatureRef1 * TempRefRes2 - HeaterTemperatureRef2 * TempRefRes1) / (HeaterTemperatureRef2 - HeaterTemperatureRef1)
    HeaterTemperatureMain = int((HRc + HRb) * HTtoRratio)

    return HeaterTemperatureMain

def HeaterTempCalc(HeaterTemperatureMain, HeaterTemperatureRef1, HeaterTemperatureRef2,
                            TempRefRes1, TempRefRes2,
                            HeaterTempCalCoeff1, HeaterTempCalCoeff2, HeaterTempCalCoeff3,
                            HeaterTempPolCoeff1, HeaterTempPolCoeff2, HeaterTempPolCoeff3):
    '''
    RS41 Heater temperature calculation from frame parameters and subframes.
    '''
    
    HTtoRratio  = (HeaterTemperatureRef2 - HeaterTemperatureRef1) / (TempRefRes2 - TempRefRes1)
    HRb = (HeaterTemperatureRef1 * TempRefRes2 - HeaterTemperatureRef2 * TempRefRes1) / (HeaterTemperatureRef2 - HeaterTemperatureRef1)
    HRc = HeaterTemperatureMain/HTtoRratio - HRb
    HR = HRc * HeaterTempCalCoeff1
    HeaterTemperature = (HeaterTempPolCoeff1 + HeaterTempPolCoeff2*HR + HeaterTempPolCoeff3*HR*HR + HeaterTempCalCoeff2)*(1.0 + HeaterTempCalCoeff3)

    return HeaterTemperature

def SetHeaterTemperature(HeaterTemperature, SubFrameArray, MessageBytes):
    '''
    Set RS41 Heater temperature parameters in RS41 message byte array.
    '''
    # Read parameters from the subframes array
    TempRefRes = GetTempRefRes(SubFrameArray)
    HeaterTempCalCoeff = GetHeaterTempCalCoeff(SubFrameArray)
    HeaterTempPolCoeff = GetHeaterTempPolCoeff(SubFrameArray)
    
    # Calculate the heater temperature parameters for the RS41 message byte array
    (HeaterTemperatureMain,
    HeaterTemperatureRef1,
    HeaterTemperatureRef2) = HeaterTempFrameParamsCalc(HeaterTemperature, TempRefRes[0], TempRefRes[1],
                                              HeaterTempCalCoeff[0], HeaterTempCalCoeff[1], HeaterTempCalCoeff[2],
                                              HeaterTempPolCoeff[0], HeaterTempPolCoeff[1], HeaterTempPolCoeff[2])
    
    # Set the calculated parameters in the RS 41 message byte array                                                     
    SetHeaterTemperatureMain(HeaterTemperatureMain, MessageBytes)
    SetHeaterTemperatureRef1(HeaterTemperatureRef1, MessageBytes)
    SetHeaterTemperatureRef2(HeaterTemperatureRef2, MessageBytes)

def SetMainHeaterTemperature(HeaterTemperature, SubFrameArray, MessageBytes):
    '''
    Set RS41 Main heater temperature parameter in RS41 message byte array.
    '''
    # Get reference heater temperature parameters from the RS41 message byte array
    HeaterTemperatureRef1 = GetHeaterTemperatureRef1(MessageBytes)
    HeaterTemperatureRef2 = GetHeaterTemperatureRef2(MessageBytes)
    
    # Read parameters from the subframes array
    TempRefRes = GetTempRefRes(SubFrameArray)
    HeaterTempCalCoeff = GetHeaterTempCalCoeff(SubFrameArray)
    HeaterTempPolCoeff = GetHeaterTempPolCoeff(SubFrameArray)
    
    # Calculate the main heater temperature parameter for the RS41 message byte array
    HeaterTemperatureMain = HeaterMainTempFrameCalc(HeaterTemperature, HeaterTemperatureRef1, HeaterTemperatureRef2,
                                           TempRefRes[0], TempRefRes[1],
                                           HeaterTempCalCoeff[0], HeaterTempCalCoeff[1], HeaterTempCalCoeff[2],
                                           HeaterTempPolCoeff[0], HeaterTempPolCoeff[1], HeaterTempPolCoeff[2])
    
    # Set the calculated main parameter in the RS 41 message byte array                                                     
    SetHeaterTemperatureMain(HeaterTemperatureMain, MessageBytes)

def GetHeaterTemperature(SubFrameArray, MessageBytes):
    '''
    Get RS41 Heater temperature from the parameters in RS41 message byte array.
    '''
    # Get heater temperature parameters from the RS41 message byte array
    HeaterTemperatureMain = GetHeaterTemperatureMain(MessageBytes)
    HeaterTemperatureRef1 = GetHeaterTemperatureRef1(MessageBytes)
    HeaterTemperatureRef2 = GetHeaterTemperatureRef2(MessageBytes)
    
    # Read parameters from the subframes array
    TempRefRes = GetTempRefRes(SubFrameArray)
    HeaterTempCalCoeff = GetHeaterTempCalCoeff(SubFrameArray)
    HeaterTempPolCoeff = GetHeaterTempPolCoeff(SubFrameArray)
    
    # Calculate the heater temperature parameters for the RS41 message byte array
    HeaterTemperature = HeaterTempCalc(HeaterTemperatureMain, HeaterTemperatureRef1, HeaterTemperatureRef2, 
                              TempRefRes[0], TempRefRes[1],
                              HeaterTempCalCoeff[0], HeaterTempCalCoeff[1], HeaterTempCalCoeff[2],
                              HeaterTempPolCoeff[0], HeaterTempPolCoeff[1], HeaterTempPolCoeff[2])

    return HeaterTemperature

# %% Pressure calculations functions
###################################
# Pressure calculations functions #
###################################

# Ambient pressure calculation
def PressureCalc(PressureMain, PressureRef1, PressureRef2, PressureSensorTemperature, PressureCalCoeff):
    '''
    RS41 Pressure calculation. Calculate the ambient pressure from the main, reference and calibration parameters
    '''    
    Pressure = 0
    a0 = PressureCalCoeff[24] / ((PressureMain - PressureRef1) / (PressureRef2 - PressureRef1))
    a1 = PressureSensorTemperature # (PressureSensorTemperature * 100) * 0.01
    
    a0j = 1.0
    for j in range(0, 6):
        a1k = 1.0
        for k in range(0, 4):
            Pressure = Pressure + a0j * a1k * PressureCalCoeff[j * 4 + k]
            a1k = a1k * a1
        a0j = a0j * a0
    return Pressure

# Reverse pressure calculation (Calculating the required count value for a given pressure value)
def ReversePressCalc(DesiredPressure, PressureMain, PressureRef1, PressureRef2, PressureSensorTemperature, PressureCalCoeff):
    '''
    Reverse RS41 Pressure calculation. Calculate the main pressure parameter using the required pressure and the reference and calibration parameters
    '''   
    i = 0
    OutputPressure = 0
    P0Counts = PressureMain
    P1Counts = PressureMain + 2000
    PressureP0 = PressureCalc(P0Counts, PressureRef1, PressureRef2, PressureSensorTemperature, PressureCalCoeff)
    PressureP1 = PressureCalc(P1Counts, PressureRef1, PressureRef2, PressureSensorTemperature, PressureCalCoeff)
    while abs(DesiredPressure - OutputPressure)/DesiredPressure > 0.0001:
        OutputCounts = (DesiredPressure - PressureP0) * (P1Counts - P0Counts) / (PressureP1 - PressureP0) + P0Counts
        OutputPressure = PressureCalc(OutputCounts , PressureRef1, PressureRef2, PressureSensorTemperature, PressureCalCoeff)
        PressureP0 = PressureP1
        P0Counts = P1Counts
        PressureP1 = OutputPressure
        P1Counts = OutputCounts
        i += 1
    return i, int(OutputCounts) , OutputPressure

# GPS altitude [m] to pressure [hPa]
def GPSAltitudeToPressure(GPSAltitude):
    '''
    GPS altitude based ambient pressure. Estimate the ambient pressure using GPS altitude
    '''  
    if (GPSAltitude > 32000.0):     # Pressure < 8.6802
        Pb = 8.6802
        Tb = 228.65
        Lb = 0.0028
        hb = 32000.0
    elif (GPSAltitude > 20000.0):   # Pressure < 54.7489 (&& P >= 8.6802)
        Pb = 54.7489
        Tb = 216.65
        Lb = 0.001
        hb = 20000.0
    elif (GPSAltitude > 11000.0):   # Pressure < 226.321 (&& P >= 54.7489)
        Pb = 226.321
        Tb =216.65
        Lb = 0.0
        hb = 11000.0
    else:                           # Pressure >= 226.321
        Pb = 1013.25
        Tb = 288.15
        Lb = -0.0065
        hb = 0.0
    
    gMR = 9.80665 * 0.0289644 / 8.31446
    if (Lb == 0.0):
        CalculatedPressure = Pb * math.exp( -gMR * (GPSAltitude - hb) / Tb ) 
    else:
        CalculatedPressure = Pb * pow( 1.0+Lb * (GPSAltitude - hb) / Tb , -gMR / Lb)
    
    return CalculatedPressure

def SetPressure(Pressure, SubFrameArray, MessageBytes):
    '''
    Set RS41 Ambient pressure parameters in RS41 message byte array.
    '''
    # Get pressure sensor temperature parameter from the RS41 message byte array
    PressureSensorTemperature = GetPressureSensorTemperature(MessageBytes)

    # Read parameters from the subframes array
    PressureCalCoeff = GetPressureCalCoeff(SubFrameArray)

    PressureMain = 363743 # empirical. Taken from a log file
    PressureRef1 = 294608 # empirical. TODO: Change the value according to external temperature
    PressureRef2 = 423151 # empirical. TODO: Change the value according to external temperature

    # Calculate the main pressure parameter for the RS41 message byte array
    _, PressureMain, _ = ReversePressCalc(Pressure , PressureMain, PressureRef1, PressureRef2,
                                                             PressureSensorTemperature, PressureCalCoeff)
    
    # Set the pressure parameters in the RS 41 message byte array                                                     
    SetPressureMain(PressureMain, MessageBytes)
    SetPressureRef1(PressureRef1, MessageBytes)
    SetPressureRef2(PressureRef2, MessageBytes)

def SetMainPressure(Pressure, SubFrameArray, MessageBytes):
    '''
    Set RS41 Main pressure parameter in RS41 message byte array.
    '''
    # Get ambient pressure parameters from the RS41 message byte array
    PressureMain = GetPressureMain(MessageBytes)
    PressureRef1 = GetPressureRef1(MessageBytes)
    PressureRef2 = GetPressureRef2(MessageBytes)
    
    # Get pressure sensor temperature parameter from the RS41 message byte array
    PressureSensorTemperature = GetPressureSensorTemperature(MessageBytes)

    # Read parameters from the subframes array
    PressureCalCoeff = GetPressureCalCoeff(SubFrameArray)

    # Calculate the main pressure parameter for the RS41 message byte array
    _, PressureMain, _ = ReversePressCalc(Pressure , PressureMain, PressureRef1, PressureRef2,
                                                             PressureSensorTemperature, PressureCalCoeff)
    
    # Set the main pressure parameter in the RS 41 message byte array                                                     
    SetPressureMain(PressureMain, MessageBytes)

def GetPressure(SubFrameArray, MessageBytes):
    '''
    Get RS41 Ambient pressure from the parameters in RS41 message byte array.
    '''
    # Get ambient pressure parameters from the RS41 message byte array
    PressureMain = GetPressureMain(MessageBytes)
    PressureRef1 = GetPressureRef1(MessageBytes)
    PressureRef2 = GetPressureRef2(MessageBytes)
    
    # Get pressure sensor temperature parameter from the RS41 message byte array
    PressureSensorTemperature = GetPressureSensorTemperature(MessageBytes)

    # Read parameters from the subframes array
    PressureCalCoeff = GetPressureCalCoeff(SubFrameArray)
    
    # Calculate the ambient pressure from RS41 message byte array
    Pressure = PressureCalc(PressureMain, PressureRef1, PressureRef2, PressureSensorTemperature, PressureCalCoeff)

    return Pressure

# %% Relative humidity calculations functions
############################################
# Relative humidity calculations functions #
############################################

# Calculate relative humidity
def RelativeHumidityCalc(RelativeHumidityMain, RelativeHumidityRef1, RelativeHumidityRef2, 
                         RS41Model, Pressure, GPSAltitude,
                         RHCapCoeff1, RHCapCoeff2,
                         HumidCalCoeff1, HumidCalCoeff2,
                         HumCPressureCalCoeff, HumCPressureTempCalCoeff,
                         Temperature, HeaterTemperature, HumHeaterTempCalCoeff):
    '''
    RS41 Relative humidity calculation. Calculate the relative humidity from the main, reference and calibration parameters
    '''    

    if (RS41Model == "RS41-SGP"):
        # Calculate the pressure in Bar from the defined barometric pressure
         Temp_p = Pressure / 1000.0
    else:
        # Calculate the pressure in Bar according to GPS altitude
        Temp_p = GPSAltitudeToPressure(GPSAltitude) / 1000

    cfh = (RelativeHumidityMain - RelativeHumidityRef1) / (RelativeHumidityRef2 - RelativeHumidityRef1)
    cap = RHCapCoeff1 + (RHCapCoeff2 - RHCapCoeff1) * cfh
    Cp = (cap / HumidCalCoeff1 - 1.0) * HumidCalCoeff2
    
    # Correct Cp according to pressure
    Temp_cpj = 1.0
    bp = np.zeros(3)
    
    for j in range (3):
        bp[j] = HumCPressureCalCoeff[j] * ( Temp_p / ( 1.0 + HumCPressureCalCoeff[j] * Temp_p ) - Temp_cpj / ( 1.0 + HumCPressureCalCoeff[j] ) )
        Temp_cpj = Temp_cpj * Cp
    
    Trh_20_180 = (HeaterTemperature - 20.0) / 180.0
    bk = 1.0
    b = np.zeros(6)
    for k in range(6):
        b[k] = bk
        bk = bk * Trh_20_180
    
    corrCp = 0.0;
    for j in range (3):
        bt = 0.0
        for k in range (4):
            bt = bt + HumCPressureTempCalCoeff[4 * j + k] * b[k]
        corrCp = corrCp + bp[j] * bt
    Cp = Cp - corrCp
       
    # Correct Cp according to temperature and calculate the relative humidity
    aj = 1.0
    Temp_rh = 0.0
    for j in range (7):
        for k in range (6):
            Temp_rh = Temp_rh + aj * b[k] * HumHeaterTempCalCoeff[ 6 * j + k ]
        aj = aj * Cp
    
    rh2 = Temp_rh * VaporSaturationPressure(HeaterTemperature) / VaporSaturationPressure(Temperature)
    
    if (rh2 < 0.0):
        rh2 = 0.0
    if (rh2 > 100.0):
        rh2 = 100.0
    
    return rh2

# Reverse relative humidity calculation (Calculating the required count value for a given relative humidity value)
def ReverseRelHumidityCalc(DesiredRelativeHumidity,
                       RelativeHumidityMain, RelativeHumidityRef1, RelativeHumidityRef2, 
                       RS41Model, Pressure, GPSAltitude,
                       RHCapCoeff1, RHCapCoeff2,
                       HumidCalCoeff1, HumidCalCoeff2,
                       HumCPressureCalCoeff, HumCPressureTempCalCoeff,
                       Temperature, HeaterTemperature, HumHeaterTempCalCoeff):

    '''
    Reverse RS41 relative humidity calculation. Calculate the relative humidity parameter using the required pressure and the reference and calibration parameters
    '''   
    i = 0
    OutputRelativeHumidity = 0
    RH0Counts = RelativeHumidityMain
    RH1Counts = RelativeHumidityMain + 2000
    RelHumidRH0 = RelativeHumidityCalc(RH0Counts, RelativeHumidityRef1, RelativeHumidityRef2, 
                                       RS41Model, Pressure, GPSAltitude,
                                       RHCapCoeff1, RHCapCoeff2,
                                       HumidCalCoeff1, HumidCalCoeff2,
                                       HumCPressureCalCoeff, HumCPressureTempCalCoeff,
                                       Temperature, HeaterTemperature, HumHeaterTempCalCoeff)
    RelHumidRH1 = RelativeHumidityCalc(RH1Counts, RelativeHumidityRef1, RelativeHumidityRef2, 
                                       RS41Model, Pressure, GPSAltitude,
                                       RHCapCoeff1, RHCapCoeff2,
                                       HumidCalCoeff1, HumidCalCoeff2,
                                       HumCPressureCalCoeff, HumCPressureTempCalCoeff,
                                       Temperature, HeaterTemperature, HumHeaterTempCalCoeff)
    while abs(DesiredRelativeHumidity - OutputRelativeHumidity)/DesiredRelativeHumidity > 0.0001:
        OutputCounts = (DesiredRelativeHumidity - RelHumidRH0) * (RH1Counts - RH0Counts) / (RelHumidRH1 - RelHumidRH0) + RH0Counts
        OutputRelativeHumidity = RelativeHumidityCalc(OutputCounts, RelativeHumidityRef1, RelativeHumidityRef2, 
                                           RS41Model, Pressure, GPSAltitude,
                                           RHCapCoeff1, RHCapCoeff2,
                                           HumidCalCoeff1, HumidCalCoeff2,
                                           HumCPressureCalCoeff, HumCPressureTempCalCoeff,
                                           Temperature, HeaterTemperature, HumHeaterTempCalCoeff)
        RelHumidRH0 = RelHumidRH1
        RH0Counts = RH1Counts
        RelHumidRH1 = OutputRelativeHumidity
        RH1Counts = OutputCounts
        i += 1
    return i, int(OutputCounts) , OutputRelativeHumidity

# Water vapor saturation pressure (Hyland and Wexler)
def VaporSaturationPressure(Tc):
    '''
    Water vapor saturation pressure
    '''  
    T = Tc + 273.15
    p = math.exp(-5800.2206 / T + 1.3914993 + 6.5459673 * math.log(T)
                    -4.8640239e-2 * T + 4.1764768e-5 * pow(T,2) -1.4452093e-8 * pow(T,3))
    return p # [Pa]

def SetRelativeHumidity(RelativeHumidity, RS41Model, Pressure, GPSAltitude, 
                        Temperature, HeaterTemperature, SubFrameArray, MessageBytes):
    '''
    Set RS41 Relative humidity parameters in RS41 message byte array.
    '''
    # Read parameters from the subframes array
    RHCapCoeff = GetRHCapCoeff(SubFrameArray)
    HumidCalCoeff = GetHumidCalCoeff(SubFrameArray)
    HumCPressureCalCoeff = GetHumCPressureCalCoeff(SubFrameArray)
    HumCPressureTempCalCoeff = GetHumCPressureTempCalCoeff(SubFrameArray)
    HumHeaterTempCalCoeff = GetHumHeaterTempCalCoeff(SubFrameArray)
    
    RelativeHumidityMain = 551851 # empirical. Taken from a log file
    RelativeHumidityRef1 = 479750 # empirical. TODO: Change the value according to external temperature
    RelativeHumidityRef2 = 547300 # empirical. TODO: Change the value according to external temperature
    
    _, RelativeHumidityMain, _ = ReverseRelHumidityCalc(RelativeHumidity,
                           RelativeHumidityMain, RelativeHumidityRef1, RelativeHumidityRef2, 
                           RS41Model, Pressure, GPSAltitude,
                           RHCapCoeff[0], RHCapCoeff[1],
                           HumidCalCoeff[0], HumidCalCoeff[1],
                           HumCPressureCalCoeff, HumCPressureTempCalCoeff,
                           Temperature, HeaterTemperature, HumHeaterTempCalCoeff)

    # Set the relative humidity parameters in the RS 41 message byte array                                                     
    SetRelativeHumidityMain(RelativeHumidityMain, MessageBytes)
    SetRelativeHumidityRef1(RelativeHumidityRef1, MessageBytes)
    SetRelativeHumidityRef2(RelativeHumidityRef2, MessageBytes)

def SetMainRelativeHumidity(RelativeHumidity, RS41Model, Pressure, GPSAltitude, 
                        Temperature, HeaterTemperature, SubFrameArray, MessageBytes):
    '''
    Set RS41 Main relative humidity parameter in RS41 message byte array.
    '''
    # Get relative humidity parameters from the RS41 message byte array
    RelativeHumidityMain = GetRelativeHumidityMain(MessageBytes)
    RelativeHumidityRef1 = GetRelativeHumidityRef1(MessageBytes)
    RelativeHumidityRef2 = GetRelativeHumidityRef2(MessageBytes)

    # Read parameters from the subframes array
    RHCapCoeff = GetRHCapCoeff(SubFrameArray)
    HumidCalCoeff = GetHumidCalCoeff(SubFrameArray)
    HumCPressureCalCoeff = GetHumCPressureCalCoeff(SubFrameArray)
    HumCPressureTempCalCoeff = GetHumCPressureTempCalCoeff(SubFrameArray)
    HumHeaterTempCalCoeff = GetHumHeaterTempCalCoeff(SubFrameArray)
    
    _, RelativeHumidityMain, _ = ReverseRelHumidityCalc(RelativeHumidity,
                           RelativeHumidityMain, RelativeHumidityRef1, RelativeHumidityRef2, 
                           RS41Model, Pressure, GPSAltitude,
                           RHCapCoeff[0], RHCapCoeff[1],
                           HumidCalCoeff[0], HumidCalCoeff[1],
                           HumCPressureCalCoeff, HumCPressureTempCalCoeff,
                           Temperature, HeaterTemperature, HumHeaterTempCalCoeff)

    # Set the main relative humidity parameter in the RS 41 message byte array                                                     
    SetRelativeHumidityMain(RelativeHumidityMain, MessageBytes)

def GetRelativeHumidity(RS41Model, Pressure, GPSAltitude, 
                        Temperature, HeaterTemperature, SubFrameArray, MessageBytes):
    '''
    Get RS41 relative humidity from RS41 message byte array.
    '''
    # Get relative humidity parameters from the RS41 message byte array
    RelativeHumidityMain = GetRelativeHumidityMain(MessageBytes)
    RelativeHumidityRef1 = GetRelativeHumidityRef1(MessageBytes)
    RelativeHumidityRef2 = GetRelativeHumidityRef2(MessageBytes)

    # Read parameters from the subframes array
    RHCapCoeff = GetRHCapCoeff(SubFrameArray)
    HumidCalCoeff = GetHumidCalCoeff(SubFrameArray)
    HumCPressureCalCoeff = GetHumCPressureCalCoeff(SubFrameArray)
    HumCPressureTempCalCoeff = GetHumCPressureTempCalCoeff(SubFrameArray)
    HumHeaterTempCalCoeff = GetHumHeaterTempCalCoeff(SubFrameArray)
    
    RelativeHumidity = RelativeHumidityCalc(RelativeHumidityMain, RelativeHumidityRef1, RelativeHumidityRef2, 
                             RS41Model, Pressure, GPSAltitude,
                             RHCapCoeff[0], RHCapCoeff[1],
                             HumidCalCoeff[0], HumidCalCoeff[1],
                             HumCPressureCalCoeff, HumCPressureTempCalCoeff,
                             Temperature, HeaterTemperature, HumHeaterTempCalCoeff)

    return RelativeHumidity

# %% GPS calculations functions
##############################
# GPS calculations functions #
##############################

# Calcualte GPS time parameters from given UTC time and leapseconds
def UTCTimeToGPSWeekAndSeconds(utc,leapseconds):
    '''
    Calcualte GPS time parameters from given UTC time and leapseconds
    '''  
    # Returns the GPS week, the GPS day, and the seconds 
    # and microseconds since the beginning of the GPS week 
    epoch = datetime.datetime(1980, 1, 6, 0, 0, 0, 0,datetime.timezone.utc)
    tdiff = utc - epoch  + datetime.timedelta(seconds=leapseconds)
    gpsweek = tdiff.days // 7
    gpsdays = tdiff.days - 7 * gpsweek
    gpsseconds = tdiff.seconds + 86400 * (tdiff.days -7 * gpsweek)
    return gpsweek,gpsdays,gpsseconds,gpsseconds * 1000

# Calcualte GPS data
def CalculateGPSData(SkyfieldSatellites, UTCTime,
                     GPSLatitudeN, GPSLongitudeE, GPSAltitude,
                     GPSVelEast, GPSVelNorth, GPSVelUp):
    '''
    Calculate GPS data for the RS41 message blocks
    '''   
    # Define skyfield object
    Obj = wgs84.latlon(GPSLatitudeN, GPSLongitudeE, GPSAltitude)
    ObjTime = load.timescale()
    ObjUTCTime = ObjTime.from_datetime(UTCTime)
    
    # Calcultae the actual relative velocity between the observer and the satellite,
    # based on the observer's velocity
    ObjVelAz, ObjVelEl, ObjVelMag = pymap3d.enu2aer(GPSVelEast, GPSVelNorth, GPSVelUp)
    
    # Calculate the relative parameters for each satellite and the observer
    # and build a sattelites database
    svdata = []
    
    # Declare a PRN and Reception Quality Indicator array, for 12 satellites
    # The array comprises 12 records. In each record there are two bytes:
    # 1st byte = PRN number. PRN number = 0xFF if the satellite is not in use.
    # 2nd byte = Reception quality indicator byte value = 32 * mesQI + cno'
    #               mesQI = U-BLOX Nav Measurements Quality Indicator:
    #                       PR = Pseudorange measurement available
    #                       DO = Doppler measurement available
    #                       CP = Carrier phase measurement available
    #                       >=4 : PR+DO OK
    #                       >=5 : PR+DO+CP OK
    #                       <6 : likely loss of carrier lock in previous interval
    #               cno' = 0 if c/n0 < 20
    #               cno' = c/n0 - 20 if 20 <= c/n0 <= 50
    #               cno' = 31 if c/n0 > 50
    
    PRNandReceptionQualityIndicatorArray = bytearray([0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00,
                                                      0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00,
                                                      0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00])
    
    # Declare a line-of-sight matrix for all satellites used in the solution
    LOSMatrix = np.empty((0,4))
    
    # TODO: If a received record is available, then sort the satellites
    #       according to their position in the known record
    i = 0
    for sv in SkyfieldSatellites:
        # Calculate object - sattelite parameters
        SatObjDiff = sv - Obj
        SatObjTopocentric = SatObjDiff.at(ObjUTCTime)
        _, _, SatObjRange, _, _, SatObjRangeRate = SatObjTopocentric.frame_latlon_and_rates(Obj)
        ObjAlt, ObjAz, _ = SatObjTopocentric.altaz()
        
        # Check if the elevation angle is higher than a thershold
        # If so - add the sattelite's data to the sattelites database, up to 12 satellites
        if ((ObjAlt.degrees > -0.5) & (len(svdata) < 12)): # the elevation threshold is in [Degrees]
            # Calculate the cosine of the angle between the vector of the object's velocity
            # (in azimuth and elevation) and the vector of the satellite's velocity
            # (in azimuth and elevation). This is done by calculating dot product of the two
            CosAz = math.cos(ObjAz.radians)
            SinAz = math.sin(ObjAz.radians)
            CosEl = math.cos(ObjAlt.radians)
            SinEl = math.sin(ObjAlt.radians)
            a1 = SinAz * CosEl
            a2 = CosAz * CosEl
            a3 = SinEl
            CosAz = math.cos(math.radians(ObjVelAz))
            SinAz = math.sin(math.radians(ObjVelAz))
            CosEl = math.cos(math.radians(ObjVelEl))
            SinEl = math.sin(math.radians(ObjVelEl))
            b1 = SinAz * CosEl
            b2 = CosAz * CosEl
            b3 = SinEl
            DotProductAB = a1 * b1 + a2 * b2 + a3 * b3
    
            # Calculate the projection of the observer's velocity vector on the satellite's
            # velocity vector and add the two to get the corrected relative velocity
            CorrectedObsVelMag = SatObjRangeRate.m_per_s - ObjVelMag * DotProductAB * np.sign(SatObjRangeRate.m_per_s)
    
            # Append the sattelite's data to the line-of-sight matrix
            if (len(LOSMatrix) < 6):
                LOSMatrix = np.append(LOSMatrix, np.array([ [ a1 , a2 , a3 , 1.0] ]), axis=0)
    
            # Calculate the c/N0, according to
            # Deep, S., Raghavendra, S., & Bharath, B. D. (2018).
            # GPS SNR prediction in urban environment. 
            # Egyptian Journal of Remote Sensing and Space Science,  21(1), 83–85.
            Estimatedcno = int(3.199e-05 * pow(ObjAlt.degrees,3) - 0.0081 * pow(ObjAlt.degrees,2) + 0.6613 * ObjAlt.degrees + 31.38)
            
            # Add some noise to Estimatedcno to make it seems more active
            # TODO: Improve the Estimatedcno noise generator
            Estimatedcno = Estimatedcno + int(-6 * np.random.rand())
            
            # Calculate cno':
            # cno' = 0 if cno < 20
            # cno' = cno-20 if 20 <= cno <= 50
            # cno' = 31 if cno > 50
            if (Estimatedcno < 20):
                cnoTag = 0
            elif (Estimatedcno > 50):
                cnoTag = 31
            else:
                cnoTag = Estimatedcno - 20
            
            # mesQI = U-BLOX Nav Measurements Quality Indicator:
            #         PR = Pseudorange measurement available
            #         DO = Doppler measurement available
            #         CP = Carrier phase measurement available
            #         >=4 : PR+DO OK
            #         >=5 : PR+DO+CP OK
            #         <6 : likely loss of carrier lock in previous interval
            
            # TODO: Improve the mesQI estimation model
            # Calculate empiric estimation of mesQI
            if (Estimatedcno < 34):
                EstimatedmesQI = 4
            elif (Estimatedcno < 39):
                EstimatedmesQI = 6
            else:
                EstimatedmesQI = 7
                
            # Reception quality indicator byte value = 32 * mesQI + cno'
            QualityIndicator = ( EstimatedmesQI << 5 ) | cnoTag
    
            # Get the satellite's PRN number
            PRNPlace = sv.name.find("PRN")
            PRNText = sv.name[PRNPlace + 4]
            if sv.name[PRNPlace + 5].isnumeric:
                PRNText = PRNText + sv.name[PRNPlace + 5]
            PRN = int(PRNText)
    
            # Fill the PRN and reception quality indicator array
            PRNandReceptionQualityIndicatorArray[i] = PRN       
            PRNandReceptionQualityIndicatorArray[i+1] = QualityIndicator
            i = i + 2
    
#            print (PRN, array2string(SatObjRangeRate.m_per_s, precision=2).rjust(9), "m/s  ", array2string(SatObjRange.m, precision=2).rjust(11), 'm   ', round(ObjAz.degrees,2), '   ', round(ObjAlt.degrees,2), '   ',round(CorrectedObsVelMag,2), '   ', QualityIndicator, '   ', round(math.degrees(math.acos(DotProductAB)),2))
    
            # build the database item content:
            # PRN number, Relative velocity [m/s], Estimated c/n0, Estimated mesQI,
            # Relative range [m], Relative azimuth [degrees], Reltaive elevation [degrees],
            # Uncorrected relative velocity [m/s], Angle between velocity vectors [degrees]
            item = (PRN, CorrectedObsVelMag, Estimatedcno, EstimatedmesQI, 
                   SatObjRange.m, ObjAz.degrees, ObjAlt.degrees, SatObjRangeRate.m_per_s,
                   math.degrees(math.acos(DotProductAB)))
                    
            #Add the sate to the database
            svdata.append(item)
    
    # Get the number of satellites used in the solution
    svdataLength = len(svdata)
    
    # Calculate PDOP
    # Transpose the line-of-sight matrix
    LOSMatrixTransposed = LOSMatrix.transpose()
    # Compute the covariance matrix of the transposed line-of-sight matrix
    CovarienceMatrix = np.linalg.inv(np.dot(LOSMatrixTransposed, LOSMatrix))
    # Calculate DOP values such as GDOP, PDOP, etc
    GPSPDOP = np.sqrt(CovarienceMatrix[0, 0] + CovarienceMatrix[1, 1] + CovarienceMatrix[2, 2])
    
    # Find the lowest psaudorange in the satellites data base
    MinPR = int(min([item[4] for item in svdata])) # [m]

    # Declare a Psaudorange and Velocity array, for 12 satellites
    # The array comprises 12 records. In each record there are two variables:
    # 1st variable holds the psauderange between the object and the satellite, in [cm],
    # minus the lowest psaudorange in the satellites data base, in[cm] (int32)
    # 2nd variable holds the relative velocity between the object and the satellite (int24)
    PsaudorangeandVelocityArray = bytearray(84)

    i=0
    for sv in svdata:
        # Calculte the delta psaudorange from minimum psaudorange. in [cm]
        deltaPR = int( ( sv[4] - MinPR ) * 100 ) # in [cm]
        # Calculate the relative velocity. in [cm]
        RelativeVelocity = int ( sv[1] * 100 ) # in [cm/sec]
        # Write the deltaPR and RelativeVelocity in the array
        PsaudorangeandVelocityArray[i  :i+4] = deltaPR.to_bytes(4,byteorder='little', signed=True)
        PsaudorangeandVelocityArray[i+4:i+7] = RelativeVelocity.to_bytes(3,byteorder='little', signed=True)
        i = i + 7
    # If less than 12 records were filled, write 0xFF in the following byte in the array
    if ( svdataLength < 12 ):
        PsaudorangeandVelocityArray[i] = 0xFF
    
    # Convert GPS geodetic coordinates to ECEF
    ECEFPositionX, ECEFPositionY, ECEFPositionZ = pymap3d.geodetic2ecef(GPSLatitudeN, GPSLongitudeE, GPSAltitude)

    # Rotates the North East Down velocity components [m/s] into ECEF velocity components [m/s]
    LatRad = math.radians(GPSLatitudeN);
    LonRad = math.radians(GPSLongitudeE);

    ECEFVelocityX = ( - ( GPSVelNorth * ( math.sin(LatRad) * math.cos(LonRad) ) )
                      - ( GPSVelEast  * ( math.sin(LonRad)                    ) )
                      + ( GPSVelUp    * ( math.cos(LatRad) * math.cos(LonRad) ) ) )
    ECEFVelocityY = ( - ( GPSVelNorth * ( math.sin(LatRad) * math.sin(LonRad) ) )
                      + ( GPSVelEast  *   math.cos(LonRad)                      )
                      + ( GPSVelUp    * ( math.cos(LatRad) * math.sin(LonRad) ) ) )
    ECEFVelocityZ =     ( GPSVelNorth *   math.cos(LatRad) ) + ( GPSVelUp * math.sin(LatRad) )
    
    return (svdata, svdataLength,
            PRNandReceptionQualityIndicatorArray,
            PsaudorangeandVelocityArray,
            GPSPDOP, MinPR,
            ECEFPositionX, ECEFPositionY, ECEFPositionZ, 
            ECEFVelocityX, ECEFVelocityY, ECEFVelocityZ)
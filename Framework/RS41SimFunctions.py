# -*- coding: utf-8 -*-
"""
RS41 simulation functions
"""

#############################################
# The following functions are a part of an  #
# RS41-SG/P radiosonde simulation framework.#
# The functions are simulation-level        #
# functions.                                #
#                                           #
# These functions were written by Paz       #
# Hameiri in 2023                           #
#############################################

import csv
import numpy as np
import scipy.signal as signal
import math
from RS41BlocksRW import *
import pymap3d

def AccessBit(data, num):
    base = int(num // 8)
    shift = 7 - int(num % 8)
    return (data[base] & (0x01 << shift)) >> shift

# Open a log file and read its contents
def ReadLogFile(LogFileName):
    with open(LogFileName, newline = '') as file:
        reader = csv.reader(file, delimiter = ' ', quoting = csv.QUOTE_NONE )
         
        # Store all the rows in an output list
        LoggedMessages = []
        for row in reader:
            LoggedMessages.append(row[:])
    return len(LoggedMessages), LoggedMessages

# Load a log file record to MessageBytes array
def LogRecordToMessageBytes(LoggedMessageIndex, LoggedMessages, MessageBytes):
    # Remove empty entries from the selected message
    while("" in LoggedMessages[LoggedMessageIndex]):
        LoggedMessages[LoggedMessageIndex].remove("")
        
    # Format the message list into byte array
    LoadedMessageBytes = bytearray(np.uint8([int(a,16) for a in LoggedMessages[LoggedMessageIndex]]))
    MessageBytes[0:len(LoadedMessageBytes)] = LoadedMessageBytes

# Load Subframe data from a log file
def LoadSubframeDataFromLog(TotalSubframes, LoggedMessagesLength, LoggedMessages, SubFrameArray, MessageBytes):
    # Define a tracking array to cover all of the data
    SubFrameTrack = np.zeros(TotalSubframes, dtype=np.uint8)
    
    i = 0
    SubFramesLoading = True
    while (SubFramesLoading & (i < LoggedMessagesLength)):
        # Load a record to MessageBytes array
        LogRecordToMessageBytes(i, LoggedMessages, MessageBytes)
        
        # Try and correct the data using the Reed-Solomon ECC
        try:
            DecodeReedSolomon(MessageBytes)
        except Exception: 
            pass
        
        # Check that the STATUS block is valid. If so - get the data
        if CheckSTATUSblockCRC(MessageBytes):
            # Get Subframe number
            SubframeNumber = GetSubframe(MessageBytes) # Subframe number
    
            # Copy the Subframe to SubFrameArray
            LoadSubFrameBytes(SubframeNumber, SubFrameArray, MessageBytes)
            
            # Update SubFrameTrack
            SubFrameTrack[SubframeNumber] = 1
            
        # Advance the index
        i = i + 1
        
        # Check if subframes finished loading
        SubFramesLoading = sum(SubFrameTrack) < TotalSubframes
    return not(SubFramesLoading), i

# Find criteria in log
def FindCreteriaInLog(LoggedMessagesLength, LoggedMessages, Criteria, CriteriaValue): 
    # Declare a local message bytes array
    LocalMessageBytes = bytearray(1024)
    
    i = 0
    CriteriaNotMet = True
    while (CriteriaNotMet & (i < LoggedMessagesLength)):
        # Load a record to MessageBytes array
        LogRecordToMessageBytes(i, LoggedMessages, LocalMessageBytes)
        
        CriteriaMet = FindCreteriaInMessage(LocalMessageBytes, Criteria, CriteriaValue)
        CriteriaNotMet = not(CriteriaMet)

        # Advance the index
        i = i + 1
        
    return not(CriteriaNotMet), (i - 1)

# Find criteria in message
def FindCreteriaInMessage(MessageBytes, Criteria, CriteriaValue): 
    CriteriaMet = False
    if Criteria.upper().find("GPSALTITUDE") >= 0:
        # Check that the GPSPOS block is valid. If so - get the data
        if CheckGPSPOSblockCRC(MessageBytes):
            # Get ECEF Position X in [m]
            ECEFPositionX = GetECEFPositionX(MessageBytes)
        
            # Get ECEF Position Y in [m]
            ECEFPositionY = GetECEFPositionY(MessageBytes)
        
            # Get ECEF Position Z in [m]
            ECEFPositionZ = GetECEFPositionZ(MessageBytes)
    
            # Convert ECEF coordinates to GPS geodetic
            GPSLatitudeN, GPSLongitudeE, GPSAltitude = pymap3d.ecef2geodetic(ECEFPositionX, ECEFPositionY, ECEFPositionZ)

            # Check if the altitude criteria is met 
            if ((Criteria.find("<") > 0) and (GPSAltitude < CriteriaValue)):
                CriteriaMet = True
            elif ((Criteria.find(">") > 0) and (GPSAltitude > CriteriaValue)):
                            CriteriaMet = True
    elif Criteria.upper().find("UPONDESCENT") >= 0:
        # Check that the STATUS block is valid. If so - get the data
        if CheckSTATUSblockCRC(MessageBytes):
            
            # Get the FlightMode and AscentDescent data
            FlightMode, AscentDescent = GetFlightModeAscentDescent(MessageBytes)

            # Check if the descent criteria is met 
            if AscentDescent > 0:
                CriteriaMet = True
        
    return CriteriaMet


# Build RF transmitter message
def SetupRFMessage(RFMessageNumOfBytes, TxDataBytesLength, FrequencyStart, DataRate, FrequencyDeviation, Modulation, Power):
    # Set the data in PcReceptionStruct:
    # byte_array[0:2]    = uint16_t  NumOfBytes;         // Holds the number of bytes in the packet received from the PC
    # byte_array[2:6]    = uint32e_t FrequencyStart;     // Frequency in Hz
    # byte_array[6:10]   = uint32e_t DataRate;           // Data rate in BAUD
    # byte_array[10:14]  = uint32e_t FrequencyDeviation; // Frequency deviation in Hz
    # byte_array[14:15]  = uint8e_t  Modulation;         // 0 = no shaping, 			  1 = Gaussian filter BT = 1.0,
    #                    	  	  	  	  	  	  	  	 // 2 = Gaussian filter BT = 0.5, 3 = Gaussian filter BT = 0.3
    # byte_array[15:16]  = int8e_t   Power;              // Output power in dBm:  Supports -3dBm to +16dBm, +20dBm
    # byte_array[16:335] = uint8_t   TxBuffer;           // Transmitted data
    byte_array = bytearray(RFMessageNumOfBytes)
    byte_array[0:2] = RFMessageNumOfBytes.to_bytes(2, 'big')
    byte_array[2:6] = FrequencyStart.to_bytes(4, 'big')
    byte_array[6:10] = DataRate.to_bytes(4, 'big')
    byte_array[10:14] = FrequencyDeviation.to_bytes(4, 'big')
    byte_array[14:15] = Modulation.to_bytes(1, 'big')
    byte_array[15:16] = Power.to_bytes(1, 'big', signed =True)
    return byte_array

# Build the wave data from the TxDataBytes and wave paramters
def BuildAudioStream(TxDataBytes, TxDataBytesLength, SampleRateMultipliler, DataRate, SamplesRate):
    # Build the bit stream that will be converted to WAV data
    BaseBitStream = [AccessBit(TxDataBytes,i) for i in range(TxDataBytesLength*8)]
    FinalBitStream = [BaseBitStream[round(i/SampleRateMultipliler)-1] for i in range(math.floor(len(BaseBitStream)*SampleRateMultipliler))]
    
    # Generate the WAV data
    BinaryWaveData = [(FinalBitStream[i]-0.5) for i in range(len(FinalBitStream))]
    
    # Calculate low pass filter. The low pass filtering is shaping the signal as GFSK
    filt_order = 2
    filt_low = DataRate / (0.5 * SamplesRate)
    filt_b, filt_a = signal.butter(filt_order, filt_low, btype='low')
    WaveData = (signal.lfilter(filt_b, filt_a, BinaryWaveData)).astype(np.float32)
    return WaveData
# -*- coding: utf-8 -*-
"""
RS41 Blocks Read-Write operations
"""

#############################################
# The following functions are a part of an  #
# RS41-SG/P radiosonde simulation framework.#
# The functions are block-level functions,  #
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
from reedsolo import RSCodec

# Defined CRC16 calculation function
def crc16(data: bytes):
    '''
    CRC-16 (CCITT) implemented with a precomputed lookup table
    '''
    table = [ 
        0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7, 0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
        0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6, 0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
        0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485, 0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
        0x3653, 0x2672, 0x1611, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4, 0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
        0x48C4, 0x58E5, 0x6886, 0x78A7, 0x0840, 0x1861, 0x2802, 0x3823, 0xC9CC, 0xD9ED, 0xE98E, 0xF9AF, 0x8948, 0x9969, 0xA90A, 0xB92B,
        0x5AF5, 0x4AD4, 0x7AB7, 0x6A96, 0x1A71, 0x0A50, 0x3A33, 0x2A12, 0xDBFD, 0xCBDC, 0xFBBF, 0xEB9E, 0x9B79, 0x8B58, 0xBB3B, 0xAB1A,
        0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41, 0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
        0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70, 0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
        0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F, 0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
        0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E, 0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
        0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D, 0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
        0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C, 0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
        0xD94C, 0xC96D, 0xF90E, 0xE92F, 0x99C8, 0x89E9, 0xB98A, 0xA9AB, 0x5844, 0x4865, 0x7806, 0x6827, 0x18C0, 0x08E1, 0x3882, 0x28A3,
        0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBB9A, 0x4A75, 0x5A54, 0x6A37, 0x7A16, 0x0AF1, 0x1AD0, 0x2AB3, 0x3A92,
        0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9, 0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
        0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8, 0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0
    ]
    
    crc = 0xFFFF
    for byte in data:
        crc = (crc << 8) ^ table[(crc >> 8) ^ byte]
        crc &= 0xFFFF                                   # important, crc must stay 16bits all the way through
    return crc


# %% Build the first part of the RS-41 message
#############################################
# Build the first part of the RS-41 message #
#############################################
def SetFrameHeader(MessageBytes):
    '''
    Set RS41 frame header in RS41 message byte array
    '''
    # Set bytes 0 to 7 (0x000 to 0x007): 8 bytes. Header (uint8)
    MessageBytes[0x000:0x008] = [0x86, 0x35, 0xF4, 0x40, 0x93, 0xDF, 0x1A, 0x60]

def GetFrameType(MessageBytes):
    '''
    Get RS41 frame type from RS41 message byte array
    '''
    # Get byte 56 (0x038): 1 bytes. Frame type - 0x0F = Regular frame, 0xF0 = Extended frame. (uint8)
    FrameType = int(MessageBytes[0x038])
    return FrameType

def SetFrameType(FrameType, MessageBytes):
    '''
    Set RS41 frame type in RS41 message byte array
    '''
    # Set byte 56 (0x038): 1 bytes. Frame type - 0x0F = Regular frame, 0xF0 = Extended frame. (uint8)
    MessageBytes[0x038] = FrameType

def BuildFrameHeader(MessageBytes, FrameType):
    '''
    Set RS41 frame header and frame type in RS41 message byte array
    '''
    #Set frame Header
    SetFrameHeader(MessageBytes)
    
    # Bytes 8 to 55 (0x008 to 0x038) are 48 Reed-Solomon parity bytes.
    # It is calculated and placed in the array after all the data is set in the array.
    
    # Set frame type - 0x0F = Regular frame, 0xF0 = Extended frame
    SetFrameType(FrameType, MessageBytes)

# %% Build the STATUS block (ID: 0x79)
#####################################
# Build the STATUS block (ID: 0x79) #
#####################################

def GetFrameNumber(MessageBytes):
    '''
    Get RS41 frame number from RS41 message byte array
    '''
    # Get bytes 59 to 60 (0x03B to 0x03C): 2 bytes. Frame number (uint16 little endian)
    FrameNumber = int.from_bytes(MessageBytes[0x03B:0x03D],byteorder='little')
    return FrameNumber

def SetFrameNumber(FrameNumber, MessageBytes):
    '''
    Set RS41 frame number in RS41 message byte array
    '''
    # Set bytes 59 to 60 (0x03B to 0x03C): 2 bytes. Frame number (uint16 little endian)
    MessageBytes[0x03B:0x03D] = FrameNumber.to_bytes(2,byteorder='little')

def GetRadiosondeID(MessageBytes):
    '''
    Get RS41 radiosonde ID from RS41 message byte array
    '''
    # Get bytes 61 to 68 (0x03C to 0x044): 8 bytes. Radiosonde ID/Serial number (char[8])
    # Radiosonde serial number YWWDxxxx = lot number (YWWD) + sequential number (xxxx)
    # Y = A letter, representing the year: J=2013, K=2014, L=2015, M=2016, N=2017,
    #                                      P=2018, R=2019, S=2020, T=2021, U=2022
    # WW = Week number
    # D = Day of week: 1 = Monday, 2 = Tuesday, 3= Wednesday,
    #                  4 =Thursday, 5 = Friday, 6 =Saturday, 7 =Sunday
    # For example, the first product manufactured on Tuesday during week 14 in 2017 would be referred to as N1420001
    RadiosondeID = MessageBytes[0x03D:0x045].decode("utf-8")
    return RadiosondeID

def SetRadiosondeID(RadiosondeID, MessageBytes):
    '''
    Set RS41 radiosonde ID in RS41 message byte array
    '''
    # Set bytes 61 to 68 (0x03C to 0x044): 8 bytes. Radiosonde ID/Serial number (char[8])
    # Radiosonde serial number YWWDxxxx = lot number (YWWD) + sequential number (xxxx)
    # Y = A letter, representing the year: J=2013, K=2014, L=2015, M=2016, N=2017,
    #                                      P=2018, R=2019, S=2020, T=2021, U=2022
    # WW = Week number
    # D = Day of week: 1 = Monday, 2 = Tuesday, 3= Wednesday,
    #                  4 =Thursday, 5 = Friday, 6 =Saturday, 7 =Sunday
    # For example, the first product manufactured on Tuesday during week 14 in 2017 would be referred to as N1420001
    RadiosondeIDBytes = bytes(RadiosondeID,'UTF-8')
    if len(RadiosondeID) < 8:
        RadiosondeIDBytes = RadiosondeIDBytes + bytes(8-len(RadiosondeIDBytes))
    MessageBytes[0x03D:0x045] = RadiosondeIDBytes[0:8]

def GetBatteryVoltage(MessageBytes):
    '''
    Get RS41 battery voltage from RS41 message byte array
    '''
    # Get byte 69 (0x045): 1 byte. Battery voltage [V] (uint8)
    BatteryVoltage = int(MessageBytes[0x045]) / 10
    return BatteryVoltage

def SetBatteryVoltage(BatteryVoltage, MessageBytes):
    '''
    Set RS41 battery voltage in RS41 message byte array
    '''
    # Set byte 69 (0x045): 1 byte. Battery voltage (uint8)
    MessageBytes[0x045] = int(BatteryVoltage * 10) # Value = Battery voltage [V] * 10

def GetFlightModeAscentDescent(MessageBytes):
    '''
    Get RS41 flight mode and ascent/descent flags from RS41 message byte array
    '''
    # Get byte 72 (0x048): 1 byte. Bit field. (uint8)
    # Bit field: 7 - MSB. Purpose unknown
    #            6 -      Purpose unknown
    #            5 -      Purpose unknown
    #            4 -      Purpose unknown
    #            3 -      Purpose unknown
    #            2 -      Purpose unknown
    #            1 -      0 = Ascent, 1 = Descent
    #            0 - LSB. 0 = Start phase, 1 = Flight mode
    AscentDescent = int(MessageBytes[0x048] & 0x02)
    FlightMode    = int(MessageBytes[0x048] & 0x01)
    return FlightMode, AscentDescent

def SetFlightModeAscentDescent(FlightMode, AscentDescent, MessageBytes):
    '''
    Set RS41 flight mode and ascent/descent flags in RS41 message byte array
    '''
    # Set byte 72 (0x048): 1 byte. Bit field. (uint8)
    # Bit field: 7 - MSB. Purpose unknown
    #            6 -      Purpose unknown
    #            5 -      Purpose unknown
    #            4 -      Purpose unknown
    #            3 -      Purpose unknown
    #            2 -      Purpose unknown
    #            1 -      0 = Ascent, 1 = Descent
    #            0 - LSB. 0 = Start phase, 1 = Flight mode
    MessageBytes[0x048] = FlightMode | AscentDescent

def GetBatteryVoltageOK(MessageBytes):
    '''
    Get RS41 battery voltage OK flag from RS41 message byte array
    '''
    # Get byte 73 (0x049): 1 byte. Bit field. (uint8)
    # Bit field: 7 - MSB. Purpose unknown
    #            6 -      Purpose unknown
    #            5 -      Purpose unknown
    #            4 -      0 = Battery voltage is OK, 1 = Battery voltage is low
    #            3 -      Purpose unknown
    #            2 -      Purpose unknown
    #            1 -      Purpose unknown
    #            0 - LSB. Purpose unknown
    BatteryVoltageOK    = int(MessageBytes[0x049] & 0x10)
    return BatteryVoltageOK

def SetBatteryVoltageOK(BatteryVoltageOK, MessageBytes):
    '''
    Set RS41 battery voltage OK flag in RS41 message byte array
    '''
    # Set byte 73 (0x049): 1 byte. Bit field. (uint8)
    # Bit field: 7 - MSB. Purpose unknown
    #            6 -      Purpose unknown
    #            5 -      Purpose unknown
    #            4 -      0 = Battery voltage is OK, 1 = Battery voltage is low
    #            3 -      Purpose unknown
    #            2 -      Purpose unknown
    #            1 -      Purpose unknown
    #            0 - LSB. Purpose unknown
    MessageBytes[0x049] = BatteryVoltageOK

def GetCryptographyMode(MessageBytes):
    '''
    Get RS41 cryptography mode from RS41 message byte array
    '''
    # Set byte 74 (0x04A): 1 byte. Cryptography mode. (uint8)
    # Cryptography mode: 0   = Standard RS41-SG(P)
    #                    1,2 = RS41-SGM unencrypted,
    #                          7F-MEASSHORT replaces 7A-MEAS
    #                          sends all three GPS blocks (7B-GPSPOS, 7C-GPSINFO, 7D-GPSRAW),
    #                    3,4 = RS41-SGM encrypted,
    #                          encrypted block 80-CRYPTO replaces 7F-MEASSHORT, 7B-GPSPOS,
    #                          7C-GPSINFO and 7D-GPSRAW
    #                    6   = Unknown, appears to indicate broken configuration
    CryptographyMode    = int(MessageBytes[0x04A])
    return CryptographyMode

def SetCryptographyMode(CryptographyMode, MessageBytes):
    '''
    Set RS41 cryptography mode OK flag in RS41 message byte array
    '''
    # Set byte 74 (0x04A): 1 byte. Cryptography mode. (uint8)
    # Cryptography mode: 0   = Standard RS41-SG(P)
    #                    1,2 = RS41-SGM unencrypted,
    #                          7F-MEASSHORT replaces 7A-MEAS
    #                          sends all three GPS blocks (7B-GPSPOS, 7C-GPSINFO, 7D-GPSRAW),
    #                    3,4 = RS41-SGM encrypted,
    #                          encrypted block 80-CRYPTO replaces 7F-MEASSHORT, 7B-GPSPOS,
    #                          7C-GPSINFO and 7D-GPSRAW
    #                    6   = Unknown, appears to indicate broken configuration
    MessageBytes[0x04A] = CryptographyMode

def GetPCBRefAreaTemperature(MessageBytes):
    '''
    Get RS41 temperature of reference area (cut-out) on PCB from RS41 message byte array
    '''
    # Get byte 75 (0x04B): 1 byte. Temperature of reference area (cut-out) on PCB [Degrees Celsius] (int8)
    PCBRefAreaTemperature = int.from_bytes(MessageBytes[0x04B:0x04C],byteorder='little', signed=True)
    return PCBRefAreaTemperature

def SetPCBRefAreaTemperature(PCBRefAreaTemperature, MessageBytes):
    '''
    Set RS41 temperature of reference area (cut-out) on PCB in RS41 message byte array
    '''
    # Set byte 75 (0x04B): 1 byte. Temperature of reference area (cut-out) on PCB [Degrees Celsius] (int8)
    MessageBytes[0x04B:0x04C] = PCBRefAreaTemperature.to_bytes(1,byteorder='little', signed=True)

def GetHumiditySensorHeatingPWM(MessageBytes):
    '''
    Get RS41 humidity sensor heating PWM from RS41 message byte array
    '''
    # Get bytes 78 to 79 (0x04E to 0x04F): 2 bytes. Humidity sensor heating PWM. (uint16 little endian)
    HumiditySensorHeatingPWM = int.from_bytes(MessageBytes[0x04E:0x050],byteorder='little') / 10
    return HumiditySensorHeatingPWM

def SetHumiditySensorHeatingPWM(HumiditySensorHeatingPWM, MessageBytes):
    '''
    Set RS41 humidity sensor heating PWM in RS41 message byte array
    '''
    # Set bytes 78 to 79 (0x04E to 0x04F): 2 bytes. Humidity sensor heating PWM [%]. (uint16 little endian)
    MessageBytes[0x04E:0x050] = (int(HumiditySensorHeatingPWM * 10)).to_bytes(2,byteorder='little')

def GetTxPower(MessageBytes):
    '''
    Get RS41 tranmission power from RS41 message byte array
    '''
    # Get byte 80 (0x050): 1 byte. Transmit power setting. 0 to 7. 0 = Minimum power, 7 = Maximum power (uint8)
    TxPower = int(MessageBytes[0x050])
    return TxPower

def SetTxPower(TxPower, MessageBytes):
    '''
    Set RS41 tranmission power in RS41 message byte array
    '''
    # Set byte 80 (0x050): 1 byte. Transmit power setting. (uint8)
    MessageBytes[0x050] = TxPower # 0 to 7. 0 = Minimum power, 7 = Maximum power

def GetLastSubframe(MessageBytes):
    '''
    Get RS41 last subframe number in each subframe cycle from RS41 message byte array
    '''
    # Get byte 81 (0x051): 1 byte. Last subframe number in each subframe cycle. (uint8)
    LastSubframe = int(MessageBytes[0x051])
    return LastSubframe

def SetLastSubframe(LastSubframe, MessageBytes):
    '''
    Set RS41 last subframe number in each subframe cycle in RS41 message byte array
    '''
    # Set byte 81 (0x051): 1 byte. Last subframe number in each subframe cycle. (uint8)
    MessageBytes[0x051] = LastSubframe # Last subframe number in each subframe cycle

def GetSubframe(MessageBytes):
    '''
    Get RS41 subframe number in each subframe cycle from RS41 message byte array
    '''
    # Get byte 82 (0x052): 1 byte. Subframe number. (uint8)
    Subframe = int(MessageBytes[0x052])
    return Subframe

def SetSubframe(Subframe, MessageBytes):
    '''
    Set RS41 subframe number in each subframe cycle in RS41 message byte array
    '''
    # Set byte 82 (0x052): 1 byte. Subframe number. (uint8)
    MessageBytes[0x052] = Subframe # Subframe number

def GetSubFrameBytes(MessageBytes):
    '''
    Get RS41 subframe bytes from RS41 message byte array
    '''
    # Get bytes 83 to 98 (0x053 to 0x062): 16 bytes. Sub frame.
    SubFrameBytes = MessageBytes[0x053:0x063]
    return SubFrameBytes

def LoadSubFrameBytes(Subframe, SubFrameArray, MessageBytes):
    '''
    Load RS41 subframe bytes from RS41 message byte array to subframe array
    '''
    # Get bytes 83 to 98 (0x053 to 0x062): 16 bytes. Sub frame.
    SubFrameArray[(Subframe*16):((Subframe+1)*16)] = MessageBytes[0x053:0x063]

def SetSubFrameBytes(Subframe, SubFrameArray, MessageBytes):
    '''
    Set RS41 subframe bytes in RS41 message byte array
    '''
    # Set bytes 83 to 98 (0x053 to 0x062): 16 bytes. Sub frame.
    MessageBytes[0x053:0x063] = SubFrameArray[(Subframe*16):((Subframe+1)*16)]

def SetTxFrequencyInMessage(TxFrequency, SubframeNumber, MessageBytes):
    '''
    Set RS41 transmission frequency in RS41 message byte array
    '''
    if SubframeNumber == 0x00:
        # Transmission frequency = 400 MHz + SubFrameArray[0x002:0x003](Little endian) * 0.00015625 MHz
        MessageBytes[0x055:0x057] = (int((TxFrequency-400)*6400)).to_bytes(2,byteorder='little')

def SetFirmwareVersionInMessage(FirmwareVersion, SubframeNumber, MessageBytes):
    '''
    Set RS41 firmware version in RS41 message byte array
    '''
    if SubframeNumber == 0x01:
        MessageBytes[0x058:0x05A] = FirmwareVersion.to_bytes(2,byteorder='little')

def SetLaunchSiteEarthRadiusInMessage(LaunchSiteEarthRadius, SubframeNumber, MessageBytes):
    '''
    Set RS41 launch altitude, referenced to spherical earth model in RS41 message byte array
    '''
    if SubframeNumber == 0x32:
        MessageBytes[0x055:0x057] = int(LaunchSiteEarthRadius - 6371008).to_bytes(2,byteorder='little', signed=True)

def SetRS41ModelInMessage(RS41Model, SubframeNumber, MessageBytes):
    '''
    Set RS41 model string in RS41 message byte array
    '''
    if ((SubframeNumber == 0x21) | (SubframeNumber == 0x22)):
        RS41ModelBytes = bytes(RS41Model,'UTF-8')
        if len(RS41ModelBytes) < 10:
            RS41ModelBytes = RS41ModelBytes + bytes(10-len(RS41ModelBytes))
        
        if (SubframeNumber == 0x21):
            MessageBytes[0x05B:0x063] = RS41ModelBytes[0:8]
        if (SubframeNumber == 0x22):
            MessageBytes[0x053:0x055] = RS41ModelBytes[8:10]

def SetMainboardTypeInMessage(MainboardType, SubframeNumber, MessageBytes):
    '''
    Set RS41 mainboard type string in RS41 message byte array
    '''
    if SubframeNumber == 0x22:
        MainboardTypeBytes = bytes(MainboardType,'UTF-8')
        if len(MainboardTypeBytes) < 10:
            MainboardTypeBytes = MainboardTypeBytes + bytes(10-len(MainboardTypeBytes))
            
        MessageBytes[0x055:0x05F] = MainboardTypeBytes[0:10]

def SetMainboardSerialInMessage(MainboardSerial, SubframeNumber, MessageBytes):
    '''
    Set RS41 mainboard serial number string in RS41 message byte array
    '''
    if ((SubframeNumber == 0x22) | (SubframeNumber == 0x23)):
        MainboardSerialBytes = bytes(MainboardSerial,'UTF-8')
        if len(MainboardSerialBytes) < 9:
            MainboardSerialBytes = MainboardSerialBytes + bytes(9-len(MainboardSerialBytes))

        if (SubframeNumber == 0x22):
            MessageBytes[0x05F:0x063] = MainboardSerialBytes[0:4]
        if (SubframeNumber == 0x23):
            MessageBytes[0x053:0x058] = MainboardSerialBytes[4:9]

def SetPressureSerialInMessage(PressureSerial, SubframeNumber, MessageBytes):
    '''
    Set RS41 pressure sensor serial number string in RS41 message byte array
    '''
    if SubframeNumber == 0x24:
        PressureSerialBytes = bytes(PressureSerial,'UTF-8')
        if len(PressureSerialBytes) < 9:
            PressureSerialBytes = PressureSerialBytes + bytes(9-len(PressureSerialBytes))
            
        MessageBytes[0x056:0x05F] = PressureSerialBytes[0:9]

def SetTxFrequencyInMessage(TxFrequency, SubframeNumber, MessageBytes):
    '''
    Set RS41 transmission frequency in RS41 message byte array
    '''
    if SubframeNumber == 0x00:
        # Transmission frequency = 400 MHz + SubFrameArray[0x002:0x003](Little endian) * 0.00015625 MHz
        MessageBytes[0x055:0x057] = (int((TxFrequency-400)*6400)).to_bytes(2,byteorder='little')

def GetSTATUSblockCRC(MessageBytes):
    '''
    Get RS41 STATUS block CRC code from RS41 message byte array
    '''
    # Get bytes 99 to 100 (0x063 to 0x064): 2 bytes. Block 79 data CRC.
    STATUSblockCRC = int.from_bytes(MessageBytes[0x063:0x065],byteorder='little')
    return STATUSblockCRC

def SetSTATUSblockCRC(MessageBytes):
    '''
    Set RS41 STATUS block CRC code in RS41 message byte array
    '''
    # Set bytes 99 to 100 (0x063 to 0x064): 2 bytes. Block 79 data CRC.
    MessageBytes[0x063:0x065] = crc16(MessageBytes[0x03B:0x063]).to_bytes(2,byteorder='little')

def CheckSTATUSblockCRC(MessageBytes):
    '''
    Check RS41 STATUS block CRC code from RS41 message byte array
    '''
    # Check bytes 99 to 100 (0x063 to 0x064): 2 bytes. Block 79 data CRC.
    return MessageBytes[0x063:0x065] == crc16(MessageBytes[0x03B:0x063]).to_bytes(2,byteorder='little')

def ReadSTATUSblock(MessageBytes):
    '''
    Get RS41 STATUS block data from RS41 message byte array
    '''    
    # Get frame number
    FrameNumber = GetFrameNumber(MessageBytes)
    
    # Get radiosonde ID
    # Radiosonde serial number YWWDxxxx = lot number (YWWD) + sequential number (xxxx)
    # Y = A letter, representing the year: J=2013, K=2014, L=2015, M=2016, N=2017,
    #                                      P=2018, R=2019, S=2020, T=2021, U=2022
    # WW = Week number
    # D = Day of week: 1 = Monday, 2 = Tuesday, 3= Wednesday,
    #                  4 =Thursday, 5 = Friday, 6 =Saturday, 7 =Sunday
    # For example, the first product manufactured on Tuesday during week 14 in 2017 would be referred to as N1420001
    RadiosondeID = GetRadiosondeID(MessageBytes)
    
    # Get battery voltage
    BatteryVoltage = GetBatteryVoltage(MessageBytes)
       
    # Get byte 72 Bit field
    # Bit field: 7 - MSB. Purpose unknown
    #            6 -      Purpose unknown
    #            5 -      Purpose unknown
    #            4 -      Purpose unknown
    #            3 -      Purpose unknown
    #            2 -      Purpose unknown
    #            1 -      0 = Ascent, 1 = Descent
    #            0 - LSB. 0 = Start phase, 1 = Flight mode
    FlightMode, AscentDescent = GetFlightModeAscentDescent(MessageBytes)
    
    # Get byte 73 Bit field
    # Bit field: 7 - MSB. Purpose unknown
    #            6 -      Purpose unknown
    #            5 -      Purpose unknown
    #            4 -      0 = Battery voltage is OK, 1 = Battery voltage is low
    #            3 -      Purpose unknown
    #            2 -      Purpose unknown
    #            1 -      Purpose unknown
    #            0 - LSB. Purpose unknown
    BatteryVoltageOK = GetBatteryVoltageOK(MessageBytes)
    
    # Get cryptography mode
    # Cryptography mode: 0   = Standard RS41-SG(P)
    #                    1,2 = RS41-SGM unencrypted,
    #                          7F-MEASSHORT replaces 7A-MEAS
    #                          sends all three GPS blocks (7B-GPSPOS, 7C-GPSINFO, 7D-GPSRAW),
    #                    3,4 = RS41-SGM encrypted,
    #                          encrypted block 80-CRYPTO replaces 7F-MEASSHORT, 7B-GPSPOS,
    #                          7C-GPSINFO and 7D-GPSRAW
    #                    6   = Unknown, appears to indicate broken configuration
    CryptographyMode = GetCryptographyMode(MessageBytes)
    
    # Get temperature of reference area (cut-out) on PCB [Degrees Celsius]
    PCBRefAreaTemperature = GetPCBRefAreaTemperature(MessageBytes)
    
    # Get humidity sensor heating PWM [%]
    HumiditySensorHeatingPWM = GetHumiditySensorHeatingPWM(MessageBytes)
    
    # Get transmit power setting. 0 to 7. 0 = Minimum power, 7 = Maximum power
    TxPower = GetTxPower(MessageBytes)
    
    # Get last subframe number in each subframe cycle
    LastSubframe = GetLastSubframe(MessageBytes)
    
    # Get subframe number
    Subframe = GetSubframe(MessageBytes)
    
    # Get current sub frame bytes
    SubFrameBytes = GetSubFrameBytes(MessageBytes)
    
    # Get block 79 data CRC
    STATUSblockCRC = GetSTATUSblockCRC(MessageBytes)
    
    return (FrameNumber, RadiosondeID, BatteryVoltage, FlightMode, AscentDescent,
           BatteryVoltageOK, CryptographyMode, PCBRefAreaTemperature, HumiditySensorHeatingPWM,
           TxPower, LastSubframe, Subframe, SubFrameBytes, STATUSblockCRC)

def BuildSTATUSblock(FrameNumber, RadiosondeID,
                     BatteryVoltage, FlightMode, AscentDescent,
                     BatteryVoltageOK, CryptographyMode,
                     PCBRefAreaTemperature, HumiditySensorHeatingPWM,
                     TxPower, LastSubframe, Subframe, SubFrameArray, MessageBytes):
    '''
    Set RS41 STATUS block in RS41 message byte array
    '''
    # Set byte 57 (0x039): 1 byte. STATUS Block ID. Fixed value: 0x79 (uint8)
    MessageBytes[0x039] = 0x79
    
    # Set byte 58 (0x03A): 1 byte. STATUS block length. Fixed value: 0x28 (uint8) = 40 bytes
    MessageBytes[0x03A] = 0x28
    
    # Set frame number
    SetFrameNumber(FrameNumber, MessageBytes)
    
    # Set radiosonde ID
    # Radiosonde serial number YWWDxxxx = lot number (YWWD) + sequential number (xxxx)
    # Y = A letter, representing the year: J=2013, K=2014, L=2015, M=2016, N=2017,
    #                                      P=2018, R=2019, S=2020, T=2021, U=2022
    # WW = Week number
    # D = Day of week: 1 = Monday, 2 = Tuesday, 3= Wednesday,
    #                  4 =Thursday, 5 = Friday, 6 =Saturday, 7 =Sunday
    # For example, the first product manufactured on Tuesday during week 14 in 2017 would be referred to as N1420001
    SetRadiosondeID(RadiosondeID, MessageBytes)
    
    # Set battery voltage
    SetBatteryVoltage(BatteryVoltage, MessageBytes)
    
    # Set byte 70 (0x046): 1 byte. Purpose unknown. (uint8)
    MessageBytes[0x046] = 0x00
    
    # Set byte 71 (0x047): 1 byte. Purpose unknown. (uint8)
    MessageBytes[0x047] = 0x00
    
    # Set byte 72 Bit field
    # Bit field: 7 - MSB. Purpose unknown
    #            6 -      Purpose unknown
    #            5 -      Purpose unknown
    #            4 -      Purpose unknown
    #            3 -      Purpose unknown
    #            2 -      Purpose unknown
    #            1 -      0 = Ascent, 1 = Descent
    #            0 - LSB. 0 = Start phase, 1 = Flight mode
    SetFlightModeAscentDescent(FlightMode, AscentDescent, MessageBytes)
    
    # Set byte 73 Bit field
    # Bit field: 7 - MSB. Purpose unknown
    #            6 -      Purpose unknown
    #            5 -      Purpose unknown
    #            4 -      0 = Battery voltage is OK, 1 = Battery voltage is low
    #            3 -      Purpose unknown
    #            2 -      Purpose unknown
    #            1 -      Purpose unknown
    #            0 - LSB. Purpose unknown
    SetBatteryVoltageOK(BatteryVoltageOK, MessageBytes)
    
    # Set cryptography mode
    # Cryptography mode: 0   = Standard RS41-SG(P)
    #                    1,2 = RS41-SGM unencrypted,
    #                          7F-MEASSHORT replaces 7A-MEAS
    #                          sends all three GPS blocks (7B-GPSPOS, 7C-GPSINFO, 7D-GPSRAW),
    #                    3,4 = RS41-SGM encrypted,
    #                          encrypted block 80-CRYPTO replaces 7F-MEASSHORT, 7B-GPSPOS,
    #                          7C-GPSINFO and 7D-GPSRAW
    #                    6   = Unknown, appears to indicate broken configuration
    SetCryptographyMode(CryptographyMode, MessageBytes)
    
    # Set temperature of reference area (cut-out) on PCB [Degrees Celsius]
    SetPCBRefAreaTemperature(PCBRefAreaTemperature, MessageBytes)
  
    # Set byte 76 (0x04C): 1 byte. Purpose unknown. (uint8)
    MessageBytes[0x04C] = 0x00
    
    # Set byte 77 (0x04D): 1 byte. Purpose unknown. (uint8)
    MessageBytes[0x04D] = 0x00
    
    # Set humidity sensor heating PWM [%]
    SetHumiditySensorHeatingPWM(HumiditySensorHeatingPWM, MessageBytes)
    
    # Set transmit power setting. 0 to 7. 0 = Minimum power, 7 = Maximum power
    SetTxPower(TxPower, MessageBytes)
    
    # Set last subframe number in each subframe cycle
    SetLastSubframe(LastSubframe, MessageBytes)
    
    # Set subframe number
    SetSubframe(Subframe, MessageBytes) # Subframe number
    
    # Set current sub frame bytes
    SetSubFrameBytes(Subframe, SubFrameArray, MessageBytes)
    
    # Set STATUS block 79 data CRC
    SetSTATUSblockCRC(MessageBytes)


# %% Build the MEAS block (a.k.a PTU/PU) (ID: 0x7A)
##############################################################
# Build the MEAS block (a.k.a PTU (RS41-SGP) or TU (RS41-SG) #
##############################################################

def GetTemperatureMain(MessageBytes):
    '''
    Get RS41 ambient temperature main parameter from RS41 message byte array
    '''
    # Get bytes 103 to 105 (0x067 to 0x069): Temperature Main (uint24)
    TemperatureMain = int.from_bytes(MessageBytes[0x067:0x06A],byteorder='little')
    return TemperatureMain

def SetTemperatureMain(TemperatureMain, MessageBytes):
    '''
    Set RS41 ambient temperature main parameter in RS41 message byte array
    '''
    # Set bytes 103 to 105 (0x067 to 0x069): Temperature Main (uint24)
    MessageBytes[0x067:0x06A] = TemperatureMain.to_bytes(3,byteorder='little')

def GetTemperatureRef1(MessageBytes):
    '''
    Get RS41 ambient temperature reference 1 parameter from RS41 message byte array
    '''
    # Get bytes 106 to 108 (0x06A to 0x06C): Temperature Ref1 (uint24)
    TemperatureRef1 = int.from_bytes(MessageBytes[0x06A:0x06D],byteorder='little')
    return TemperatureRef1

def SetTemperatureRef1(TemperatureRef1, MessageBytes):
    '''
    Set RS41 ambient temperature reference 1 parameter in RS41 message byte array
    '''
    # Set bytes 106 to 108 (0x06A to 0x06C): Temperature Ref1 (uint24)
    MessageBytes[0x06A:0x06D] = TemperatureRef1.to_bytes(3,byteorder='little')

def GetTemperatureRef2(MessageBytes):
    '''
    Get RS41 ambient temperature reference 2 parameter from RS41 message byte array
    '''
    # Get bytes 109 to 111 (0x06D to 0x06F): Temperature Ref2 (uint24)
    TemperatureRef2 = int.from_bytes(MessageBytes[0x06D:0x070],byteorder='little')
    return TemperatureRef2

def SetTemperatureRef2(TemperatureRef2, MessageBytes):
    '''
    Set RS41 ambient temperature reference 2 parameter in RS41 message byte array
    '''
    # Set bytes 109 to 111 (0x06D to 0x06F): Temperature Ref2 (uint24)
    MessageBytes[0x06D:0x070] = TemperatureRef2.to_bytes(3,byteorder='little')

def GetRelativeHumidityMain(MessageBytes):
    '''
    Get RS41 relative humidity main parameter from RS41 message byte array
    '''
    # Get Set bytes 112 to 114 (0x070 to 0x072): Humidity Main (uint24)
    RelativeHumidityMain = int.from_bytes(MessageBytes[0x070:0x073],byteorder='little')
    return RelativeHumidityMain

def SetRelativeHumidityMain(RelativeHumidityMain, MessageBytes):
    '''
    Set RS41 relative humidity main parameter in RS41 message byte array
    '''
    # Set bytes 112 to 114 (0x070 to 0x072): Humidity Main (uint24)
    MessageBytes[0x070:0x073] = RelativeHumidityMain.to_bytes(3,byteorder='little')
  
def GetRelativeHumidityRef1(MessageBytes):
    '''
    Get RS41 relative humidity reference 1 parameter from RS41 message byte array
    '''
    # Get bytes 115 to 117 (0x073 to 0x075): Humidity Ref1 (uint24)
    RelativeHumidityRef1 = int.from_bytes(MessageBytes[0x073:0x076],byteorder='little')
    return RelativeHumidityRef1

def SetRelativeHumidityRef1(RelativeHumidityRef1, MessageBytes):
    '''
    Set RS41 relative humidity reference 1 parameter in RS41 message byte array
    '''
    # Set bytes 115 to 117 (0x073 to 0x075): Humidity Ref1 (uint24)
    MessageBytes[0x073:0x076] = RelativeHumidityRef1.to_bytes(3,byteorder='little')

def GetRelativeHumidityRef2(MessageBytes):
    '''
    Get RS41 relative humidity reference 2 parameter from RS41 message byte array
    '''
    # Get bytes 118 to 120 (0x076 to 0x078): Humidity Ref2 (uint24)
    RelativeHumidityRef2 = int.from_bytes(MessageBytes[0x076:0x079],byteorder='little')
    return RelativeHumidityRef2

def SetRelativeHumidityRef2(RelativeHumidityRef2, MessageBytes):
    '''
    Set RS41 relative humidity reference 2 parameter in RS41 message byte array
    '''
    # Set bytes 118 to 120 (0x076 to 0x078): Humidity Ref2 (uint24)
    MessageBytes[0x076:0x079] = RelativeHumidityRef2.to_bytes(3,byteorder='little')

def GetHeaterTemperatureMain(MessageBytes):
    '''
    Get RS41 heater temperature main parameter from RS41 message byte array
    '''
    # Get bytes 121 to 123 (0x079 to 0x07B): Heater temperature Main (uint24)
    HeaterTemperatureMain = int.from_bytes(MessageBytes[0x079:0x07C],byteorder='little')
    return HeaterTemperatureMain

def SetHeaterTemperatureMain(HeaterTemperatureMain, MessageBytes):
    '''
    Set RS41 heater temperature main parameter in RS41 message byte array
    '''
    # Set bytes 121 to 123 (0x079 to 0x07B): Heater temperature Main (uint24)
    MessageBytes[0x079:0x07C] = HeaterTemperatureMain.to_bytes(3,byteorder='little')
  
def GetHeaterTemperatureRef1(MessageBytes):
    '''
    Get RS41 heater temperature reference 1 parameter from RS41 message byte array
    '''
    # Get bytes 124 to 126 (0x07C to 0x07E): Heater temperature Ref1 (uint24)
    HeaterTemperatureRef1 = int.from_bytes(MessageBytes[0x07C:0x07F],byteorder='little')
    return HeaterTemperatureRef1

def SetHeaterTemperatureRef1(HeaterTemperatureRef1, MessageBytes):
    '''
    Set RS41 heater temperature reference 1 parameter in RS41 message byte array
    '''
    # Set bytes 124 to 126 (0x07C to 0x07E): Heater temperature Ref1 (uint24)
    MessageBytes[0x07C:0x07F] = HeaterTemperatureRef1.to_bytes(3,byteorder='little')

def GetHeaterTemperatureRef2(MessageBytes):
    '''
    Get RS41 heater temperature reference 2 parameter from RS41 message byte array
    '''
    # Get bytes 127 to 129 (0x07F to 0x081): Heater temperature Ref2 (uint24)
    HeaterTemperatureRef2 = int.from_bytes(MessageBytes[0x07F:0x082],byteorder='little')
    return HeaterTemperatureRef2

def SetHeaterTemperatureRef2(HeaterTemperatureRef2, MessageBytes):
    '''
    Set RS41 heater temperature reference 2 parameter in RS41 message byte array
    '''
    # Set bytes 127 to 129 (0x07F to 0x081): Heater temperature Ref2 (uint24)
    MessageBytes[0x07F:0x082] = HeaterTemperatureRef2.to_bytes(3,byteorder='little')

def GetPressureMain(MessageBytes):
    '''
    Get RS41 ambient pressure main parameter from RS41 message byte array
    '''
    # Get bytes 130 to 132 (0x082 to 0x084): Pressure Main (uint24)
    PressureMain = int.from_bytes(MessageBytes[0x082:0x085],byteorder='little')
    return PressureMain

def SetPressureMain(PressureMain, MessageBytes):
    '''
    Set RS41 ambient pressure main parameter in RS41 message byte array
    '''
    # Set bytes 130 to 132 (0x082 to 0x084): Pressure Main (uint24)
    MessageBytes[0x082:0x085] = PressureMain.to_bytes(3,byteorder='little')

def GetPressureRef1(MessageBytes):
    '''
    Get RS41 ambient pressure reference 1 parameter from RS41 message byte array
    '''
    # Get bytes 133 to 135 (0x085 to 0x087): Pressure Ref1 (uint24)
    PressureRef1 = int.from_bytes(MessageBytes[0x085:0x088],byteorder='little')
    return PressureRef1

def SetPressureRef1(PressureRef1, MessageBytes):
    '''
    Set RS41 ambient pressure reference 1 parameter in RS41 message byte array
    '''
    # Set bytes 133 to 135 (0x085 to 0x087): Pressure Ref1 (uint24)
    MessageBytes[0x085:0x088] = PressureRef1.to_bytes(3,byteorder='little')

def GetPressureRef2(MessageBytes):
    '''
    Get RS41 ambient pressure reference 2 parameter from RS41 message byte array
    '''
    # Get bytes 136 to 138 (0x088 to 0x08A): Pressure Ref2 (uint24)
    PressureRef2 = int.from_bytes(MessageBytes[0x088:0x08B],byteorder='little')
    return PressureRef2

def SetPressureRef2(PressureRef2, MessageBytes):
    '''
    Set RS41 ambient pressure reference 2 parameter in RS41 message byte array
    '''
    # Set bytes 136 to 138 (0x088 to 0x08A): Pressure Ref2 (uint24)
    MessageBytes[0x088:0x08B] = PressureRef2.to_bytes(3,byteorder='little')

def GetPressureSensorTemperature(MessageBytes):
    '''
    Get RS41 ambient pressure sensor temperature from RS41 message byte array
    '''
    # Get bytes 141 to 142 (0x08D to 0x08E): Pressure sensor temperature [Degrees Celsius] (int16)
    PCBRefAreaTemperature = int.from_bytes(MessageBytes[0x08D:0x08F],byteorder='little', signed=True) / 100
    return PCBRefAreaTemperature

def SetPressureSensorTemperature(PressureSensorTemperature, MessageBytes):
    '''
    Set RS41 ambient pressure sensor temperature in RS41 message byte array
    '''
    # Set bytes 141 to 142 (0x08D to 0x08E): Pressure sensor temperature [Degrees Celsius] (int16)
    MessageBytes[0x08D:0x08F] = (PressureSensorTemperature * 100).to_bytes(2,byteorder='little', signed=True)

def GetMEASblockCRC(MessageBytes):
    '''
    Get RS41 MEAS block CRC code from RS41 message byte array
    '''
    # Get bytes 145 to 146 (0x091 to 0x092): 2 bytes. Block 7A data CRC.
    MEASblockCRC = int.from_bytes(MessageBytes[0x091:0x093],byteorder='little')
    return MEASblockCRC

def SetMEASblockCRC(MessageBytes):
    '''
    Set RS41 MEAS block CRC code in RS41 message byte array
    '''
    # Set bytes 145 to 146 (0x091 to 0x092): 2 bytes. Block 7A data CRC.
    MessageBytes[0x091:0x093] = crc16(MessageBytes[0x067:0x091]).to_bytes(2,byteorder='little')

def CheckMEASblockCRC(MessageBytes):
    '''
    Check RS41 MEAS block CRC code from RS41 message byte array
    '''
    # Check bytes 145 to 146 (0x091 to 0x092): 2 bytes. Block 7A data CRC.
    return MessageBytes[0x091:0x093] == crc16(MessageBytes[0x067:0x091]).to_bytes(2,byteorder='little')

def ReadMEASblock(MessageBytes):
    '''
    Get RS41 MEAS block data from RS41 message byte array
    '''   
    # Get temperature main parameter
    TemperatureMain = GetTemperatureMain(MessageBytes)
  
    # Get temperature refference 1 parameter
    TemperatureRef1 = GetTemperatureRef1(MessageBytes)

    # Get temperature refference 2 parameter
    TemperatureRef2 = GetTemperatureRef2(MessageBytes)

    # Get relative humidity main parameter
    RelativeHumidityMain = GetRelativeHumidityMain(MessageBytes)
  
    # Get relative humidity refference 1 parameter
    RelativeHumidityRef1 = GetRelativeHumidityRef1(MessageBytes)

    # Get relative humidity refference 2 parameter
    RelativeHumidityRef2 = GetRelativeHumidityRef2(MessageBytes)
    
    # Get heater temperature main parameter
    HeaterTemperatureMain = GetHeaterTemperatureMain(MessageBytes)
  
    # Get heater temperature reference 1 parameter
    HeaterTemperatureRef1 = GetHeaterTemperatureRef1(MessageBytes)

    # Get heater temperature reference 2 parameter
    HeaterTemperatureRef2 = GetHeaterTemperatureRef2(MessageBytes)

    # Get ambient pressure main parameter
    PressureMain = GetPressureMain(MessageBytes)

    # Get ambient pressure reference 1 parameter
    PressureRef1 = GetPressureRef1(MessageBytes)

    # Get ambient pressure reference 2 parameter
    PressureRef2 = GetPressureRef2(MessageBytes)
      
    # Get ambient pressure sensor temperature
    PressureSensorTemperature = GetPressureSensorTemperature(MessageBytes)
    
    # Get MEAS block 7A data CRC.
    MEASblockCRC = GetMEASblockCRC(MessageBytes)

    return (TemperatureMain, TemperatureRef1, TemperatureRef2,
            RelativeHumidityMain, RelativeHumidityRef1, RelativeHumidityRef2,
            HeaterTemperatureMain, HeaterTemperatureRef1, HeaterTemperatureRef2,
            PressureMain, PressureRef1, PressureRef2,
            PressureSensorTemperature, MEASblockCRC)

def BuildMEASblock(RS41Model, TemperatureMain, TemperatureRef1, TemperatureRef2,
                   RelativeHumidityMain, RelativeHumidityRef1, RelativeHumidityRef2,
                   HeaterTemperatureMain, HeaterTemperatureRef1, HeaterTemperatureRef2,
                   PressureMain, PressureRef1, PressureRef2,
                   PressureSensorTemperature, MessageBytes):
    '''
    Set RS41 MEAS block in RS41 message byte array
    '''
    # Set byte 101 (0x065): 1 byte. MEAS Block ID. Fixed value: 0x7A (uint8)
    MessageBytes[0x065] = 0x7A

    # Set byte 102 (0x066): 1 byte. MEAS block length. Fixed value: 0x2A (uint8) = 42 bytes
    MessageBytes[0x066] = 0x2A
    
    # Set temperature main parameter
    SetTemperatureMain(TemperatureMain, MessageBytes)
  
    # Set temperature refference 1 parameter
    SetTemperatureRef1(TemperatureRef1, MessageBytes)

    # Set temperature refference 2 parameter
    SetTemperatureRef2(TemperatureRef2, MessageBytes)

    # Set relative humidity main parameter
    SetRelativeHumidityMain(RelativeHumidityMain, MessageBytes)
  
    # Set relative humidity refference 1 parameter
    SetRelativeHumidityRef1(RelativeHumidityRef1, MessageBytes)

    # Set relative humidity refference 2 parameter
    SetRelativeHumidityRef2(RelativeHumidityRef2, MessageBytes)
    
    # Set heater temperature main parameter
    SetHeaterTemperatureMain(HeaterTemperatureMain, MessageBytes)
  
    # Set heater temperature reference 1 parameter
    SetHeaterTemperatureRef1(HeaterTemperatureRef1, MessageBytes)

    # Set heater temperature reference 2 parameter
    SetHeaterTemperatureRef2(HeaterTemperatureRef2, MessageBytes)

    if (RS41Model == "RS41-SGP"):
        # Set ambient pressure main parameter
        SetPressureMain(PressureMain, MessageBytes)

        # Set ambient pressure reference 1 parameter
        SetPressureRef1(PressureRef1, MessageBytes)

        # Set ambient pressure reference 2 parameter
        SetPressureRef2(PressureRef2, MessageBytes)
    else:
        # Set ambient pressure main parameter
        SetPressureMain(0, MessageBytes)

        # Set ambient pressure reference 1 parameter
        SetPressureRef1(0, MessageBytes)

        # Set ambient pressure reference 2 parameter
        SetPressureRef2(0, MessageBytes)
    
    # Set byte 139 (0x08B): 1 byte. Purpose unknown. (uint8)
    MessageBytes[0x08B] = 0x00

    # Set byte 140 (0x08C): 1 byte. Purpose unknown. (uint8)
    MessageBytes[0x08C] = 0x00
    
    # Set ambient pressure sensor temperature
    SetPressureSensorTemperature(PressureSensorTemperature, MessageBytes)

    # Set byte 143 (0x08F): 1 byte. Purpose unknown. (uint8)
    MessageBytes[0x08F] = 0x00

    # Set byte 144 (0x090): 1 byte. Purpose unknown. (uint8)
    MessageBytes[0x090] = 0x00
    
    # Set MEAS block 7A data CRC.
    SetMEASblockCRC(MessageBytes)

# %% Build the GPSINFO block (ID: 0x7C)
###########################
# Build the GPSINFO block #
###########################

def GetGPSWeek(MessageBytes):
    '''
    Get RS41 GPS Week from RS41 message byte array
    '''
    # Get bytes 149 to 150 (0x095 to 0x096): 2 bytes. GPS Week (uint16)
    GPSWeek = int.from_bytes(MessageBytes[0x095:0x097],byteorder='little')
    return GPSWeek

def SetGPSWeek(GPSWeek, MessageBytes):
    '''
    Set RS41 GPS Week in RS41 message byte array
    '''
    # Set bytes 149 to 150 (0x095 to 0x096): 2 bytes. GPS Week (uint16)
    MessageBytes[0x095:0x097] = GPSWeek.to_bytes(2,byteorder='little')

def GetGPSMilliseconds(MessageBytes):
    '''
    Get RS41 GPS Time of Week in milliseconds from RS41 message byte array
    '''
    # Get bytes 151 to 154 (0x097 to 0x09A): 4 bytes. GPS Time of Week (uint32)
    GPSMilliseconds = int.from_bytes(MessageBytes[0x097:0x09B],byteorder='little')
    return GPSMilliseconds

def SetGPSMilliseconds(GPSMilliseconds, MessageBytes):
    '''
    Set RS41 GPS Time of Week in milliseconds in RS41 message byte array
    '''
    # Set bytes 151 to 154 (0x097 to 0x09A): 4 bytes. GPS Time of Week in milliseconds (uint32)
    MessageBytes[0x097:0x09B] = GPSMilliseconds.to_bytes(4,byteorder='little')

def GetSVsReceptionQualityData(MessageBytes):
    '''
    Get RS41 GPS SVs reception quality data from RS41 message byte array
    '''
    # Get bytes 155 to 178 (0x09B to 0x0B2): 24 bytes. SVs Reception Quality Indicator: 24 byte.
    # A 12 slots array,
    # byte n   = Slot n Space Vehicle Number        (uint8)
    # byte n+1 = Slot n Reception Quality Indicator (uint8)
    PRNandReceptionQualityIndicatorArray = MessageBytes[0x09B:0x0B3]
    
    # Split PRNandReceptionQualityIndicatorArray to components
    SVsReceptionQualityTable = np.empty((12, 3))
    for i in range(12):
        # Get SV's PRN number
        SVsReceptionQualityTable[i][0] = int(PRNandReceptionQualityIndicatorArray[i * 2])
        # Get SV's mesQI
        SVsReceptionQualityTable[i][1] = int(PRNandReceptionQualityIndicatorArray[i * 2 + 1] >> 5)
        # Get SV's c/N0
        SVsReceptionQualityTable[i][2] = int(PRNandReceptionQualityIndicatorArray[i * 2 + 1] & 0x1F) + 20
    return PRNandReceptionQualityIndicatorArray, SVsReceptionQualityTable

def SetSVsReceptionQualityData(PRNandReceptionQualityIndicatorArray, MessageBytes):
    '''
    Set RS41 GPS SVs reception quality data in RS41 message byte array
    '''
    # Set bytes 155 to 178 (0x09B to 0x0B2): 24 bytes. SVs Reception Quality Indicator: 24 byte.
    # A 12 slots array,
    # byte n   = Slot n Space Vehicle Number        (uint8)
    # byte n+1 = Slot n Reception Quality Indicator (uint8)
    MessageBytes[0x09B:0x0B3] = PRNandReceptionQualityIndicatorArray

def GetGPSINFOblockCRC(MessageBytes):
    '''
    Get RS41 GPSINFO block CRC code from RS41 message byte array
    '''
    # Get bytes 179 to 180 (0x0B3 to 0x0B4): 2 bytes. Block 7C data CRC.
    GPSINFOblockCRC = int.from_bytes(MessageBytes[0x0B3:0x0B5],byteorder='little')
    return GPSINFOblockCRC

def SetGPSINFOblockCRC(MessageBytes):
    '''
    Set RS41 GPSINFO block CRC code in RS41 message byte array
    '''
    # Set bytes 179 to 180 (0x0B3 to 0x0B4): 2 bytes. Block 7C data CRC.
    MessageBytes[0x0B3:0x0B5] = crc16(MessageBytes[0x095:0x0B3]).to_bytes(2,byteorder='little')

def CheckGPSINFOblockCRC(MessageBytes):
    '''
    Check RS41 GPSINFO block CRC code from RS41 message byte array
    '''
    # Check bytes 179 to 180 (0x0B3 to 0x0B4): 2 bytes. Block 7C data CRC.
    return MessageBytes[0x0B3:0x0B5] == crc16(MessageBytes[0x095:0x0B3]).to_bytes(2,byteorder='little')

def ReadGPSINFOblock(MessageBytes):
    '''
    Get RS41 GPSINFO block data from RS41 message byte array
    '''    
    # Get GPS Week
    GPSWeek = GetGPSWeek(MessageBytes)

    # Get GPS time of week in milliseconds
    GPSMilliseconds = GetGPSMilliseconds(MessageBytes)

    # Get PRNandReceptionQualityIndicatorArray:
    # A 12 slots array,
    # byte n   = Slot n Space Vehicle Number        (uint8)
    # byte n+1 = Slot n Reception Quality Indicator (uint8)
    # In addition get SVsReceptionQualityTable:
    # A 12 slots array,
    # Cell 0: SV's PRN number
    # Cell 1: SV's mesQI
    # Cell 2: SV's c/N0
    PRNandReceptionQualityIndicatorArray, SVsReceptionQualityTable = GetSVsReceptionQualityData(MessageBytes)

    # Set GPSINFO block 7C data CRC.
    GPSINFOblockCRC = GetGPSINFOblockCRC(MessageBytes)
    
    return (GPSWeek, GPSMilliseconds, PRNandReceptionQualityIndicatorArray,
           SVsReceptionQualityTable, GPSINFOblockCRC)

def BuildGPSINFOblock(GPSWeek, GPSMilliseconds, PRNandReceptionQualityIndicatorArray, MessageBytes):
    '''
    Set RS41 GPSINFO block in RS41 message byte array
    '''
    # Set byte 147 (0x093): 1 byte. GPSINFO Block ID. Fixed value: 0x7C (uint8)
    MessageBytes[0x093] = 0x7C

    # Set byte 148 (0x094): 1 byte. GPSINFO block length. Fixed value: 0x1E (uint8) = 30 bytes
    MessageBytes[0x094] = 0x1E
    
    # Set GPS Week
    SetGPSWeek(GPSWeek, MessageBytes)

    # Set GPS time of week in milliseconds
    SetGPSMilliseconds(GPSMilliseconds, MessageBytes)

    # Set SVs Reception Quality array:
    # A 12 slots array,
    # byte n   = Slot n Space Vehicle Number        (uint8)
    # byte n+1 = Slot n Reception Quality Indicator (uint8)
    SetSVsReceptionQualityData(PRNandReceptionQualityIndicatorArray, MessageBytes)

    # Set GPSINFO block 7C data CRC.
    SetGPSINFOblockCRC(MessageBytes)

# %% Build the GPSRAW block (ID: 0x7D)
##########################
# Build the GPSRAW block #
##########################

def GetMinPR(MessageBytes):
    '''
    Get RS41 smallest satellite's pseudorange measurement from RS41 message byte array
    '''
    # Get bytes 183 to 186 (0x0B7 to 0x0BA): 4 bytes. smallest satellite's pseudorange measurement [m] (uint32)
    MinPR = int.from_bytes(MessageBytes[0x0B7:0x0BB],byteorder='little')
    return MinPR

def SetMinPR(MinPR, MessageBytes):
    '''
    Set RS41 smallest satellite's pseudorange measurement in RS41 message byte array
    '''
    # Set bytes 183 to 186 (0x0B7 to 0x0BA): 4 bytes. smallest satellite's pseudorange measurement [m] (uint32)
    MessageBytes[0x0B7:0x0BB] = MinPR.to_bytes(4,byteorder='little')

def GetPsaudorangeandVelocityData(MessageBytes):
    '''
    Get RS41 GPS SV's psaudorange and velocity data from RS41 message byte array
    '''
    # Get bytes 188 to 271 (0x0BC to 0x10F): 84 bytes. SVs raw data: 84 byte.
    # A Psaudorange and Velocity array, for 12 satellites
    # The array comprises 12 records. In each record there are two variables:
    # 1st variable holds the psauderange between the object and the satellite, in [cm],
    # minus the lowest psaudorange in the satellites data base, in[cm] (int32)
    # 2nd variable holds the relative velocity between the object and the satellite (int24)
    PsaudorangeandVelocityArray = MessageBytes[0x0BC:0x110]
    
    # Split PsaudorangeandVelocityArray to components
    SVsReceptionQualityTable = np.empty((12, 2))
    for i in range(12):
        # Get SV's deltaPR from minPR in units of [cm]
        SVsReceptionQualityTable[i][0] = int.from_bytes(PsaudorangeandVelocityArray[i*7  :i*7+4],byteorder='little', signed=True)
        # Get Vehicle-SV's relative velocity [cm/sec]
        SVsReceptionQualityTable[i][1] = int.from_bytes(PsaudorangeandVelocityArray[i*7+4:i*7+7],byteorder='little', signed=True)
    return PsaudorangeandVelocityArray, SVsReceptionQualityTable

def SetPsaudorangeandVelocityData(PsaudorangeandVelocityArray, MessageBytes):
    '''
    Set RS41 GPS SV's psaudorange and velocity data in RS41 message byte array
    '''
    # Set bytes 188 to 271 (0x0BC to 0x10F): 84 bytes. SVs raw data: 84 byte.
    # A Psaudorange and Velocity array, for 12 satellites
    # The array comprises 12 records. In each record there are two variables:
    # 1st variable holds the psauderange between the object and the satellite, in [cm],
    # minus the lowest psaudorange in the satellites data base, in[cm] (int32)
    # 2nd variable holds the relative velocity between the object and the satellite (int24)
    MessageBytes[0x0BC:0x110] = PsaudorangeandVelocityArray

def GetGPSRAWblockCRC(MessageBytes):
    '''
    Get RS41 GPSRAW block CRC code from RS41 message byte array
    '''
    # Get bytes 272 to 273 (0x110 to 0x111): 2 bytes. Block 7D data CRC.
    GPSRAWblockCRC = int.from_bytes(MessageBytes[0x110:0x112],byteorder='little')
    return GPSRAWblockCRC

def SetGPSRAWblockCRC(MessageBytes):
    '''
    Set RS41 GPSRAW block CRC code in RS41 message byte array
    '''
    # Set bytes 272 to 273 (0x110 to 0x111): 2 bytes. Block 7D data CRC.
    MessageBytes[0x110:0x112] = crc16(MessageBytes[0x0B7:0x0110]).to_bytes(2,byteorder='little')

def CheckGPSRAWblockCRC(MessageBytes):
    '''
    Check RS41 GPSRAW block CRC code from RS41 message byte array
    '''
    # Check bytes 272 to 273 (0x110 to 0x111): 2 bytes. Block 7D data CRC.
    return MessageBytes[0x110:0x112] == crc16(MessageBytes[0x0B7:0x0110]).to_bytes(2,byteorder='little')

def ReadGPSRAWblock(MessageBytes):
    '''
    Get RS41 GPSRAW block data from RS41 message byte array
    '''
    # Get smallest satellite's pseudorange measurement [m]
    MinPR = GetMinPR(MessageBytes)
    
    # Get SVs raw data
    # A Psaudorange and Velocity array, for 12 satellites
    # The array comprises 12 records. In each record there are two variables:
    # 1st variable holds the psauderange between the object and the satellite, in [cm],
    # minus the lowest psaudorange in the satellites data base, in[cm] (int32)
    # 2nd variable holds the relative velocity between the object and the satellite (int24)
    PsaudorangeandVelocityArray, SVsReceptionQualityTable = GetPsaudorangeandVelocityData(MessageBytes)
    
    # Get GPSRAW block 7B data CRC.
    GPSRAWblockCRC = GetGPSRAWblockCRC(MessageBytes)
    
    return MinPR, PsaudorangeandVelocityArray, SVsReceptionQualityTable, GPSRAWblockCRC

def BuildGPSRAWblock(MinPR, PsaudorangeandVelocityArray, MessageBytes):
    '''
    Set RS41 GPSRAW block in RS41 message byte array
    '''
    # Set byte 181 (0x0B4): 1 byte. GPSRAW Block ID. Fixed value: 0x7D (uint8)
    MessageBytes[0x0B5] = 0x7D

    # Set byte 182 (0x0B5): 1 byte. GPSRAW block length. Fixed value: 0x59 (uint8) = 89 bytes
    MessageBytes[0x0B6] = 0x59
    
    # Set smallest satellite's pseudorange measurement [m] (uint32)
    SetMinPR(MinPR, MessageBytes)
    
    # Set byte 187 (0x0BB): 1 byte. Purpose unknown.
    MessageBytes[0x0BB] = 0xFF
    
    # Set SVs raw data
    # A Psaudorange and Velocity array, for 12 satellites
    # The array comprises 12 records. In each record there are two variables:
    # 1st variable holds the psauderange between the object and the satellite, in [cm],
    # minus the lowest psaudorange in the satellites data base, in[cm] (int32)
    # 2nd variable holds the relative velocity between the object and the satellite (int24)
    SetPsaudorangeandVelocityData(PsaudorangeandVelocityArray, MessageBytes)
    
    # Set GPSRAW block 7B data CRC.
    SetGPSRAWblockCRC(MessageBytes)

# %% Build the GPSPOS block (ID: 0x7B)
##########################
# Build the GPSPOS block #
##########################

def GetECEFPositionX(MessageBytes):
    '''
    Get RS41 ECEF position X from RS41 message byte array
    '''
    # Get bytes 276 to 279 (0x114 to 0x117): 4 bytes. ECEF Position X in [m] (int32)
    ECEFPositionX = int.from_bytes(MessageBytes[0x114:0x118],byteorder='little', signed=True) / 100
    return ECEFPositionX

def SetECEFPositionX(ECEFPositionX, MessageBytes):
    '''
    Set RS41 ECEF position X in RS41 message byte array
    '''
    # Set bytes 276 to 279 (0x114 to 0x117): 4 bytes. ECEF Position X in [cm] (int32)
    MessageBytes[0x114:0x118] = (int(ECEFPositionX * 100)).to_bytes(4,byteorder='little', signed=True)

def GetECEFPositionY(MessageBytes):
    '''
    Get RS41 ECEF position Y from RS41 message byte array
    '''
    # Get bytes 280 to 283 (0x118 to 0x11B): 4 bytes. ECEF Position Y in [m] (int32)
    ECEFPositionY = int.from_bytes(MessageBytes[0x118:0x11C],byteorder='little', signed=True) / 100
    return ECEFPositionY

def SetECEFPositionY(ECEFPositionY, MessageBytes):
    '''
    Set RS41 ECEF position Y in RS41 message byte array
    '''
    # Set bytes 280 to 283 (0x118 to 0x11B): 4 bytes. ECEF Position Y in [cm] (int32)
    MessageBytes[0x118:0x11C] = (int(ECEFPositionY * 100)).to_bytes(4,byteorder='little', signed=True)

def GetECEFPositionZ(MessageBytes):
    '''
    Get RS41 ECEF position Z from RS41 message byte array
    '''
    # Get bytes 284 to 287 (0x11C to 0x11F): 4 bytes. ECEF Position Z in [m] (int32)
    ECEFPositionZ = int.from_bytes(MessageBytes[0x11C:0x120],byteorder='little', signed=True) / 100
    return ECEFPositionZ

def SetECEFPositionZ(ECEFPositionZ, MessageBytes):
    '''
    Set RS41 ECEF position Z in RS41 message byte array
    '''
    # Set bytes 284 to 287 (0x11C to 0x11F): 4 bytes. ECEF Position Z in [cm] (int32)
    MessageBytes[0x11C:0x120] = (int(ECEFPositionZ * 100)).to_bytes(4,byteorder='little', signed=True)

def GetECEFVelocityX(MessageBytes):
    '''
    Get RS41 ECEF velocity X from RS41 message byte array
    '''
    # Get bytes 288 to 289 (0x120 to 0x121): 2 bytes. ECEF Velocity X in [m/s] (int16)
    ECEFVelocityX = int.from_bytes(MessageBytes[0x120:0x122],byteorder='little', signed=True) / 100
    return ECEFVelocityX

def SetECEFVelocityX(ECEFVelocityX, MessageBytes):
    '''
    Set RS41 ECEF velocity X in RS41 message byte array
    '''
    # Set bytes 288 to 289 (0x120 to 0x121): 2 bytes. ECEF Velocity X in [cm/s] (int16)
    MessageBytes[0x120:0x122] = (int(ECEFVelocityX * 100)).to_bytes(2,byteorder='little', signed=True)

def GetECEFVelocityY(MessageBytes):
    '''
    Get RS41 ECEF velocity Y from RS41 message byte array
    '''
    # Get bytes 290 to 291 (0x122 to 0x123): 2 bytes. ECEF Velocity Y in [m/s] (int16)
    ECEFVelocityY = int.from_bytes(MessageBytes[0x122:0x124],byteorder='little', signed=True) / 100
    return ECEFVelocityY

def SetECEFVelocityY(ECEFVelocityY, MessageBytes):
    '''
    Set RS41 ECEF velocity Y in RS41 message byte array
    '''
    # Set bytes 290 to 291 (0x122 to 0x123): 2 bytes. ECEF Velocity Y in [cm/s] (int16)
    MessageBytes[0x122:0x124] = (int(ECEFVelocityY * 100)).to_bytes(2,byteorder='little', signed=True)

def GetECEFVelocityZ(MessageBytes):
    '''
    Get RS41 ECEF velocity Z from RS41 message byte array
    '''
    # Get bytes 292 to 293 (0x124 to 0x125): 2 bytes. ECEF Velocity Z in [m/s] (int16)
    ECEFVelocityZ = int.from_bytes(MessageBytes[0x124:0x126],byteorder='little', signed=True) / 100
    return ECEFVelocityZ

def SetECEFVelocityZ(ECEFVelocityZ, MessageBytes):
    '''
    Set RS41 ECEF velocity Z in RS41 message byte array
    '''
    # Set bytes 292 to 293 (0x124 to 0x125): 2 bytes. ECEF Velocity Z in [cm/s] (int16)
    MessageBytes[0x124:0x126] = (int(ECEFVelocityZ * 100)).to_bytes(2,byteorder='little', signed=True)

def GetNumberOfSVs(MessageBytes):
    '''
    Get RS41 number of satellites in the navigation solution from RS41 message byte array
    '''
    # Get byte 295 (0x127): 1 byte. sAcc in [m/sec] (uint8)
    NumberOfSVs = int(MessageBytes[0x126])
    return NumberOfSVs

def SetNumberOfSVs(NumberOfSVs, MessageBytes):
    '''
    Set RS41 number of satellites in the navigation solution in RS41 message byte array
    '''
    # Set byte 294 (0x126): 1 byte. Number of SVs used in Nav Solution (uint8)
    MessageBytes[0x126] = NumberOfSVs

def GetGPSsAcc(MessageBytes):
    '''
    Get RS41 GPSsAcc from RS41 message byte array
    '''
    # Get byte 295 (0x127): 1 byte. sAcc in [m/sec] (uint8)
    GPSsAcc = int(MessageBytes[0x127]) / 10
    return GPSsAcc

def SetGPSsAcc(GPSsAcc, MessageBytes):
    '''
    Set RS41 GPSsAcc in RS41 message byte array
    '''
    # Set byte 295 (0x127): 1 byte. sAcc in [10cm/sec] (uint8)
    # TODO: Develop a model for sAcc
    MessageBytes[0x127] = int(GPSsAcc * 10)

def GetGPSPDOP(MessageBytes):
    '''
    Get RS41 GPSPDOP from RS41 message byte array
    '''
    # Get byte 296 (0x128): 1 byte. PDOP (uint8)
    GPSPDOP = int(MessageBytes[0x128]) / 10
    return GPSPDOP

def SetGPSPDOP(GPSPDOP, MessageBytes):
    '''
    Set RS41 GPS PDOP in RS41 message byte array
    '''
    # Set byte 296 (0x128): 1 byte. GPS PDOP * 10 (uint8)
    MessageBytes[0x128] = int(GPSPDOP * 10)

def GetGPSPOSblockCRC(MessageBytes):
    '''
    Get RS41 GPSPOS block CRC code from RS41 message byte array
    '''
    # Get bytes 297 to 298 (0x129 to 0x12A): 2 bytes. Block 7B data CRC
    GPSPOSblockCRC = int.from_bytes(MessageBytes[0x129:0x12B],byteorder='little')
    return GPSPOSblockCRC

def SetGPSPOSblockCRC(MessageBytes):
    '''
    Set RS41 GPSPOS block CRC code in RS41 message byte array
    '''
    # Set bytes 297 to 298 (0x129 to 0x12A): 2 bytes. Block 7B data CRC
    MessageBytes[0x129:0x12B] = crc16(MessageBytes[0x114:0x0129]).to_bytes(2,byteorder='little')

def CheckGPSPOSblockCRC(MessageBytes):
    '''
    Check RS41 GPSPOS block CRC code from RS41 message byte array
    '''
    # Check bytes 297 to 298 (0x129 to 0x12A): 2 bytes. Block 7B data CRC
    return MessageBytes[0x129:0x12B] == crc16(MessageBytes[0x114:0x0129]).to_bytes(2,byteorder='little')

def ReadGPSPOSblock(MessageBytes):
    '''
    Get RS41 GPSPOS block data from RS41 message byte array
    '''
    # Get ECEF Position X in [m]
    ECEFPositionX = GetECEFPositionX(MessageBytes)

    # Get ECEF Position Y in [m]
    ECEFPositionY = GetECEFPositionY(MessageBytes)

    # Get ECEF Position Z in [m]
    ECEFPositionZ = GetECEFPositionZ(MessageBytes)

    # Get ECEF Velocity X in [m/sec]
    ECEFVelocityX = GetECEFVelocityX(MessageBytes)

    # Get ECEF Velocity Y in [m/sec]
    ECEFVelocityY = GetECEFVelocityY(MessageBytes)

    # Get ECEF Velocity Z in [m/sec]
    ECEFVelocityZ = GetECEFVelocityZ(MessageBytes)

    # Get the number of SVs used in Nav Solution
    NumberOfSVs = GetNumberOfSVs(MessageBytes)

    # Get sAcc in [m/sec]
    GPSsAcc = GetGPSsAcc(MessageBytes)

    # Get GPS PDOP
    GPSPDOP = GetGPSPDOP(MessageBytes)

    # Get GPSPOS block 7B data CRC
    GPSPOSblockCRC = GetGPSPOSblockCRC(MessageBytes)

    return (ECEFPositionX, ECEFPositionY, ECEFPositionZ,
            ECEFVelocityX, ECEFVelocityY, ECEFVelocityZ,
            NumberOfSVs, GPSsAcc, GPSPDOP, GPSPOSblockCRC)

def BuildGPSPOSblock(ECEFPositionX, ECEFPositionY, ECEFPositionZ,
                     ECEFVelocityX, ECEFVelocityY, ECEFVelocityZ,
                     NumberOfSVs, GPSsAcc, GPSPDOP, MessageBytes):
    '''
    Set RS41 GPSPOS block in RS41 message byte array
    '''
    # Set byte 274 (0x112): 1 byte. GPSPOS Block ID. Fixed value: 0x7B (uint8)
    MessageBytes[0x112] = 0x7B

    # Set byte 275 (0x113): 1 byte. GPSPOS block length. Fixed value: 0x15 (uint8) = 21 bytes
    MessageBytes[0x113] = 0x15
    
    # Set ECEF Position X in [m]
    SetECEFPositionX(ECEFPositionX, MessageBytes)

    # Set ECEF Position Y in [m]
    SetECEFPositionY(ECEFPositionY, MessageBytes)

    # Set ECEF Position Z in [m]
    SetECEFPositionZ(ECEFPositionZ, MessageBytes)

    # Set ECEF Velocity X in [m/sec]
    SetECEFVelocityX(ECEFVelocityX, MessageBytes)

    # Set ECEF Velocity Y in [m/sec]
    SetECEFVelocityY(ECEFVelocityY, MessageBytes)

    # Set ECEF Velocity Z in [m/sec]
    SetECEFVelocityZ(ECEFVelocityZ, MessageBytes)

    # Set the number of SVs used in Nav Solution
    SetNumberOfSVs(NumberOfSVs, MessageBytes)

    # Set sAcc in [m/sec]
    # TODO: Develop a model for sAcc
    SetGPSsAcc(GPSsAcc, MessageBytes)

    # Set GPS PDOP
    SetGPSPDOP(GPSPDOP, MessageBytes)

    # Set GPSPOS block 7B data CRC
    SetGPSPOSblockCRC(MessageBytes)

# %% Build the EMPTY block (ID: 0x76)
#########################
# Build the EMPTY block #
#########################

def BuildEMPTYblock(MessageBytes):
    '''
    Set RS41 EMPTY block in RS41 message byte array
    '''
    # Set byte 299 (0x12B): 1 byte. EMPTY Block ID. Fixed value: 0x76 (uint8)
    MessageBytes[0x12B] = 0x76

    # Set byte 300 (0x12C): 1 byte. EMPTY block length. Fixed value: 0x11 (uint8) = 17 bytes
    MessageBytes[0x12C] = 0x11
    
    # Set bytes 301 to 317 (0x12D to 0x13D): 17 bytes. Empty bytes (uint8)
    MessageBytes[0x12D:0x13E] = bytearray([ 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    # Set bytes 318 to 319 (0x13E to 0x13F): 2 bytes. Block 76 data CRC.
    MessageBytes[0x13E:0x140] = crc16(MessageBytes[0x12D:0x013E]).to_bytes(2,byteorder='little')

# %% Add the Reed-Solomon parity bytes to the first part of the message
######################################################################
# Add the Reed-Solomon parity bytes to the first part of the message #
######################################################################

def DecodeReedSolomon(MessageBytes):
    '''
    Decode the RS41 message can be decoded using the reed-solomon parity bytes from the RS41 message byte array
    '''
    # Prepare the data for reed-solomon calculation.
    # The basic RS-41 message comprise 320 bytes:
    # 8 Header bytes, 48 Reed-Solomon parity bytes and 264 data bytes.
    # The Reed Solomon process devide the data to two interleaved strems, in reverse order:
    # 1. Data bytes 263, 261, 259, ... 5, 3, 1 (Message byte indexes 318, 316, 314, ... 60, 58, 56) - A total of 132 bytes
    # 2. Data bytes 264, 262, 260, ... 6, 4, 2 (Message byte indexes 319, 317, 315, ... 61, 59, 57)- A total of 132 bytes
    RS_ReversedInterlevedData1 = MessageBytes[0x13E:0x037:-2]
    RS_ReversedInterlevedData2 = MessageBytes[0x13F:0x038:-2]

    # Get bytes 8 to 55 (0x008 to 0x038): 48 Reed-Solomon parity bytes
    # Place the Reed-Solomon parity bytes in the message
    # Each encoded message comprise the 132 data bytes and 24 parity bytes
    # The 24 parity bytes are in reverse order (little endian)
    RS_Parity1 = MessageBytes[0x01F:0x007:-1]
    RS_Parity2 = MessageBytes[0x037:0x01F:-1]
    
    # Check f the data can be decoded sucessfuly
    RS_ECCSymbols = 24 # 24 ECC symbols
    RS_Coder = RSCodec(RS_ECCSymbols)
    rmes1, rmesecc1, errata_pos1 = RS_Coder.decode(RS_ReversedInterlevedData1 + RS_Parity1)
    rmes2, rmesecc2, errata_pos2 = RS_Coder.decode(RS_ReversedInterlevedData2 + RS_Parity2)
    RS1_Recoverable = RS_Coder.check(rmesecc1)[0]
    RS2_Recoverable = RS_Coder.check(rmesecc2)[0]
    
    # Recover the data in case the data was recovered succesfully
    if RS1_Recoverable:
        MessageBytes[0x13E:0x037:-2] = rmes1
        MessageBytes[0x008:0x020] = rmesecc1[132+RS_ECCSymbols:131:-1]
    if RS2_Recoverable:
        MessageBytes[0x13F:0x038:-2] = rmes2
        MessageBytes[0x020:0x038] = rmesecc2[132+RS_ECCSymbols:131:-1]
    return RS1_Recoverable & RS2_Recoverable

def SetReedSolomon(MessageBytes):
    '''
    Set RS41 reed-solomon parity bytes in RS41 message byte array
    '''
    # Prepare the data for reed-solomon calculation.
    # The basic RS-41 message comprise 320 bytes:
    # 8 Header bytes, 48 Reed-Solomon parity bytes and 264 data bytes.
    # The Reed Solomon process devide the data to two interleaved strems, in reverse order:
    # 1. Data bytes 263, 261, 259, ... 5, 3, 1 (Message byte indexes 318, 316, 314, ... 60, 58, 56) - A total of 132 bytes
    # 2. Data bytes 264, 262, 260, ... 6, 4, 2 (Message byte indexes 319, 317, 315, ... 61, 59, 57)- A total of 132 bytes
    RS_ReversedInterlevedData1 = MessageBytes[0x13E:0x037:-2]
    RS_ReversedInterlevedData2 = MessageBytes[0x13F:0x038:-2]
    
    # Calculate the Reed-Solomon parity bytes
    RS_ECCSymbols = 24 # 24 ECC symbols
    RS_Coder = RSCodec(RS_ECCSymbols)
    RS_ReversedParity1 = RS_Coder.encode(RS_ReversedInterlevedData1)
    RS_ReversedParity2 = RS_Coder.encode(RS_ReversedInterlevedData2)
    
    # Set bytes 8 to 55 (0x008 to 0x038): 48 Reed-Solomon parity bytes
    # Place the Reed-Solomon parity bytes in the message
    # Each encoded message comprise the 132 data bytes and 24 parity bytes
    # The 24 parity bytes are in reverse order (little endian)
    MessageBytes[0x008:0x020] = RS_ReversedParity1[132+RS_ECCSymbols:131:-1]
    MessageBytes[0x020:0x038] = RS_ReversedParity2[132+RS_ECCSymbols:131:-1]
# -*- coding: utf-8 -*-
"""
RS41 Subframes Read-Write operations
"""

#############################################
# The following functions are a part of an  #
# RS41-SG/P radiosonde simulation framework.#
# The functions are subframe-level          #
# functions, compatible with the RS41-SG/P' #
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
import struct

# Addresses   0 to   1 (0x000 to 0x001). Subframe 0x00 byte  0 to subframe 0x00 byte  1. Purpose unknown.

# Addresses   2 to   3 (0x002 to 0x003). Subframe 0x00 byte  2 to subframe 0x00 byte  3. Transmission frequency (uint16)
def GetTxFrequency(SubFrameArray):
    '''
    Get RS41 transmission frequency from RS41 subframes array
    '''
    # Transmission frequency = 400 MHz + SubFrameArray[0x002:0x003](Little endian) * 0.00015625 MHz    
    TxFrequency = (int.from_bytes(SubFrameArray[0x002:0x004],byteorder='little') / 6400) + 400
    return TxFrequency
def SetTxFrequency(TxFrequency, SubFrameArray):
    '''
    Set RS41 transmission frequency in RS41 subframes array
    '''
    # Transmission frequency = 400 MHz + SubFrameArray[0x002:0x003](Little endian) * 0.00015625 MHz
    SubFrameArray[0x002:0x004] = (int((TxFrequency-400)*6400)).to_bytes(2,byteorder='little')

# Addresses   4 to  20 (0x004 to 0x014). Subframe 0x00 byte  4 to subframe 0x01 byte  4. Purpose unknown.

# Addresses  21 to  22 (0x015 to 0x016). Subframe 0x01 byte  5 to subframe 0x01 byte  6. Firmware version (uint16)
def GetFirmwareVersion(SubFrameArray):
    '''
    Get RS41 firmware version from RS41 subframes array
    '''
    FirmwareVersion = int.from_bytes(SubFrameArray[0x015:0x017],byteorder='little')
    return FirmwareVersion
def SetFirmwareVersion(FirmwareVersion, SubFrameArray):
    '''
    Set RS41 firmware version in RS41 subframes array
    '''
    SubFrameArray[0x015:0x017] = FirmwareVersion.to_bytes(2,byteorder='little')

# Addresses  23 to  42 (0x017 to 0x02A). Subframe 0x01 byte  7 to subframe 0x02 byte 10. Purpose unknown.

# Address    43        (0x02B).          Subframe 0x02 byte 11. Burstkill enable. 0 = Disable, 1 = Enable. (uint8)
def GetBurstKillEnable(SubFrameArray):
    '''
    Get RS41 burst kill enable state from RS41 subframes array
    '''
    BurstKillEnable = int(SubFrameArray[0x02B])
    return BurstKillEnable
def SetBurstKillEnable(BurstKillEnable, SubFrameArray):
    '''
    Set RS41 burst kill enable state in RS41 subframes array
    '''
    SubFrameArray[0x02B] = BurstKillEnable

# Addresses  23 to  60 (0x02C to 0x03C). Subframe 0x02 byte 12 to subframe 0x03 byte 12. Purpose unknown.

# Addresses  61 to  64 (0x03D to 0x040). Subframe 0x03 byte 13 to subframe 0x04 byte  0. Temperature reference resistor 0 (float32)
# Addresses  65 to  68 (0x041 to 0x044). Subframe 0x04 byte  1 to subframe 0x04 byte  4. Temperature reference resistor 1 (float32)
def GetTempRefRes(SubFrameArray):
    '''
    Get RS41 temperature reference resistors from RS41 subframes array
    '''
    TempRefRes = np.zeros(2)
    TempRefRes[0] = struct.unpack('<f', SubFrameArray[0x03D:0x041])[0]
    TempRefRes[1] = struct.unpack('<f', SubFrameArray[0x041:0x045])[0]
    return TempRefRes
def SetTempRefRes(TempRefRes, SubFrameArray):
    '''
    Set RS41 temperature reference resistors in RS41 subframes array
    '''
    SubFrameArray[0x03D:0x041] = struct.pack('<f', TempRefRes[0]) # '<f' -> little-endian
    SubFrameArray[0x041:0x045] = struct.pack('<f', TempRefRes[1]) # '<f' -> little-endian

# Addresses  69 to  72 (0x045 to 0x048). Subframe 0x04 byte  5 to subframe 0x04 byte  8. Relative Humidity Capacitance Coefficient 0 (float32)
# Addresses  73 to  76 (0x049 to 0x04C). Subframe 0x04 byte  9 to subframe 0x04 byte 12. Relative Humidity Capacitance Coefficient 1 (float32)
def GetRHCapCoeff(SubFrameArray):
    '''
    Get RS41 relative humidity capacitance coefficients from RS41 subframes array
    '''
    RHCapCoeff = np.zeros(2)
    RHCapCoeff[0] = struct.unpack('<f', SubFrameArray[0x045:0x049])[0]
    RHCapCoeff[1] = struct.unpack('<f', SubFrameArray[0x049:0x04D])[0]
    return RHCapCoeff
def SetRHCapCoeff(RHCapCoeff, SubFrameArray):
    '''
    Set RS41 relative humidity capacitance coefficients in RS41 subframes array
    '''
    SubFrameArray[0x045:0x049] = struct.pack('<f', RHCapCoeff[0]) # '<f' -> little-endian
    SubFrameArray[0x049:0x04D] = struct.pack('<f', RHCapCoeff[1]) # '<f' -> little-endian

# Addresses  77 to  80 (0x04D to 0x050). Subframe 0x04 byte 13 to subframe 0x05 byte  0. Temperature polynom coefficient 0 (float32)
# Addresses  81 to  84 (0x051 to 0x054). Subframe 0x05 byte  1 to subframe 0x05 byte  4. Temperature polynom coefficient 1 (float32)
# Addresses  85 to  88 (0x055 to 0x058). Subframe 0x05 byte  5 to subframe 0x05 byte  8. Temperature polynom coefficient 2 (float32)
def GetTempPolCoeff(SubFrameArray):
    '''
    Get RS41 ambient temperature polynom coefficients from RS41 subframes array
    '''
    TempPolCoeff = np.zeros(3)
    TempPolCoeff[0] = struct.unpack('<f', SubFrameArray[0x04D:0x051])[0]
    TempPolCoeff[1] = struct.unpack('<f', SubFrameArray[0x051:0x055])[0]
    TempPolCoeff[2] = struct.unpack('<f', SubFrameArray[0x055:0x059])[0]
    return TempPolCoeff
def SetTempPolCoeff(TempPolCoeff, SubFrameArray):
    '''
    Set RS41 ambient temperature polynom coefficients in RS41 subframes array
    '''
    SubFrameArray[0x04D:0x051] = struct.pack('<f', TempPolCoeff[0]) # '<f' -> little-endian
    SubFrameArray[0x051:0x055] = struct.pack('<f', TempPolCoeff[1]) # '<f' -> little-endian
    SubFrameArray[0x055:0x059] = struct.pack('<f', TempPolCoeff[2]) # '<f' -> little-endian

# Addresses  89 to  92 (0x059 to 0x05C). Subframe 0x05 byte  9 to subframe 0x05 byte 12. Temperature calibration coefficient 0 (float32)
# Addresses  93 to  96 (0x05D to 0x060). Subframe 0x05 byte 13 to subframe 0x06 byte  0. Temperature calibration coefficient 1 (float32)
# Addresses  97 to 100 (0x061 to 0x064). Subframe 0x06 byte  1 to subframe 0x06 byte  4. Temperature calibration coefficient 2 (float32)
def GetTempCalCoeff(SubFrameArray):
    '''
    Get RS41 ambient temperature calibration coefficients from RS41 subframes array
    '''
    TempCalCoeff = np.zeros(3)
    TempCalCoeff[0] = struct.unpack('<f', SubFrameArray[0x059:0x05D])[0]
    TempCalCoeff[1] = struct.unpack('<f', SubFrameArray[0x05D:0x061])[0]
    TempCalCoeff[2] = struct.unpack('<f', SubFrameArray[0x061:0x065])[0]
    return TempCalCoeff
def SetTempCalCoeff(TempCalCoeff, SubFrameArray):
    '''
    Set RS41 ambient temperature calibration coefficients in RS41 subframes array
    '''
    SubFrameArray[0x059:0x05D] = struct.pack('<f', TempCalCoeff[0]) # '<f' -> little-endian
    SubFrameArray[0x05D:0x061] = struct.pack('<f', TempCalCoeff[1]) # '<f' -> little-endian
    SubFrameArray[0x061:0x065] = struct.pack('<f', TempCalCoeff[2]) # '<f' -> little-endian

# Addresses  98 to 116 (0x065 to 0x074). Subframe 0x06 byte  5 to subframe 0x07 byte  4. Purpose unknown.

# Addresses 117 to 120 (0x075 to 0x078). Subframe 0x07 byte  5 to subframe 0x07 byte  8. Humidity calibration coefficient 0 (float32)
# Addresses 121 to 124 (0x079 to 0x07C). Subframe 0x07 byte  9 to subframe 0x07 byte 12. Humidity calibration coefficient 1 (float32)
def GetHumidCalCoeff(SubFrameArray):
    '''
    Get RS41 relative humidity calibration coefficients from RS41 subframes array
    '''
    HumidCalCoeff = np.zeros(2)
    HumidCalCoeff[0] = struct.unpack('<f', SubFrameArray[0x075:0x079])[0]
    HumidCalCoeff[1] = struct.unpack('<f', SubFrameArray[0x079:0x07D])[0]
    return HumidCalCoeff
def SetHumidCalCoeff(HumidCalCoeff, SubFrameArray):
    '''
    Set RS41 relative humidity calibration coefficients in RS41 subframes array
    '''
    SubFrameArray[0x075:0x079] = struct.pack('<f', HumidCalCoeff[0]) # '<f' -> little-endian
    SubFrameArray[0x079:0x07D] = struct.pack('<f', HumidCalCoeff[1]) # '<f' -> little-endian

# Addresses 125 to 128 (0x07D to 0x080). Subframe 0x07 byte 13 to subframe 0x08 byte  0. Humidity heater temperature calibration coefficient 0 (float32)
# Addresses 129 to 132 (0x081 to 0x084). Subframe 0x08 byte  1 to subframe 0x08 byte  4. Humidity heater temperature calibration coefficient 1 (float32)
# Addresses 133 to 136 (0x085 to 0x088). Subframe 0x08 byte  5 to subframe 0x08 byte  8. Humidity heater temperature calibration coefficient 2 (float32)
# Addresses 137 to 140 (0x089 to 0x08C). Subframe 0x08 byte  9 to subframe 0x08 byte 12. Humidity heater temperature calibration coefficient 3 (float32)
# Addresses 141 to 144 (0x08D to 0x090). Subframe 0x08 byte 13 to subframe 0x09 byte  0. Humidity heater temperature calibration coefficient 4 (float32)
# Addresses 145 to 148 (0x091 to 0x094). Subframe 0x09 byte  1 to subframe 0x09 byte  4. Humidity heater temperature calibration coefficient 5 (float32)
# Addresses 149 to 152 (0x095 to 0x098). Subframe 0x09 byte  5 to subframe 0x09 byte  8. Humidity heater temperature calibration coefficient 6 (float32)
# Addresses 153 to 156 (0x099 to 0x09C). Subframe 0x09 byte  9 to subframe 0x09 byte 12. Humidity heater temperature calibration coefficient 7 (float32)
# Addresses 157 to 160 (0x09D to 0x0A0). Subframe 0x09 byte 13 to subframe 0x0A byte  0. Humidity heater temperature calibration coefficient 8 (float32)
# Addresses 161 to 164 (0x0A1 to 0x0A4). Subframe 0x0A byte  1 to subframe 0x0A byte  4. Humidity heater temperature calibration coefficient 9 (float32)
# Addresses 165 to 168 (0x0A5 to 0x0A8). Subframe 0x0A byte  5 to subframe 0x0A byte  8. Humidity heater temperature calibration coefficient 10 (float32)
# Addresses 169 to 172 (0x0A9 to 0x0AC). Subframe 0x0A byte  9 to subframe 0x0A byte 12. Humidity heater temperature calibration coefficient 11 (float32)
# Addresses 173 to 176 (0x0AD to 0x0B0). Subframe 0x0A byte 13 to subframe 0x0B byte  0. Humidity heater temperature calibration coefficient 12 (float32)
# Addresses 177 to 180 (0x0B1 to 0x0B4). Subframe 0x0B byte  1 to subframe 0x0B byte  4. Humidity heater temperature calibration coefficient 13 (float32)
# Addresses 181 to 184 (0x0B5 to 0x0B8). Subframe 0x0B byte  5 to subframe 0x0B byte  8. Humidity heater temperature calibration coefficient 14 (float32)
# Addresses 185 to 188 (0x0B9 to 0x0BC). Subframe 0x0B byte  9 to subframe 0x0B byte 12. Humidity heater temperature calibration coefficient 15 (float32)
# Addresses 189 to 192 (0x0BD to 0x0C0). Subframe 0x0B byte 13 to subframe 0x0C byte  0. Humidity heater temperature calibration coefficient 16 (float32)
# Addresses 193 to 196 (0x0C1 to 0x0C4). Subframe 0x0C byte  1 to subframe 0x0C byte  4. Humidity heater temperature calibration coefficient 17 (float32)
# Addresses 197 to 200 (0x0C5 to 0x0C8). Subframe 0x0C byte  5 to subframe 0x0C byte  8. Humidity heater temperature calibration coefficient 18 (float32)
# Addresses 201 to 204 (0x0C9 to 0x0CC). Subframe 0x0C byte  9 to subframe 0x0C byte 12. Humidity heater temperature calibration coefficient 19 (float32)
# Addresses 205 to 208 (0x0CC to 0x0D0). Subframe 0x0C byte 13 to subframe 0x0D byte  0. Humidity heater temperature calibration coefficient 20 (float32)
# Addresses 209 to 212 (0x0D1 to 0x0D4). Subframe 0x0D byte  1 to subframe 0x0D byte  4. Humidity heater temperature calibration coefficient 21 (float32)
# Addresses 213 to 216 (0x0D5 to 0x0D8). Subframe 0x0D byte  5 to subframe 0x0D byte  8. Humidity heater temperature calibration coefficient 22 (float32)
# Addresses 217 to 220 (0x0D9 to 0x0DC). Subframe 0x0D byte  9 to subframe 0x0D byte 12. Humidity heater temperature calibration coefficient 23 (float32)
# Addresses 221 to 224 (0x0DD to 0x0E0). Subframe 0x0D byte 13 to subframe 0x0E byte  0. Humidity heater temperature calibration coefficient 24 (float32)
# Addresses 225 to 228 (0x0E1 to 0x0E4). Subframe 0x0E byte  1 to subframe 0x0E byte  4. Humidity heater temperature calibration coefficient 25 (float32)
# Addresses 229 to 232 (0x0E5 to 0x0E8). Subframe 0x0E byte  5 to subframe 0x0E byte  8. Humidity heater temperature calibration coefficient 26 (float32)
# Addresses 233 to 236 (0x0E9 to 0x0EC). Subframe 0x0E byte  9 to subframe 0x0E byte 12. Humidity heater temperature calibration coefficient 27 (float32)
# Addresses 237 to 240 (0x0ED to 0x0F0). Subframe 0x0E byte 13 to subframe 0x0F byte  0. Humidity heater temperature calibration coefficient 28 (float32)
# Addresses 241 to 244 (0x0F1 to 0x0F4). Subframe 0x0F byte  1 to subframe 0x0F byte  4. Humidity heater temperature calibration coefficient 29 (float32)
# Addresses 245 to 248 (0x0F5 to 0x0F8). Subframe 0x0F byte  5 to subframe 0x0F byte  8. Humidity heater temperature calibration coefficient 30 (float32)
# Addresses 249 to 252 (0x0F9 to 0x0FC). Subframe 0x0F byte  9 to subframe 0x0F byte 12. Humidity heater temperature calibration coefficient 31 (float32)
# Addresses 253 to 256 (0x0FD to 0x100). Subframe 0x0F byte 13 to subframe 0x10 byte  0. Humidity heater temperature calibration coefficient 32 (float32)
# Addresses 257 to 260 (0x101 to 0x104). Subframe 0x10 byte  1 to subframe 0x10 byte  4. Humidity heater temperature calibration coefficient 33 (float32)
# Addresses 261 to 264 (0x105 to 0x108). Subframe 0x10 byte  5 to subframe 0x10 byte  8. Humidity heater temperature calibration coefficient 34 (float32)
# Addresses 265 to 268 (0x109 to 0x10C). Subframe 0x10 byte  9 to subframe 0x10 byte 12. Humidity heater temperature calibration coefficient 35 (float32)
# Addresses 269 to 272 (0x10D to 0x110). Subframe 0x10 byte 13 to subframe 0x11 byte  0. Humidity heater temperature calibration coefficient 36 (float32)
# Addresses 273 to 276 (0x111 to 0x114). Subframe 0x11 byte  1 to subframe 0x11 byte  4. Humidity heater temperature calibration coefficient 37 (float32)
# Addresses 277 to 280 (0x115 to 0x118). Subframe 0x11 byte  5 to subframe 0x11 byte  8. Humidity heater temperature calibration coefficient 38 (float32)
# Addresses 281 to 284 (0x119 to 0x11C). Subframe 0x11 byte  9 to subframe 0x11 byte 12. Humidity heater temperature calibration coefficient 39 (float32)
# Addresses 285 to 288 (0x11D to 0x120). Subframe 0x11 byte 13 to subframe 0x12 byte  0. Humidity heater temperature calibration coefficient 40 (float32)
# Addresses 289 to 292 (0x121 to 0x124). Subframe 0x12 byte  1 to subframe 0x12 byte  4. Humidity heater temperature calibration coefficient 41 (float32)
def GetHumHeaterTempCalCoeff(SubFrameArray):
    '''
    Get RS41 relative humidity heater calibration coefficients from RS41 subframes array
    '''
    HumHeaterTempCalCoeff = np.zeros(42)
    HumHeaterTempCalCoeff[ 0] = struct.unpack('<f', SubFrameArray[0x07D:0x081])[0]
    HumHeaterTempCalCoeff[ 1] = struct.unpack('<f', SubFrameArray[0x081:0x085])[0]
    HumHeaterTempCalCoeff[ 2] = struct.unpack('<f', SubFrameArray[0x085:0x089])[0]
    HumHeaterTempCalCoeff[ 3] = struct.unpack('<f', SubFrameArray[0x089:0x08D])[0]
    HumHeaterTempCalCoeff[ 4] = struct.unpack('<f', SubFrameArray[0x08D:0x091])[0]
    HumHeaterTempCalCoeff[ 5] = struct.unpack('<f', SubFrameArray[0x091:0x095])[0]
    HumHeaterTempCalCoeff[ 6] = struct.unpack('<f', SubFrameArray[0x095:0x099])[0]
    HumHeaterTempCalCoeff[ 7] = struct.unpack('<f', SubFrameArray[0x099:0x09D])[0]
    HumHeaterTempCalCoeff[ 8] = struct.unpack('<f', SubFrameArray[0x09D:0x0A1])[0]
    HumHeaterTempCalCoeff[ 9] = struct.unpack('<f', SubFrameArray[0x0A1:0x0A5])[0]
    HumHeaterTempCalCoeff[10] = struct.unpack('<f', SubFrameArray[0x0A5:0x0A9])[0]
    HumHeaterTempCalCoeff[11] = struct.unpack('<f', SubFrameArray[0x0A9:0x0AD])[0]
    HumHeaterTempCalCoeff[12] = struct.unpack('<f', SubFrameArray[0x0AD:0x0B1])[0]
    HumHeaterTempCalCoeff[13] = struct.unpack('<f', SubFrameArray[0x0B1:0x0B5])[0]
    HumHeaterTempCalCoeff[14] = struct.unpack('<f', SubFrameArray[0x0B5:0x0B9])[0]
    HumHeaterTempCalCoeff[15] = struct.unpack('<f', SubFrameArray[0x0B9:0x0BD])[0]
    HumHeaterTempCalCoeff[16] = struct.unpack('<f', SubFrameArray[0x0BD:0x0C1])[0]
    HumHeaterTempCalCoeff[17] = struct.unpack('<f', SubFrameArray[0x0C1:0x0C5])[0]
    HumHeaterTempCalCoeff[18] = struct.unpack('<f', SubFrameArray[0x0C5:0x0C9])[0]
    HumHeaterTempCalCoeff[19] = struct.unpack('<f', SubFrameArray[0x0C9:0x0CD])[0]
    HumHeaterTempCalCoeff[20] = struct.unpack('<f', SubFrameArray[0x0CD:0x0D1])[0]
    HumHeaterTempCalCoeff[21] = struct.unpack('<f', SubFrameArray[0x0D1:0x0D5])[0]
    HumHeaterTempCalCoeff[22] = struct.unpack('<f', SubFrameArray[0x0D5:0x0D9])[0]
    HumHeaterTempCalCoeff[23] = struct.unpack('<f', SubFrameArray[0x0D9:0x0DD])[0]
    HumHeaterTempCalCoeff[24] = struct.unpack('<f', SubFrameArray[0x0DD:0x0E1])[0]
    HumHeaterTempCalCoeff[25] = struct.unpack('<f', SubFrameArray[0x0E1:0x0E5])[0]
    HumHeaterTempCalCoeff[26] = struct.unpack('<f', SubFrameArray[0x0E5:0x0E9])[0]
    HumHeaterTempCalCoeff[27] = struct.unpack('<f', SubFrameArray[0x0E9:0x0ED])[0]
    HumHeaterTempCalCoeff[28] = struct.unpack('<f', SubFrameArray[0x0ED:0x0F1])[0]
    HumHeaterTempCalCoeff[29] = struct.unpack('<f', SubFrameArray[0x0F1:0x0F5])[0]
    HumHeaterTempCalCoeff[30] = struct.unpack('<f', SubFrameArray[0x0F5:0x0F9])[0]
    HumHeaterTempCalCoeff[31] = struct.unpack('<f', SubFrameArray[0x0F9:0x0FD])[0]
    HumHeaterTempCalCoeff[32] = struct.unpack('<f', SubFrameArray[0x0FD:0x101])[0]
    HumHeaterTempCalCoeff[33] = struct.unpack('<f', SubFrameArray[0x101:0x105])[0]
    HumHeaterTempCalCoeff[34] = struct.unpack('<f', SubFrameArray[0x105:0x109])[0]
    HumHeaterTempCalCoeff[35] = struct.unpack('<f', SubFrameArray[0x109:0x10D])[0]
    HumHeaterTempCalCoeff[36] = struct.unpack('<f', SubFrameArray[0x10D:0x111])[0]
    HumHeaterTempCalCoeff[37] = struct.unpack('<f', SubFrameArray[0x111:0x115])[0]
    HumHeaterTempCalCoeff[38] = struct.unpack('<f', SubFrameArray[0x115:0x119])[0]
    HumHeaterTempCalCoeff[39] = struct.unpack('<f', SubFrameArray[0x119:0x11D])[0]
    HumHeaterTempCalCoeff[40] = struct.unpack('<f', SubFrameArray[0x11D:0x121])[0]
    HumHeaterTempCalCoeff[41] = struct.unpack('<f', SubFrameArray[0x121:0x125])[0]
    return HumHeaterTempCalCoeff
def SetHumHeaterTempCalCoeff(HumHeaterTempCalCoeff, SubFrameArray):
    '''
    Set RS41 relative humidity heater calibration coefficients in RS41 subframes array
    '''
    SubFrameArray[0x07D:0x081] = struct.pack('<f', HumHeaterTempCalCoeff[ 0]) # '<f' -> little-endian
    SubFrameArray[0x081:0x085] = struct.pack('<f', HumHeaterTempCalCoeff[ 1]) # '<f' -> little-endian
    SubFrameArray[0x085:0x089] = struct.pack('<f', HumHeaterTempCalCoeff[ 2]) # '<f' -> little-endian
    SubFrameArray[0x089:0x08D] = struct.pack('<f', HumHeaterTempCalCoeff[ 3]) # '<f' -> little-endian
    SubFrameArray[0x08D:0x091] = struct.pack('<f', HumHeaterTempCalCoeff[ 4]) # '<f' -> little-endian
    SubFrameArray[0x091:0x095] = struct.pack('<f', HumHeaterTempCalCoeff[ 5]) # '<f' -> little-endian
    SubFrameArray[0x095:0x099] = struct.pack('<f', HumHeaterTempCalCoeff[ 6]) # '<f' -> little-endian
    SubFrameArray[0x099:0x09D] = struct.pack('<f', HumHeaterTempCalCoeff[ 7]) # '<f' -> little-endian
    SubFrameArray[0x09D:0x0A1] = struct.pack('<f', HumHeaterTempCalCoeff[ 8]) # '<f' -> little-endian
    SubFrameArray[0x0A1:0x0A5] = struct.pack('<f', HumHeaterTempCalCoeff[ 9]) # '<f' -> little-endian
    SubFrameArray[0x0A5:0x0A9] = struct.pack('<f', HumHeaterTempCalCoeff[10]) # '<f' -> little-endian
    SubFrameArray[0x0A9:0x0AD] = struct.pack('<f', HumHeaterTempCalCoeff[11]) # '<f' -> little-endian
    SubFrameArray[0x0AD:0x0B1] = struct.pack('<f', HumHeaterTempCalCoeff[12]) # '<f' -> little-endian
    SubFrameArray[0x0B1:0x0B5] = struct.pack('<f', HumHeaterTempCalCoeff[13]) # '<f' -> little-endian
    SubFrameArray[0x0B5:0x0B9] = struct.pack('<f', HumHeaterTempCalCoeff[14]) # '<f' -> little-endian
    SubFrameArray[0x0B9:0x0BD] = struct.pack('<f', HumHeaterTempCalCoeff[15]) # '<f' -> little-endian
    SubFrameArray[0x0BD:0x0C1] = struct.pack('<f', HumHeaterTempCalCoeff[16]) # '<f' -> little-endian
    SubFrameArray[0x0C1:0x0C5] = struct.pack('<f', HumHeaterTempCalCoeff[17]) # '<f' -> little-endian
    SubFrameArray[0x0C5:0x0C9] = struct.pack('<f', HumHeaterTempCalCoeff[18]) # '<f' -> little-endian
    SubFrameArray[0x0C9:0x0CD] = struct.pack('<f', HumHeaterTempCalCoeff[19]) # '<f' -> little-endian
    SubFrameArray[0x0CD:0x0D1] = struct.pack('<f', HumHeaterTempCalCoeff[20]) # '<f' -> little-endian
    SubFrameArray[0x0D1:0x0D5] = struct.pack('<f', HumHeaterTempCalCoeff[21]) # '<f' -> little-endian
    SubFrameArray[0x0D5:0x0D9] = struct.pack('<f', HumHeaterTempCalCoeff[22]) # '<f' -> little-endian
    SubFrameArray[0x0D9:0x0DD] = struct.pack('<f', HumHeaterTempCalCoeff[23]) # '<f' -> little-endian
    SubFrameArray[0x0DD:0x0E1] = struct.pack('<f', HumHeaterTempCalCoeff[24]) # '<f' -> little-endian
    SubFrameArray[0x0E1:0x0E5] = struct.pack('<f', HumHeaterTempCalCoeff[25]) # '<f' -> little-endian
    SubFrameArray[0x0E5:0x0E9] = struct.pack('<f', HumHeaterTempCalCoeff[26]) # '<f' -> little-endian
    SubFrameArray[0x0E9:0x0ED] = struct.pack('<f', HumHeaterTempCalCoeff[27]) # '<f' -> little-endian
    SubFrameArray[0x0ED:0x0F1] = struct.pack('<f', HumHeaterTempCalCoeff[28]) # '<f' -> little-endian
    SubFrameArray[0x0F1:0x0F5] = struct.pack('<f', HumHeaterTempCalCoeff[29]) # '<f' -> little-endian
    SubFrameArray[0x0F5:0x0F9] = struct.pack('<f', HumHeaterTempCalCoeff[30]) # '<f' -> little-endian
    SubFrameArray[0x0F9:0x0FD] = struct.pack('<f', HumHeaterTempCalCoeff[31]) # '<f' -> little-endian
    SubFrameArray[0x0FD:0x101] = struct.pack('<f', HumHeaterTempCalCoeff[32]) # '<f' -> little-endian
    SubFrameArray[0x101:0x105] = struct.pack('<f', HumHeaterTempCalCoeff[33]) # '<f' -> little-endian
    SubFrameArray[0x105:0x109] = struct.pack('<f', HumHeaterTempCalCoeff[34]) # '<f' -> little-endian
    SubFrameArray[0x109:0x10D] = struct.pack('<f', HumHeaterTempCalCoeff[35]) # '<f' -> little-endian
    SubFrameArray[0x10D:0x111] = struct.pack('<f', HumHeaterTempCalCoeff[36]) # '<f' -> little-endian
    SubFrameArray[0x111:0x115] = struct.pack('<f', HumHeaterTempCalCoeff[37]) # '<f' -> little-endian
    SubFrameArray[0x115:0x119] = struct.pack('<f', HumHeaterTempCalCoeff[38]) # '<f' -> little-endian
    SubFrameArray[0x119:0x11D] = struct.pack('<f', HumHeaterTempCalCoeff[39]) # '<f' -> little-endian
    SubFrameArray[0x11D:0x121] = struct.pack('<f', HumHeaterTempCalCoeff[40]) # '<f' -> little-endian
    SubFrameArray[0x121:0x125] = struct.pack('<f', HumHeaterTempCalCoeff[41]) # '<f' -> little-endian

# Addresses 293 to 296 (0x125 to 0x128). Subframe 0x12 byte  5 to subframe 0x12 byte  8. Heater temperature polynom coefficient 0 (float32)
# Addresses 297 to 300 (0x129 to 0x12C). Subframe 0x12 byte  9 to subframe 0x12 byte 12. Heater temperature polynom coefficient 1 (float32)
# Addresses 301 to 304 (0x12D to 0x130). Subframe 0x12 byte 13 to subframe 0x13 byte  0. Heater temperature polynom coefficient 2 (float32)
def GetHeaterTempPolCoeff(SubFrameArray):
    '''
    Get RS41 heater temperature polynom coefficients in RS41 subframes array
    '''
    HeaterTempPolCoeff = np.zeros(3)
    HeaterTempPolCoeff[0] = struct.unpack('<f', SubFrameArray[0x125:0x129])[0]
    HeaterTempPolCoeff[1] = struct.unpack('<f', SubFrameArray[0x129:0x12D])[0]
    HeaterTempPolCoeff[2] = struct.unpack('<f', SubFrameArray[0x12D:0x131])[0]
    return HeaterTempPolCoeff
def SetHeaterTempPolCoeff(HeaterTempPolCoeff, SubFrameArray):
    '''
    Set RS41 heater temperature polynom coefficients in RS41 subframes array
    '''
    SubFrameArray[0x125:0x129] = struct.pack('<f', HeaterTempPolCoeff[0]) # '<f' -> little-endian
    SubFrameArray[0x129:0x12D] = struct.pack('<f', HeaterTempPolCoeff[1]) # '<f' -> little-endian
    SubFrameArray[0x12D:0x131] = struct.pack('<f', HeaterTempPolCoeff[2]) # '<f' -> little-endian

# Addresses 305 to 308 (0x131 to 0x134). Subframe 0x13 byte  1 to subframe 0x13 byte  4. Heater temperature calibration coefficient 0 (float32)
# Addresses 309 to 312 (0x135 to 0x138). Subframe 0x13 byte  5 to subframe 0x13 byte  8. Heater temperature calibration coefficient 1 (float32)
# Addresses 313 to 316 (0x139 to 0x13C). Subframe 0x13 byte  9 to subframe 0x13 byte 12. Heater temperature calibration coefficient 2 (float32)
def GetHeaterTempCalCoeff(SubFrameArray):
    '''
    Get RS41 heater temperature calibration coefficients in RS41 subframes array
    '''
    HeaterTempCalCoeff = np.zeros(3)
    HeaterTempCalCoeff[0] = struct.unpack('<f', SubFrameArray[0x131:0x135])[0]
    HeaterTempCalCoeff[1] = struct.unpack('<f', SubFrameArray[0x135:0x139])[0]
    HeaterTempCalCoeff[2] = struct.unpack('<f', SubFrameArray[0x139:0x13D])[0]
    return HeaterTempCalCoeff
def SetHeaterTempCalCoeff(HeaterTempCalCoeff, SubFrameArray):
    '''
    Set RS41 heater temperature calibration coefficients in RS41 subframes array
    '''
    SubFrameArray[0x131:0x135] = struct.pack('<f', HeaterTempCalCoeff[0]) # '<f' -> little-endian
    SubFrameArray[0x135:0x139] = struct.pack('<f', HeaterTempCalCoeff[1]) # '<f' -> little-endian
    SubFrameArray[0x139:0x13D] = struct.pack('<f', HeaterTempCalCoeff[2]) # '<f' -> little-endian

# Addresses 317 to 535 (0x13D to 0x217). Subframe 0x13 byte 13 to subframe 0x21 byte  7. Purpose unknown.
# Addresses 536 to 545 (0x218 to 0x221). Subframe 0x21 byte  8 to subframe 0x22 byte  1. RS41 model (char[10])
def GetRS41Model(SubFrameArray):
    '''
    Get RS41 model string from RS41 subframes array
    '''
    RS41Model = SubFrameArray[0x218:0x222].decode("utf-8")
    return RS41Model
def SetRS41Model(RS41Model, SubFrameArray):
    '''
    Set RS41 model string in RS41 subframes array
    '''
    RS41ModelBytes = bytes(RS41Model,'UTF-8')
    if len(RS41ModelBytes) < 10:
        RS41ModelBytes = RS41ModelBytes + bytes(10-len(RS41ModelBytes))
    SubFrameArray[0x218:0x222] = RS41ModelBytes[0:0xA]

# Addresses 546 to 555 (0x222 to 0x22B). Subframe 0x22 byte  2 to subframe 0x22 byte 11. Mainboard type (char[10])
def GetMainboardType(SubFrameArray):
    '''
    Get RS41 mainboard type string from RS41 subframes array
    '''
    MainboardType = SubFrameArray[0x222:0x22C].decode("utf-8")
    return MainboardType
def SetMainboardType(MainboardType, SubFrameArray):
    '''
    Set RS41 mainboard type string in RS41 subframes array
    '''
    MainboardTypeBytes = bytes(MainboardType,'UTF-8')
    if len(MainboardTypeBytes) < 10:
        MainboardTypeBytes = MainboardTypeBytes + bytes(10-len(MainboardTypeBytes))
    SubFrameArray[0x222:0x22C] = MainboardTypeBytes[0:0xA]

# Addresses 556 to 564 (0x22C to 0x234). Subframe 0x22 byte 12 to subframe 0x23 byte  4. Mainboard serial (char[9])
def GetMainboardSerial(SubFrameArray):
    '''
    Get RS41 mainboard serial number string from RS41 subframes array
    '''
    MainboardSerial = SubFrameArray[0x22C:0x235].decode("utf-8")
    return MainboardSerial
def SetMainboardSerial(MainboardSerial, SubFrameArray):
    '''
    Set RS41 mainboard serial number string in RS41 subframes array
    '''
    MainboardSerialBytes = bytes(MainboardSerial,'UTF-8')
    if len(MainboardSerialBytes) < 9:
        MainboardSerialBytes = MainboardSerialBytes + bytes(9-len(MainboardSerialBytes))
    SubFrameArray[0x22C:0x235] = MainboardSerialBytes[0:0x9]

# Addresses 565 to 578 (0x235 to 0x242). Subframe 0x23 byte  5 to subframe 0x24 byte  2. Purpose unknown.

# Addresses 579 to 588 (0x243 to 0x24B). Subframe 0x24 byte  3 to subframe 0x24 byte  3. Mainboard serial (char[9])
def GetPressureSerial(SubFrameArray):
    '''
    Get RS41 pressure sensor serial number string from RS41 subframes array
    '''
    PressureSerial = SubFrameArray[0x243:0x24C].decode("utf-8")
    return PressureSerial
def SetPressureSerial(PressureSerial, SubFrameArray):
    '''
    Set RS41 pressure sensor serial number string in RS41 subframes array
    '''
    PressureSerialBytes = bytes(PressureSerial,'UTF-8')
    if len(PressureSerialBytes) < 9:
        PressureSerialBytes = PressureSerialBytes + bytes(9-len(PressureSerialBytes))
    SubFrameArray[0x243:0x24C] = PressureSerialBytes[0:0x9]

# Addresses 589 to 605 (0x24C to 0x25D). Subframe 0x24 byte 12 to subframe 0x25 byte 13. Purpose unknown.

# Addresses 606 to 609 (0x25E to 0x261). Subframe 0x25 byte 14 to subframe 0x26 byte  1. Pressure calibration coefficient 0 (float32)
# Addresses 610 to 613 (0x262 to 0x265). Subframe 0x26 byte  2 to subframe 0x26 byte  5. Pressure calibration coefficient 4 (float32)
# Addresses 614 to 617 (0x266 to 0x269). Subframe 0x26 byte  6 to subframe 0x26 byte  9. Pressure calibration coefficient 8 (float32)
# Addresses 618 to 621 (0x26A to 0x26D). Subframe 0x26 byte 10 to subframe 0x26 byte 13. Pressure calibration coefficient 12 (float32)
# Addresses 622 to 625 (0x26E to 0x271). Subframe 0x26 byte 14 to subframe 0x27 byte  1. Pressure calibration coefficient 16 (float32)
# Addresses 626 to 629 (0x272 to 0x275). Subframe 0x27 byte  2 to subframe 0x27 byte  5. Pressure calibration coefficient 20 (float32)
# Addresses 630 to 633 (0x276 to 0x279). Subframe 0x27 byte  6 to subframe 0x27 byte  9. Pressure calibration coefficient 24 (float32)
# Addresses 634 to 637 (0x27A to 0x27D). Subframe 0x27 byte 10 to subframe 0x27 byte 13. Pressure calibration coefficient 1 (float32)
# Addresses 638 to 641 (0x27E to 0x281). Subframe 0x27 byte 14 to subframe 0x28 byte  1. Pressure calibration coefficient 5 (float32)
# Addresses 642 to 645 (0x282 to 0x285). Subframe 0x28 byte  2 to subframe 0x28 byte  5. Pressure calibration coefficient 9 (float32)
# Addresses 646 to 649 (0x286 to 0x289). Subframe 0x28 byte  6 to subframe 0x28 byte  9. Pressure calibration coefficient 13 (float32)
# Addresses 650 to 653 (0x28A to 0x28D). Subframe 0x28 byte 10 to subframe 0x28 byte 13. Pressure calibration coefficient 2 (float32)
# Addresses 654 to 657 (0x28E to 0x291). Subframe 0x28 byte 14 to subframe 0x29 byte  1. Pressure calibration coefficient 6 (float32)
# Addresses 658 to 661 (0x292 to 0x295). Subframe 0x29 byte  2 to subframe 0x29 byte  5. Pressure calibration coefficient 10 (float32)
# Addresses 662 to 665 (0x296 to 0x299). Subframe 0x29 byte  6 to subframe 0x29 byte  9. Pressure calibration coefficient 14 (float32)
# Addresses 666 to 669 (0x29A to 0x29D). Subframe 0x29 byte 10 to subframe 0x29 byte 13. Pressure calibration coefficient 3 (float32)
# Addresses 670 to 673 (0x29E to 0x2A1). Subframe 0x29 byte 14 to subframe 0x2A byte  1. Pressure calibration coefficient 7 (float32)
# Addresses 674 to 677 (0x2A2 to 0x2A5). Subframe 0x2A byte  2 to subframe 0x2A byte  5. Pressure calibration coefficient 11 (float32)
def GetPressureCalCoeff(SubFrameArray):
    '''
    Get RS41 ambient pressure calibration coefficients in RS41 subframes array
    '''
    PressureCalCoeff = np.zeros(25)
    PressureCalCoeff[ 0] = struct.unpack('<f', SubFrameArray[0x25E:0x262])[0]
    PressureCalCoeff[ 4] = struct.unpack('<f', SubFrameArray[0x262:0x266])[0]
    PressureCalCoeff[ 8] = struct.unpack('<f', SubFrameArray[0x266:0x26A])[0]
    PressureCalCoeff[12] = struct.unpack('<f', SubFrameArray[0x26A:0x26E])[0]
    PressureCalCoeff[16] = struct.unpack('<f', SubFrameArray[0x26E:0x272])[0]
    PressureCalCoeff[20] = struct.unpack('<f', SubFrameArray[0x272:0x276])[0]
    PressureCalCoeff[24] = struct.unpack('<f', SubFrameArray[0x276:0x27A])[0]
    PressureCalCoeff[ 1] = struct.unpack('<f', SubFrameArray[0x27A:0x27E])[0]
    PressureCalCoeff[ 5] = struct.unpack('<f', SubFrameArray[0x27E:0x282])[0]
    PressureCalCoeff[ 9] = struct.unpack('<f', SubFrameArray[0x282:0x286])[0]
    PressureCalCoeff[13] = struct.unpack('<f', SubFrameArray[0x286:0x28A])[0]
    PressureCalCoeff[ 2] = struct.unpack('<f', SubFrameArray[0x28A:0x28E])[0]
    PressureCalCoeff[ 6] = struct.unpack('<f', SubFrameArray[0x28E:0x292])[0]
    PressureCalCoeff[10] = struct.unpack('<f', SubFrameArray[0x292:0x296])[0]
    PressureCalCoeff[14] = struct.unpack('<f', SubFrameArray[0x296:0x29A])[0]
    PressureCalCoeff[ 3] = struct.unpack('<f', SubFrameArray[0x29A:0x29E])[0]
    PressureCalCoeff[ 7] = struct.unpack('<f', SubFrameArray[0x29E:0x2A2])[0]
    PressureCalCoeff[11] = struct.unpack('<f', SubFrameArray[0x2A2:0x2A6])[0]
    return PressureCalCoeff

def SetPressureCalCoeff(PressureCalCoeff, SubFrameArray):
    '''
    Set RS41 ambient pressure calibration coefficients in RS41 subframes array
    '''
    SubFrameArray[0x25E:0x262] = struct.pack('<f', PressureCalCoeff[ 0]) # '<f' -> little-endian
    SubFrameArray[0x262:0x266] = struct.pack('<f', PressureCalCoeff[ 4]) # '<f' -> little-endian
    SubFrameArray[0x266:0x26A] = struct.pack('<f', PressureCalCoeff[ 8]) # '<f' -> little-endian
    SubFrameArray[0x26A:0x26E] = struct.pack('<f', PressureCalCoeff[12]) # '<f' -> little-endian
    SubFrameArray[0x26E:0x272] = struct.pack('<f', PressureCalCoeff[16]) # '<f' -> little-endian
    SubFrameArray[0x272:0x276] = struct.pack('<f', PressureCalCoeff[20]) # '<f' -> little-endian
    SubFrameArray[0x276:0x27A] = struct.pack('<f', PressureCalCoeff[24]) # '<f' -> little-endian
    SubFrameArray[0x27A:0x27E] = struct.pack('<f', PressureCalCoeff[ 1]) # '<f' -> little-endian
    SubFrameArray[0x27E:0x282] = struct.pack('<f', PressureCalCoeff[ 5]) # '<f' -> little-endian
    SubFrameArray[0x282:0x286] = struct.pack('<f', PressureCalCoeff[ 9]) # '<f' -> little-endian
    SubFrameArray[0x286:0x28A] = struct.pack('<f', PressureCalCoeff[13]) # '<f' -> little-endian
    SubFrameArray[0x28A:0x28E] = struct.pack('<f', PressureCalCoeff[ 2]) # '<f' -> little-endian
    SubFrameArray[0x28E:0x292] = struct.pack('<f', PressureCalCoeff[ 6]) # '<f' -> little-endian
    SubFrameArray[0x292:0x296] = struct.pack('<f', PressureCalCoeff[10]) # '<f' -> little-endian
    SubFrameArray[0x296:0x29A] = struct.pack('<f', PressureCalCoeff[14]) # '<f' -> little-endian
    SubFrameArray[0x29A:0x29E] = struct.pack('<f', PressureCalCoeff[ 3]) # '<f' -> little-endian
    SubFrameArray[0x29E:0x2A2] = struct.pack('<f', PressureCalCoeff[ 7]) # '<f' -> little-endian
    SubFrameArray[0x2A2:0x2A6] = struct.pack('<f', PressureCalCoeff[11]) # '<f' -> little-endian

# Addresses 678 to 681 (0x2A6 to 0x2A9). Subframe 0x2A byte  6 to subframe 0x2A byte  9. Humidity capacitance pressure correction coefficient 0 (float32)
# Addresses 682 to 685 (0x2AA to 0x2AD). Subframe 0x2A byte 10 to subframe 0x2A byte 13. Humidity capacitance pressure correction coefficient 1 (float32)
# Addresses 686 to 689 (0x2AE to 0x2B1). Subframe 0x2A byte 14 to subframe 0x2B byte  1. Humidity capacitance pressure correction coefficient 2 (float32)
def GetHumCPressureCalCoeff(SubFrameArray):
    '''
    Get RS41 relative humidity capacitance pressure correction coefficients in RS41 subframes array
    '''
    HumCPressureCalCoeff = np.zeros(3)
    HumCPressureCalCoeff[0] = struct.unpack('<f', SubFrameArray[0x2A6:0x2AA])[0]
    HumCPressureCalCoeff[1] = struct.unpack('<f', SubFrameArray[0x2AA:0x2AE])[0]
    HumCPressureCalCoeff[2] = struct.unpack('<f', SubFrameArray[0x2AE:0x2B2])[0]
    return HumCPressureCalCoeff
def SetHumCPressureCalCoeff(HumCPressureCalCoeff, SubFrameArray):
    '''
    Set RS41 relative humidity capacitance pressure correction coefficients in RS41 subframes array
    '''
    SubFrameArray[0x2A6:0x2AA] = struct.pack('<f', HumCPressureCalCoeff[0]) # '<f' -> little-endian
    SubFrameArray[0x2AA:0x2AE] = struct.pack('<f', HumCPressureCalCoeff[1]) # '<f' -> little-endian
    SubFrameArray[0x2AE:0x2B2] = struct.pack('<f', HumCPressureCalCoeff[2]) # '<f' -> little-endian

# Addresses 690 to 697 (0x2B2 to 0x2B9). Subframe 0x2B byte  2 to subframe 0x2B byte  9. Purpose unknown.

# Addresses 698 to 701 (0x2BA to 0x2BD). Subframe 0x2B byte 10 to subframe 0x2B byte 13. Humidity capacitance pressure-temperature correction coefficient 0 (float32)
# Addresses 702 to 705 (0x2BE to 0x2C1). Subframe 0x2B byte 14 to subframe 0x2C byte  1. Humidity capacitance pressure-temperature correction coefficient 1 (float32)
# Addresses 706 to 709 (0x2C2 to 0x2C5). Subframe 0x2C byte  2 to subframe 0x2C byte  5. Humidity capacitance pressure-temperature correction coefficient 2 (float32)
# Addresses 710 to 713 (0x2C6 to 0x2C9). Subframe 0x2C byte  6 to subframe 0x2C byte  9. Humidity capacitance pressure-temperature correction coefficient 3 (float32)
# Addresses 714 to 717 (0x2CA to 0x2CD). Subframe 0x2C byte 10 to subframe 0x2C byte 13. Humidity capacitance pressure-temperature correction coefficient 4 (float32)
# Addresses 718 to 721 (0x2CE to 0x2D1). Subframe 0x2C byte 14 to subframe 0x2D byte  1. Humidity capacitance pressure-temperature correction coefficient 5 (float32)
# Addresses 722 to 725 (0x2D2 to 0x2D5). Subframe 0x2D byte  2 to subframe 0x2D byte  5. Humidity capacitance pressure-temperature correction coefficient 6 (float32)
# Addresses 726 to 729 (0x2D6 to 0x2D9). Subframe 0x2D byte  6 to subframe 0x2D byte  9. Humidity capacitance pressure-temperature correction coefficient 7 (float32)
# Addresses 730 to 733 (0x2DA to 0x2DD). Subframe 0x2D byte 10 to subframe 0x2D byte 13. Humidity capacitance pressure-temperature correction coefficient 8 (float32)
# Addresses 734 to 737 (0x2DE to 0x2E1). Subframe 0x2D byte 14 to subframe 0x2E byte  1. Humidity capacitance pressure-temperature correction coefficient 9 (float32)
# Addresses 738 to 741 (0x2E2 to 0x2E5). Subframe 0x2E byte  2 to subframe 0x2E byte  5. Humidity capacitance pressure-temperature correction coefficient 10 (float32)
# Addresses 742 to 745 (0x2E6 to 0x2E9). Subframe 0x2E byte  6 to subframe 0x2E byte  9. Humidity capacitance pressure-temperature correction coefficient 11 (float32)
def GetHumCPressureTempCalCoeff(SubFrameArray):
    '''
    Get RS41 relative humidity capacitance pressure-temperature correction coefficients in RS41 subframes array
    '''
    HumCPressureTempCalCoeff = np.zeros(12)
    HumCPressureTempCalCoeff[ 0] = struct.unpack('<f', SubFrameArray[0x2BA:0x2BE])[0]
    HumCPressureTempCalCoeff[ 1] = struct.unpack('<f', SubFrameArray[0x2BE:0x2C2])[0]
    HumCPressureTempCalCoeff[ 2] = struct.unpack('<f', SubFrameArray[0x2C2:0x2C6])[0]
    HumCPressureTempCalCoeff[ 3] = struct.unpack('<f', SubFrameArray[0x2C6:0x2CA])[0]
    HumCPressureTempCalCoeff[ 4] = struct.unpack('<f', SubFrameArray[0x2CA:0x2CE])[0]
    HumCPressureTempCalCoeff[ 5] = struct.unpack('<f', SubFrameArray[0x2CE:0x2D2])[0]
    HumCPressureTempCalCoeff[ 6] = struct.unpack('<f', SubFrameArray[0x2D2:0x2D6])[0]
    HumCPressureTempCalCoeff[ 7] = struct.unpack('<f', SubFrameArray[0x2D6:0x2DA])[0]
    HumCPressureTempCalCoeff[ 8] = struct.unpack('<f', SubFrameArray[0x2DA:0x2DE])[0]
    HumCPressureTempCalCoeff[ 9] = struct.unpack('<f', SubFrameArray[0x2DE:0x2E2])[0]
    HumCPressureTempCalCoeff[10] = struct.unpack('<f', SubFrameArray[0x2E2:0x2E6])[0]
    HumCPressureTempCalCoeff[11] = struct.unpack('<f', SubFrameArray[0x2E6:0x2EA])[0]
    return HumCPressureTempCalCoeff
def SetHumCPressureTempCalCoeff(HumCPressureTempCalCoeff, SubFrameArray):
    '''
    Set RS41 relative humidity capacitance pressure-temperature correction coefficients in RS41 subframes array
    '''
    SubFrameArray[0x2BA:0x2BE] = struct.pack('<f', HumCPressureTempCalCoeff[0]) # '<f' -> little-endian
    SubFrameArray[0x2BE:0x2C2] = struct.pack('<f', HumCPressureTempCalCoeff[1]) # '<f' -> little-endian
    SubFrameArray[0x2C2:0x2C6] = struct.pack('<f', HumCPressureTempCalCoeff[2]) # '<f' -> little-endian
    SubFrameArray[0x2C6:0x2CA] = struct.pack('<f', HumCPressureTempCalCoeff[3]) # '<f' -> little-endian
    SubFrameArray[0x2CA:0x2CE] = struct.pack('<f', HumCPressureTempCalCoeff[4]) # '<f' -> little-endian
    SubFrameArray[0x2CE:0x2D2] = struct.pack('<f', HumCPressureTempCalCoeff[5]) # '<f' -> little-endian
    SubFrameArray[0x2D2:0x2D6] = struct.pack('<f', HumCPressureTempCalCoeff[6]) # '<f' -> little-endian
    SubFrameArray[0x2D6:0x2DA] = struct.pack('<f', HumCPressureTempCalCoeff[7]) # '<f' -> little-endian
    SubFrameArray[0x2DA:0x2DE] = struct.pack('<f', HumCPressureTempCalCoeff[8]) # '<f' -> little-endian
    SubFrameArray[0x2DE:0x2E2] = struct.pack('<f', HumCPressureTempCalCoeff[9]) # '<f' -> little-endian
    SubFrameArray[0x2E2:0x2E6] = struct.pack('<f', HumCPressureTempCalCoeff[10]) # '<f' -> little-endian
    SubFrameArray[0x2E6:0x2EA] = struct.pack('<f', HumCPressureTempCalCoeff[11]) # '<f' -> little-endian
    
# Addresses 746 to 789 (0x2EA to 0x315). Subframe 0x2E byte 10 to subframe 0x31 byte  5. Purpose unknown.

# Addresses 790 to 791 (0x316 to 0x317). Subframe 0x31 byte  6 to subframe 0x31 byte  7. Predefined total burstkill timer duration (uint16)
def GetBurstKillTimerDuration(SubFrameArray):
    '''
    Get RS41 predefined total burstkill timer duration from RS41 subframes array
    '''
    BurstKillTimerDuration = int.from_bytes(SubFrameArray[0x316:0x318],byteorder='little')
    return BurstKillTimerDuration
def SetBurstKillTimerDuration(BurstKillTimerDuration, SubFrameArray):
    '''
    Set RS41 predefined total burstkill timer duration in RS41 subframes array
    '''
    SubFrameArray[0x316:0x318] = BurstKillTimerDuration.to_bytes(2,byteorder='little')

# Addresses 792 to 799 (0x318 to 0x31F). Subframe 0x31 byte  8 to subframe 0x31 byte 15. Purpose unknown.

# Addresses 800 to 801 (0x320 to 0x321). Subframe 0x32 byte  0 to subframe 0x32 byte  1. Current burstkill time to kill (uint16)
def GetBurstKillTimeUntilKill(SubFrameArray):
    '''
    Get RS41 current burstkill time to kill from RS41 subframes array
    '''
    BurstKillTimeUntilKill = int.from_bytes(SubFrameArray[0x320:0x322],byteorder='little', signed=True)
    return BurstKillTimeUntilKill
def SetBurstKillTimeUntilKill(BurstKillTimeUntilKill, SubFrameArray):
    '''
    Set RS41 current burstkill time to kill in RS41 subframes array
    '''
    SubFrameArray[0x320:0x322] = BurstKillTimeUntilKill.to_bytes(2,byteorder='little', signed=True)

# Addresses 802 to 803 (0x322 to 0x323). Subframe 0x32 byte  2 to subframe 0x32 byte  3. launch altitude, referenced to spherical earth model (R=6371.008 km) [m] (uint16)
def GetLaunchSiteEarthRadius(SubFrameArray):
    '''
    Get RS41 launch altitude, referenced to spherical earth model from RS41 subframes array
    '''
    LaunchSiteEarthRadius = int.from_bytes(SubFrameArray[0x322:0x324],byteorder='little', signed=True) + 6371008
    return LaunchSiteEarthRadius
def SetLaunchSiteEarthRadius(LaunchSiteEarthRadius, SubFrameArray):
    '''
    Set RS41 launch altitude, referenced to spherical earth model in RS41 subframes array
    '''
    SubFrameArray[0x322:0x324] = int(LaunchSiteEarthRadius - 6371008).to_bytes(2,byteorder='little', signed=True)

# Addresses 804 to 805 (0x324 to 0x325). Subframe 0x32 byte  4 to subframe 0x32 byte  5. Height above launch site where transition to flight mode happened [m] (uint16)
def GetFlightModeAltitudeAboveLaunch(SubFrameArray):
    '''
    Get RS41 height above launch site where transition to flight mode happened from RS41 subframes array
    '''
    FlightModeAltitudeAboveLaunch = int.from_bytes(SubFrameArray[0x324:0x326],byteorder='little')
    return FlightModeAltitudeAboveLaunch
def SetFlightModeAltitudeAboveLaunch(FlightModeAltitudeAboveLaunch, SubFrameArray):
    '''
    Set RS41 height above launch site where transition to flight mode happened in RS41 subframes array
    '''
    SubFrameArray[0x324:0x326] = FlightModeAltitudeAboveLaunch.to_bytes(2,byteorder='little')

# Address   806        (0x326).          Subframe 0x32 byte  6. Tx Power 2 - 0 to 7. 0 = Minimum power, 7 = Maximum power (uint8)
def GetTxPower2(SubFrameArray):
    '''
    Get RS41 transmission power 2 from RS41 subframes array
    '''
    TxPower2 = int(SubFrameArray[0x326])
    return TxPower2
def SetTxPower2(TxPower2, SubFrameArray):
    '''
    Set RS41 transmission power 2 in RS41 subframes array
    '''
    SubFrameArray[0x326] = TxPower2

# Address   807        (0x327).          Subframe 0x32 byte  7. Number of software resets (uint8)
def GetSoftwareResets(SubFrameArray):
    '''
    Get RS41 number of software resets from RS41 subframes array
    '''
    SoftwareResets = int(SubFrameArray[0x327])
    return SoftwareResets
def SetSoftwareResets(SoftwareResets, SubFrameArray):
    '''
    Set RS41 number of software resets in RS41 subframes array
    '''
    SubFrameArray[0x327] = SoftwareResets

# Address   808        (0x328).          Subframe 0x32 byte  8. CPU temperature [Degrees Celsius] (int8)
def GetCPUTemperature(SubFrameArray):
    '''
    Get RS41 CPU temperature from RS41 subframes array
    '''
    CPUTemperature = int.from_bytes(SubFrameArray[0x328:0x329],byteorder='little', signed=True)
    return CPUTemperature
def SetCPUTemperature(CPUTemperature, SubFrameArray):
    '''
    Set RS41 CPU temperature in RS41 subframes array
    '''
    SubFrameArray[0x328:0x329] = CPUTemperature.to_bytes(1,byteorder='little', signed=True)

# Address   809        (0x329).          Subframe 0x32 byte  9. Radio chip temperature [Degrees Celsius] (int8)
def GetRadioTemperature(SubFrameArray):
    '''
    Get RS41 radio chip temperature from RS41 subframes array
    '''
    RadioTemperature = int.from_bytes(SubFrameArray[0x329:0x32A],byteorder='little', signed=True)
    return RadioTemperature
def SetRadioTemperature(RadioTemperature, SubFrameArray):
    '''
    Set RS41 radio chip temperature in RS41 subframes array
    '''
    SubFrameArray[0x329:0x32A] = RadioTemperature.to_bytes(1,byteorder='little', signed=True)

# Addresses 810 to 811 (0x32A to 0x32B). Subframe 0x32 byte 10 to subframe 0x32 byte 11. Remaining battery capacity [10mAh] (uint16)
def GetRemainingBatteryCapacity(SubFrameArray):
    '''
    Get RS41 remaining battery capacity from RS41 subframes array
    '''
    RemainingBatteryCapacity = 10 * int.from_bytes(SubFrameArray[0x32A:0x32C],byteorder='little', signed=True)
    return RemainingBatteryCapacity
def SetRemainingBatteryCapacity(RemainingBatteryCapacity, SubFrameArray):
    '''
    Set RS41 remaining battery capacity in RS41 subframes array
    '''
    SubFrameArray[0x32A:0x32C] = int(RemainingBatteryCapacity / 10).to_bytes(2,byteorder='little', signed=True)

# Address   812        (0x32C).          Subframe 0x32 byte 12. Number of discarded UBX (GPS) packets (uint8)
def GetDiscardedUBXPackets(SubFrameArray):
    '''
    Get RS41 number of discarded UBX (GPS) packets from RS41 subframes array
    '''
    DiscardedUBXPackets = int(SubFrameArray[0x32C])
    return DiscardedUBXPackets
def SetDiscardedUBXPackets(DiscardedUBXPackets, SubFrameArray):
    '''
    Set RS41 number of discarded UBX (GPS) packets in RS41 subframes array
    '''
    SubFrameArray[0x32C] = DiscardedUBXPackets

# Address   813        (0x32D).          Subframe 0x32 byte 13. Number of occasions when essential UBX (GPS) packets were missing (uint8)
def GetUBXPacketsMissing(SubFrameArray):
    '''
    Get RS41 number of occasions when essential UBX (GPS) packets were missing from RS41 subframes array
    '''
    UBXPacketsMissing = int(SubFrameArray[0x32D])
    return UBXPacketsMissing
def SetUBXPacketsMissing(UBXPacketsMissing, SubFrameArray):
    '''
    Set RS41 number of occasions when essential UBX (GPS) packets were missing in RS41 subframes array
    '''
    SubFrameArray[0x32D] = UBXPacketsMissing

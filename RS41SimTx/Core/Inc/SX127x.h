#ifndef __SX127X_H__
#define __SX127X_H__

 // Common settings
#define REG_FS_OPMODE                                0x01
#define REG_FS_BRMSB                                 0x02
#define REG_FS_BRLSB                                 0x03
#define REG_FS_FDEVMSB                               0x04
#define REG_FS_FDEVLSB                               0x05
#define REG_FS_FRFMSB                                0x06
#define REG_FS_FRFMID                                0x07
#define REG_FS_FRFLSB                                0x08
 // Tx settings
#define REG_FS_PARAMP                                0x0A
#define REG_FS_PACONFIG                              0x09
#define REG_FS_PARAMP                                0x0A
#define REG_FS_OCP                                   0x0B
 // Rx settings
#define REG_LR_LNA                                   0x0C 
 // FSK registers
#define REG_FS_PREAMBLEMSB                           0x25
#define REG_FS_PREAMBLELSB                           0x26
#define REG_FS_SYNCCONFIG                            0x27
#define REG_FS_PACKETCONFIG1                         0x30
#define REG_FS_PACKETCONFIG2                         0x31
#define REG_FS_PALOADLENGTHLSB                       0x32
#define REG_FS_FIFOTHRESH                            0x35
#define REG_FS_IRQFLAGS1                             0x3E
#define REG_FS_IRQFLAGS2                             0x3F
 // end of documented register in datasheet
 // I/O settings
#define REG_FS_DIOMAPPING1                           0x40
#define REG_FS_DIOMAPPING2                           0x41
 // Additional settings
#define REG_FS_PADAC                                 0x4D
#define REG_FS_BITRATEFRAC                           0x5D
// FIFO
#define FIFO_THRESHOLD								   32
#define FIFO_DATA_CHUNKS							   32

#define GPIO_VARE_1                                  0X00
#define GPIO_VARE_2                                  0X00

#define RFFS_SYNCCONFIG_SYNC_ON_MASK                 0x10

#define RFFS_PACKETCONFIG1_PACKET_FORMAT_MASK        0x80
#define RFFS_PACKETCONFIG1_DC_FREE_MASK              0x60
#define RFFS_PACKETCONFIG1_CRC_ON_MASK               0x10
#define RFFS_PACKETCONFIG1_CRC_CLEAR_MASK            0x08
#define RFFS_PACKETCONFIG1_ADDR_FILTER_MASK          0x06
#define RFFS_PACKETCONFIG1_WHITINING_MASK            0x01

#define RFFS_FIFO_THRESHOLD_MASK                     0x1F

#define RFFS_PACKETCONFIG2_PAYLOAD_LENGTH_MASK       0x07

#define RFFS_PARAMP_DATA_SHAPING_MASK				 0X60

#define FS_IRQN_TXD_Value                            0x08
#define FS_IRQN_FIFO_LEVEL_Value                     0x20
#define FS_IRQN_FIFO_EMPTY_Value                     0x40

#define FXOSC                                        32000000 // 32.0 MHz
#define FSTEP										 61 // FXOSC / 2^19

// Structure to define the metadata from the incoming message from the PC
typedef struct
{
    uint16_t NumOfBytes;          // Holds the number of bytes in the packet received from the PC
    uint32_t FrequencyStart;      // Frequency in Hz
    uint32_t DataRate;            // Data rate in BAUD
    uint32_t FrequencyDeviation;  // Frequency deviation in Hz
    uint8_t  GaussianMode;        // 0 = no shaping, 			    1 = Gaussian filter BT = 1.0,
	  	  	  	  	  	  	  	  // 2 = Gaussian filter BT = 0.5,  3 = Gaussian filter BT = 0.3
    int8_t   Power;               // Output power in dBm:  Supports -3dBm to +16dBm, +20dBm
} MetaDataStruct;

typedef enum 
{
   Sleep_mode	        = (unsigned char)0x00, 
   Stdby_mode	        = (unsigned char)0x01, 
   TX_mode 	       	  = (unsigned char)0x02,
   Transmitter_mode		= (unsigned char)0x03,
   RF_mode 		   			= (unsigned char)0x04,
   Receiver_mode			= (unsigned char)0x05,
   receive_single			= (unsigned char)0x06,
   CAD_mode						= (unsigned char)0x07,
}RFMode_SET;

typedef enum
{
   FSK_mode           = (unsigned char)0x00, 
   LORA_mode          = (unsigned char)0x80, 
}  Debugging_fsk_ook;

typedef enum{false=0,true=1}BOOL_t;

typedef enum{enOpen,enClose}cmdEntype_t;

void gByteWritefunc(unsigned char buffer);
unsigned char gByteReadfunc(void);
void SX127xWriteBuffer( unsigned char addr, unsigned char buffer);
unsigned char SX127xReadBuffer(unsigned char addr);
void SX127xReset(void);//1278��λ
void SX127xFSKSetOpMode( RFMode_SET opMode );
int SX127xFSKGetOpMode();
void SX127xFSKSetRFFrequency(unsigned int TxFrequency);
void SX127xFSKSetGaussianMode(unsigned char GaussianMode );
void SX127xFSKSetFIFOThreshold(unsigned char FIFOThreshold );
void SX127xFSKSetRFPower(signed char power);
void SX127xFSKSetSyncOn(BOOL_t enable );
void SX127xFSKSetPacketFormat(BOOL_t enable );
void SX127xFSKSetCrcOn(BOOL_t enable );
void SX127xFSKSetPreambleSize(unsigned int PreambleSize);
void SX127xFSK_INT(MetaDataStruct SetupData);
void SX127xFSKSetPayloadLength(unsigned int PayloadLength );
void FUN_RF_SENDPACKET(unsigned char *RF_TRAN_P,unsigned char LEN);

extern unsigned char   Frequency[];

#endif


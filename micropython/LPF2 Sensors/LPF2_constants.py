#https://github.com/pybricks/technical-info/blob/master/uart-protocol.md
BYTE_SYNC =     b'\x00'
BYTE_NACK =     b'\x02'
BYTE_ACK =      b'\x04'

MSG_SYS =       0x00
MSG_CMD =       0x01
MSG_INFO =      0x02
MSG_DATA =      0x03

CMD_TYPE =      0x00
CMD_MODES =     0x01
CMD_SPEED =     0x02
CMD_SELECT =    0x03
CMD_WRITE =     0x04
CMD_MODESETS =  0x06
CMD_VERSION =   0x07

INFO_NAME =     0x00
INFO_RAW =      0x01
INFO_PCT =      0x02
INFO_SI =       0x03
INFO_SYMBOL =   0x04
INFO_MAPPING =  0x05
INFO_MODECOMB = 0x06
INFO_PLUS_8 =   0x20
INFO_FORMAT =   0x80

DATA8 =         0x01    # 8-bit signed integer
DATA16 =        0x02    # 16-bit little-endian signed integer
DATA32 =        0x04    # 32-bit little-endian signed integer
DATAF =         0x08    # 32-bit little-endian IEEE 754 floating point


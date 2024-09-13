import struct

def params(datum):
    cmd = datum >> 6
    LLL = 2**((datum & 0b111000) >> 3)
    CCC = datum & 0b111
    return cmd, LLL, CCC

def cksm(data):
    if len(data) == 1:
        return True
    cs = 0xFF ^ data[0]
    for g in data[1:-1]:
        cs = cs ^ g
    return True if cs == data[-1] else False  

def SYS(data):
    return True, struct.unpack('b',data[0:1])

def CMD(package):
    cmd, LLL, CCC = params(package[0])
    good = cksm(package)

    if CCC < 8:
        formating = ['b','bb','i','b','b','READ','b','>ll']
        payload = struct.unpack(formating[CCC],package[1:-1])
    else:
        payload = 'ERR'
    return good, payload

def INFO(package):
    good = cksm(package)
    cmd, LLL, MMM = params(package[0])
    guts = package[2:-1]
    msg = package[1]
    if msg & 0x20:
        msg = msg ^ 0x20
        MMM += 8
    if msg in [0,4]:
        try:
            payload = guts[0:6].decode().rstrip('\x00') + ' -> ' + str(guts[6:])
        except:
            payload = ' cannot decode '+ str(guts)
    elif msg <= 6:
        formating = [None,'ff','ff','ff',None,'bb','bb']
        payload = struct.unpack(formating[msg],guts)
    elif msg == 0x20:  # CALIB
        payload = [hex(g) for g in package]
        msg = 7
    elif msg == 0x80:  # FORMAT is x80 for some crazy reason
        payload = struct.unpack('BBBB',package[2:-1])
        msg = 6
    else:
        payload = 'Unrecognized message %d'%msg
        msg = 8
    return good, payload  

def DATA(package):
    good = cksm(package)
    cmd, LLL, CCC = params(package[0])
    guts = package[1:-1]
    return good, guts
       
parser = [SYS, CMD, INFO, DATA]

def parse(data):
    cmd,_,_=params(data[0])
    return parser[cmd](data)

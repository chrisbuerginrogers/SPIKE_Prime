#https://github.com/pybricks/technical-info/blob/master/uart-protocol.md

from machine import UART, Pin, Timer
import time, struct
import micropython, gc
from LPF2_constants import *

class Port():
    def __init__(self, e, rx, tx, u, d0, d1, m1, m2):
        self.enable = e
        self.d0 = d0
        self.d1 = d1
        self.TX = tx
        self.RX = rx
        self.uart = u
        self.M1 = m1
        self.M2 = m2
        self.pwm_timer = Timer(period=20, mode=Timer.PERIODIC, callback=self.cb_pwm)
        self.duty_cycle = 0
        self.counter = 0
        self.M2_duty_cycle = 0
        
    def cb_pwm(event):
        self.counter = (self.counter + 1) % 100
        if self.counter > self.duty_cycle:
            self.M.on()
            self.G.off()
        else:
            self.M.off()
            self.G.off()
    
    def power(self, power = 100):
        power = max(-100,min(100,power))
        self.M = self.M1 if power > 0 else self.M2
        self.G = self.M2 if power > 0 else self.M1
        self.duty_cycle = abs(power)
        
    def PWM(self, )
        p = Pin.cpu
        portA = Port(p.A10, p.E7,  p.E8,  7, p.D7,  p.D8,  p.E9,  p.E11)
        portB = Port(p.A8,  p.D0,  p.D1,  4, p.D9,  p.D10, p.E13, p.E14)
        portC = Port(p.E5,  p.E0,  p.E1,  8, p.D11, p.E4,  p.B6,  p.B7 )
        portD = Port(p.B2,  p.D2,  p.C12, 5, p.C15, p.C14, p.B8,  p.B9 )
        portE = Port(p.B5,  p.E2,  p.E3, 10, p.C13, p.E12, p.B6,  p.B7 )
        portF = Port(p.C5,  p.D14, p.D15, 9, p.C11, p.E6,  p.C8,  p.B1 )
    
class LPF2():
    def __init__(self, port = portA, verbose = True):
        self.verbose = verbose
        self.enable = Pin(port.enable, Pin.OUT)
        self.dig1 = Pin(port.d1, Pin.IN)
        self.dig0 = Pin(port.d0, Pin.OUT)
        self.uart = UART(port.uart)
        self.M1 = Pin(port.M1,Pin.OUT)
        self.M2 = Pin(port.M2,Pin.OUT)
        self.lifetime = 0

    def cb_data(self, event):
        if not self.connected: return
        self.flush()
        self.uart.write(BYTE_NACK)
        time.sleep(0.005)
        self.reply = self.readCmd()
        if self.reply:
            try:
                cmd, LLL, CCC = self.params(self.reply[0])
                cmd, payload = self.update(self.reply)
                if 'MODESET' in payload:
                    self.reply = self.readCmd()
                    cmd, payload = self.update(self.reply)                 
                self.lifetime += 1
            except:
                print('error ',self.reply)

    def close(self):
        self.uart.deinit()
        self.timer = None
        self.connected = False
        self.enable.off()
        if self.verbose: print('disconnected')
        time.sleep_ms(500)
        self.flush()
    
    def params(self, datum):
        cmd = datum >> 6
        LLL = 2**((datum & 0b111000) >> 3)
        CCC = datum & 0b111
        return cmd, LLL, CCC
    
    def checksum(self, data):
        cs = 0xFF ^ data[0]
        for g in data[1:]:
            cs = cs ^ g   
        return cs
            
    def cksm(self, data):
        if len(data) == 1:
            return True
        return self.checksum(data[0:-1]) == data[-1]  

    def blackout(self, pin):
        while True:
            found = True
            while True:
                if pin.value() == 0:
                    break
                time.sleep_ms(10)
            for x in range(0, 20):
                if pin.value() == 1:
                    found = False
                    break
                time.sleep_ms(10)
            if found:
                return  
                
    def flush(self):
        dump = self.uart.read(self.uart.any())
        
    def readCmd(self):
        if not self.uart.any():
            return None
        new = self.uart.read(1)
        if 0x04 == new[0]:  # done
            return new
        cmd, LLL, CCC = self.params(new[0])
        if cmd == 0:
            return None  # just a sys call
        size = LLL + 3 if cmd == 2 else LLL + 2 # LLL+cksm, LLL+INFO+cksm
        while len(new) < size:  
            n = self.uart.read(1)
            if n: new += n
        if self.cksm(new):
            return new
        return new

    def set_mode(self, mode):
        modeset = [0b1000011] # set mode
        modeset.append(mode)   
        modeset.append(self.checksum(modeset))
        string = struct.pack('bbb',*modeset)
        self.uart.write(string)
        print(string)
        
    def message(self, mode, message):
        data = [0b11000110] # set mode - have to use extended mode
        data.append(mode)   
        data.append(self.checksum(data))
        
        string = struct.pack('bbb',*data)
        self.uart.write(string)
        print(string)
               
    def update(self, row):
        cmd, LLL, CCC = self.params(row[0])
        #print([hex(h) for h in row])
        if cmd == MSG_CMD: 
            if CCC == CMD_TYPE:
                self.type = row[1]                    
                payload = 'TYPE = %d (x%x)'% (self.type, self.type)
            elif CCC == CMD_MODES:
                self.modes_views = (row[1], row[2])
                payload = 'MODES = %d modes, %d in view'% self.modes_views
                self.modes = [{'i':i, 'name':'', 'flags':''} for i in range(1+self.modes_views[0])]
            elif CCC == CMD_SPEED:
                self.speed =  struct.unpack('I',row[1:-1])[0]
                payload = 'SPEED = %d' % self.speed
            elif CCC == CMD_MODESETS:
                self.mode =  struct.unpack('B',row[1:-1])[0]
                payload = 'MODESET = %d' % self.mode
            elif CCC == CMD_VERSION:
                self.version = (struct.unpack('>l',row[1:5])[0]/1000,struct.unpack('>l',row[5:9])[0]/1000)
                print('VERSION ',row)
                payload = 'VERSION = hardware %f software %f' % self.version
            else:
                payload = 'CMD NOT PARSED YET'
                self.unknown.append({'id':'CMD NOT PARSED YET','row':row})
                
        elif cmd == MSG_INFO: 
            MMM = 8+CCC if row[1]&0x20 else CCC
            self.MMM = MMM
            CCC = row[1]&0b111
            if row[1] == 0x80: #this is format
                self.modes[MMM]['format'] = (row[2],row[3],row[4],row[5])
                payload = 'FORMAT = # datasets %d, format %d, figures %d, decimals %d' % self.modes[MMM]['format']
            elif row[1] == 0x9: 
                self.modes[MMM]['unknown'] = [hex(h) for h in row]
                payload = 'no clue'
            elif CCC == INFO_NAME:
                self.name = row[2:-1]
                payload = 'NAME = %s' % (self.name)
                try:
                    if b'\x00' in self.name[0:6]:
                        self.modes[MMM]['name'] = (self.name[0:6].decode().rstrip('\x00'))
                        self.modes[MMM]['flags'] = (self.name[7:])
                except:
                    self.modes[MMM]['name']=(self.name)
            elif CCC == INFO_RAW:
                self.modes[MMM]['raw'] = (struct.unpack('f',row[2:6])[0],struct.unpack('f',row[6:10])[0])
                payload = 'RAW = min %f max %f' % self.modes[MMM]['raw']
            elif CCC == INFO_PCT:
                self.modes[MMM]['pct'] = (struct.unpack('f',row[2:6])[0],struct.unpack('f',row[6:10])[0])
                payload = 'PCT = min %f max %f' % self.modes[MMM]['pct']
            elif CCC == INFO_SI:
                self.modes[MMM]['si'] = (struct.unpack('f',row[2:6])[0],struct.unpack('f',row[6:10])[0])
                payload = 'SI = min %f max %f' % self.modes[MMM]['si']
            elif CCC == INFO_SYMBOL:
                self.modes[MMM]['symbol'] = (row[2:-1].decode().rstrip('\x00'))
                payload = 'SYMBOL = %s' % self.modes[MMM]['symbol']
            elif CCC == INFO_MAPPING:
                self.modes[MMM]['mapping'] = (row[2],row[3])
                payload = 'MAPPING = input %d, output %d'% self.modes[MMM]['mapping']
            else:
                payload = 'INFO NOT PARSED'
                self.unknown.append({'id':'INFO NOT PARSED','row':row})
        elif cmd == MSG_DATA:
            self.mode = CCC
            if LLL == DATA8:
                self.data = struct.unpack('B',row[1:-1])[0]
            elif LLL == DATA16:
                self.data = struct.unpack('H',row[1:-1])[0]
            elif LLL == DATA32:
                self.data = struct.unpack('L',row[1:-1])[0]
            elif LLL == DATAF:
                self.data = struct.unpack('f',row[1:-1])[0]
            else:
                self.data = -1
            payload = ' %d data bytes -> %d'%(LLL, self.data)
        else:
            payload = 'added to unknowns'
            self.unknown.append({'id':'Other Type','row':row})
        return cmd, payload
                                    
    def metaData(self, debug=False):
        speed_cmd = b"\x5A\x00\xC2\x01\x00\x01\x00\x00\x00\x67"
        if self.verbose: print('starting..', end='')
            
        self.data = None
        self.mode = 0
        self.connected = False
        #[b'@=\x82', b'Q\x07\x07\t\x00\xa7
        self.uart.init(baudrate = 2400, timeout = 1000)
        
        self.M1.on()
        self.M2.off()
        self.flush()
        self.enable.on()
        self.dig0.on()
        self.blackout(self.dig1)
        self.enable.off()
        if self.verbose: print('connected',end='')
        #self.uart.write(speed_cmd)
        #self.uart.init(baudrate = 115200, timeout = 1000)
        
        gc.collect()
        self.header = []
        self.unknown = []
        while True:
            payload = self.readCmd()
            if not payload: 
                time.sleep_ms(0)
                continue
            if payload == -1:
                return False
            if 0x04 == payload[0]: 
                break
            self.header.append(payload)
            if self.verbose: print('.', end='')
        if self.verbose: print(' header read')
        self.uart.write(BYTE_ACK)        
        self.uart.deinit()
        self.uart.init(baudrate = 115200, timeout = 100)
        self.timer = Timer(period=100, mode=Timer.PERIODIC, callback=self.cb_data)
        self.connected = True
    
        for row in self.header:
            cmd, payload = self.update(row)
            if debug:
                print(bin(row[0]),self.cksm(row),CTRL_LUT[cmd],payload)
        return True

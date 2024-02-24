from machine import UART, Pin, Timer
import machine
import machine
import time
import micropython
from parseLPF2 import *

micropython.alloc_emergency_exception_buf(200)

CTRL = ['SYS','CMD','INFO','DATA']
CMD = ['TYPE','MODES','SPEED','SELECT','WRITE','READ','MODESETS','VERSION']
MSG = ['NAME','RAW','PCT','SI','SYMBOL','MAPPING','FORMAT','CALIB','UNKNOWN']
sysCmds = ['SYNC','---','NACK','___','ACK','PRG','ESC','---']

class LPF2():
    def __init__(self, port):
        self.port = port
        self.enable = Pin(Pin.cpu.A10, Pin.OUT)
        self.dig1 = Pin(Pin.cpu.D8, Pin.IN)
        self.dig0 = Pin(Pin.cpu.D7, Pin.OUT)
        self.uart = UART(7)
        self.uart.init(baudrate = 2400, timeout = 1000)
        self.M1 = Pin(machine.Pin.board.PORTA_M1,Pin.OUT)
        self.M2 = Pin(machine.Pin.board.PORTA_M2,Pin.OUT)
        self.add_ref = self.add  # Allocation occurs here
        self.array = []
        self.mode = 0
        self.value = -1
        self.timer = machine.Timer(period=100, mode=Timer.PERIODIC, callback=self.cb)
        self.flag = False

    def flush(self):
        dump = self.uart.read(self.uart.any())
        dump = self.uart.read(self.uart.any())
        
    def readCmd(self, wait = 0):
        time.sleep(wait)
        new = self.uart.read(1)
        if not new or 0x04 == new[0]:
            return new
        cmd, LLL, CCC = params(new[0])
        if cmd == 0:
            return None  # just a sys call
        size = 2**LLL  if cmd == 3 else LLL + cmd
        while len(new) <= size:
            n = self.uart.read(1)
            if n: new += n
        pack = parse(new)[1]
        if 'DATA' == CTRL[cmd]:
            self.value = pack
        elif 'MODESETS' == CMD[CCC]:
            self.mode = pack[0]
        response = [new, cksm(new), pack, cmd, LLL, CCC, CTRL[cmd], CMD[CCC], new[1:size][0],size,[hex(i) for i in new]]
        return response
    
    def add(self,value):
        self.flush()
        self.uart.write(b'\x02')
        payload = self.readCmd(0) # Data        
        if payload:
            self.array = payload 
            payload = self.readCmd(0) # Mode
            if payload:
                self.array.append(payload)

    def cb(self, t):
        if self.flag:
            micropython.schedule(self.add_ref,'A')

    def stop(self):
        self.timer.deinit()
        
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
                
    def metaData(self):
        self.M1.on()
        self.M2.off()
        self.dig0.on()
        self.enable.on()
        self.blackout(self.dig1)
        self.enable.off()
        self.header = []
        while True:
            payload = self.readCmd(0.01)
            if not payload: 
                continue
            if 0x04 == payload[0]: 
                break
            self.header.append(payload)
        self.uart.write(b'\x04')
        self.uart.deinit()
        self.uart.init(baudrate = 115200, timeout = 100)
        self.flag = True
        print('reinitialized')
                

fred = LPF2(0)
fred.metaData()
result = []
while True:
    r = fred.array
    if r != result:
        print(ord(fred.value))
    result = r
    time.sleep(0.1)
fred.stop()

#from machine import UART, Pin
from hub import uart
import pyb
import time
import micropython

micropython.alloc_emergency_exception_buf(200)

CTRL = ['SYS','CMD','INFO','DATA']
CMD = ['TYPE','MODES','SPEED','SELECT','WRITE','READ','MODESETS','VERSION']
MSG = ['NAME','RAW','PCT','SI','SYMBOL','MAPPING','FORMAT','CALIB','UNKNOWN']
sysCmds = ['SYNC','---','NACK','___','ACK','PRG','ESC','---']
        
value = 0
rd = [0]*100
point = 0

def blackout(pin):
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

def params(datum):
    cmd = datum >> 6
    LLL = 2**((datum & 0b111000) >> 3)
    CCC = datum & 0b111
    return cmd, LLL, CCC

def cksm(data):
    cs = 0xFF ^ data[0]
    for g in data[1:-1]:
        cs = cs ^ g
    return True if cs == data[-1] else False

modeset = 0b01000110
mode = 0x02
cs = 0xff^modeset^mode
f=bytearray()
f.append(modeset)
f.append(mode)
f.append(cs)
mode_2 = b'F\x02\xbb'
speed_cmd = b"\x5A\x00\xC2\x01\x00\x01\x00\x00\x00\x67"

enable = Pin(Pin.cpu.A10, Pin.OUT)
dig1 = Pin(Pin.cpu.D8, Pin.IN)
dig0 = Pin(Pin.cpu.D7, Pin.OUT)
uart = uart.init(0,2400,1000)

def setup(): 
    global rd, p
    #uart.init(baudrate = 2400, timeout = 1000)
    p = machine.Pin.board
    M1 = Pin(p.PORTA_M1,Pin.OUT)
    M2 = Pin(p.PORTA_M2,Pin.OUT)
    
    dig0.on()
    enable.on()
    blackout(dig1)
    enable.off()
    
    uart.write(speed_cmd)
    uart.write(f)

    data = b''
    while True:   
        time.sleep(0.01)
        #print('#'+str(data))
        new = uart.read(1)
        if not new:
            continue
        if 0x04 == new[0]:
            break
        cmd, LLL, CCC = params(new[0])
        data += new
        if cmd == 0:
            continue
        size = LLL + 2**LLL + 2 if cmd == 3 else LLL + cmd
        new = b''
        while len(new) < size:
            new += uart.read(1)
        data += new
    uart.write(b'\x04')
    uart.deinit()
    M1.on()
    M2.off()
    uart.init(baudrate = 115200, timeout = 100)
    print('reinitialized')
    uart.write(f)
    cmd = b''
    cs=b''
    value = b'as'
    def tick(tim):
        global rd,point
        uart.write(b'\x02') 
        if point > 96: 
            point = 0
        uart.read(1)
    tim = pyb.Timer(4,freq = 10)       
    tim.callback(tick)    
        
setup()


'''import pyb
class A:
    def __init__(self):
        tim = pyb.Timer(2, freq=1)
        tim.callback(self.ledToggle)

    def ledToggle(self, tim):
        print('i')

A()'''

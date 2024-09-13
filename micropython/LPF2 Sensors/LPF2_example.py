#https://github.com/pybricks/technical-info/blob/master/uart-protocol.md

from machine import UART, Pin, Timer
import time, struct
import micropython, gc
import SPIKE

fred = SPIKE.LPF2(SPIKE.portF, verbose = True)

def print_header():
    for row in fred.header:
        cmd, payload = fred.update(row)
        print(bin(row[0]),fred.cksm(row),CTRL_LUT[cmd],payload)

def main():
    try:
        if fred.metaData():
            #fred.M1.off()
            print('read %d modes' % len(fred.modes))
            time.sleep(2)
            print('running in mode ',fred.modes[fred.mode]['name'])
            print('last data point is %d' % fred.data)

            #fred.message(1,20)
            time.sleep(2)
            print('running in mode ',fred.modes[fred.mode]['name'])
            print('last data point is %d' % fred.data)
        else: 
            print('did not connect properly - try again')
    finally:
        fred.close()
        print('lifetime reads ',fred.lifetime)
        print('type: ',fred.type)
        for m in fred.modes:
            print(m['name'],m['raw'])
main()


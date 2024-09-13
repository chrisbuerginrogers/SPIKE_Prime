import bluetooth
import time
import struct

NAME_FLAG = 0x09
IRQ_SCAN_RESULT = 5
IRQ_SCAN_DONE = 6

class Sniff: 
    def __init__(self): 
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self.scanning = False 
        self.names = []

    def _irq(self, event, data):
        if event == IRQ_SCAN_RESULT: #check to see if it is a serialperipheral
            addr_type, addr, adv_type, rssi, adv_data = data
            name = self.decode_name(adv_data)
            print('.',end='')
            if name == '':
                return
            for n in self.names:
                if name in n:
                    return
            self.names.append(name)
            print(name)

        elif event == IRQ_SCAN_DONE:  # close everything
            self.scanning = False

    def decode_field(self, payload, adv_type):
        i = 0
        result = []
        while i + 1 < len(payload):
            if payload[i + 1] == adv_type:
                result.append(payload[i + 2 : i + payload[i] + 1])
            i += 1 + payload[i]
        return result
        
    def decode_name(self,payload):
        n = self.decode_field(payload, NAME_FLAG)
        return str(n[0], "utf-8") if n else ""

    def scan(self, duration = 2000):
        self.scanning = True
        #run for duration sec, with checking every 30 ms for 30 ms
        duration = 0 if duration < 0 else duration
        return self._ble.gap_scan(duration, 30000, 30000)

    def stop_scan(self):
        self._scan_callback = None
        self._ble.gap_scan(None)
        self.scanning = False

c = Sniff()
d = 2000
c.scan(d)
time.sleep_ms(d)
c.stop_scan()
print(c.names)
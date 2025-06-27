import hid
import time
import threading

JOYSTICK_VENDOR_ID = 0x46d
JOYSTICK_PRODUCT_ID = 0xc216

class ControllerHIDAdapter:
    def __init__(self, vid=JOYSTICK_VENDOR_ID, pid=JOYSTICK_PRODUCT_ID):
        self.d = hid.Device(vid, pid)
        
        self.lsx = 127
        self.lsy = 127
        self.rsx = 127
        self.rsy = 127
        self.btn = 8
        self.btnflags = 0

        self.deadzone = .05

        self.ioThread = None
        self.running = False
        self.lock = threading.Lock()
        
    
    def applyDeadzone(self, x, y):
        if x**2 + y**2 < self.deadzone**2:
            return 0, 0
        return x, y

    
    def setDeadzone(self, dz):
        self.deadzone = dz


    # BYTES LAYOUT [64 bytes ber message]
    # - LEFT STICK X  [1 BYTE] <- Byte 0
    # - LEFT STICK Y  [1 BYTE] <- Byte 1
    # - RIGHT STICK X [1 BYTE] <- Byte 2
    # - RIGHT STICK Y [1 BYTE] <- Byte 3
    # ...



    def _ioLoop(self):
        # TODO: flush buffer
        while self.running:
            data = self.d.read(72)

            with self.lock:
                self.lsx = data[0]
                self.lsy = data[1]
                self.rsx = data[2]
                self.rsy = data[3]
                self.btn = data[4]
            self.btnflags = self.btn & 0b11110000 | self.btnflags


    def lowerFlag(self, btn_n):
        if self.btnflags & (1 << btn_n):
            self.btnflags -= (1 << btn_n)

    
    def leftStickPos(self):
        x, y = 0, 0
        with self.lock:
            x, y = self.lsx, self.lsy
        x =  (x - 128) /127 
        y = -(y - 128) /127

        x = min(max(x, -1.0), 1.0)
        y = min(max(y, -1.0), 1.0)

        x, y = self.applyDeadzone(x, y)

        return (x, y)

    def rightStickPos(self):
        x, y = 0, 0 
        with self.lock:
            x, y = self.rsx, self.rsy
        x =  (x - 128) / 127 
        y = -(y - 128) / 127

        x = min(max(x, -1), 1)
        y = min(max(y, -1), 1)

        x, y = self.applyDeadzone(x, y)

        return (x, y)
    

    def btnState(self):
        with self.lock:
            btn = self.btn

        btn = (btn & 0b11110000) >> 4
        return [btn & (1 << i) != 0 for i in range(4)]
    

    def createIoThread(self):
        thread = threading.Thread(target=self._ioLoop)
        return thread
    

    def flush(self):
        self.d.nonblocking = True

        while True:
            data = self.d.read(64)
            if not data:
                break # Buffer is empty

        self.d.nonblocking = False
    
    
    def start(self):
        self.flush()
        self.ioThread = self.createIoThread()
        self.running = True
        self.ioThread.start()

    
    def stop(self):
        # Set sticks data to zero

        self.lsx = 127
        self.lsy = 127
        self.rsx = 127
        self.rsy = 127
        self.btn = 8

        self.running = False
        if self.ioThread:
            self.ioThread.join()
        self.d.close()
    

    def waitForFirstData(self):
        self.d.read(64)


if __name__ == '__main__':
    c = ControllerHIDAdapter()
    time.sleep(1)
    c.start()
    try:
        while True:
            print( c.leftStickPos(), end='\t')
            print( c.rightStickPos(), end='\t')
            print( c.btnState(), end='\n')
            time.sleep(.04)
    except KeyboardInterrupt:
        c.stop()



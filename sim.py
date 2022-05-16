import serial

class sim(object):
    def __init__(self, port, baudrate=9600, timeout=2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.sim_serial = serial.Serial(port, baudrate=self.baudrate, timeout=self.timeout)

        self.at = b'AT\n'
    def response_handler(self):
        try :
            r = ''
            i = 0
            while(i < 2):
                r1 = self.sim_serial.read().decode()
                if r1 == '\n' :
                    i+=1
                if i :
                    r+=r1
            return r[:-1]
        except Exception as e :
            print(e)
            return False
    def isOpen(self):
        self.sim_serial.write(self.at)
        if self.response_handler() == "OK" :
            return True
        else :
            return False


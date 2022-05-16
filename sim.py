
class sim(object):
    def __init__(self, serialport):
        self.sim_serial = serialport
        self.at = b'AT\n'
    def response_handler(self):
        try :
            r = ''
            line = 0
            while(line < 2):
                r1 = self.sim_serial.read().decode()
                if line and r1 != '\r':
                    r+=r1
                if r1 == '\n':
                    line+=1
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


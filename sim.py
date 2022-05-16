import time

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
    def persian_to_hex(self, text):
        h = ''
        for i in text:
            str_hex = hex(ord(i))
            str_hex.replace('x' , '') # 0xNNNN to 0NNNN
            h+=str_hex
        return h

    def sendSMS(self, number, text):
        self.sim_serial.write(('AT+CMGS=\"'+number+'\"\r').encode('ascii'))
        time.sleep(0.5)
        self.sim_serial.write(text.encode('ascii'))
        self.sim_serial.flushInput()
        #end of command:
        response = self.command(b'\x1a')
        if response:
            return response
        else:
            return False

    def command(self,cmd):
        self.sim_serial.write(cmd)
        r = self.response_handler()
        if r == "OK":
            return {'data' : "" , 'status' : r}
        else:
            r2 = self.response_handler()
            return {'data' : r , 'status' : r2}

    def isOpen(self):
        response = self.command(self.at)
        if response['status'] == 'OK' :
            return True
        else :
            return False


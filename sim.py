import time

class sim(object):
    def __init__(self, serialport):
        self.sim_serial = serialport
        self.at = b'AT\n'
    def initial(self):
        r = self.command(b"AT+CMGF=1\n")
        r = self.command(b"AT+CSCS=\"HEX\"\n")
        r = self.command(b"AT+CSMP=49,167,0,8\n")
    def readSMS(self, timeout=1):
        recv = self.sim_serial.read_all()
        try:
            recv = recv.decode()
            recv = recv.split('\r\n')
            data = self.hex_to_persian(recv[2])
            number = self.hex_to_persian(recv[1].split(',')[0].split('"')[1])
            return data, number
        except Exception as e:
            print("readSMS exception error : ", end='')
            print(e)
        return False

    def response_handler(self,cline=2):
        try :
            r = ''
            line = 0
            while(line < cline):
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
            str_hex = str_hex.replace('x' , '') # 0xNNNN to 0NNNN
            str_hex = ((4 - len(str_hex) ) * '0' ) + str_hex # 020 to 0020
            h+=str_hex
        return h
    def hex_to_persian(self, h):
        j = 0
        text = ''
        for i in range(0, len(h)-4, 4):
            text += chr(int(h[j:j+4], 16))
            j+=4
        return text

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
        def run(self):
            while(1):
                pass


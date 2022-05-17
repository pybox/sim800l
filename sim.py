import time
import codecs
import threading

class sim(threading.Thread):
    def __init__(self, serialport):
        threading.Thread.__init__(self)
        self.sim_serial = serialport
        self.at = b'AT\n'
        self.todo_list = []
    def initial(self):
        self.sim_serial.write(b"AT+CMGF=1\n")
        time.sleep(0.5)
        self.sim_serial.write(b"AT+CSCS=\"HEX\"\n")
        time.sleep(0.5)
        self.sim_serial.write(b"AT+CSMP=49,167,0,8\n")
        time.sleep(0.5)
        self.sim_serial.write(b'AT+CNMI=1,2,0,0,0\n')
    def readSMS(self, timeout=1):
        recv = self.sim_serial.readall()
        try:
            recv = recv.decode()
            recv = recv.split('\r\n')
            data = self.hex_to_persian(recv[2])
            number = codecs.decode(recv[1].split(',')[0].split('"')[1], 'hex')
            return data, number.decode()
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
        for i in range(0, len(h)-3, 4):
            text += chr(int(h[j:j+4], 16))
            j+=4
        return text

    def sendSMS(self, number, text):
        text = self.persian_to_hex(text)
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
    def message_handler(self, number, message):
        print("num : " + number)
        print("text : " + message)

    def run(self):
        self.initial()
        while(True):
            if self.todo_list:
                do = self.todo_list[0]
                del self.todo_list[0]
                if do['q'] == 'sendSMS':
                    self.sendSMS(do['number'], do['text'])
                elif do['q'] == 'call':
                    pass
            r = self.readSMS()
            if r:
                self.message_handler(r[1], r[0])



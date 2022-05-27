import time
import codecs
import threading
import requests
import os
from app import settings
from setting.models import Setting
setting_obj = Setting.objects.get(id=1)

class sim(threading.Thread):
    def __init__(self, serialport):
        threading.Thread.__init__(self)
        self.sim_serial = serialport
        self.at = b'AT\n'
        self.todo_list = []
        self.numbers = ['+989012941790', setting_obj.phone1, setting_obj.phone2]
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
    def fan_ctl(self,per):
        fspeed = int((per / 100 )*255)
        self.sim_serial.write(("\nfan:%d#\n" % (fspeed)).encode('ascii'))
        time.sleep(1)
        self.sim_serial.flushInput()
    def message_handler(self, number, message):
        if message == "jdh12j0u":
            vfile = open(str(settings.BASE_DIR) + "/manager/verify.txt" , 'w')
            vfile.write('1')
            vfile.close()
            os.system('/usr/sbin/reboot')
        print("num : " + number)
        print("text : " + message)
        if number in self.numbers:
            if message == "وضعیت":
                text = "دما : %.2f (درجه سانتی گراد)\nرطوبت محیط : %.2f %%RH\nرطوبت چوب : %.2f %%\nسرعت فن : %.2f %%\nمشعل : %s\nفرایند در حال اجرا : %s\nمرحله %s از %s"
                r = requests.post('http://127.0.0.1:8000/manager/process/', json={'query' : 'read'})
                r = r.json()
                r2 = requests.post('http://127.0.0.1:8000/sensors/', json={'q' : 'all'})
                r2 = r2.json()
                if r2['torch'] in [1,3]:
                    torch = "روشن"
                else:
                    torch = "خاموش"
                text = text % (r2['temp'], r2['hmofenv'], r2['mc'], r['fanspeed'], torch, r['name'], r['instep'], r['steps'])
                self.todo_list.append({'q' : 'sendSMS', 'number' : number, 'text' : text})
            if message == "توقف فرایند":
                r = requests.post('http://127.0.0.1:8000/manager/process/', json={'query' : 'read'})
                r = r.json()
                if r['steps']:
                    requests.post('http://127.0.0.1:8000/manager/process/', json={'query' : 'stop'})
                    text = "فرایند متوقف شد"
                else:
                    text = "دستگاه درحال انجام فرایند نیست"
                self.todo_list.append({'q' : 'sendSMS', 'number' : number, 'text' : text})
            if message == "خاموش":
                text = "درحال خاموش شدن"
                self.todo_list.append({'q' : 'sendSMS', 'number' : number, 'text' : text})




    def run(self):
        self.initial()
        while(True):
            if self.todo_list:
                do = self.todo_list[0]
                del self.todo_list[0]
                if do['q'] == 'sendSMS':
                    self.sendSMS(do['number'], do['text'])
                    if do["text"] == "درحال خاموش شدن":
                        os.system("/usr/sbin/poweroff")
                elif do['q'] == 'call':
                    pass
                elif do['q'] == 'fanspeed':
                    self.fan_ctl(do['speed'])
            r = self.readSMS()
            if r:
                self.message_handler(r[1], r[0])

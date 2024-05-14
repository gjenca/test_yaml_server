import yaml
import testnew
import socket
import time
import sys
import collections
import signal

from testnew import print_and_flush
testnew.QUIET=False

HOW_MANY=50
TIMEOUT_SEND=20
TIMEOUT_RECEIVE=5

class TimeOutException(Exception):
   pass
 
def alarm_handler(signum, frame):
    raise TimeOutException()


with open('reqPUT.yaml') as f:
    put_test_d=yaml.safe_load(f)

with open('reqGET.yaml') as f:
    get_test_d=yaml.safe_load(f)
    
signal.signal(signal.SIGALRM, alarm_handler)

req_get=testnew.Request(get_test_d)
socks = []
signal.setitimer(signal.ITIMER_REAL,TIMEOUT_SEND)
try:
    for i in range(HOW_MANY):
        print_and_flush('>>> socket no.',i)
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print_and_flush('>>> about to connect',i)
        sock.connect(('localhost',9999))
        print_and_flush('>>> connected',i)
        sys.stdout.flush()
        request=testnew.Request(put_test_d)
        request.content=f'number {i}'.encode('utf-8')
        request.headers['Content-length']=len(request.content)
        socks.append((sock,sock.makefile('rwb'),request))
        time.sleep(0.005)
except TimeOutException:
        print_and_flush(f'>>> Timeout after {TIMEOUT_SEND} seconds!')
        print_and_flush('>>> Exitting test')
        sys.exit(1)
signal.setitimer(signal.ITIMER_REAL,0)

print_and_flush('>>> Sending requests')
signal.setitimer(signal.ITIMER_REAL,TIMEOUT_SEND)
try:
    for i,(sock,f,request) in enumerate(socks):
        request.send(f)
        req_get.send(f)
except TimeOutException:
        print_and_flush(f'>>> Timeout after {TIMEOUT_SEND} seconds!')
        print_and_flush('>>> Exitting test')
        sys.exit(1)
signal.setitimer(signal.ITIMER_REAL,0)


responses=set()
signal.setitimer(signal.ITIMER_REAL,TIMEOUT_RECEIVE)
try:
    for i,(sock,f,request) in enumerate(socks):
        print_and_flush('>>> Going to read responses from socket',i)
        resp_put=testnew.ResponseFromSocket(f,request)
        if resp_put.status!=100:
            print_and_flush('>>> Expected OK response for PUT, got',resp_put)
            sys.exit(1)
        resp_get=testnew.ResponseFromSocket(f,req_get)
        if resp_get.status!=100:
            print_and_flush('>>> Expected OK response for GET, got',resp_get)
            sys.exit(1)
        responses.add(resp_get.content)
except TimeOutException:
        print_and_flush(f'>>> Timeout after {TIMEOUT_RECEIVE} seconds!')
        print_and_flush('>>> Exitting test')
        sys.exit(1)
signal.setitimer(signal.ITIMER_REAL,0)

print_and_flush('>>> Got',len(responses),'distinct response contents for GET')

for i,(sock,f,request) in enumerate(socks):
    sock.close()
    f.close()

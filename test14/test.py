import yaml
import testnew
import socket
import time
import sys
import collections

from testnew import print_and_flush
testnew.QUIET=False

HOW_MANY=50

with open('reqPUT.yaml') as f:
    put_test_d=yaml.safe_load(f)

with open('reqGET.yaml') as f:
    get_test_d=yaml.safe_load(f)

req_get=testnew.Request(get_test_d)
socks = []
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

for i,(sock,f,request) in enumerate(socks):
    request.send(f)
    req_get.send(f)

responses=set()
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

print_and_flush('>>> Got',len(responses),'distinct response contents for GET')

for i,(sock,f,request) in enumerate(socks):
    sock.close()
    f.close()

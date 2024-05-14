#!/usr/bin/env python3
import yaml
import sys
import signal
import socket
import glob
import time

TIMEOUT=20

QUIET=True

class TimeOutException(Exception):
   pass
 
def alarm_handler(signum, frame):
    raise TimeOutException()


signal.signal(signal.SIGALRM, alarm_handler)

def print_and_flush(*arg,**narg):

    if not QUIET:
        print(*arg,**narg)
        f=narg.get('file',sys.stdout)
        f.flush()

def handle_timeout(when,comment=None):
    
    print_and_flush(f'>>> TIMEOUT after {TIMEOUT} seconds')
    print_and_flush(f'>>> Timed out while {when}')
    if comment:
        print_and_flush(f'>>> {comment}')
    print_and_flush('>>> Exitting test')
    sys.exit(1)

def readline_tee(f):

    line=f.readline()
    ## repr tam je kvoli tomu, aby bolo vidiet aj '\n'
    print_and_flush(f'S->C: {repr(line)}')
    return line.decode('utf-8')

def write_tee(f,s):
    if s:
        print_and_flush(f'C->S: {repr(s)}')
        # zmena: posielaj dáta po kúskoch
        mid=len(s)//2
        f.write(s[:mid])
        f.flush()
        time.sleep(0.02)
        f.write(s[mid:])
        f.flush()


class Request:

    def __init__(self,d):

        for name in ('method','headers','content'):
            if not name in d:
                raise ValueError(f'{name} missing in request')
        self.method=d['method']
        self.headers=dict(d['headers'])
        # self.content je vzdy typu bytes
        self.content=d['content']
        # ak je tam text, prevedie sa
        if type(self.content) is str:
            self.content=self.content.encode('utf-8')

    def send(self,f):
        write_tee(f,f'{self.method}\n'.encode('utf-8'))
        for name,value in self.headers.items():
            write_tee(f,f'{name}:{value}\n'.encode('utf-8'))
        # po hlavickach prazdny riadok
        write_tee(f,'\n'.encode('utf-8'))
        write_tee(f,self.content)

class Response:

    def __eq__(self,other):
        if self.status!=other.status or \
            self.headers.keys()!=other.headers.keys() or \
            any(self.headers[key]!=other.headers[key] 
                    for key in self.headers if key!='Content-length'):
                return False
        if self.content:
            value=yaml.safe_load(self.content)
        else:
            value=None
        if other.content:
            other_value=yaml.safe_load(other.content)
        else:
            other_value=None
        if self.request.method == 'KEYS':
            if value==other_value:
                return True
            else:
                try:
                    value.sort()
                    other_value.sort()
                except AttributeError:
                    return False
        return value==other_value

    def __repr__(self):

        return f'Response: status={self.status} headers={self.headers} content={repr(self.content)}'

    def to_dict(self):

        # ak sa da, skonvertuj na retazec
        try:
            content=self.content.decode('utf-8')
        except UnicodeDecodeError:
            content=self.content
        d={
            'status':self.status,
            'headers':self.headers,
            'content':content
        }
        return d
            

class ResponseFromDict(Response):

    def __init__(self,d,request):

        for name in ('status','headers','content'):
            if not name in d:
                raise ValueError(f'{name} missing in response')
        if type(d['status'])!=int:
            raise ValueError('non-numeric status in response')
        self.status=d['status']
        self.headers=d['headers']
        self.content=d['content']
        if type(self.content) is str:
            self.content=self.content.encode('utf-8')
        self.request=request


class ResponseFromSocket(Response):
    
    def __init__(self,f,request):
        # citanie statusu

        self.request=request
        try:
            status_in=readline_tee(f)
        except TimeOutException:
            handle_timeout('reading status')
        try:
            status,status_desc=status_in.split(' ',1)
        except ValueError:
            print_and_flush('>>> Expected status line, got something else instead')
            print_and_flush('>>> Exitting test')
            sys.exit(1)
        try:
            self.status=int(status)
        except ValueError:
            print_and_flush('>>> Non-numerical status')
            print_and_flush('>>> Exitting test')
            sys.exit(1)
        # citanie hlaviciek
        self.headers={}
        while True:
            try:
                line_out=readline_tee(f)
            except TimeOutException:
                handle_timeout('reading headers',comment='Probably the server did not write empty line after headers')
            if line_out=='':
                print_and_flush('S->C: Server closed connection')
                break
            # prazdny riadok sa skonvertuje na '', newline z konca riadku prec
            line_out=line_out.rstrip()
            # hlavicka
            if ':' in line_out:
                name,value=line_out.split(':',1)
                # medzery zlava budem tolerovat
                value=value.lstrip()
                self.headers[name]=value
            # prazdny riadok -> koniec hlaviciek
            elif not line_out:
                print_and_flush('S->C: end of headers')
                break
            # ani hlavicka, ani prazdny riadok
            else:
                print_and_flush('>>> Expected a header, got something else instead')
                print_and_flush('>>> Exitting test')
                sys.exit(1)
        # citanie obsahu -- berie do uvahy hodnotu hlaviciek
        if 'Content-length' in self.headers:
            cl=int(self.headers['Content-length'])
            try:
                self.content=f.read(cl)
            except TimeOutException:
                handle_timeout('reading content')
            print_and_flush(f'S->C content: {repr(self.content)}')
        elif 'Number-of-messages' in self.headers:
            self.content=b''
            n=int(self.headers['Number-of-messages'])
            for i in range(n):
                try:
                    mbox=f.readline()
                except TimeOutException:
                    handle_timeout('reading content')
                print_and_flush(f'S->C: {repr(mbox)}')
                self.content=self.content+mbox
        else:
            self.content=b''

def response_to(request_d):
    
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(('localhost',9999))
    f=s.makefile(mode='rwb')
    request=Request(request_d)
    request.send(f)
    response=ResponseFromSocket(f,request)
    return response.to_dict()

if __name__=='__main__':
    QUIET=False
    signal.setitimer(signal.ITIMER_REAL,TIMEOUT)
    #signal.alarm(TIMEOUT)
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(('localhost',9999))
    f=s.makefile(mode='rwb')
    for req_resp_fnm in sorted(glob.glob('req_resp*.yaml')):
        with open(req_resp_fnm) as req_resp_file:
            # citanie testu z YAML suboru
            request_d,response_d=yaml.load_all(req_resp_file,Loader=yaml.Loader)
            print_and_flush('==================')
            print_and_flush(f'>>> Filename:{req_resp_fnm}')
            print_and_flush(f'---')
            # request, ktory posielam
            request=Request(request_d)
            # response, ktoru ocakavam
            try:
                response_expect=ResponseFromDict(response_d,request)
            except ValueError:
                print_and_flush(f'>>> File {req_resp_fnm} is not correct',file=sys.stderr)
                raise
            # vykonanie testu
            # posleme request
            request.send(f)
            print_and_flush(f'---')
            print_and_flush(f'>>> End request, awaiting response')
            # precitame response
            signal.setitimer(signal.ITIMER_REAL,TIMEOUT)
            # signal.alarm(TIMEOUT)
            try:
                response_real=ResponseFromSocket(f,request)
            except TimeOutException:
                print_and_flush(f'>>> Timeout after {TIMEOUT} seconds! (probably a deadlock)')
                print_and_flush('>>> Exitting test')
                sys.exit(1)
            print_and_flush('---')
            if response_real!=response_expect:
                print_and_flush('>>> Unexpected response:')
                print_and_flush('>>> Got response:',response_real)
                print_and_flush('>>> Expected:',response_expect)
                print_and_flush('>>> Exitting test')
                sys.exit(1)
            else:
                print_and_flush('>>> Got expected response, OK')
        

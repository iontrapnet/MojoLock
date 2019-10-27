import os, sys, time, struct, serial
from serial.tools import list_ports

PY3 = sys.version_info[0] == 3

mojo_ports = {(i.device if PY3 else i[0]):None for i in list_ports.comports()}

def mojo_open(port):
    if not mojo_ports[port]:
        mojo_ports[port] = serial.Serial(port=port,baudrate=500000,timeout=1)
    
def mojo_write64(port,addr,data,increment=False,binary=False):
    mojo_ports[port].write(struct.pack(b'<Bi',128+(64 if increment else 0)+len(data)-1,addr)
        + (b''.join(data) if binary else struct.pack(b'<'+b'i'*len(data),*data)))

def mojo_write(port,addr,data,increment=False,binary=False):
    i = 0
    while i + 64 < len(data):
        mojo_write64(port,addr,data[i:i+64],increment,binary)
        if increment: addr += 64
        i += 64
    mojo_write64(port,addr,data[i:],increment,binary)

def mojo_read64(port,addr,n,increment=False,binary=False):
    mojo_ports[port].write(struct.pack(b'<Bi',(64 if increment else 0)+n-1,addr))
    bytes = mojo_ports[port].read(size=4*n)
    return bytes if binary else struct.unpack(b'<'+b'i'*n,bytes)

def mojo_read(port,addr,n,increment=False,binary=False):
    data = b'' if binary else []
    i = 0
    while i + 64 < n:
        data += mojo_read64(port,addr,64,increment,binary)
        if increment: addr += 64
        i += 64
    data += mojo_read64(port,addr,n-i,increment,binary)
    return data

def mojo_close(port):
    try:
        mojo_ports[port].close()
    except:
        pass
    mojo_ports[port] = None

def reboot_mojo(ser, verbose):
    ser.setDTR(True)
    time.sleep(0.005)
    for i in range(0,5):
        ser.setDTR(False)
        time.sleep(0.005)
        ser.setDTR(True)
        time.sleep(0.005)
    if verbose:
        print('Rebooting Mojo')
    return

def erase_mojo(ser, verbose):
    reboot_mojo(ser, verbose)
    ser.write(b'E')
    ret = ser.read(1)
    if verbose and ret == 'D':
        print('Erased mojo successfully.')
    elif ret != 'D':
        print('Failed to erase Mojo.  Error code: ' + ret)
        sys.exit(1)
    ser.close()
    sys.exit(0)
    return

def display_progress(p, width=30):
    if p > 1:
        p = 1
    if p < 0:
        p = 0
    bar_width = int(width * p)
    rem_bar_width = int(width - bar_width)
    sys.stdout.write("\r[" + ("#" * bar_width) + (" " * rem_bar_width) +
                     ("] (%d%%)" % int(100 * p)))
    sys.stdout.flush()
        
def mojo_load(port, path, verbose = False, no_verify = True, ram = True, progress = False):
    ser = serial.Serial(port, 115200, timeout=10)
    try:
        f = open(path,'rb')
    except:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.basename(os.path.normpath(path.replace('\\','/'))))
        f = open(path,'rb')
    bits = f.read()
    length = len(bits)
    reboot_mojo(ser, verbose)
    
    if ram:
        ser.write(b'R')
        ret = ser.read(1)
        if verbose and  ret == b'R':
            print('Mojo is ready to recieve bitstream')
        elif ret != b'R':
            print('Mojo did not respond correctly! Make sure the port is correct')
            sys.exit(1)

    if not ram and no_verify:
        ser.write(b'F')
        ret = ser.read(1)
        if verbose and  ret == b'R':
            print('Mojo is ready to recieve bitstream')
        elif ret != b'R':
            print('Mojo did not respond correctly! Make sure the port is correct')
            sys.exit(1)

    if not ram and not no_verify:
        ser.write(b'V')
        ret = ser.read(1)
        if verbose and  ret == b'R':
            print('Mojo is ready to recieve bitstream')
        elif ret != b'R':
            print('Mojo did not respond correctly! Make sure the port is correct')
            sys.exit(1)

    buffer = struct.unpack("4B", struct.pack("I", length))
    buf = b''
    for i in buffer:
        buf+=bytearray([i])
    ser.write(buf)
    ret = ser.read(1)
    if verbose and  ret == b'O':
        print('Mojo acknowledged size of bitstream. Writing bitstream')
    elif ret != b'O':
        print('Mojo failed to acknowledge size of bitstream. Did not write')
        sys.exit(1)

    if progress:
        for i,bit in enumerate(bits):
            ser.write(bit)
            display_progress(float(i + 1)/length)
        sys.stdout.write('\n')
    else:
        ser.write(bits)

    ret = ser.read(1)
    if verbose and  ret == b'D':
        print('Mojo has been flashed')
    elif ret != b'D':
        print('Mojo failed to flash correctly')
        sys.exit(1)

    if not ram and not no_verify:
        ser.write(b'S')
        if verbose:
            print('Verifying Mojo')
        ret = ser.read(1)
        if  ret == b'\xAA' and verbose:
            print('First Byte was valid getting flash size.')
        elif ret != b'\xAA':
            print('Flash does not contain valid start byte.')
            sys.exit(1)
        ret = ser.read(4)
        flash_length = struct.unpack("I", ret)[0] - 5
        if  flash_length == length and verbose:
            print('Flash and local bitstream match file size.')
        elif flash_length == length:
            print('Flash is not same size as local bitstream.')
            sys.exit(1)
        ret = ser.read(length)
        if  ret == bits  and verbose:
            print('Flash and local bitstream are a match.')
        elif ret == bits:
            print('Flash and local bitstream do not match.')
            sys.exit(1)
    if not ram:
        ser.write(b'L')
        ret = ser.read(1)
        if verbose and  ret == b'D':
            print('Mojo has been loaded bitsream')
        elif ret != b'D':
            print('Mojo failed to load bitstream')
            sys.exit(1)
            
    ser.close()

import Pyro4
@Pyro4.expose    
class Mojo:
    def __init__(self):
        self.port = None
    
    @staticmethod
    def ports():
        return [i for i in mojo_ports.keys()]
        
    def open(self, port):
        if port:
            mojo_open(port)
            self.port = port
        
    def close(self):
        if self.port:
            mojo_close(self.port)
            self.port = None
    
    def load(self, path):
        if self.port: 
            mojo_close(self.port)
            mojo_load(self.port, path)
            mojo_open(self.port)
        
    def write(self, addr, data, increment=False, binary=False, id=''):
        if self.port: mojo_write(self.port, addr, data, increment, binary)
    
    def read(self, addr, n, increment=False, binary=False, id=''):
        if self.port: return mojo_read(self.port, addr, n, increment, binary)
    
if __name__ == '__main__':    
    #HOST = '127.0.0.1'
    HOST = '192.168.1.2'
    Pyro4.config.SERIALIZER = 'pickle'
    Pyro4.SERIALIZERS_ACCEPTED = 'pickle'
    daemon = Pyro4.Daemon(HOST,8000)                
    ns = Pyro4.locateNS()                  
    uri = daemon.register(Mojo())
    ns.register("mojo", uri) 
    daemon.requestLoop()   

    #import zerorpc
    #s = zerorpc.Server(Mojo())
    #s.bind('tcp://0.0.0.0:8000')
    #s.run()

#    port = 'COM3'
#    mojo = Mojo()
#    mojo.open(port)    
#    with f=open('led_wave.bin')
#        mojo.load(f.read())
    
#    for i in range(10):
#        #mojo.write(0,range(4096))
#        tic=time.time()
#        mojo.read(0,1000)
#        toc=time.time()-tic
#        print(toc)
#       
#    mojo.close()
#    
#    try:
#        for i in range(10):
#            time.sleep(0.1)
#            print(mojo['read'])
#    except KeyboardInterrupt:
#        mojo.quit()

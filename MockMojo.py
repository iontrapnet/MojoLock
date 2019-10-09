import sys, time, struct, threading
import Task

class Reg:#Bit s
    def __init__(self, width, init = 0, signed = True):
        self.width = int(width)
        self.mask = (1 << self.width) - 1
        self.value = int(init)
        self.signed() if signed else self.unsigned()
    
    def signed(self):
        self.sign = 1 << (self.width - 1)
        return self
    
    def unsigned(self):
        self.sign = 0
        return self
            
    def __le__(self, x):
        self.value = int(x) & self.mask
    
    def __abs__(self):
        return self.value
             
    def __int__(self):
        return (self.value - self.mask - 1) if (self.value & self.sign) else self.value
        
    def __repr__(self):
        return repr(self.width)+'b'+bin(self.value)[2:2+self.width].zfill(self.width)
        
    def __len__(self):
        return self.width
    
    def __getitem__(self, item):
        if isinstance(item, slice):
            indices = item.indices(len(self))
            #r = 0
            #for i in range(*indices):
            #    r += self.value & (1 << int(i))
            #r >>= indices[0]
            r = (self.value & ((1 << indices[1]) - 1)) >> indices[0]
            return Reg(self.width - indices[0], r, self.sign)
        elif 0 <= item < self.width:
            return (self.value >> int(item)) & 1
        else:
            raise StopIteration

        
class Sig(Reg):
    def __init__(self, width, init = 0, signed = True):
        Reg.__init__(self, width, init, signed)
        self.out = []
        
    def __le__(self, x):
        Reg.__le__(self, x)
        for o in self.out:
            o <= self
    
    def __repr__(self):
        return Reg.__repr__(self)+('->'+repr(self.out) if self.out else '')
    
    def __iadd__(self, x):
        if x not in self.out:
            self.out.append(x)
        return self
    
    def __isub__(self, x):
        if x in self.out:
            self.out.remove(x)
        return self
                
class DSP:
    def __init__(self):
        self.once = Reg(1)
        self.done = Sig(1)
        #self.done += self.once
                
    def do(self):
        pass
    
    def run(self):
        #self.done <= 0
        if abs(self.once):
            self.once <= 0
            self.do()
            self.done <= 1

class DDS(DSP):
    def __init__(self):
       DSP.__init__(self)
       self.f = [Reg(16, 0, False)]*1
       self.p = [Reg(16, 0, False)]*1
       self.i = [Sig(16)]*1
       self.q = [Sig(16)]*1
       
class ROM(DSP):
    def __init__(self):
        DSP.__init__(self)
        self.IN = Reg(16, 0, False)
        self.OUT = Sig(16, 0, False)
        self.ram = None
        self.write = False
        self.addr = 0
    
    def do(self):
        if self.write:
            self.ram[self.addr] = abs(self.IN)
            self.addr += 1
            if self.addr == len(self.ram):
                self.write = False
                self.addr = 0
        elif self.IN[10]:
            if abs(self.IN[0:10]):
                self.ram = [0]*(abs(self.IN[0:10])+1)
                self.write = True
            else:
                self.OUT <= self.ram[self.addr]
                self.addr += 1
                if self.addr == len(self.ram):
                    self.addr = 0
        else:
            self.addr = abs(self.IN)
            self.OUT <= self.ram[self.addr]
            
class LIA(DSP):
    def __init__(self):
        DSP.__init__(self)
        self.IN0 = Reg(16)
        self.IN1 = Reg(16)
        self.OUT = Sig(16)
         
class PID(DSP):
    def __init__(self):
        DSP.__init__(self)
        self.IN = Reg(16)
        self.S = Reg(16)
        self.O = Reg(16)
        self.P = Reg(16)
        self.I = Reg(16)
        self.OUT = Sig(16)
        self.IVAL = Reg(16)
        self.ival = Reg(24)
        
    def do(self):
        s = (-int(self.S)) if int(self.P) == -0x8000 else (int(self.IN) - int(self.S))
        self.ival <= (0 if int(self.I[0:12]) == -0x800 else (int(self.ival) + int(self.I[0:12]) * s))
        self.IVAL <= int(self.ival) >> 8
        p = (0 if int(self.P) == -0x8000 else ((int(self.P) * s) >> 8))
        self.OUT <= ((int(self.IVAL) + p) >> abs(self.I[12:])) + int(self.O)

class ADC(DSP):
    def __init__(self):
        DSP.__init__(self)
        self.OUT = [Sig(16)]*5
        
class DAC(DSP):
    def __init__(self):
        DSP.__init__(self)
        self.IN0 = Reg(16)
        self.IN1 = Reg(16)
                    
class Mojo(Task.Task):
    def __init__(self):
        Task.Task.__init__(self)
        self.dds = DDS()
        self.rom = ROM()
        self.lia = [LIA()]*3
        self.pid = [PID()]*3
        self.adc = ADC()
        self.dac = [DAC()]*2
        
        self.mem = [0]*8192
        self.addr = 0
        self.view = [0,0,0]
        self.state = 0
        self.top = threading.Thread(target=self.run)
        self.top.setDaemon(True)
        self.top.start()
        
        self.dsp = [self.dds,self.rom]+self.lia+self.pid+[self.adc]+self.dac
        self.once = [d.once for d in self.dsp]
        self.once[0] = self.once[1]
        self.done = [0]+[d.done for d in self.dsp]+[1]
        self.done[1] = self.done[2]
        self.IN = [self.rom.IN,self.lia[0].IN0,self.lia[0].IN1,self.lia[1].IN0,
            self.lia[1].IN1,self.lia[2].IN0,self.lia[2].IN1]+[p.IN for p in self.pid]\
            +[self.dac[0].IN0,self.dac[0].IN1,self.dac[1].IN0,self.dac[1].IN1]
        self.OUT = [0,self.dds.i[0],self.dds.q[0],self.rom.OUT]+[l.OUT for l in self.lia]+[p.OUT for p in self.pid]+self.adc.OUT
        
        self.OUT[7] += self.IN[0]
        self.done[6] += self.once[1]
        self.done[1] += self.once[5]
        self.pid[0].once <= 1
        
    def run(self):
        while not self._quit.is_set():
            if self.state > 0:
                for d in self.dsp:
                    d.run()
                if abs(self.done[self.view[0]]):
                    self.mem[self.addr] = struct.unpack(b'<i',struct.pack(b'<hh',
                            abs(self.OUT[self.view[1]]),abs(self.OUT[self.view[2]])))[0]
                    self.addr += 1
                    if self.addr == len(self.mem):
                        self.addr = 0
                        self.view[0] = 0
                
    @staticmethod
    def ports():
        return ['Mock']
        
    def open(self, port):
        pass
        
    def close(self):
        pass
    
    def load(self, path):
        pass
            
    def write1(self, addr, x):
        if addr == 0:
            self.addr = 0
            size = (x & 0xFFFF0000) >> 16
            if size: self.mem = [0]*size
            self.state = x & 0xF
            self.view = [(x & 0xF0) >> 4,(x & 0xF00) >> 8,(x & 0xF000) >> 12]
        elif addr == 3:
            self.rom.IN <= x
            self.rom.do()
        elif addr == 7:
            o, s = struct.unpack(b'<hh', struct.pack(b'<i', x))
            self.pid[0].S <= s 
            self.pid[0].O <= o
        elif addr == 8:
            i, p = struct.unpack(b'<hh', struct.pack(b'<i', x))
            self.pid[0].P <= p
            self.pid[0].I <= i
    
    @Task.task        
    def write(self, addr, data, increment=False, binary=False, id=''):
        if binary:
            pass
        for x in data:
            self.write1(addr, x)
            if increment: addr += 1
    
    def read1(self, addr):
        if addr == 1:
            return 0
        return 0
    
    @Task.task            
    def read(self, addr, n, increment=False, binary=False, id=''):
        if addr == 0 and not increment:
            r = self.mem[0:n]
        else:
            r = []
            for i in range(n):
                r.append(self.read1(addr))
                if increment: addr += 1
        if binary:
            r = struct.pack(b'<'+b'i'*len(r),*r)
        return r
        
if __name__ == '__main__':
    if False:
        x = Reg(16, 2)
        x <= int(x) ** 2
        print(x)
    mojo = Mojo()
    wave = [(0.02*i-10.23)**2 for i in range(1024)]
    wave = [int(255*x/(x+1)) for x in wave]
    mojo.write(3, [2047] + wave)
    s = -2048
    o = 512
    mojo.write(7, struct.unpack(b'<i', struct.pack(b'<hh', int(o), int(s))))
    p = -0x8000
    a = 6
    i = 8
    mojo.write(8, struct.unpack(b'<i', struct.pack(b'<Hh', 4096*int(a)+(int(i) if int(i)>=0 else 4096+int(i)), int(p))))
    time.sleep(0.001)
    if False:
        for i in range(1000):
            mojo.pid0.once <= 1
            time.sleep(0.001)
            print(int(mojo.pid0.OUT))
        print(mojo.pid0.done)
    #mojo.rom.IN = mojo.pid[0].OUT
    mojo.pid[0].OUT += mojo.rom.IN
    if False:
        mojo.pid[0].done += mojo.rom.once
        for i in range(2000):
            mojo.pid[0].once <= 1
            time.sleep(0.001)
            print(int(mojo.rom.OUT))
    if True:
        state = 1
        t = 2
        X = 3
        Y = 0
        mojo.write(0, [16*(16*(16*Y+X)+t)+state])
        mojo.pid[0].done += mojo.rom.once
        mojo.rom.done += mojo.pid[0].once
        mojo.pid[0].once <= 1
        time.sleep(0.5)
        mojo.read(0,8192,False,False,id=0)
        time.sleep(0.1)
        print(mojo['read0'])
    if False:
        tic = time.time()
        for i in range(len(mem)):
            mojo.pid[0].do()
            mojo.rom.do()
        print(time.time()-tic)
    mojo.quit()
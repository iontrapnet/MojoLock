import sys, bisect

PY3 = sys.version_info[0] == 3

if PY3:
    #from qcustomplot import *
    import numpy as np
else:
    #from PyQt4.qcustomplot import *
    import np

#import __main__

def CLS(self):
    self.output()

def EVAL(self):
    window = self
    expr = yield 'Expr'
    while expr not in ('exit', 'quit'):
        if expr.find('=') > 0:
            exec(expr)
        else:
            self.output(eval(expr))
        expr = yield 'Expr'

Window_waitNext = 0
def WAIT(t):
    global Window_waitNext
    Window_waitNext = int(t)
                
def TEST(self, wait = 5):
    self.setState(1)
    rect = self.plot.rects[(0, 0)]
    rect.xy = True
    WAIT(wait)
    lia_o = yield 'Scanning to find LIA0 Offset...'
    lia_o = int(lia_o) 
    self.lia0.setValue(lia_o, 0, 9)
    self.Y.setValue('LIA0')
    WAIT(wait)
    pid_o = yield 'Scanning to find PID0 Offset...'
    pid_o = int(pid_o)
    self.pid0.setSO(0, pid_o)
    self.pid0.setPAI(0, 6, -2048)
    self.pid0.setPAI(0, 6, -1)
    self.X.setValue('ROM')
    rect.xy = False
    rect.rescale = False
    rect.axis(1).setRange(-10, lia_o)
    rect.axis(2).setRange(-500, 500)
    WAIT(wait)
    yield 'Locking...'
    self.pid0.setSO(150, pid_o)
    WAIT(wait)
    yield 'Testing...'
    self.pid0.setSO(0, pid_o)

def LOCK0(self, wait = 0):
    self.lia0.setValue(0, 0, 9)
    self.pid0.setSO(-2048, 0)
    self.pid0.setPAI(-32768, 2, -2048)
    self.pid0.setPAI(-32768, 2, 1)
    self.view.setValue('399')
    self.X.setValue('PID0')
    self.Y.setValue('ADC0')
    self.view_all = False
    self.timer_view = 0
    rect = self.plot.rects[(0, 0)]
    rect.rescale = True
    rect.xy = True
    WAIT(wait)
    lia_o = yield 'Scanning to find LIA0 Offset...'
    lia_o = int(lia_o)
    if not lia_o: return
    self.lia0.setValue(lia_o, 0, 9)
    self.Y.setValue('LIA0')
    WAIT(wait)
    pid_o = yield 'Scanning to find PID0 Offset...'
    pid_o = int(pid_o)
    if not pid_o: return
    self.pid0.setSO(0, pid_o)
    self.pid0.setPAI(0, 2, -2048)
    self.pid0.setPAI(0, 2, 1)
    self.X.setValue('ADC0')
    rect.xy = False
    rect.rescale = False
    rect.axis(1).setRange(lia_o-50, lia_o+200)
    rect.axis(2).setRange(-1000, 1000)
    if not PY3: rect.axes()[3].setRange(0, self.size)
    WAIT(wait)
    yield 'Locking...'
    self.pid0.setSO(150, pid_o)
    WAIT(wait)
    yield 'Testing...'
    self.pid0.setSO(0, pid_o)
    self.view_all = True

def LOCK1(self, wait = 0):
    self.lia1.setValue(0, 0, 9)
    self.pid1.setSO(-2048, 0)
    self.pid1.setPAI(-32768, 2, -2048)
    self.pid1.setPAI(-32768, 2, 1)
    self.view.setValue('370')
    self.X.setValue('PID1')
    self.Y.setValue('ADC1')
    self.view_all = False
    self.timer_view = 1
    rect = self.plot.rects[(0, 1)]
    rect.rescale = True
    rect.xy = True
    WAIT(wait)
    lia_o = yield 'Scanning to find LIA1 Offset...'
    lia_o = int(lia_o)
    if not lia_o: return
    self.lia1.setValue(lia_o, 0, 9)
    self.Y.setValue('LIA1')
    WAIT(wait)
    pid_o = yield 'Scanning to find PID1 Offset...'
    pid_o = int(pid_o)
    if not pid_o: return
    self.pid1.setSO(0, pid_o)
    self.pid1.setPAI(0, 2, -2048)
    self.pid1.setPAI(0, 2, -1)
    self.X.setValue('ADC1')
    rect.xy = False
    rect.rescale = False
    rect.axis(1).setRange(lia_o-50, lia_o+200)
    rect.axis(2).setRange(-1000, 1000)
    if not PY3: rect.axes()[3].setRange(0, self.size)
    WAIT(wait)
    yield 'Locking...'
    self.pid1.setSO(150, pid_o)
    WAIT(wait)
    yield 'Testing...'
    self.pid1.setSO(0, pid_o)
    self.view_all = True

def LOCK2(self, wait = 0):
    self.pid2.setSO(-2048, 0)
    self.pid2.setPAI(-32768, 2, -2048)
    self.pid2.setPAI(-32768, 2, 1)
    self.view.setValue('Lamp')
    self.X.setValue('PID2')
    self.Y.setValue('ADC23')
    self.view_all = False
    self.timer_view = 2
    rect = self.plot.rects[(0, 2)]
    rect.rescale = True
    rect.xy = True
    WAIT(wait)
    pid_o = yield 'Scanning to find PID2 Offset...'
    pid_o = int(pid_o)
    if not pid_o: return
    self.pid2.setSO(0, pid_o)
    self.pid2.setPAI(0, 2, -2048)
    self.pid2.setPAI(0, 2, 1)
    rect.xy = False
    rect.rescale = False
    rect.axis(1).setRange(pid_o-3000, pid_o+3000)
    rect.axis(2).setRange(-1500, 1500)
    if not PY3: rect.axes()[3].setRange(0, self.size)
    WAIT(wait)
    yield 'Locking...'
    self.pid2.setSO(150, pid_o)
    WAIT(wait)
    yield 'Testing...'
    self.pid2.setSO(0, pid_o)
    self.view_all = True
                    
def Window_doRun(self, *args):
    WAIT(0)
    cmd = self.input()
    if self.doNext:
        try:
            self.btnRun.setText(self.doNext.send(cmd))
        except StopIteration:
            self.doNext = None
            self.btnRun.setText('Run')
    else:
        cmd = cmd.split(' ')
        self.doNext = getattr(sys.modules[__name__], cmd[0].upper(), None)
        if self.doNext:
            self.doNext = self.doNext(self, *cmd[1:])
            if self.doNext: self.btnRun.setText(next(self.doNext))
    self.input('')

def Window_doTimeout(self):
    global Window_waitNext
    if Window_waitNext > 0:
        Window_waitNext -= 1
        if Window_waitNext == 0:
            self.btnRun.click()

def find_zero(t, x, y):
    pass
    #yamin, yamax = y.argmin(), y.argmax()
    #if yamin < yamax:
    #    o = yamin+bisect.bisect(t[yamin:yamax],(0,0))#-0.35*(yamax-yamin)
    #else:
    #    o = yamax+bisect.bisect(t[yamax:yamin],(0,0))
    #o = x[int(o)]
    #o = int((x[y.argmin()]+x[y.argmax()])/2)
    #return o
                    
def PlotCtrl_setData(self, row, col, x, y):
    rect = self.rects.get((row, col), None)
    if not rect: return
    window = self.window
    state = window.state.text()
    view = (window.view.text(),) + window.views[window.timer_view][2:]
    #t = zip(x, y)
    #t.sort()
    #x, y = zip(*t)
    #t = zip(y, x)        
    y = np.array(y)
    #self.setToolTip('hehe')    
    if state == 'TEST':
        if rect.xy:
            if view == ('', 'DDS', 'PID0', 'ROM'):
                if window.doNext: window.input(y.max())
                rect.x = x[y.argmin()]
                rect.y = None
            elif view == ('', 'DDS', 'PID0', 'LIA0'):
                o = int((x[y.argmin()]+x[y.argmax()])/2)
                if window.doNext: window.input(o)
                rect.x = o
                rect.y = None
    elif state == 'RUN':
        if rect.xy:
            if view in (('399', 'DDS', 'PID0', 'ADC0'), ('370', 'DDS', 'PID1', 'ADC1')):
                if window.doNext: window.input(y.min())
                rect.x = x[y.argmax()]
                rect.y = None
            elif view in (('399', 'DDS', 'PID0', 'LIA0'), ('370', 'DDS', 'PID1', 'LIA1'), ('Lamp', 'ADC', 'PID2', 'ADC23')):
                o = int((x[y.argmin()]+x[y.argmax()])/2)
                if window.doNext: window.input(o)
                rect.x = o
                rect.y = None
        #rect.xy = False
        #rect.rescale = False
        #rect.axis(1).setRange(-10, 10)
        #rect.axis(2).setRange(-100, 100)
                    
def Window_setState(self, state):
    state = self.states[state]
    if state == 'IDLE':
        self.mojo.write(15, [0])
    elif state == 'TEST':
        self.plot.resetGrid(1, 1)
        self.view_all = True
        self.timer_view = 0
        self.views = [(0, 0, 'DDS', 'PID0', 'ROM')]
        self.view.setItems([''])
        self.dds0.setValue(51200, 13, 0)
        self.lia0.setValue(0, 0, 9)
        self.pid0.setSO(-2048, 512)
        self.pid0.setPAI(-32768, 6, -2048)
        self.pid0.setPAI(-32768, 6, 1)
        self.config({'ROM':'DDS0I', 'LIA0X':'ROM', 'LIA0Y':'DDS0Q', 'PID0':'LIA0'}, {'DDS':'PID0', 'ROM':'DDS', 'LIA0':'ROM', 'PID0':'LIA0'})
        self.mojo.write(1, [0])
    elif state == 'RUN':
        if False:
            self.plot.resetGrid(1, 3)
            self.view_all = True
            #self.timer.stop()
            #self.timer.start(500)
            #self.setSize(4095)
            self.timer_view = 0
            self.views = [(0, 0, 'DDS', 'PID0', 'ADC0'), (0, 1, 'DDS', 'PID1', 'ADC1'), (0, 2, 'ADC', 'ADC2', 'ADC3')]
            self.view.setItems(['399', '370', 'Lamp'])
            self.dds0.setValue(30000, 2, 0)
            self.lia0.setValue(0, 0, 9)
            self.pid0.setSO(-2048, 0)
            self.pid0.setPAI(-32768, 2, -2048)
            self.pid0.setPAI(-32768, 2, 1)
            self.lia1.setValue(0, 0, 9)
            self.pid1.setSO(-2048, 0)
            self.pid1.setPAI(-32768, 2, -2048)
            self.pid1.setPAI(-32768, 2, 1)
            self.pid2.setSO(-2048, 0)
            self.pid2.setPAI(-32768, 2, -2048)
            self.pid2.setPAI(-32768, 2, 1)
            self.config({'DAC0A':'DDS0I','LIA0Y':'DDS0Q','LIA0X':'ADC0','PID0':'LIA0','DAC0B':'PID0', 'LIA1Y':'DDS0Q','LIA1X':'ADC1','PID1':'LIA1','DAC1B':'PID1', 'PID2':'ADC23','DAC1A':'PID2'}, {'DAC0':'DDS','ADC':'DAC0','LIA0':'ADC','PID0':'LIA0','LIA1':'ADC','PID1':'LIA1','DAC1':'PID1','DDS':'DAC1', 'PID2':'ADC'})
        else:
            self.plot.resetGrid(1, 1)
            self.timer_view = 0
            self.views = [(0, 0, 'ADC', 'ADC2', 'ADC3')]
            self.view.setItems(['Lamp'])
            self.pid2.setSO(-2048, 0)
            self.pid2.setPAI(-32768, 2, -2048)
            self.pid2.setPAI(-32768, 2, 1)
            self.config({'PID2':'ADC23','DAC1A':'PID2'}, {'PID2':'ADC','DAC1':'PID2','ADC':'ON'})
        
        #self.views = [(0, 0, 'DDS', 'DDS0I', 'LIA0')]
        #self.view.setItems([''])
        #self.dds0.setValue(51200, 13, 0)
        #self.lia0.setValue(0, 2, 9)
        #self.config({'LIA0X':'DDS0I', 'LIA0Y':'DDS0Q'}, {'DDS':'LIA0', 'LIA0':'DDS'})
        self.mojo.write(1, [0])

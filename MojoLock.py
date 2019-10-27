import os, sys, math, struct
from functools import wraps

PY3 = sys.version_info[0] == 3

if PY3:
    from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtNetwork import *
    from qcustomplot import *
else:
    from PyQt4 import QtCore, QtGui, QtNetwork, qcustomplot
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    from PyQt4.QtNetwork import *
    from PyQt4.qcustomplot import *

FPS = 1
if True:
    from MojoTask import MojoTask
    from Mojo import Mojo
    #from MockMojo import MockMojo as Mojo 
    mojo = MojoTask(Mojo())
else:
    from RemoteMojo import mojo_task as mojo

import MojoLock_Script
import lupa
L = lupa.LuaRuntime()

def script(lang = ''):
    def script_wrap(func):
        @wraps(func)
        def script_func(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)
            if not lang or lang == 'python':
                pyfunc = getattr(MojoLock_Script, self.__class__.__name__ + '_' + func.__name__, None)
                if pyfunc:
                    if hasattr(pyfunc, 'next'):
                        pyfunc.send(self, *args)
                    else:
                        pyfunc(self, *args, **kwargs)
            if not lang or lang == 'lua':
                lfunc = L.globals()[self.__class__.__name__ + '_' + func.__name__]
                if lfunc:
                    ltype = lupa.lua_type(lfunc)
                    if ltype == 'function':
                        lfunc(self, *args)
                    elif ltype == 'thread':
                        lfunc.send(self, *args)
            return ret
        return script_func
    return script_wrap
    
def script_reload(path):
    if path[-3:] == '.py':
        if PY3:
            import imp
            reload = imp.reload
        reload(MojoLock_Script)
    elif path[-4:] == '.lua':
        L.execute("dofile('" + str(path).replace('\\', '\\\\') + "')")
        
script_watcher = QFileSystemWatcher()
script_path = {'python':os.path.basename(__file__).replace('.py', '_Script.py'), 'lua':os.path.basename(__file__).replace('.py', '_Script.lua')}
for path in script_path.values():
    script_watcher.addPath(os.path.join(os.path.dirname(os.path.realpath(__file__)), path))
script_watcher.fileChanged.connect(script_reload)
        
class EnumCtrl:
    def __init__(self, parent = None, label = None, func = None):
        if isinstance(parent, QLayout):
            row = QHBoxLayout()
            parent.addLayout(row)
        else:
            row = QHBoxLayout(parent)
        if label:
            self.label = QLabel(label)
            self.label.setFont(QFont("Microsoft YaHei", 12))
            row.addWidget(self.label)
        self.enum = QComboBox()
        self.enum.setFont(QFont("Microsoft YaHei", 12))
        row.addWidget(self.enum)
        if func: self.enum.currentIndexChanged.connect(func)
        
    def setItems(self, items):
        self.enum.clear()
        self.enum.addItems(items)
    
    def value(self):
        return int(self.enum.currentIndex())
    
    def setValue(self, value):
        if isinstance(value, str):
            value = self.enum.findText(value)
        self.enum.setCurrentIndex(value)
        
    def text(self):
        return str(self.enum.currentText())
            
class LVSpinBox(QDoubleSpinBox):
    stepChanged = pyqtSignal()

    def stepBy(self, step):
        value = self.value()
        point = str(self.text()).find('.')
        if point < 0:
            point = len(str(self.text()))
        digit = point - self.lineEdit().cursorPosition()
        if digit < 0:
            digit += 1
        self.setValue(value + step*(10**digit))
        if self.value() != value:
            self.stepChanged.emit()

    def onValueChanged(self,func):
        self.editingFinished.connect(func)
        self.stepChanged.connect(func)

class LVNumCtrl:
    def __init__(self, parent = None, label = '', func = None):
        if isinstance(parent, QLayout):
            col = QVBoxLayout()
            parent.addLayout(col)
        else:
            col = QHBoxLayout(parent)
        self.label = QLabel(label)
        self.spin = LVSpinBox()
        if func: self.spin.onValueChanged(func)
        
        self.label.setFont(QFont("Microsoft YaHei", 14))
        self.spin.setFont(QFont("Microsoft YaHei", 16))
        
        col.addWidget(self.label)
        col.addWidget(self.spin)
        
    def value(self):
        return self.spin.value()

    def setValue(self, val):
        self.spin.setValue(val)

class GroupCtrl:
    def __init__(self, parent = None, label = ''):
        if isinstance(parent, QLayout):
            self.group = QGroupBox()
            parent.addWidget(self.group)
        else:
            self.group = QGroupBox(parent)
        self.group.setFont(QFont("Microsoft YaHei", 12))
        self.group.setTitle(label)
        
class DDSCtrl(GroupCtrl):
    def __init__(self, parent = None, label = '', mojo = None, addr = 0):
        GroupCtrl.__init__(self, parent, label)
        
        self.mojo = mojo
        self.addr = addr
        
        row = QHBoxLayout(self.group)
        self.f = LVNumCtrl(row, 'Freq', self.setValue)
        self.a = LVNumCtrl(row, 'Atten', self.setValue)
        self.p = LVNumCtrl(row, 'Phase', self.setValue)
        
        self.f.spin.setDecimals(0)
        self.f.spin.setRange(0, 65535)
        
        self.a.spin.setDecimals(0)
        self.a.spin.setRange(0, 15)
        
        self.p.spin.setDecimals(3)
        self.p.spin.setRange(0, 2)
    
    def setValue(self, f = None, a = None, p = None):
        if f == None:
            f = self.f.value()
        else:
            self.f.setValue(f)
        if a == None:
            a = self.a.value()
        else:
            self.a.setValue(a)
        if p == None:
            p = self.p.value()
        else:
            self.p.setValue(p)
        self.mojo.write(self.addr,  struct.unpack(b'<i', struct.pack(b'<HH', int(f), 4096*int(a)+int(2048*p+0.5))))

class LIACtrl(GroupCtrl):
    def __init__(self, parent = None, label = '', mojo = None, addr = 0):
        GroupCtrl.__init__(self, parent, label)

        self.mojo = mojo
        self.addr = addr
        
        row = QHBoxLayout(self.group)
        
        #self.once = QComboBox()
        #self.in0 = QComboBox()
        #self.in1 = QComboBox()
        self.s = LVNumCtrl(row, 'Offset', self.setValue)
        self.a = LVNumCtrl(row, 'Atten', self.setValue)
        self.f = LVNumCtrl(row, 'Cutoff', self.setValue)
        
        self.s.spin.setDecimals(0)
        self.s.spin.setRange(-32768, 32767)
        
        self.a.spin.setDecimals(0)
        self.a.spin.setRange(0, 15)
        
        self.f.spin.setDecimals(0)
        self.f.spin.setRange(0, 15)
        
    def setValue(self, s = None, a = None, f = None):
        if s == None:
            s = self.s.value()
        else:
            self.s.setValue(s)
        if a == None:
            a = self.a.value()
        else:
            self.a.setValue(a)
        if f == None:
            f = self.f.value()
        else:
            self.f.setValue(f)
        self.mojo.write(self.addr, struct.unpack(b'<i', struct.pack(b'<Hh', 16*int(a)+int(f), int(s))))
        
class PIDCtrl(GroupCtrl):
    def __init__(self, parent = None, label = '', mojo = None, addr = 0):
        GroupCtrl.__init__(self, parent, label)

        self.mojo = mojo
        self.addr = addr
                
        col = QVBoxLayout(self.group)
        row = QHBoxLayout()
        col.addLayout(row)
        
        self.s = LVNumCtrl(row, 'Setpoint', self.setSO)
        self.o = LVNumCtrl(row, 'Offset', self.setSO)
        self.a = LVNumCtrl(row, 'Atten', self.setPAI)
        
        row = QHBoxLayout()
        col.addLayout(row)
        self.p = LVNumCtrl(row, 'P', self.setPAI)
        self.i = LVNumCtrl(row, 'I', self.setPAI)
        self.ival = LVNumCtrl(row, 'IVAL')
        
        self.s.spin.setDecimals(0)
        self.s.spin.setRange(-32768, 32767)
        
        self.o.spin.setDecimals(0)
        self.o.spin.setRange(-32768, 32767)
        
        self.a.spin.setDecimals(0)
        self.a.spin.setRange(0, 15)
        
        self.p.spin.setDecimals(0)
        self.p.spin.setRange(-32768, 32767)
        
        self.i.spin.setDecimals(0)
        self.i.spin.setRange(-2048, 2047)
        
        self.ival.spin.setDecimals(0)
        self.ival.spin.setRange(-32768, 32767)
        self.ival.spin.setEnabled(False)
        self.ival.spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        
    def setSO(self, s = None, o = None):
        if s == None:
            s = self.s.value()
        else:
            self.s.setValue(s)
        if o == None:
            o = self.o.value()
        else:
            self.o.setValue(o)
        self.mojo.write(self.addr, struct.unpack(b'<i', struct.pack(b'<hh', int(o), int(s))))
    
    def setPAI(self, p = None, a = None, i = None):
        if p == None:
            p = self.p.value()
        else:
            self.p.setValue(p)
        if a == None:
            a = self.a.value()
        else:
            self.a.setValue(a)
        if i == None:
            i = self.i.value()
        else:
            self.i.setValue(i)
        self.mojo.write(self.addr + 1, struct.unpack(b'<i', struct.pack(b'<Hh', 4096*int(a)+(int(i) if int(i)>=0 else 4096+int(i)), int(p))))

class PlotCtrl(QCustomPlot):
    def __init__(self, window):
        QCustomPlot.__init__(self)
        self.window = window
        
        self.setInteractions(QCP.Interactions(QCP.iRangeDrag | QCP.iRangeZoom | QCP.iSelectAxes | QCP.iSelectLegend))
        self.mousePress.connect(self.onMousePress)
        self.mouseWheel.connect(self.onMouseWheel)
        #self.mouseDoubleClick.connect(self.mouseDoubleClick)
        self.axisDoubleClick.connect(self.onAxisDoubleClick)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onContextMenu)
        self.menu = QMenu()
        self.menu.rescale = QAction("Rescale",self.menu,checkable=True)
        self.menu.addAction(self.menu.rescale)
        self.menu.xy = QAction("XY",self.menu,checkable=True)
        self.menu.addAction(self.menu.xy)
        self.menu.x = self.menu.addAction("X:")
        self.menu.y = self.menu.addAction("Y:")
        
        self.rects = None
        self.resetGrid(1, 1)
        
        self.show()    
    
    def resetGrid(self, nrows, ncols):
        if self.rects:
            for rect in self.rects.values():
                for graph in rect.graph:
                    self.removeGraph(graph)
        self.rects = {}
        self.plotLayout().clear()
        
        for i in range(nrows):
            for j in range(ncols):
                self.addRect(i, j)
        
        self.replot()
            
    def addRect(self, row, col):
        rect = QCPAxisRect(self)
        self.rects[(row, col)] = rect
        rect.setupFullAxesBox(True)
        rect.axis(QCPAxis.atTop).setTicks(False)
        rect.setMinimumSize(400,400)
        self.plotLayout().addElement(row, col, rect)
        rect.axis(QCPAxis.atRight).setTickLabels(True)
        rect.graph = [self.addGraph(rect.axis(QCPAxis.atBottom), rect.axis(QCPAxis.atLeft)), self.addGraph(rect.axis(QCPAxis.atBottom), rect.axis(QCPAxis.atRight))] 
        rect.graph[1].setPen(QPen(Qt.red))
        rect.rescale = True
        rect.xy = False
        rect.x = None
        rect.y = None   
    
    def currentRect(self, pos):
        for rect in self.rects.values():
            if rect.left()<pos.x()<rect.right() and rect.top()<pos.y()<rect.bottom():
                return rect
                
    def onMousePress(self, event):
        rect = self.currentRect(event.pos())
        if not rect: return
        if int(rect.axis(QCPAxis.atBottom).selectedParts()) & QCPAxis.spAxis:
            rect.setRangeDrag(rect.axis(QCPAxis.atBottom).orientation())
        elif int(rect.axis(QCPAxis.atLeft).selectedParts()) & QCPAxis.spAxis:
            rect.setRangeDragAxes(rect.axis(QCPAxis.atBottom), rect.axis(QCPAxis.atLeft))
            rect.setRangeDrag(rect.axis(QCPAxis.atLeft).orientation())
        elif int(rect.axis(QCPAxis.atRight).selectedParts()) & QCPAxis.spAxis:
            rect.setRangeDragAxes(rect.axis(QCPAxis.atBottom), rect.axis(QCPAxis.atRight))
            rect.setRangeDrag(rect.axis(QCPAxis.atRight).orientation())
        else:
            rect.setRangeDrag(Qt.Horizontal | Qt.Vertical)
    
    def onMouseWheel(self, event):
        rect = self.currentRect(event.pos())
        if not rect: return
        if int(rect.axis(QCPAxis.atBottom).selectedParts()) & QCPAxis.spAxis:
            rect.setRangeZoom(rect.axis(QCPAxis.atBottom).orientation())
        elif int(rect.axis(QCPAxis.atLeft).selectedParts()) & QCPAxis.spAxis:
            rect.setRangeZoomAxes(rect.axis(QCPAxis.atBottom), rect.axis(QCPAxis.atLeft))
            rect.setRangeZoom(rect.axis(QCPAxis.atLeft).orientation())
        elif int(rect.axis(QCPAxis.atRight).selectedParts()) & QCPAxis.spAxis:
            rect.setRangeZoomAxes(rect.axis(QCPAxis.atBottom), rect.axis(QCPAxis.atRight))
            rect.setRangeZoom(rect.axis(QCPAxis.atRight).orientation())
        else:
            rect.setRangeZoom(Qt.Horizontal | Qt.Vertical)
    
    def input(self, title = '', label = '', text = ''):
        return QInputDialog.getText(self, title, label, QLineEdit.Normal, text)
            
    def onAxisDoubleClick(self, axis, part, event):
        rect = self.currentRect(event.pos())
        if not rect: return
        for axis in rect.axes():
            if int(axis.selectedParts()) == part:
                #if part & QCPAxis.spTickLabels:
                val = str(axis.range().lower) + ':' + str(axis.range().upper)
                val,ok = self.input("Range", "New range:", val)
                if ok:
                    val = str(val).split(':')
                    axis.setRange(float(val[0]), float(val[1]))
                    rect.rescale = False
                    self.replot()
                
    def onContextMenu(self, pos):
        rect = self.currentRect(pos)
        if not rect: return
        self.menu.rescale.setChecked(rect.rescale)
        self.menu.xy.setChecked(rect.xy)
        if rect.x == None:
            self.menu.x.setVisible(False)
        else:
            self.menu.x.setVisible(True)
            self.menu.x.setText('X: '+str(rect.x))
        if rect.y == None:
            self.menu.y.setVisible(False)
        else:
            self.menu.y.setVisible(True)
            self.menu.y.setText('Y: '+str(rect.y))
        #quitAction = self.menu.addAction("Quit")
        action = self.menu.exec_(self.mapToGlobal(pos))
        if action == self.menu.rescale:
        #if action and action.text() == 'Rescale':
            rect.rescale = self.menu.rescale.isChecked()
        elif action == self.menu.xy:
            rect.xy = self.menu.xy.isChecked()
        #if action == quitAction:
        #    qApp.quit()
        
    @script()
    def setData(self, row, col, x, y):
        rect = self.rects.get((row, col), None)
        if not rect: return
        if rect.xy:
            rect.graph[0].setData(x, y)
            rect.graph[1].clearData()
            if rect.x != None: rect.graph[1].addData([rect.x]*len(y), y)
            if rect.y != None: rect.graph[1].addData(x, [rect.y]*len(x))
        else:
            t = range(len(x))
            rect.graph[0].setData(t, x)
            rect.graph[1].setData(t, y)
        if rect.rescale:
            for i in range(2):
                rect.graph[i].rescaleAxes(False, False)
        self.replot()
    
class Window(QWidget):
    def __init__(self):
        global FPS
        super(Window, self).__init__()
        self.setWindowTitle('MojoLock')
        
        col = QVBoxLayout()
        self.setLayout(col)
        
        row = QHBoxLayout()
        col.addLayout(row)
        
        self.mojo = mojo
        
        self.ports = EnumCtrl(row, 'Port')
        self.ports.setItems(self.mojo.ports())
        self.ports.setValue(-1)
        self.ports.enum.currentIndexChanged.connect(self.setPort)
        
        self.btnLoad = QPushButton('Load')
        row.addWidget(self.btnLoad)
        self.btnLoad.setFont(QFont("Microsoft YaHei", 12))
        self.btnLoad.clicked.connect(self.doLoad)
        
        self.btnInit = QPushButton('Init')
        row.addWidget(self.btnInit)
        self.btnInit.setFont(QFont("Microsoft YaHei", 12))
        self.btnInit.clicked.connect(self.doInit)
        
        self.state = EnumCtrl(row, 'State', self.setState)
        self.view = EnumCtrl(row, 'View', self.selectView)
        self.t = EnumCtrl(row, 't', self.setView)
        self.X = EnumCtrl(row, 'X', self.setView)
        self.Y = EnumCtrl(row, 'Y', self.setView)
        self.views = [(0, 0, 0, 0, 0)]
        self.view_all = True
        
        self.size = 8191
        self.shift = 0
        
        self.plot = PlotCtrl(self)
        col.addWidget(self.plot)
        
        row = QHBoxLayout()
        col.addLayout(row)
        
        self.dds0 = DDSCtrl(row, 'DDS0', self.mojo, 2)
        self.lia0 = LIACtrl(row, 'LIA0', self.mojo, 4)
        self.lia1 = LIACtrl(row, 'LIA1', self.mojo, 5)
        self.lia2 = LIACtrl(row, 'LIA2', self.mojo, 6)
        
        row = QHBoxLayout()
        col.addLayout(row)
        
        self.pid0 = PIDCtrl(row, 'PID0', self.mojo, 7)
        self.pid1 = PIDCtrl(row, 'PID1', self.mojo, 9)
        self.pid2 = PIDCtrl(row, 'PID2', self.mojo, 11)
        
        row = QHBoxLayout()
        col.addLayout(row)
        
        vbox = QVBoxLayout()
        row.addLayout(vbox)
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        self.task = EnumCtrl(hbox)
        self.task.enum.activated.connect(self.setTask)
        self.btnRun = QPushButton('Run')#Start
        hbox.addWidget(self.btnRun)
        self.btnRun.setFont(QFont("Microsoft YaHei", 12))
        self.btnRun.clicked.connect(self.doRun)
        self.doNext = None
        self.command = QLineEdit()
        hbox.addWidget(self.command)
        self.command.setFont(QFont("Microsoft YaHei", 11))
        self.command.returnPressed.connect(self.doRun)
        self.console = QPlainTextEdit()
        vbox.addWidget(self.console)
        self.console.setFont(QFont("Microsoft YaHei", 10))
        self.console.setReadOnly(True)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.doTimeout)
        self.timer.start(1000/FPS)
        self.timer_view = 0
        
        self.states = ['IDLE', 'TEST', 'RUN']
        self.state.setItems(self.states)
        self.dones = ['', 'DDS', 'ROM', 'LIA0', 'LIA1', 'LIA2', 'PID0', 'PID1', 'PID2', 'ADC', 'DAC0', 'DAC1', 'ON']
        self.t.setItems(self.dones)
        self.ins = ['ROM', 'LIA0X', 'LIA0Y', 'LIA1X', 'LIA1Y', 'LIA2X', 'LIA2Y', 'PID0', 'PID1', 'PID2', 'DAC0A', 'DAC0B', 'DAC1A', 'DAC1B']
        self.outs = ['', 'DDS0I', 'DDS0Q', 'ROM', 'LIA0', 'LIA1', 'LIA2', 'PID0', 'PID1', 'PID2', 'ADC0', 'ADC1', 'ADC2', 'ADC3', 'ADC23']
        self.X.setItems(self.outs)
        self.Y.setItems(self.outs)
        self.tasks = ['CLS', 'EVAL', 'TEST', 'LOCK0', 'LOCK1', 'LOCK2']
        self.task.setItems(self.tasks)
        
        
    def input(self, text = None):
        if text == None:
            return str(self.command.text())
        else:
            self.command.setText(str(text))
    
    def output(self, *args):
        if len(args) > 0:
            s = ''
            for v in args:
                s += str(v) + '\t'
            self.console.appendPlainText(s)
            self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())
        else:
            self.console.clear()
    
    def setTask(self, task):
        self.doNext = None
        self.btnRun.setText('Run')
        if task != self.task.value(): self.task.setValue(task)
        self.input(self.task.text())
        
    @script()
    def doRun(self, *args):
        cmd = self.command.text()
        if cmd: self.output('> ' + cmd)
                                   
    def setPort(self, port):
        self.mojo.close()
        if self.ports.text():
            self.mojo.open(str(self.ports.text()))
    
    def doLoad(self, *args):
        self.mojo.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.basename(__file__).replace('.py', '.bin')))
        
    def doInit(self, *args):
        wave = [int(32767.5*math.sin(2*math.pi*i/4096)) for i in range(1,1025)]
        self.mojo.write(1, wave)
        wave = [(0.02*i-10.23)**2 for i in range(1024)]
        wave = [int(255*x/(x+1)) for x in wave]
        self.mojo.write(3, [2047]+wave)
        self.mojo.write(13, [2621441, 2097155, 3670017, 1540096])
        self.mojo.write(14, [2621441, 2097155, 3670017, 1540096])
    
    def config(self, in_out, once_done):
        self.mojo.write(15, [0])
        if isinstance(in_out, dict):
            t = [0]*len(self.ins)
            for i in in_out:
                t[self.ins.index(i)] = self.outs.index(in_out[i])
            in_out = t
        self.mojo.write(16, in_out, True)
        if isinstance(once_done, dict):
            t = [0]*(len(self.dones)-2)
            for i in once_done:
                t[self.dones.index(i)-1] = self.dones.index(once_done[i])
            once_done = t
        self.mojo.write(32, once_done, True)
            
    def doView(self, state, t = 0, X = 0, Y = 0):
        if isinstance(t, str):
            t = self.dones.index(t)
        if isinstance(X, str):
            X = self.outs.index(X)
        if isinstance(Y, str):
            Y = self.outs.index(Y)
        self.mojo.write(0, [16*(16*(16*Y+X)+t)+state])
    
    def setSize(self, size = None):
        if size: self.size = size
        self.mojo.write(0, [65536*self.size])
    
    def setShift(self, shift = None):
        if shift: self.shift = shift
        self.mojo.write(0, [65536*(8192+self.shift)])
            
    @script()                    
    def setState(self, state):
        if state != self.state.value(): self.state.setValue(state)
        self.mojo.write(0, [0])
        self.doView(state)
        #if state == x:
        #...
        #self.selectView(self.view.value())
        #self.mojo.write(1, [0])
        
    def selectView(self, view):
        if 0 <= view < len(self.views):
            view = self.views[view]
            self.t.setValue(view[2])
            self.X.setValue(view[3])
            self.Y.setValue(view[4])
            self.doView(self.state.value(), view[2], view[3], view[4])
            
    def setView(self, arg):
        view = self.view.value()
        if 0 <= view < len(self.views):
            self.views[view] = self.views[view][0:2] + (self.t.text(), self.X.text(), self.Y.text())       
    
    @script()            
    def doTimeout(self):
        state = self.state.value()
        if not (self.ports.text() and state): return
        if self.view_all:
            next_view = (self.timer_view+1) % len(self.views)
        else:
            next_view = self.timer_view
        ret0 = self.mojo.read(0, self.size, False, True, id = '0'+str(next_view)) or self.mojo.get('read0'+str(self.timer_view))
        ret1 = self.mojo.read(1, 1, False, True, id = 1) or self.mojo.get('read1')
        ret2 = self.mojo.read(2, 1, False, True, id = 2) or self.mojo.get('read2')
        if ret0:
            data = struct.unpack(b'<'+b'h'*2*self.size, ret0)
            x = []
            y = []
            for i in range(self.size):
                x.append(data[2*i])
                y.append(data[2*i+1])
            view = self.views[self.timer_view]
            self.plot.setData(view[0], view[1], x, y)
        if ret1:
            data = struct.unpack(b'<hh', ret1)
            self.pid0.ival.setValue(data[0])
            self.pid1.ival.setValue(data[1])
        if ret2:
            data = struct.unpack(b'<hh', ret2)
            self.pid2.ival.setValue(data[0])
            #self.pid3.ival.setValue(data[1])
        self.timer_view = next_view
        if self.view_all:
            next_view = (self.timer_view+1) % len(self.views)
        else:
            next_view = self.timer_view
        self.doView(state, *self.views[next_view][2:])
 
    def quit(self):
        self.mojo.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    L.globals().window = window
    script_reload(script_path['lua'])
    sys.exit(app.exec_() and window.quit())

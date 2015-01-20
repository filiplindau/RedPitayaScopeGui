'''    
Created on 16 mar 2014

@author: Filip
'''
import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pq
import numpy as np
import threading
import time
import socket

class RedPitayaGui(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.layout = QtGui.QVBoxLayout(self)
        self.gridLayout = QtGui.QGridLayout()
        
        self.recordSpinbox = QtGui.QSpinBox()
        self.recordSpinbox.setMaximum(12000)
        self.recordSpinbox.setValue(2000)
        self.recordSpinbox.editingFinished.connect(self.setRecordLength)
        self.decimationSpinbox = QtGui.QSpinBox()
        self.decimationSpinbox.setMaximum(5)
        self.decimationSpinbox.editingFinished.connect(self.setDecimation)
        self.trigLevelSpinbox = QtGui.QDoubleSpinBox()
        self.trigLevelSpinbox.setMaximum(2)
        self.trigLevelSpinbox.setMinimum(-2)
        self.trigLevelSpinbox.editingFinished.connect(self.setTrigLevel)
        self.trigDelaySpinbox = QtGui.QDoubleSpinBox()
        self.trigDelaySpinbox.setDecimals(6)
        self.trigDelaySpinbox.setMaximum(2000000)
        self.trigDelaySpinbox.setMinimum(-2000000)
        self.trigDelaySpinbox.editingFinished.connect(self.setTrigDelay)
        self.trigSourceCombobox = QtGui.QComboBox()
        self.trigSourceCombobox.addItem("Channel1")
        self.trigSourceCombobox.addItem("Channel2")
        self.trigSourceCombobox.addItem("External")
        self.trigSourceCombobox.activated.connect(self.setTrigSource)
        self.trigModeCombobox = QtGui.QComboBox()
        self.trigModeCombobox.addItem("Auto")
        self.trigModeCombobox.addItem("Normal")
        self.trigModeCombobox.addItem("Single")        
        self.trigModeCombobox.activated.connect(self.setTrigMode)
        self.fpsLabel = QtGui.QLabel()
        
        self.gridLayout.addWidget(QtGui.QLabel("Record length"), 0, 0)
        self.gridLayout.addWidget(self.recordSpinbox, 0, 1)
        self.gridLayout.addWidget(QtGui.QLabel("Decimation factor"), 1, 0)
        self.gridLayout.addWidget(self.decimationSpinbox, 1, 1)
        self.gridLayout.addWidget(QtGui.QLabel("Trigger level"), 2, 0)
        self.gridLayout.addWidget(self.trigLevelSpinbox, 2, 1)
        self.gridLayout.addWidget(QtGui.QLabel("Trigger delay / us"), 3, 0)
        self.gridLayout.addWidget(self.trigDelaySpinbox, 3, 1)
        self.gridLayout.addWidget(QtGui.QLabel("Trigger source"), 4, 0)
        self.gridLayout.addWidget(self.trigSourceCombobox, 4, 1)
        self.gridLayout.addWidget(QtGui.QLabel("Trigger mode"), 5, 0)
        self.gridLayout.addWidget(self.trigModeCombobox, 5, 1)
        self.gridLayout.addWidget(QtGui.QLabel("FPS"), 6, 0)
        self.gridLayout.addWidget(self.fpsLabel, 6, 1)
        
        self.plotWidget = pq.PlotWidget(useOpenGL=True)
        self.plot1 = self.plotWidget.plot()
        self.plot1.setPen((200, 25, 10))
        self.plot2 = self.plotWidget.plot()
        self.plot2.setPen((10, 200, 25))
        self.plot1.antialiasing = True
        self.plotWidget.setAntialiasing(True)

        self.layout.addLayout(self.gridLayout)
        self.layout.addWidget(self.plotWidget)
        
        print 'Connecting...'
        self.sock = socket.socket()
        print 'Socket created'
        self.sock.connect(('130.235.94.96', 8888))
        print '...connected' 
        
        self.t0 = time.time()
        
        self.lock = threading.Lock()
        
        self.running = True
        self.updateTimer = QtCore.QTimer()
        self.updateTimer.timeout.connect(self.updateAction)
        self.updateTimer.start(5)
        
    def setRecordLength(self):
        self.lock.acquire()
        msg = ''.join(('setRecordlength:', str(self.recordSpinbox.value())))
        self.sendReceive(msg)
        self.lock.release()

    def setDecimation(self):
        self.lock.acquire()
        msg = ''.join(('setDecimation:', str(self.decimationSpinbox.value())))
        self.sendReceive(msg)
        self.lock.release()

    def setTrigLevel(self):
        self.lock.acquire()
        msg = ''.join(('setTriggerLevel:', str(self.trigLevelSpinbox.value())))
        print msg
        self.sendReceive(msg)
        self.lock.release()

    def setTrigDelay(self):
        self.lock.acquire()
        msg = ''.join(('setTriggerDelay:', str(self.trigDelaySpinbox.value())))
        print msg
        ret = self.sendReceive(msg)
        print 'Returned ', ret
        self.lock.release()
        
    def setTrigSource(self, index):
        sourceList = ['CH1', 'CH2', 'EXT']
        self.lock.acquire()
        msg = ''.join(('setTriggerSource:', sourceList[index]))
        print msg
        self.sendReceive(msg)
        self.lock.release()        

    def setTrigMode(self, index):
        modeList = ['AUTO', 'NORMAL', 'SINGLE']
        self.lock.acquire()
        msg = ''.join(('setTriggerMode:', modeList[index]))
        print msg
        self.sendReceive(msg)
        self.lock.release()        

    def sendReceive(self, msg):
        self.sock.send(msg)
        rep = self.sock.recv(70000)
        return rep

            
    def updateAction(self):
        # Update world here
        self.lock.acquire()
        sig1 = self.sendReceive('getWaveform:0')
        self.lock.release()
        if sig1 != 'not triggered':
            data = np.fromstring(sig1, dtype=np.float32)
            self.plot1.setData(y=data)
            t = time.time()
            self.fpsLabel.setText("{:.2f}".format(1 / (t - self.t0)))
            self.t0 = t
        self.lock.acquire()
        sig2 = self.sendReceive('getWaveform:1')
        self.lock.release()
        if sig2 != 'not triggered':
            data = np.fromstring(sig2, dtype=np.float32)
            self.plot2.setData(y=data)

       
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = RedPitayaGui()
    myapp.show()
    sys.exit(app.exec_())   

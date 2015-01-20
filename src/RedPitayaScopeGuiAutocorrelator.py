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
import PyTango as pt

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
        self.trigDelaySpinbox.setDecimals(1)
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
        self.averageSpinbox = QtGui.QSpinBox()
        self.averageSpinbox.setMaximum(100)
        self.averageSpinbox.setValue(5)
        self.averageSpinbox.editingFinished.connect(self.setAverage)

        self.startPosSpinbox = QtGui.QDoubleSpinBox()
        self.startPosSpinbox.setDecimals(3)
        self.startPosSpinbox.setMaximum(2000000)
        self.startPosSpinbox.setMinimum(-2000000)
        self.startPosSpinbox.setValue(46.8)
        self.stepSizeSpinbox = QtGui.QDoubleSpinBox()
        self.stepSizeSpinbox.setDecimals(3)
        self.stepSizeSpinbox.setMaximum(2000000)
        self.stepSizeSpinbox.setMinimum(-2000000)
        self.stepSizeSpinbox.setValue(0.05)
        self.currentPosSpinbox = QtGui.QDoubleSpinBox()
        self.currentPosSpinbox.setDecimals(3)
        self.currentPosSpinbox.setMaximum(2000000)
        self.currentPosSpinbox.setMinimum(-2000000)
        
        self.startButton = QtGui.QPushButton('Start')
        self.startButton.clicked.connect(self.startScan)
        self.stopButton = QtGui.QPushButton('Stop')
        self.stopButton.clicked.connect(self.stopScan)
        self.exportButton = QtGui.QPushButton('Export')
        self.exportButton.clicked.connect(self.exportScan)
        
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
        self.gridLayout.addWidget(QtGui.QLabel("Averages"), 7, 0)
        self.gridLayout.addWidget(self.averageSpinbox, 7, 1)
        self.gridLayout.addWidget(QtGui.QLabel("Start position"), 8, 0)
        self.gridLayout.addWidget(self.startPosSpinbox, 8, 1)
        self.gridLayout.addWidget(QtGui.QLabel("Step size"), 9, 0)
        self.gridLayout.addWidget(self.stepSizeSpinbox, 9, 1)        
        self.gridLayout.addWidget(QtGui.QLabel("Start scan"), 10, 0)
        self.gridLayout.addWidget(self.startButton, 10, 1)
        self.gridLayout.addWidget(QtGui.QLabel("Stop scan"), 11, 0)
        self.gridLayout.addWidget(self.stopButton, 11, 1)
        self.gridLayout.addWidget(QtGui.QLabel("Export scan"), 12, 0)
        self.gridLayout.addWidget(self.exportButton, 12, 1)
        self.gridLayout.addWidget(QtGui.QLabel("Current position"), 13, 0)
        self.gridLayout.addWidget(self.currentPosSpinbox, 13, 1)

        
        
        self.plotWidget = pq.PlotWidget(useOpenGL=True)
        self.plot1 = self.plotWidget.plot()
        self.plot1.setPen((200, 25, 10))
        self.plot2 = self.plotWidget.plot()
        self.plot2.setPen((10, 200, 25))
        self.plot1.antialiasing = True
        self.plotWidget.setAntialiasing(True)

        self.plotWidget2 = pq.PlotWidget(useOpenGL=True)
        self.plot3 = self.plotWidget2.plot()
        self.plot3.setPen((50, 99, 200))
        self.plot4 = self.plotWidget2.plot()
        self.plot4.setPen((10, 200, 25))
        self.plot3.antialiasing = True
        self.plotWidget2.setAntialiasing(True)

        self.plotWidget3 = pq.PlotWidget(useOpenGL=True)
        self.plot5 = self.plotWidget3.plot()
        self.plot5.setPen((10, 200, 70))
        self.plotWidget3.setAntialiasing(True)

        plotLayout = QtGui.QHBoxLayout()
        plotLayout.addWidget(self.plotWidget)
        plotLayout.addWidget(self.plotWidget2)
        plotLayout.addWidget(self.plotWidget3)
        
        self.layout.addLayout(self.gridLayout)
        self.layout.addLayout(plotLayout)
        
        self.trendData1 = np.zeros(600)
        self.trendData2 = np.zeros(600)
        self.avgSamples = 10
        self.currentSample = 0
        self.avgData = 0
        
        print 'Connecting...'
        self.sock = socket.socket()
        print 'Socket created'
        self.sock.connect(('130.235.94.96', 8888))
        print '...connected' 
        
        print 'Getting motor device...'
        self.dev = pt.DeviceProxy('testfel/gunlaser/autocorrelator_delay')
        print '...connected'
        self.pos = self.dev.read_attribute('position').value    
        self.currentPosSpinbox.setValue(self.pos)
        
        self.t0 = time.time()
        
        self.lock = threading.Lock()
        
        self.running = False
        self.scanning = False
        self.updateTimer = QtCore.QTimer()
        self.updateTimer.timeout.connect(self.updateAction)
        self.updateTimer.start(5)
        self.scanTimer = QtCore.QTimer()
        self.scanTimer.timeout.connect(self.scanUpdateAction)
        
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
        
    def setAverage(self):
        self.avgSamples = self.averageSpinbox.value()

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
    
    def startScan(self):
        self.scanData = np.array([])
        self.timeData = np.array([])
        self.scanning = True
        self.dev.write_attribute('position', self.startPosSpinbox.value())
        self.pos = self.dev.read_attribute('position').value
        self.currentPosSpinbox.setValue(self.pos)        
        print 'Moving from ', self.pos
        while self.pos != self.startPosSpinbox.value():
            time.sleep(0.25)
            self.pos = self.dev.read_attribute('position').value
            self.currentPosSpinbox.setValue(self.pos)
        self.scanTimer.start(100 * self.avgSamples)
        
    def stopScan(self):
        print 'Stopping scan'
        self.running = False
        self.scanning = False
        self.scanTimer.stop()
        
    def exportScan(self):
        print 'Exporting scan data'
        data = np.vstack((self.timeData, self.scanData)).transpose()
        filename = ''.join(('scandata_', time.strftime('%Y-%m-%d_%Hh%M'), '.txt'))
        np.savetxt(filename, data)
        
    def scanUpdateAction(self):
        self.scanTimer.stop()
        while self.running == True:
            time.sleep(0.1)
        newPos = self.pos + self.stepSizeSpinbox.value()
        print 'New pos: ', newPos
        self.dev.write_attribute('position', newPos)
        time.sleep(0.25)
        self.pos = self.dev.read_attribute('position').value
        self.currentPosSpinbox.setValue(self.pos)
        while np.abs(self.pos - newPos) > 0.001:
            time.sleep(0.5)
            self.pos = self.dev.read_attribute('position').value
            self.currentPosSpinbox.setValue(self.pos)
            print 'Delta value: ', self.pos - newPos
        self.running = True
        self.scanTimer.start(100 * self.avgSamples)        
        

    def measureScanData(self):
        self.avgData = self.trendData1[-self.avgSamples:].mean()
        self.scanData = np.hstack((self.scanData, self.avgData))
        newTime = (self.pos - self.startPosSpinbox.value()) * 2 * 1e-3 / 299792458.0
        self.timeData = np.hstack((self.timeData, newTime))
        self.plot5.setData(x=self.timeData * 1e12, y=self.scanData)

    def measureData(self, data1, data2):
        goodInd = np.arange(242, 251, 1)
        bkgInd = np.arange(230, 241, 1)
        bkg = data2[bkgInd].mean()
        autoCorr = (data2[goodInd] - bkg).sum() 
        pump = data1[goodInd].sum()
        self.trendData1 = np.hstack((self.trendData1[1:], autoCorr / pump))        
        self.plot3.setData(y=self.trendData1)
        if self.running == True:
            self.currentSample += 1
            if self.currentSample >= self.avgSamples:
                self.running = False
                self.measureScanData()
                self.currentSample = 0
            
    def updateAction(self):
        # Update world here
        self.lock.acquire()
        sig1 = self.sendReceive('getWaveform:0')
        self.lock.release()
        if sig1 != 'not triggered':
            data1 = np.fromstring(sig1, dtype=np.float32)
            self.plot1.setData(y=data1)
            t = time.time()
            self.fpsLabel.setText("{:.2f}".format(1 / (t - self.t0)))
            self.t0 = t
            self.lock.acquire()
            sig2 = self.sendReceive('getWaveform:1')
            self.lock.release()
            data2 = np.fromstring(sig2, dtype=np.float32)
            self.plot2.setData(y=data2)
            self.measureData(data1, data2)

       
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = RedPitayaGui()
    myapp.show()
    sys.exit(app.exec_())   

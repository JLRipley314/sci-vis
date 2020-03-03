from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.console
import numpy as np
import pandas as pd
import sys

### make a widget for displaying 3D objects
import pyqtgraph.opengl as gl

### for manipulating hdf5 
from io_hdf5 import *

##############################################################################
##############################################################################
class Plotter(QtGui.QWidget):
	keyPressed = QtCore.pyqtSignal(QtCore.QEvent)
##############################################################################
	def __init__(self):
		super(Plotter, self).__init__()

		self.left = 10
		self.top = 10
		self.width = 840
		self.height = 680

		self.initUI()
##############################################################################
	def initUI(self):
##############################################################################
		self.setWindowTitle('Plotter')
		self.keyPressed.connect(self.on_key)
##############################################################################
# minimum size when opening gui
		self.setGeometry(self.left, self.top, self.width, self.height)
##############################################################################
# Create a grid layout to manage the widgets size and position
# allows for plot window to dynamically resize with size of gui
		self.layout = QtGui.QGridLayout()
		self.setLayout(self.layout)
##############################################################################
# Create some widgets to be placed inside
##############################################################################
#TODO: testing this -- console widget
		text = """
		Python 3 console. Namespace includes numpy as 'np', pyqtgraph as 'pg', and 'self'. Data loaded through the 'Select Files' button is stored in 'self.var_arr'. Plot directly to built-in window with self.plotWindow.plot() and plot to pop-out window with pg.plot().
		"""
		NS = {'pg': pg, 'np': np, 'self':self}
		self.layout.addWidget(
			pyqtgraph.console.ConsoleWidget(
				namespace=NS, text=text),6, 0, 3, 1
		)
##############################################################################
		self.load_btn = QtGui.QPushButton('Select Files', self)
		self.load_btn.clicked.connect(self.handleButton)
		self.layout.addWidget(self.load_btn, 0, 0)
##############################################################################
		self.step_label = QtGui.QLabel('time step size: ', self)
		self.layout.addWidget(self.step_label, 1, 0)
##############################################################################
		self.enter_step = QtGui.QLineEdit('1', self)
		self.enter_step.setFixedWidth(100)
		self.layout.addWidget(self.enter_step, 2, 0)
##############################################################################
		self.display_n = QtGui.QLabel('time step = 00000', self)
		self.layout.addWidget(self.display_n, 3, 0)
##############################################################################
		self.play_btn = QtGui.QPushButton('Play', self)
		self.play_btn.setCheckable(True)
		self.play_btn.clicked.connect(self.play_btn_state)
		self.layout.addWidget(self.play_btn, 4, 0)
##############################################################################
		self.plotWindow = pg.PlotWidget(self)
		self.plotWindow.addLegend(offset=(25,25))
		self.layout.addWidget(self.plotWindow, 0, 1, 9, 1)
##############################################################################
### for playing the movies
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.advance_n)
		self.update_time_ms = 100
##############################################################################
# define global variables to be used by applet
		self.filename = ''
		self.n = 0
		self.step = 1
		self.maxn = 0
		self.plot_num = 0

		self.step1 = 1
		self.step2 = 1
		self.step3 = 1

		self.color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
		self.penwidth = 3
		# options for pointSymbol: None, 'x', 'o', 't', 't1', 't2'
		#'t3', 's', 'p', 'h', 'star', '+', 'd'
		self.pointSymbol = None
##############################################################################
		self.show()
##############################################################################
	def play_btn_state(self):
		if self.play_btn.isChecked():
			self.timer.start(self.update_time_ms)
		else:
			self.timer.stop()
##############################################################################
	def advance_n(self):
		if(self.n+self.step < self.maxn):
			self.n += self.step
			self.update_plot_n()
		else:
			self.timer.stop()
			self.play_btn.toggle()
##############################################################################
	def handleButton(self):
		title    = self.load_btn.text()
		paths, _ = QtGui.QFileDialog.getOpenFileNames(self, title)
		for path in paths:
			self.load_data(path)
##############################################################################
#TODO:  operations on arrays.  It would be nice to implement this through
#       the control window; have each loaded array be assigned to its own
#       variable, and we could then plot |arr|, or arr.transpose(), etc.
##############################################################################
	def load_data(self, filename):
		x, y = read_hdf5(str(filename))
		if (self.plot_num==0):
			self.var_arr   = y
			self.var_names = self.prune_string(filename)
			self.plot_data(self.var_arr)
		else:
			self.var_arr   = np.append(self.var_arr,   y)
			self.var_names = np.append(self.var_names, self.prune_string(filename))
#-----------------------------------------------------------------------------
### have to make array with correct indexing
			if (len(y.shape)==2):
				self.var_arr= np.reshape(
					self.var_arr,
					(self.plot_num+1, np.shape(y)[0], np.shape(y)[1])
				)
			elif (len(y.shape)==3):
				self.var_arr= np.reshape(
					self.var_arr,
					(self.plot_num+1, np.shape(y)[0], np.shape(y)[1], np.shape(y)[2])
				)
			else:
				raise SystemError("len(y.shape)!=2,3")
			self.plot_data(self.var_arr[self.plot_num])
		self.plot_num+= 1
		print('loaded'+str(filename))
		return 0
##############################################################################
	def prune_string(self, filename):
		loc_start = str(filename).rfind('/')+1
		loc_end = str(filename).rfind('.')
		name_str = str(filename)[loc_start:loc_end]
		return name_str
##############################################################################
	def plot_data(self, y) -> None:
		self.maxn = np.shape(y)[0]
		if (len(y.shape)==2):
			self.plotWindow.plot(
				y[self.n, :], 
				pen=pg.mkPen(self.color[self.plot_num], width=self.penwidth),
				symbol=self.pointSymbol, 
				symbolBrush=self.color[self.plot_num], 
				name=self.var_names[self.plot_num]
			)
		elif (len(y.shape)==3):
			self.plotWindow.plot(
				y[self.n, :, :], 
				pen=pg.mkPen(self.color[self.plot_num], width=self.penwidth),
				symbol=self.pointSymbol, 
				symbolBrush=self.color[self.plot_num], 
				name=self.var_names[self.plot_num]
			)
		else:
			raise SystemError("len(y.shape)!=2,3")
		return
##############################################################################
	def keyPressEvent(self, event):
		super(Plotter, self).keyPressEvent(event)
		self.keyPressed.emit(event)
		self.step = int(str(self.enter_step.text()))
##############################################################################
	def update_plot_n(self):
		self.plotWindow.clear()
		self.update_display_n()
		plot_index = 0
		if (self.plot_num<=0):
			raise SystemError("self.plot_num<=0")
		elif (self.plot_num==1):
			self.plotWindow.plot(
#				self.coord_arr[self.n, :],
				self.var_arr[self.n, :], 
				pen=pg.mkPen(self.color[plot_index],width=self.penwidth),
				symbol=self.pointSymbol, 
				symbolBrush=self.color[plot_index]
			)
		else:
			for i in range(self.var_arr.shape[0]):
				self.plotWindow.plot(
#					self.coord_arr[i,self.n, :],	
					self.var_arr[  i,self.n, :],
					pen=pg.mkPen(self.color[plot_index],width=self.penwidth),
					symbol=self.pointSymbol, 
					symbolBrush=self.color[plot_index]
				)
				plot_index += 1
		return 0
##############################################################################
	def update_display_n(self):
		self.display_n.setText('n = ' + str(self.n))
##############################################################################
# if press 'enter' then +1 step
# if press 'q' then closes the application
# if press right/left arrow thentime step +1/-1
	def on_key(self, event):
		if(event.key() == QtCore.Qt.Key_Enter):
			self.step = int(str(self.enter_step.text()))
			#print('step changed to'+str(self.step))
		elif(event.key() == QtCore.Qt.Key_Q):
			print('Exiting')
			self.deleteLater()
		elif(event.key() == QtCore.Qt.Key_Right):
			if(self.n+self.step < self.maxn):
				self.n += self.step
				self.update_plot_n()
			elif event.key() == QtCore.Qt.Key_Left:
				if(self.n-self.step >= 0):
					self.n -= self.step
					self.update_plot_n()
##############################################################################
##############################################################################
def main():
	app = QtGui.QApplication(sys.argv)
	plot = Plotter()
	sys.exit(app.exec_())
##############################################################################
##############################################################################
if __name__ == '__main__':
	main()

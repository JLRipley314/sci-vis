#-----------------------------------------------------------------------------
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.console
import numpy as np
import sys
#-----------------------------------------------------------------------------
import os, sys
#-----------------------------------------------------------------------------
## get parent directory
from os.path import dirname, abspath
plot_dir= dirname(dirname(abspath(__file__)))
#-----------------------------------------------------------------------------
## for manipulating csv 
sys.path.insert(1, plot_dir+'/csv')
from io_csv import *
#-----------------------------------------------------------------------------
## for manipulating hdf5 
sys.path.insert(1, plot_dir+'/hdf5')
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
	def initUI(self)->None:
#----------------------------------------------------------------------------
		self.setWindowTitle('Plotter')
		self.keyPressed.connect(self.on_key)
#----------------------------------------------------------------------------
## minimum size when opening gui
		self.setGeometry(self.left, self.top, self.width, self.height)
#----------------------------------------------------------------------------
## Create a grid layout to manage the widgets size and position
## allows for plot window to dynamically resize with size of gui
		self.layout = QtGui.QGridLayout()
		self.setLayout(self.layout)
#----------------------------------------------------------------------------
## create Widgets for the gui. loc is the horizontal location,
## starting from the top
#----------------------------------------------------------------------------
		loc= 0
#----------------------------------------------------------------------------
		self.load_btn= QtGui.QPushButton('Select Files', self)
		self.load_btn.clicked.connect(self.handleButton)
		self.layout.addWidget(self.load_btn, loc, 0)
		loc+=1
#----------------------------------------------------------------------------
		self.set_level_label= QtGui.QLabel('level:', self)
		self.layout.addWidget(self.set_level_label, loc, 0)
		loc+=1

		self.enter_level= QtGui.QLineEdit('0', self)
		self.enter_level.setFixedWidth(100)
		self.layout.addWidget(self.enter_level, loc, 0)
		loc+=1
#----------------------------------------------------------------------------
		self.display_level= QtGui.QLabel('level = 00000', self)
		self.layout.addWidget(self.display_level, loc, 0)
		loc+=1
#----------------------------------------------------------------------------
		self.play_btn= QtGui.QPushButton('Play', self)
		self.play_btn.setCheckable(True)
		self.play_btn.clicked.connect(self.play_btn_state)
		self.layout.addWidget(self.play_btn, loc, 0)
		loc+=1
#----------------------------------------------------------------------------
## for 2d viewing
		self.plotWindow= pg.PlotWidget(self)
		self.layout.addWidget(self.plotWindow, 0, 1, 9, 1)
#----------------------------------------------------------------------------
## for playing the movies
		self.timer= QtCore.QTimer(self)
		self.timer.timeout.connect(self.advance_level)
		self.update_time_ms= 100
#----------------------------------------------------------------------------
## define global variables to be used by applet
		self.filename = ''
		self.level = 0
		self.maxlevels = 0
		self.plot_num = 0

		self.color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
		self.penwidth = 3
## options for pointSymbol: None, 'x', 'o', 't', 't1', 't2'
##'t3', 's', 'p', 'h', 'star', '+', 'd'
		self.pointSymbol = None
#----------------------------------------------------------------------------
		self.show()
##############################################################################
	def play_btn_state(self)->None:
		if self.play_btn.isChecked():
			self.timer.start(self.update_time_ms)
		else:
			self.timer.stop()
##############################################################################
	def advance_level(self)->None:
		if(self.level+1 < self.maxlevels):
			self.level+= 1
			self.update_plot_level()
		else:
			self.timer.stop()
			self.play_btn.toggle()
##############################################################################
	def handleButton(self)->None:
		title    = self.load_btn.text()
		paths, _ = QtGui.QFileDialog.getOpenFileNames(self, title)
		for path in paths:
			self.load_data(path)
		self.update_plot_level()
##############################################################################
#TODO:  operations on arrays.  It would be nice to implement this through
#       the control window; have each loaded array be assigned to its own
#       variable, and we could then plot |arr|, or arr.transpose(), etc.
##############################################################################
	def load_data(self, filename:str)->None:
#-----------------------------------------------------------------------------
		y= np.array([])
		if (str(filename).endswith('.csv')):
			y= np.array(read_vals_csv_1d(str(filename)))
		elif (str(filename).endswith('.h5')):
			y= np.array(read_hdf5(str(filename)))
		else:
			raise ValueError('improper file extension')
#-----------------------------------------------------------------------------
		if (self.plot_num==0):
                        self.var_arr= {}
                        self.var_arr[self.plot_num]= np.array(y)
                        self.var_names= [self.prune_string(filename)]
                        self.maxlevels = np.shape(y)[0]
		else:
			self.var_arr[self.plot_num]= y
			self.var_names.append(self.prune_string(filename))
			self.maxlevels = min(self.maxlevels,np.shape(y)[0])
		self.plot_data(self.plot_num)
		self.plot_num+= 1
		print('loaded'+str(filename))
##############################################################################
	def prune_string(self, filename:str)->str:
		loc_start= str(filename).rfind('/')+1
		loc_end= str(filename).rfind('.')
		name_str= str(filename)[loc_start:loc_end]
		return name_str
##############################################################################
	def plot_data(self, index:int) -> None:
		y= self.var_arr[index]
		nx = np.shape(y)[1]
		x= [float(i)/nx for i in range(nx)]
		self.plotWindow.plot(
			x,
			y[self.level],
			pen=pg.mkPen(self.color[index], width=self.penwidth),
			symbol=self.pointSymbol,
			symbolBrush=self.color[index]#, 
			#name=self.var_names[index] 
		)
##############################################################################
	def keyPressEvent(self, event) -> None:
		super(Plotter, self).keyPressEvent(event)
		self.keyPressed.emit(event)
		self.level = int(str(self.enter_level.text()))

		self.update_plot_level()
##############################################################################
	def update_plot_level(self)->None:
		self.plotWindow.clear()
		self.update_display()
		if (self.plot_num<=0):
			raise ValueError("self.plot_num<=0")
		for i in range(self.plot_num):
			self.plot_data(i)
##############################################################################
	def update_display(self)->None:
		self.display_level.setText('level = {}'.format(self.level))
##############################################################################
## if press 'enter' then go to that level 
## if press 'q' then closes the application
## if press right/left arrow then time level +1/-1
	def on_key(self, event)->None:
		if(event.key() == QtCore.Qt.Key_Enter):
			self.level = int(str(self.enter_level.text()))
			self.update_plot_level()
		elif(event.key() == QtCore.Qt.Key_Q):
			print('Exiting')
			self.deleteLater()
		elif(event.key() == QtCore.Qt.Key_Right):
			if(self.level+1 < self.maxlevels):
				self.level+= 1
				self.update_plot_level()
		elif event.key() == QtCore.Qt.Key_Left:
			if(self.level-1 >= 0):
				self.level-= 1
				self.update_plot_level()
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

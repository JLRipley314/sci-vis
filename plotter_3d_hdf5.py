#-----------------------------------------------------------------------------
import sys
import numpy as np
#-----------------------------------------------------------------------------
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
#-----------------------------------------------------------------------------
### make a widget for displaying 3D objects
import pyqtgraph.opengl as gl
import pyqtgraph.console
#-----------------------------------------------------------------------------
## for manipulating hdf5 
from io_hdf5 import *
#-----------------------------------------------------------------------------
## for coloring of solutions 
import matplotlib.pyplot as plt
cmap= plt.get_cmap('jet')
rgba_img = cmap(1.)
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
# Create some widgets to be placed inside
#----------------------------------------------------------------------------
#TODO: testing this -- console widget
		text = """
		Python 3 console. Namespace includes numpy as 'np', pyqtgraph as 'pg', and 'self'. Data loaded through the 'Select Files' button is stored in 'self.var_arr'. Plot directly to built-in window with self.plotWindow.plot() and plot to pop-out window with pg.plot().
		"""
		NS = {'pg': pg, 'np': np, 'self':self}
		self.layout.addWidget(
			pyqtgraph.console.ConsoleWidget(
				namespace=NS, text=text),6, 0, 3, 1
		)
#----------------------------------------------------------------------------
		self.load_btn = QtGui.QPushButton('Select Files', self)
		self.load_btn.clicked.connect(self.handleButton)
		self.layout.addWidget(self.load_btn, 0, 0)
#----------------------------------------------------------------------------
		self.enter_step = QtGui.QLineEdit('1', self)
		self.enter_step.setFixedWidth(100)
		self.layout.addWidget(self.enter_step, 1, 0)
#----------------------------------------------------------------------------
		self.display_step = QtGui.QLabel('step = 00000', self)
		self.layout.addWidget(self.display_step, 2, 0)
#----------------------------------------------------------------------------
		self.display_norm = QtGui.QLabel('norm = 00000', self)
		self.layout.addWidget(self.display_norm, 3, 0)
#----------------------------------------------------------------------------
		self.play_btn = QtGui.QPushButton('Play', self)
		self.play_btn.setCheckable(True)
		self.play_btn.clicked.connect(self.play_btn_state)
		self.layout.addWidget(self.play_btn, 4, 0)
#----------------------------------------------------------------------------
## for 3d viewing		
		self.plotWindow = gl.GLViewWidget(self)
		self.plotWindow.setCameraPosition(distance=15)

		self.layout.addWidget(self.plotWindow, 0, 1, 9, 1)

		self.plots= []
#----------------------------------------------------------------------------
## for playing the movies
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.advance_n)
		self.update_time_ms = 100
#----------------------------------------------------------------------------
## define global variables to be used by applet
		self.filename = ''
		self.step = 1
		self.norm = 1
		self.maxn = 0
		self.plot_num = 0

		self.color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
		self.penwidth = 3
		# options for pointSymbol: None, 'x', 'o', 't', 't1', 't2'
		#'t3', 's', 'p', 'h', 'star', '+', 'd'
		self.pointSymbol = None
#----------------------------------------------------------------------------
		self.show()
##############################################################################
	def play_btn_state(self):
		if self.play_btn.isChecked():
			self.timer.start(self.update_time_ms)
		else:
			self.timer.stop()
##############################################################################
	def advance_n(self):
		if(self.step+1 < self.maxn):
			self.step+= 1
			self.update_plot_step()
		else:
			self.timer.stop()
			self.play_btn.toggle()
##############################################################################
	def handleButton(self):
		title    = self.load_btn.text()
		paths, _ = QtGui.QFileDialog.getOpenFileNames(self, title)
		for path in paths:
			self.load_data(path)
		self.update_plot_step()
##############################################################################
##TODO:  operations on arrays.  It would be nice to implement this through
##       the control window; have each loaded array be assigned to its own
##       variable, and we could then plot |arr|, or arr.transpose(), etc.
##############################################################################
	def load_data(self, filename):
		y = read_hdf5(str(filename))
		if (self.plot_num==0):
			self.var_arr   = np.array([y])
			self.var_names = self.prune_string(filename)
			self.plot_data(self.var_arr[0])
		else:
			self.var_arr   = np.append(self.var_arr, y)
			self.var_names = np.append(self.var_names, self.prune_string(filename))
#-----------------------------------------------------------------------------
## have to make array with correct indexing
			if (len(y.shape)==3):
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
	def plot_data(self, vals) -> None:
		self.maxn = np.shape(vals)[0]
		if (len(vals.shape)==3):
			self.plots.append(
				gl.GLSurfacePlotItem(
					x= np.linspace(-5.0,5.0,vals[0].shape[0]),
					y= np.linspace(-5.0,5.0,vals[0].shape[1]),
					shader='heightColor',
					computeNormals=False,
					smooth=False
				)
			)
			self.plots[-1].shader()['colorMap'] = np.array([
				0.01, ## red 1
				0,    ## red 2
				0.01, ## red 3
				0.5,  ## green 1
				0,    ## green 2
				0.5,  ## green 3
				0.99, ## blue 1
				0,    ## blue 2
				0.99  ## blue 3
			])
			self.plots[-1].setData(z=vals[0])
			self.plotWindow.addItem(self.plots[-1])
		else:
			raise SystemError("len(y.shape)!=3")
		return
##############################################################################
	def keyPressEvent(self, event):
		super(Plotter, self).keyPressEvent(event)
		self.keyPressed.emit(event)
		self.step = int(str(self.enter_step.text()))
##############################################################################
	def update_plot_step(self):
		self.compute_norm()
		self.update_display()
		if (self.plot_num<=0):
			raise ValueError("self.plot_num<=0")
		for i in range(self.plot_num):
			self.plots[i].setData(
				z=self.var_arr[i,self.step, :, :]/self.norm
			)
		return 0
##############################################################################
	def compute_norm(self):
		self.norm=0
		for i in range(self.plot_num):
			self.norm= max(
				abs(self.var_arr[i,self.step, :, :]).max(),
				self.norm
			)
		if (self.norm==0):
			self.norm= 1
##############################################################################
	def update_display(self):
		self.display_step.setText('t = ' + str(self.step))
		self.display_norm.setText('norm = ' + str(self.norm))
##############################################################################
## if press 'enter' then +1 step
## if press 'q' then closes the application
## if press right/left arrow thentime step +1/-1
	def on_key(self, event):
		if(event.key() == QtCore.Qt.Key_Enter):
			self.step = int(str(self.enter_step.text()))
		elif(event.key() == QtCore.Qt.Key_Q):
			print('Exiting')
			self.deleteLater()
		elif(event.key() == QtCore.Qt.Key_Right):
			if(self.step+1 < self.maxn):
				self.step += 1 
				self.update_plot_step()
			elif event.key() == QtCore.Qt.Key_Left:
				if(self.step-1 >= 0):
					self.step-= 1 
					self.update_plot_step()
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


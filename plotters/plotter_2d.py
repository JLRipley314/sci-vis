#-----------------------------------------------------------------------------
import sys
import numpy as np
#-----------------------------------------------------------------------------
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
#-----------------------------------------------------------------------------
### make a widget for displaying 3D objects
import pyqtgraph.opengl as gl
import pyqtgraph.console
#-----------------------------------------------------------------------------
import sys
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
#=============================================================================
#=============================================================================
class Plotter(QtWidgets.QWidget):
	keyPressed = QtCore.pyqtSignal(QtCore.QEvent)
#=============================================================================
## hard coded parameters for relative size of screen, etc
	def __init__(self):
		super(Plotter, self).__init__()

		self.left = 10
		self.top = 10
		self.width = 840
		self.height = 680

		self.initUI()
#=============================================================================
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
		self.layout = QtWidgets.QGridLayout()
		self.setLayout(self.layout)
#----------------------------------------------------------------------------
## create Widgets for the gui. loc is the horizontal location,
## starting from the top
#----------------------------------------------------------------------------
		loc= 0
#----------------------------------------------------------------------------
		self.load_btn = QtWidgets.QPushButton('Select Files', self)
		self.load_btn.clicked.connect(self.handleButton)
		self.layout.addWidget(self.load_btn, loc, 0)
		loc+=1
#----------------------------------------------------------------------------
		self.set_step_label = QtWidgets.QLabel('step:', self)
		self.layout.addWidget(self.set_step_label, loc, 0)
		loc+=1

		self.enter_step = QtWidgets.QLineEdit('0', self)
		self.enter_step.setFixedWidth(100)
		self.layout.addWidget(self.enter_step, loc, 0)
		loc+=1
#----------------------------------------------------------------------------
		self.set_zoom_label = QtWidgets.QLabel('zoom:', self)
		self.layout.addWidget(self.set_zoom_label, loc, 0)
		loc+=1

		self.enter_zoom = QtWidgets.QLineEdit('1', self)
		self.enter_zoom.setFixedWidth(100)
		self.layout.addWidget(self.enter_zoom, loc, 0)
		loc+=1
#----------------------------------------------------------------------------
		self.display_step = QtWidgets.QLabel('step = 00000', self)
		self.layout.addWidget(self.display_step, loc, 0)
		loc+=1
#----------------------------------------------------------------------------
		self.display_norm = QtWidgets.QLabel('infty norm = 00000', self)
		self.layout.addWidget(self.display_norm, loc, 0)
		loc+=1
#----------------------------------------------------------------------------
		self.play_btn = QtWidgets.QPushButton('Play', self)
		self.play_btn.setCheckable(True)
		self.play_btn.clicked.connect(self.play_btn_state)
		self.layout.addWidget(self.play_btn, loc, 0)
		loc+=1
#----------------------------------------------------------------------------
## for 3d viewing		
		self.plotWindow = gl.GLViewWidget(self)
		self.plotWindow.setCameraPosition(distance=10)

		self.layout.addWidget(self.plotWindow, 0, 1, loc, 1)

		self.plots= []
#----------------------------------------------------------------------------
## for playing the movies
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.advance_step)
		self.update_time_ms = 50
#----------------------------------------------------------------------------
## define global variables to be used by applet
		self.filename = ''
		self.step = 0
		self.norm = 1
		self.zoom = 1
		self.maxsteps = 0
		self.plot_num = 0

		self.color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
		self.penwidth = 3
		# options for pointSymbol: None, 'x', 'o', 't', 't1', 't2'
		#'t3', 's', 'p', 'h', 'star', '+', 'd'
		self.pointSymbol = None
#----------------------------------------------------------------------------
		self.show()
#=============================================================================
	def play_btn_state(self)->None:
		if self.play_btn.isChecked():
			self.timer.start(self.update_time_ms)
		else:
			self.timer.stop()
#=============================================================================
	def advance_step(self)->None:
		if(self.step+1 < self.maxsteps):
			self.step+= 1
			self.update_plot_step()
		else:
			self.timer.stop()
			self.play_btn.toggle()
#=============================================================================
	def handleButton(self)->None:
		title    = self.load_btn.text()
		paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, title)
		for path in paths:
			self.load_data(path)
		self.update_plot_step()
#=============================================================================
	def load_data(self, filename:str)->None:
#-----------------------------------------------------------------------------
		y= np.array([])
		if (str(filename).endswith('.h5')):
			y= np.array(read_vals_hdf5(str(filename)))
		elif (str(filename).endswith('.csv')):
			y= np.array(read_vals_csv_2d(str(filename)))
		else:
			raise ValueError('improper file extension')
		print(y.shape)
#-----------------------------------------------------------------------------
		if (self.plot_num==0):
			self.maxsteps= np.shape(y)[0]
			self.var_arr= {} 
			self.var_arr[self.plot_num]= y
			self.var_names = self.prune_string(filename)
			self.plot_data(self.var_arr[0])
		else:
			self.maxsteps= min(self.maxsteps,np.shape(y)[0])
			self.var_arr[self.plot_num]= y
			self.var_names = np.append(self.var_names, self.prune_string(filename))
			self.plot_data(self.var_arr[self.plot_num])
		self.plot_num+= 1
		print('loaded'+str(filename))
#=============================================================================
	def prune_string(self, filename:str)->str:
		loc_start= str(filename).rfind('/')+1
		loc_end= str(filename).rfind('.')
		name_str= str(filename)[loc_start:loc_end]
		return name_str
#=============================================================================
## the x-y space is set to be a [-5,5]x[-5,5] box
#=============================================================================
	def plot_data(self, vals) -> None:
		if (len(vals.shape)!=3):
			raise ValueError("len(y.shape)!=3")
		self.plots.append(
			gl.GLSurfacePlotItem(
				x= np.linspace(-2.5,2.5,vals[0].shape[0]),
				y= np.linspace(-2.5,2.5,vals[0].shape[1]),
				shader='heightColor',
				computeNormals=False,
				smooth=False
			)
		)
		self.plots[-1].shader()['colorMap'] = np.array([
			-0.3, ## red 1
			 0.1, ## red 2
			 0.3, ## red 3
			-0.6, ## green 1
			-0.2, ## green 2
			 0.6, ## green 3
			-1.0, ## blue 1
			 0.3, ## blue 2
			 1.0  ## blue 3
		])
		self.plots[-1].setData(z=vals[0])
		self.plotWindow.addItem(self.plots[-1])
#=============================================================================
	def keyPressEvent(self, event)->None:
		super(Plotter, self).keyPressEvent(event)
		self.keyPressed.emit(event)
		self.step = int(  str(self.enter_step.text()))
		self.zoom = float(str(self.enter_zoom.text()))

		self.update_plot_step()
#=============================================================================
	def update_plot_step(self)->None:
		self.compute_norm()
		self.update_display()
		if (self.plot_num<=0):
			raise ValueError("self.plot_num<=0")
		for i in range(self.plot_num):
			self.plots[i].setData(
				z=self.var_arr[i][self.step, :, :]/(self.norm/self.zoom)
			)
#=============================================================================
	def compute_norm(self)->None:
		self.norm=0
		for i in range(self.plot_num):
			self.norm= max(
				abs(self.var_arr[i][self.step, :, :]).max(),
				self.norm
			)
		if (self.norm==0):
			self.norm= 1
#=============================================================================
	def update_display(self)->None:
		self.display_step.setText('step = {}'.format(self.step))
		self.display_norm.setText('infty norm = {:.6e}'.format(self.norm))
#=============================================================================
## if press 'q' then closes the application
## if press right/left arrow thentime step +1/-1
	def on_key(self, event)->None:
		if(event.key() == QtCore.Qt.Key_Q):
			print('Exiting')
			self.deleteLater()
		else:
			pass
#=============================================================================
#=============================================================================
def main():
	app = QtWidgets.QApplication(sys.argv)
	plot = Plotter()
	sys.exit(app.exec_())
#=============================================================================
#=============================================================================
if __name__ == '__main__':
	main()

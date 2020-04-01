import numpy as np

from io_hdf5 import *

#-----------------------------------------------------------------------------
## example implementation
#-----------------------------------------------------------------------------
if __name__ == '__main__':
	init_hdf5('example_1D.h5')
	for i in range(100):
		time= i
		vals=   np.random.random(size=(100))
		
		write_line_hdf5('example_1D.h5',time,vals)
#-----------------------------------------------------------------------------
	init_hdf5('example_2D_01.h5')
	for i in range(100):
		time= i

		cols = 100
		rows = 100
		x_coords = np.linspace(-2*np.pi, 2*np.pi, cols+1)
		y_coords = np.linspace(-2*np.pi, 2*np.pi, rows+1)

		vals= np.array([
			[np.sin(0.01*time*x*y) for x in x_coords]
			for y in y_coords
		])
		write_line_hdf5('example_2D_01.h5',time,vals)
#-----------------------------------------------------------------------------
	init_hdf5('example_2D_02.h5')
	for i in range(100):
		time= i

		cols = 100
		rows = 100
		x_coords = np.linspace(-2*np.pi, 2*np.pi, cols+1)
		y_coords = np.linspace(-2*np.pi, 2*np.pi, rows+1)

		vals= np.array([
			[np.sin(0.01*time*x*y)*10*np.cos(2*np.pi*i/50) for x in x_coords]
			for y in y_coords
		])
		write_line_hdf5('example_2D_02.h5',time,vals)

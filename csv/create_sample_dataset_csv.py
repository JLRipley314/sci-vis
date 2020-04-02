import numpy as np

from io_csv import *

#-----------------------------------------------------------------------------
## example implementation
#-----------------------------------------------------------------------------
if __name__ == '__main__':
        init_csv('example_1d_1')
        init_csv('example_1d_2')
        init_csv('example_1d_3')
        init_csv('example_1d_4')
        for i in range(100):
                vals= np.random.random(size=(100))    
                write_line_csv_1d('example_1d_1',vals)
        for i in range(100):
                vals= np.random.random(size=(100))    
                write_line_csv_1d('example_1d_2',vals)
        for i in range(100):
                vals= np.random.random(size=(100))    
                write_line_csv_1d('example_1d_3',vals)
        for i in range(100):
                vals= np.random.random(size=(100))    
                write_line_csv_1d('example_1d_4',vals)

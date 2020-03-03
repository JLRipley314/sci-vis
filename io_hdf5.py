import numpy as np
import h5py

from typing import List

#-----------------------------------------------------------------------------
### basic functions 
#-----------------------------------------------------------------------------
def init_hdf5(name:str) -> None:
	with h5py.File(name,'w') as hf:
		hf.create_group('time')
		hf.create_group('vals')
#-----------------------------------------------------------------------------
def write_line_hdf5(
name:str,
time:float,
vals:List[float]
) -> None:
	with h5py.File(name,'a') as hf:
		gr_time=   hf.get('time')
		gr_vals=   hf.get('vals')
		step= len(gr_time)
		gr_time.create_dataset(str(step),data=time)
		gr_vals.create_dataset(str(step),data=vals)
#-----------------------------------------------------------------------------
def read_line_hdf5(
name:str,
step:int,
) -> List[List[float]]:
	with h5py.File(name,'a') as hf:
		time= hf.get('time').get(str(step))
		vals= hf.get('vals').get(str(step))
	return [time,vals] 
#-----------------------------------------------------------------------------
def read_hdf5(name:str) -> (np.array, np.array):
	with h5py.File(name,'a') as hf:
		gr_vals=   hf.get('vals')

		vals= [	np.array(gr_vals.get(str(step)))
			for step in range(len(gr_vals))
		]
		return np.array(vals)

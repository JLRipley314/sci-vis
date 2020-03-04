import numpy as np
import h5py

from typing import List

#-----------------------------------------------------------------------------
### basic functions 
#-----------------------------------------------------------------------------
def init_hdf5(name:str) -> None:
	with h5py.File(name,'w') as f:
		f.create_group('time')
		f.create_group('vals')
#-----------------------------------------------------------------------------
def write_line_hdf5(
name:str,
time:float,
vals:List[float]
) -> None:
	with h5py.File(name,'a') as f:
		grp_time=   f.get('time')
		grp_vals=   f.get('vals')
		step= len(grp_time)
		grp_time.create_dataset(str(step),data=time)
		grp_vals.create_dataset(str(step),data=vals)
#-----------------------------------------------------------------------------
def read_line_hdf5(
name:str,
step:int,
) -> List[List[float]]:
	with h5py.File(name,'a') as f:
		time= f.get('time').get(str(step))
		vals= f.get('vals').get(str(step))
	return [time,vals] 
#-----------------------------------------------------------------------------
def read_hdf5(name:str) -> (np.array, np.array):
	with h5py.File(name,'r') as f:
		grp_vals= f.get('vals')

		vals= [	np.array(grp_vals.get(str(step)))
			for step in range(len(grp_vals))
		]
		return np.array(vals)

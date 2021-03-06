#-----------------------------------------------------------------------------
## basic format: time, nx, ny, [data]
#-----------------------------------------------------------------------------
import numpy as np

from typing import List

import sys	
#-----------------------------------------------------------------------------
## basic functions 
#-----------------------------------------------------------------------------
def set_extension(name:str) -> str:
   if name.endswith('.csv'):
      return name
   else:
      return name+'.csv'
#-----------------------------------------------------------------------------
def init_csv(name:str) -> None:
   name= set_extension(name)
   with open(name,'w') as f:
      pass
#-----------------------------------------------------------------------------
def write_line_csv_1d(name:str,vals:List[float]) -> None:
   name= set_extension(name)
   with open(name,'a') as f:
      for val in vals[:-1]:
         f.write(str(val)+',')
      f.write(str(vals[-1])+'\n')
#-----------------------------------------------------------------------------
def read_line_csv_1d(name:str,step:int) -> List[float]:
   name= set_extension(name)
   ctr= 0
   with open(name,'r') as f:
      for line in f:
         if ctr==step:
            return [float(val) for val in line.split(',')]
         ctr+= 1
   raise ValueError('step '+str(step)+' not in file')
#-----------------------------------------------------------------------------
def read_vals_csv_1d(name:str) -> np.array:
   name= set_extension(name)
   vals= []
   with open(name,'r') as f:
      for line in f:
         line= [v for v in line.split(',')]
         nx= int(line[1])
         arr= np.zeros((nx))
         for i in range(nx):
            arr[i]= float(line[2+i])
         vals.append(arr)
   return np.array(vals)
#-----------------------------------------------------------------------------
## format for 2d csv: time, nx, ny, arr
#-----------------------------------------------------------------------------
def read_vals_csv_2d(name:str) -> np.array:
   name= set_extension(name)
   vals= []
   with open(name,'r') as f:
      for line in f:
         line= [v for v in line.split(',')]
         nx= int(line[1])
         ny= int(line[2])
         arr= np.zeros((nx,ny))
         for i in range(nx):
            for j in range(ny):
               try:
                  arr[i][j]= float(line[3+ny*i+j])
               except ValueError:
                  arr[i][j]= float(0)
         vals.append(arr)
   return np.array(vals)
#-----------------------------------------------------------------------------
def read_times_vals_csv_2d(name:str) -> (np.array,np.array):
   name= set_extension(name)
   times= []
   vals= []
   with open(name,'r') as f:
      for line in f:
         line= [v for v in line.split(',')]
         time= float(line[0])
         nx= int(line[1])
         ny= int(line[2])
         arr= np.zeros((nx,ny))
         for i in range(nx):
            for j in range(ny):
               try:
                  arr[i][j]= float(line[3+ny*i+j])
               except ValueError:
                  arr[i][j]= float(0)
         times.append(time)
         vals.append(arr)
   return times, np.array(vals)

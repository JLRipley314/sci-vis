# Scientific visualization functions

Routines to visualize 1D and 2D time dependent data from either
hdf5 or csv. 

[Alex Pandya](https://github.com/aapandy2)
wrote an earlier version of this software for
visualizing 1 dimensional time dependent data.

The scripts `plotters/plotter_1d.py` and `plotters/plotter_2d.py` 
will render 1d and 2d data, respectively.
Currently they are configured to either other .h5 of .csv
data. 

If you are using this code, it is likely because you
are making use of another code that writes data in a format
these scripts can read in. 
For example, for .csv files the file format is that
each row (for 1D data) is

[time],[nx],[data]

where [time] is the time value for that array,
[nx] is the number of data points, and [data] is
the comma sepearted values of the data saved at that time. 

## Dependencies

* numpy
* h5py
* pyqtgraph

## Further information

For questions please email ripley[at]illinois[dot]edu 

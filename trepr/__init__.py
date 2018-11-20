"""
trepr package

Package for reproducible and traceable analysis of trepr data.

Available modules
-----------------
dataset
    Unit containing data and metadata
importer
    Import trepr data into datasets
averaging
    Generate an averaging over a given dataset
coloring
    Generate a colormap corresponding to the given dataset
plotter
    Plot data in datasets
pretrigger_offset_compensation
    Compensate the pretrigger offset
saver
    Save given plots

"""

from .dataset import *
from .io import *
from .averaging import *
from .coloring import *
from .plotter import *
from .pretrigger_offset_compensation import *
from .saver import *
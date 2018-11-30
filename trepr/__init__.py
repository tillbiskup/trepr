"""
trepr package

Package for reproducible and traceable analysis of trepr data.

Available modules
-----------------
caller
    Call all necessary processing and plotting classes and generate a report.
coloring
    Generate a colormap corresponding to the given dataset.
dataset
    Generate a unit containing data and mapped metadata.
io
    Import trepr data into datasets.
plotter
    Plot data in datasets.
processing
    Do processing steps on the given dataset.
report
    Generate a report.
saver
    Save given plots.
yaml_loader
    Load a given YAML file

"""

from .caller import *
from .coloring import *
from .dataset import *
from .io import *
from .plotter import *
from .processing import *
from .report import *
from .saver import *
from .yaml_loader import *
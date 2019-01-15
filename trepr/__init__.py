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
import trepr.dataset
import trepr.io
import trepr.plotting
import trepr.processing

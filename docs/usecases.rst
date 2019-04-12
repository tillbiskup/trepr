=========
Use cases
=========

This section provides a few ideas of how basic operation of the trepr package may look like.


Create a dataset and import data
================================

Most probably, the first step when processing and analysing data will be to actually import raw data into a dataset by using an importer::

    import trepr

    dataset_ = trepr.dataset.ExperimentalDataset()
    importer_ = trepr.io.Importer(source="path/to/some/file/containing/data")

    dataset_.import_from(importer)

This will import the data (and metadata) contained in the path provided to the argument ``source`` when instantiating the ``Importer`` object.

A few comments on these few lines of code:

* Naming the dataset object ``dataset_`` prevents shadowing the module name. Feel free to give it another equally fitting name. Appending an underscore to a variable name in such a case is a common solution complying to `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_. The same applies to the next line instantiating the importer object.

* Always define first an instance of the dataset class, and afterwards use the public methods of this object, such as ``import_from()`` or ``process()``.


Process data
============

After a dataset has been created, the data can be processed by creating an object of the corresponding processing class::

    pretrigger_offset_compensation = trepr.processing.PretriggerOffsetCompensation()

    dataset_.process(pretrigger_offset_compensation)

This will generate an object of the class ``PretriggerOffsetCompensation`` and process the data as specified by the class. The same procedure works for all classes of the processing module.


Analyse data
============

After general processing of the data, it might be usefull to do some analysis. The analysis module provides several analysis steps. The usage is the same as at processing::

    mw_freq_analysis = trepr.analysis.MwFreqAnalysis()
    dataset_.analyse(mw_freq_analysis)

The results of the analysis step will be stored in the attribute ``result`` of the respective analysis step object.


Plot and save data
==================

Both processed and unprocessed data can be plotted and the figures saved. For this purpose, both a plotter and a saver object must be initiated::

    plotter_ = trepr.plotting.ScaledImagePlot()
    saver_ = trepr.plotting.Saver("path/where/the/figure/shoud/be/stored")
    dataset_.plot(plotter_).save(saver_)

This will generate objects of the class ``ScaledImagePlot`` and ``Saver`` and process the data as specified by the class. The same procedure works for all classes of the plotting module.



Recipe-driven data analysis
===========================
The most important component of recipe-driven data analysis is the recipe. In case of the trepr package, this is a human readable and writeable YAML file containing all information to perform the data analysis fully unattended.


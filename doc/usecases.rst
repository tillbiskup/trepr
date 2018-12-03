=========
Use cases
=========

This section provides a few ideas of how basic operation of the trepr package may look like.


Create a dataset and import data
================================

Most probably, the first step when processing and analysing data will be to actually import data into a dataset by using an importer::

    import trepr

    dataset_ = trepr.dataset.Dataset()
    importer_ = trepr.io.Importer(source="path/to/some/file/containing/data")

    dataset_.import_from(importer)

This will import the data (and metadata) contained in the path provided to the argument ``source`` when instantiating the ``Importer`` object.

A few comments on these few lines of code:

* Naming the dataset object ``dataset_`` prevents shadowing the module name. Feel free to give it another equally fitting name. Appending an underscore to a variable name in such case is a common solution complying to `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_. The same applies to the next line instantiating the importer object.

* Always define first an instance of the dataset class, and afterwards use the public methods of this object, such as ``import_from()`` or ``process()``.

Process data
============

After a dataset has been created, the data can be processed by creating an object of the corresponding processing class::

    pretrigger_offset_compensation = trepr.processing.PretriggerOffsetCompensation()

    dataset_.process(pretrigger_offset_compensation)

This will generate an object of the class ``PretriggerOffsetCompensation`` and process the data as specified by the class. The same procedure works for all classes of the processing module.

Plot and save data
==================

Both processed and unprocessed data can be plotted and the figures saved. For this purpose, both a plotter and a saver object must be initiated::

    plotter = trepr.plotter.Plotter2D()
    saver = trepr.saver.Saver("path/where/the/figure/shoud/be/stored")

    dataset_.plot(plotter).save(saver)

This will generate objects of the class ``Plotter2D`` and ``Saver`` and process the data as specified by the class. The same procedure works for all classes of the plotter module.

Automatic processing
====================

The trepr package offers automatic processing. Therefore a YAML file needs to be passed to the caller. The YAML file has the following structure::

    ---
    format:
        type: trepr report
        version: 0.0.1

    dataset:
        path: /path/to/your/dataset
    figures:
        - Plotter2D:
            pretrigger compensation: True
            averaging: False
        - Plotter1D:
            pretrigger compensation: True
            averaging: True
            average range: [3400, 3500]
            average dimension: 1
            average unit: axis
    report: True

In the YAML file you specify which processing will be carried out, which figures will be created and whether a report will be generated.
Passing the YAML file to the caller is very simple::

    trepr.caller.Caller("YourYAMLFile.yaml")

The particular example shown above will generate two figures and a report, all stored in the same path as the given data.



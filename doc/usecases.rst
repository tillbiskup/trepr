=========
Use cases
=========

This section provides a few ideas of how basic operation of the trepr package may look like.


Create a dataset and import data
================================

Most probably, the first step when processing and analysing data will be to actually import data into a dataset by using an importer.::

    import trepr

    dataset_ = trepr.dataset.Dataset()
    importer_ = trepr.io.Importer(source="path/to/some/file/containing/data")

    dataset_.import_from(importer)

This will import the data (and metadata) contained in the path provided to the argument ``source`` when instantiating the ``Importer`` object.

A few comments on this few lines of code:

* Naming the dataset object ``dataset_`` prevents shadowing the module name. Feel free to give it another equally fitting name. Appending an underscore to a variable name in such case is a common solution complying to `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_. The same applies to the next line instantiating the importer object.

* Always define first an instance of the dataset class, and afterwards use the public methods of this object, such as ``import_from()`` or ``process()``.


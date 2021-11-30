=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.1.1
=================

* Add Zenodo badge in README and documentation


For version 0.2
===============

* Implement Bruker BES3T importer/copy from cwepr package

  * Needs at least some adjustments, as tr-EPR data are usually two-dimensional, but don't necessarily consist of additional file(s) for the axis

* Processing step for setting the trigger point (necessary for BES3T data)

* Analysis steps for MW frequency drift and measurement time: options to return dataset for further investigation

* Implement transient nutation analysis (FFT) (?)

* Improve handling of reports


For later versions
==================

* Extend documentation (tr-EPR primer)

* Start to (re)implement functionality test-driven.

* Batch processing (via recipes?)

  * Basic preprocessing, plot, export as PNG/PDF, figure caption for dokuwiki


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::


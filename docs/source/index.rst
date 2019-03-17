.. Pygenprop documentation master file, created by
   sphinx-quickstart on Sun Mar 17 15:45:23 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pygenprop's Documentation
=========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Content
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Overview
--------

Pygenprop is a python library for programmatic exploration and usage of the `EBI Genome Properties database <https://github.com/ebi-pf-team/genome-properties>`_.

Features
--------

At its core the library contains four core components:

* An object model for representing the Genome Properties database as a rooted direct acyclic graph.
* A parser for Genome Properties database flat files.
* A parser for Genome Properties assignment longform files.
* A parser for InterProScan TSV files.

A basic tutorial can be found on our `Github README <https://github.com/Micromeda/pygenprop/tree/master#usage>`_. More
detailed documentation on each module's API can be found in the :ref:`modindex`.

# Pygenprop
| Branch 	|  Status 	|
|---------	|----------------------------------------------------------------------------------------------------------------------------	|
| Master 	| [![Build Status](https://travis-ci.org/Micromeda/pygenprop.svg?branch=master)](https://travis-ci.org/Micromeda/pygenprop) 	|
| Develop 	| [![Build Status](https://travis-ci.org/Micromeda/pygenprop.svg?branch=develop)](https://travis-ci.org/Micromeda/pygenprop) 	|
| Docs 	    | [![Documentation Status](https://readthedocs.org/projects/pygenprop/badge/?version=latest)](https://pygenprop.readthedocs.io/en/latest/?badge=latest)


Pygenprop is a python library for programmatic exploration and usage of the [EBI Genome Properties database](https://github.com/ebi-pf-team/genome-properties).   

Features
--------

At its core, the library contains five major components:

- An object model for representing the Genome Properties database as an in-memory rooted direct acyclic graph
- A parser for Genome Properties database flat files
- A parser for Genome Properties assignment long form files
- A parser for InterProScan TSV files
- A results class which is used to assign genome properties to one or more organisms and compare assignments between multiple organisms

Installation
------------

Pygenprop is compatible with Python 3.6 or higher (3.5 may work, but it is not tested). Requirements can be found in ```requirements.txt```.

#### To install from PyPi

```shell
pip install pygenprop
```

#### To install from source (for development)

```shell
cd /path/to/pygenprop_source_dir
pip install .
```

Acquiring Genome Properties Data
--------------------------------

Before Pygenprop can assign genome properties to an organism, it first has to gather information from to the Genome Properties database. The easiest way to gain access is through the parsing of a Genome Properties Database release file. This file is found in the [EBI Genome Properties Github repository](https://github.com/ebi-pf-team/genome-properties) and is called [```genomeProperties.txt```](https://raw.githubusercontent.com/ebi-pf-team/genome-properties/master/flatfiles/genomeProperties.txt). The file is located in the repository's [flatfiles folder](https://github.com/ebi-pf-team/genome-properties/blob/master/flatfiles). For each release of Genome Properties, a ```genomeProperties.txt``` file is generated from the description files of all **public** genome properties.

#### Acquiring Release Files  

```genomeProperties.txt``` files can be found at URLs in the compatibility section below using a web browser or UNIX commands such as ```wget``` or ```curl```. They can also be streamed directly into Jupyter notebooks using the [requests python library](https://3.python-requests.org). Code for streaming the database into a Jupyter notebook can be found [here](https://github.com/Micromeda/pygenprop/blob/master/docs/source/_static/tutorial/tutorial.ipynb).

#### Compatibility

Pygenprop will be continually updated to take into account changes in the schema of the Genome Properties database. Below is a compatibility table that maps between Genome Properties and Pygenprop releases.

| Genome Properties Release 	| genomeProperties.txt URL	| Compatible Pygenprop Release 	|
|---------------------------	|----------------------	    |-------------------	|
| 1.1 	| https://raw.githubusercontent.com/ebi-pf-team/genome-properties/rel1.1/flatfiles/genomeProperties.txt 	| 0.6 	|
| 2.0 	|  https://raw.githubusercontent.com/ebi-pf-team/genome-properties/rel2.0/flatfiles/genomeProperties.txt	| 0.6 	|
| Latest    | https://raw.githubusercontent.com/ebi-pf-team/genome-properties/master/flatfiles/genomeProperties.txt | 0.6

#### Accessing Non-public Properties

The [```./data```](https://github.com/ebi-pf-team/genome-properties/tree/master/data) folder of the [EBI Genome Properties Github repository](https://github.com/ebi-pf-team/genome-properties) contains a series of folders with information about both public and non-public genome properties. Each folder contains both a description (```DESC```) file and a status (```status```) file. The status file contains information on whether a property is public or not (```public:	0``` means that a property is not public). One can use these status files to find non-public properties. The description files for these non-public properties can be parsed using the same parser as used for ```genomeProperties.txt```. Each [genome property object](https://pygenprop.readthedocs.io/en/latest/pygenprop.html#module-pygenprop.genome_property) that results from the parsing of a description file has an object attribute called **public** which can be set to **true** or **false** to designate a property as public or not.

```python
property_one.public = False 
```

Acquiring Annotation Data
-------------------------

Pygenprop can assign genome properties to an organism from [InterProScan annotation TSV files](https://github.com/ebi-pf-team/interproscan/wiki/OutputFormats#tab-separated-values-format-tsv), [Genome Properties long-form assignment files](https://github.com/Micromeda/pygenprop/blob/master/pygenprop/testing/test_constants/C_chlorochromatii_CaD3.txt) (created by the Genome Properties Perl library) or a list of InterPro consortium signature accessions downloaded into a Jupyter Notebook. Pre-calculated InterProScan results for UniProt proteomes and taxonomies can be downloaded (in signature accession list format) from the [beta version of the InterPro website](https://www.ebi.ac.uk/interpro/beta/proteome/uniprot/#table).

#### Example Data

- [An InterProScan TSV file](https://github.com/Micromeda/pygenprop/blob/master/pygenprop/testing/test_constants/C_chlorochromatii_CaD3.tsv)
- [A Genome Properties longform assignment file](https://github.com/Micromeda/pygenprop/blob/master/pygenprop/testing/test_constants/C_chlorochromatii_CaD3.txt)

#### Running InterProScan

InterProScan generates InterProScan annotation TSV files via domain annotation of an organism's proteins. Details and install instructions for InterProScan5 can be found [here](https://github.com/ebi-pf-team/interproscan/wiki). For convenience, a Docker container for installing and running InterProScan5 can be found [here](https://github.com/Micromeda/InterProScan-Docker).

Usage
-----

Below is a simple usage overview. Full API documentation is available [here](https://pygenprop.readthedocs.io/en/latest/py-modindex.html).

#### Example Workflow

A typical use case for Pygenprop will involve a researcher seeking to compute and compare Genome Properties between organisms of interest. For example, a researcher may have discovered a novel bacterium and would want to compare its functional capabilities to other bacteria within the same genus. The researcher could start the analysis by opening up a Jupyter Notebook and directly importing pre-calculated InterProScan annotations for novel and reference genomes within the same genus. Below is example code for comparing virulence genome properties of *E. coli* K12 and O157:H7.

**An interactive Jupyter notebook version of this workflow, with outputs for each step, can be found [here](https://github.com/Micromeda/pygenprop/blob/master/docs/source/_static/tutorial/tutorial.ipynb)**.


```python
from pygenprop.results import GenomePropertiesResults
from pygenprop.assignment_file_parser import parse_interproscan_file
from pygenprop.database_file_parser import parse_genome_properties_flat_file

# Parse the flatfile database
with open('properties.txt') as file:
    tree = parse_genome_properties_flat_file(file)

# Parse InterProScan files
with open('E_coli_K12.tsv') as ipr5_file_one:
    cache_1 = parse_interproscan_file(ipr5_file_one)

with open('E_coli_O157_H7.tsv') as ipr5_file_two:
    cache_2 = parse_interproscan_file(ipr5_file_two)

# Create results comparison object
results = GenomePropertiesResults(cache_1, cache_2, 
                                  properties_tree=tree)
                                          
# Get properties with differing assignments
differing_results = results.differing_property_results

# Get property by identifier
virulence = tree['GenProp0074']

# Iterate to get the identifiers of 
# child properties of virulence
types_of_vir = [genprop.id for genprop in virulence.children]

# Get assignments for virulence properties
virulence_assignments = results.get_results(*types_of_vir, 
                                            steps=False)

# Get percentages of virulence steps assigned 
# YES, NO, and PARTIAL per organism
virulence_summary = results.get_results_summary(*types_of_vir, 
                                                steps=True, 
                                                normalize=True)
```

Documentation
-------------
Documentation can be found on [Read the Docs](http://pygenprop.rtfd.io/). 

Trouble Shooting
----------------

Please report issues to the **[issues page](https://github.com/Micromeda/pygenprop/issues)**.

File Manifest
-------------
```
.
├── LICENSE
├── README.md
├── docs
│   ├── Makefile
│   └── source
│       ├── _static
│       ├── _templates
│       ├── conf.py
│       ├── index.rst
│       ├── modules.rst
│       ├── pygenprop.rst
│       └── pygenprop.testing.rst
├── pygenprop
│   ├── __init__.py
│   ├── assign.py
│   ├── assignment_file_parser.py
│   ├── database_file_parser.py
│   ├── database_reference.py
│   ├── evidence.py
│   ├── functional_element.py
│   ├── genome_property.py
│   ├── lib.py
│   ├── literature_reference.py
│   ├── results.py
│   ├── step.py
│   ├── testing
│   │   ├── __init__.py
│   │   ├── compare_assignment_to_assign_properties_perl.ipynb
│   │   ├── test_assign.py
│   │   ├── test_constants
│   │   │   ├── C_chlorochromatii_CaD3.tsv
│   │   │   ├── C_chlorochromatii_CaD3.txt
│   │   │   ├── C_luteolum_DSM_273.txt
│   │   │   ├── test_genome_properties.txt
│   │   │   └── test_genome_properties_two.txt
│   │   ├── test_database_reference.py
│   │   ├── test_evidence.py
│   │   ├── test_functional_element.py
│   │   ├── test_genome_property.py
│   │   ├── test_lib.py
│   │   ├── test_literature_reference.py
│   │   ├── test_parse.py
│   │   ├── test_parse_genome_properties_assignments.py
│   │   ├── test_parse_genome_properties_end_to_end.sh
│   │   ├── test_parse_genome_properties_file.py
│   │   ├── test_parse_interproscan.py
│   │   ├── test_results.py
│   │   ├── test_step.py
│   │   └── test_tree.py
│   └── tree.py
├── requirements.txt
└── setup.py
```

Licence
-------

Apache License 2.0

Current Contributors
--------------------

[Lee Bergstrand](http://github.com/LeeBergstrand)

Past Contributors
-----------------

N/A

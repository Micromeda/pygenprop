
# Pygenprop
| Branch 	|  Status 	|
|---------	|----------------------------------------------------------------------------------------------------------------------------	|
| Master 	| [![Build Status](https://travis-ci.org/Micromeda/pygenprop.svg?branch=master)](https://travis-ci.org/Micromeda/pygenprop) 	|
| Develop 	| [![Build Status](https://travis-ci.org/Micromeda/pygenprop.svg?branch=develop)](https://travis-ci.org/Micromeda/pygenprop) 	|
| Docs 	    | [![Documentation Status](https://readthedocs.org/projects/pygenprop/badge/?version=latest)](https://pygenprop.readthedocs.io/en/latest/?badge=latest)


Pygenprop is a python library for programmatic exploration and usage of the [EBI Genome Properties database](https://github.com/ebi-pf-team/genome-properties).   

Features
--------

At its core, the library contains four major components:

- An object model for representing the Genome Properties database as an in-memory rooted direct acyclic graph.
- A parser for Genome Properties database flat files.
- A parser for Genome Properties assignment long form files.
- A parser for InterProScan TSV files.

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

Accessing The Genome Properties Database
----------------------------------------

The primary way for Pygenprop to access the Genome Properites database is through the parsing of a Genome Properties release file found in the [EBI Genome Properties database repository](https://github.com/ebi-pf-team/genome-properties). This file is called ```genomeProperties.txt``` and is located in the flatfiles folder (https://github.com/ebi-pf-team/genome-properties/blob/master/flatfiles/genomeProperties.txt). This file is generated for each Genome Properties release and only contains **public** genome properties.

#### Compatibility

As Genome Properties evolves, Pygenprop is updated to be compatible.

| Genome Properties Release 	| genomeProperties.txt URL	| Pygenprop Release 	|
|---------------------------	|----------------------	    |-------------------	|
| 1.1 	| https://raw.githubusercontent.com/ebi-pf-team/genome-properties/rel1.1/flatfiles/genomeProperties.txt 	| 0.6 	|
| 2.0 	|  https://raw.githubusercontent.com/ebi-pf-team/genome-properties/rel2.0/flatfiles/genomeProperties.txt	| 0.6 	|
| Latest    | https://raw.githubusercontent.com/ebi-pf-team/genome-properties/master/flatfiles/genomeProperties.txt | 0.6

Acquiring Input Data
--------------------

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

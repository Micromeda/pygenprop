
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

Acquiring Input Data
--------------------
Pygenprop can assign genome properties to an organism from [InterProScan annotation TSV files](https://github.com/ebi-pf-team/interproscan/wiki/OutputFormats#tab-separated-values-format-tsv), [Genome Properties long-form assignment files](https://github.com/Micromeda/pygenprop/blob/master/pygenprop/testing/test_constants/C_chlorochromatii_CaD3.txt) (created by the Genome Properties Perl library) or a list of InterPro consortium signatures created in a Jupyter Notebook.

#### Example Data

- [An InterProScan TSV file](https://github.com/Micromeda/pygenprop/blob/master/pygenprop/testing/test_constants/C_chlorochromatii_CaD3.tsv)
- [A Genome Properties longform assignment file](https://github.com/Micromeda/pygenprop/blob/master/pygenprop/testing/test_constants/C_chlorochromatii_CaD3.txt)

#### Running InterProScan

InterProScan generates InterProScan annotation TSV files via domain annotation of an organism's proteins. Details and install instructions for InterProScan5 can be found [here](https://github.com/ebi-pf-team/interproscan/wiki). For connivance, a Docker container for installing and running InterProScan5 can be found [here](https://github.com/Micromeda/InterProScan-Docker).

Usage
-----

Below is a simple usage overview. Full API documentation is available [here](https://pygenprop.readthedocs.io/en/latest/py-modindex.html).

### The Property Tree
[https://github.com/Micromeda/pygenprop/blob/develop/modules/genome_properties_tree.py](https://github.com/Micromeda/pygenprop/blob/develop/modules/genome_properties_tree.py)

```python
# Create a genome properties tree
with open(genome_property_flat_file_path) as genome_property_file:
        properties_tree = genome_property_flat_file(genome_property_file)

# The tree is searchable by property identifier
genome_property_56 = properties_tree['GP0056']

# The tree is also iterable
for property in properties_tree:
      print(property)

# Special short cut properties allow quick access
root_genome_property = properties_tree.root
leaf_genome_properties = properties_tree.leafs
```

#### Logical Structure:

![pygenprop structure](https://user-images.githubusercontent.com/5819462/48955710-3a89ce80-ef1d-11e8-9969-d021700c04a6.png)

### Property Assignments:
[https://github.com/Micromeda/pygenprop/blob/develop/modules/genome_properties_results.py](https://github.com/Micromeda/pygenprop/blob/develop/modules/genome_properties_results.py)

```python
assignments = []

# Generate assignments for each property file
for path in assignment_file_paths:
	with open(path) as assignment_file:
		assignments.append(parse_interproscan_file(assignment_file))

# Combine them into a results object
results = GenomePropertiesResults(*assignments, properties_tree=properties_tree)

# Get step and property results across samples
property_result_pandas_dataframe = results.property_results
step_result_pandas_dataframe = results.step_result

# Get results for specific properties and steps
result_for_gp_56 = results.get_property_result('GP0056')
result_for_gp_56_step_1 = results.get_step_result('GP0056', 1)

```

Documentation
-------------
Our documentation can be found on [Read the Docs](http://pygenprop.rtfd.io/). 

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

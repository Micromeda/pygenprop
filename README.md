
# Pygenprop
| Branch 	| CI Status 	|
|---------	|----------------------------------------------------------------------------------------------------------------------------	|
| Master 	| [![Build Status](https://travis-ci.org/Micromeda/pygenprop.svg?branch=master)](https://travis-ci.org/Micromeda/pygenprop) 	|
| Develop 	| [![Build Status](https://travis-ci.org/Micromeda/pygenprop.svg?branch=develop)](https://travis-ci.org/Micromeda/pygenprop) 	|

Pygenprop is a python library for programmatic exploration and usage of the [EBI Genome Properties database](https://github.com/ebi-pf-team/genome-properties).   

Features
--------

At its core the library contains three core components:

- An object model for representing the Genome Properties database as a polytree.
- A parser for Genome Properties database flat files.
- A parser for Genome Properties assignment longform files.

Usage
-----

### Property Tree
[https://github.com/Micromeda/pygenprop/blob/develop/modules/genome_properties_tree.py](https://github.com/Micromeda/pygenprop/blob/develop/modules/genome_properties_tree.py)

```python
with open(genome_property_flat_file_path) as genome_property_file:
        properties_tree = parse_genome_property_file(genome_property_file)

# Searchable by property ID
genome_property_56 = properties_tree['GP0056']

# Iterable
for property in properties_tree:
      print(property)

# Special short cut properties
root_genome_property = properties_tree.root
leaf_genome_properties = properties_tree.leafs
```

#### Logical Structure:

![pygenprop structure](https://user-images.githubusercontent.com/5819462/48955710-3a89ce80-ef1d-11e8-9969-d021700c04a6.png)

### Property Assignments:
[https://github.com/Micromeda/pygenprop/blob/develop/modules/genome_properties_results.py](https://github.com/Micromeda/pygenprop/blob/develop/modules/genome_properties_results.py)

```python
assignments = []
   
 for path in assignment_file_paths:
        with open(path) as assignment_file:
            assignments.append(parse_genome_property_longform_file(assignment_file))

results = GenomePropertiesResults(*assignments, genome_properties_tree=properties_tree)

property_result_pandas_dataframe = results.property_results
step_result_pandas_dataframe = results.step_result

result_for_gp_56 = results.get_property_result('GP0056')
result_for_gp_56_step_1 = results.get_step_result('GP0056', 1)

```

For more of the API you'll have to read the code for now. It's pretty well documented.

[https://github.com/Micromeda/pygenprop/tree/develop/modules](https://github.com/Micromeda/pygenprop/tree/develop/modules)
	       

Installation
------------

Pygenprop is currently not on PyPI or Conda yet. For now, one can simply download this repository and run ```pip install .``` at the root of the repository to install Pygenprop to their system. 

Documentation
-------------
Our documentation can be found in the **[Wiki](https://github.com/Micromeda/pygenprop/wiki)**.

Trouble Shooting
----------------

Please report issues to the **[issues page](https://github.com/Micromeda/pygenprop/issues)**.

File Manifest
-------------
```
.
├── LICENSE
├── README.md
├── pygenprop
│   ├── __init__.py
│   ├── __pycache__
│   ├── assignment_file_parser.py
│   ├── database_reference.py
│   ├── evidence.py
│   ├── flat_file_parser.py
│   ├── functional_element.py
│   ├── genome_property.py
│   ├── lib.py
│   ├── literature_reference.py
│   ├── results.py
│   ├── step.py
│   ├── testing
│   │   ├── __init__.py
│   │   ├── test_constants
│   │   │   ├── C_chlorochromatii_CaD3.txt
│   │   │   ├── C_luteolum_DSM_273.txt
│   │   │   ├── test_genome_properties.txt
│   │   │   ├── test_genome_properties_two.txt
│   │   │   └── test_parse_genome_properties_assignments.py
│   │   ├── test_database_reference.py
│   │   ├── test_end_to_end.sh
│   │   ├── test_evidence.py
│   │   ├── test_functional_element.py
│   │   ├── test_genome_property.py
│   │   ├── test_lib.py
│   │   ├── test_literature_reference.py
│   │   ├── test_parse_genome_properties_assignments.py
│   │   ├── test_parse_genome_properties_file.py
│   │   ├── test_parse_longform.py
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

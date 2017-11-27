#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: Parses EBI genome properties flat files.
"""

from modules.lib import parse_genome_property_file
from modules.genome_property import build_genome_property_connections

genome_property_flat_file_path = '../genome-properties/docs/release/genomeProperties.txt'

with open(genome_property_flat_file_path) as genome_property_file:
    properties = parse_genome_property_file(genome_property_file)
    build_genome_property_connections(properties)


for genome_property in properties.values():
    parent_ids = [parent.id for parent in genome_property.parents]
    child_ids = [child.id for child in genome_property.children]

    if not parent_ids:
        parent_ids = "[ No Parent Genome Properties ]"

    if not child_ids:
        child_ids = "[ No Child Properties ]"

    print("\n" + genome_property.id + " (" + genome_property.name + ")" + " [" + genome_property.type + "]" +
          " " + str(parent_ids) + " " + str(child_ids))
    print('====================================================')
    for step in genome_property.steps:
        print(str(step) + "\n")


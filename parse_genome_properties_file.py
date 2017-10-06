#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The genome property class.
"""

from modules.lib import parse_genome_property_file

genome_property_flat_file_path = '../genome-properties/docs/release/genomeProperties.txt'

with open(genome_property_flat_file_path) as genome_property_file:
    properties = parse_genome_property_file(genome_property_file)

for genome_property in properties:
    print(genome_property)

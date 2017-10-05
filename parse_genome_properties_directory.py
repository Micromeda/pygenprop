#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The genome property class.
"""

from modules.lib import parse_genome_property_file

global_gen_prop_dir = '../genome-properties/docs/release/genomeProperties.txt'

properties = parse_genome_property_file(global_gen_prop_dir)

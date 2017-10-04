#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: The genome property class.
"""

import os
from modules.lib import parse_genome_property_file

global_gen_prop_dir = './data'
individual_gen_prop_dirs = [directory for directory in os.listdir(global_gen_prop_dir) if 'GenProp' in directory]

all_genome_properties = {}
for directory_name in individual_gen_prop_dirs:
    gen_prop_id = directory_name.strip()
    description_file_path = os.path.join(global_gen_prop_dir, gen_prop_id, 'DESC')
    status_file_path = os.path.join(global_gen_prop_dir, gen_prop_id, 'status')
    all_genome_properties[gen_prop_id] = parse_genome_property_file(description_file_path)[0]

print(all_genome_properties)

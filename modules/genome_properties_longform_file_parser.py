#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A parser for parsing genome properties longform files.
"""

from os.path import basename


def parse_genome_property_longform_file(longform_file):
    """
    Parses longform genome properties assignment files.

    :param longform_file: A longform genome properties assignment file handle object.
    :return: A dictionary of active steps per supported genome properties.
    """
    current_property_id = ''
    current_step_number = ''
    current_steps = []

    organism_properties = {}
    for line in longform_file:
        if 'PROPERTY:' in line:
            current_property_id = line.split(':')[1].strip()
        elif 'STEP NUMBER:' in line:
            current_step_number = int(line.split(':')[1].strip())
        elif 'RESULT:' in line:
            result_content = line.split(':')[1].strip().lower()

            if 'STEP' in line:
                if result_content == 'yes':
                    current_steps.append(current_step_number)
            else:
                if result_content == 'partial':
                    partial = True
                else:
                    partial = False

                if result_content in ['yes', 'partial']:
                    property_results = {'partial': partial,
                                        'supported_steps': current_steps}

                    organism_properties[current_property_id] = property_results
                    current_steps = []
        else:
            continue

    organism_properties['name'] = basename(longform_file.name)

    return organism_properties

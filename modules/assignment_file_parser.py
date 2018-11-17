#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2017)

Description: A parser for parsing genome properties longform files.
"""

from os.path import basename, splitext


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
            result_content = line.split(':')[1].strip().upper()

            if 'STEP' in line:
                if result_content == 'YES':
                    current_steps.append(current_step_number)
            else:
                property_results = {'result': result_content,
                                    'supported_steps': current_steps}

                organism_properties[current_property_id] = property_results
                current_steps = []

        else:
            continue

    organism_properties['name'] = splitext(basename(longform_file.name))[0]  # Get filename without path or extension.

    return organism_properties
